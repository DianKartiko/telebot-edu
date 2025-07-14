from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, BadRequest
from dotenv import load_dotenv
import logging
import asyncio
import hashlib
from typing import Optional, Dict, Any
# Import Own Library
from bot.utils.logger import Logging
from bot.utils.llm_integration import EnhancedLLMIntegration

load_dotenv()

Logging.setup_logging()

class MessageManager:
    """Helper class untuk mengelola edit message dengan optimal"""
    
    def __init__(self):
        self.message_cache: Dict[str, Dict[str, Any]] = {}
        self.max_message_length = 4000  # Buffer untuk safety
        self.min_edit_interval = 0.5  # Minimum interval antara edits (seconds)
        
    def _get_message_key(self, chat_id: int, message_id: int) -> str:
        """Generate unique key untuk message"""
        return f"{chat_id}_{message_id}"
    
    def _hash_text(self, text: str) -> str:
        """Generate hash untuk membandingkan konten"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _truncate_message(self, text: str) -> str:
        """Truncate message jika terlalu panjang"""
        if len(text) <= self.max_message_length:
            return text
        
        # Truncate dengan menambahkan indicator
        truncated = text[:self.max_message_length - 50]
        # Cari posisi terakhir yang aman untuk truncate (space atau newline)
        last_safe_pos = max(
            truncated.rfind(' '),
            truncated.rfind('\n'),
            truncated.rfind('.')
        )
        
        if last_safe_pos > self.max_message_length * 0.8:
            truncated = truncated[:last_safe_pos]
        
        return truncated + "\n\n... (pesan dipotong karena terlalu panjang)"
    
    async def safe_edit_message(self, 
                               context: ContextTypes.DEFAULT_TYPE,
                               chat_id: int,
                               message_id: int,
                               text: str,
                               parse_mode: str = None) -> bool:
        """
        Safely edit message dengan berbagai validasi
        Returns True jika berhasil, False jika gagal
        """
        try:
            # Validasi input
            if not text or not text.strip():
                logging.warning(f"Empty text for edit message {message_id}")
                return False
            
            # Truncate jika terlalu panjang
            text = self._truncate_message(text.strip())
            
            # Get message key
            msg_key = self._get_message_key(chat_id, message_id)
            
            # Check cache untuk menghindari edit yang sama
            if msg_key in self.message_cache:
                cached_hash = self.message_cache[msg_key].get('hash')
                current_hash = self._hash_text(text)
                
                if cached_hash == current_hash:
                    logging.debug(f"Skipping edit - same content for message {message_id}")
                    return True
                
                # Check interval untuk rate limiting
                last_edit_time = self.message_cache[msg_key].get('last_edit_time', 0)
                current_time = asyncio.get_event_loop().time()
                
                if current_time - last_edit_time < self.min_edit_interval:
                    await asyncio.sleep(self.min_edit_interval - (current_time - last_edit_time))
            
            # Attempt to edit message
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=parse_mode
            )
            
            # Update cache
            self.message_cache[msg_key] = {
                'hash': self._hash_text(text),
                'last_edit_time': asyncio.get_event_loop().time(),
                'text': text
            }
            
            logging.debug(f"Successfully edited message {message_id}")
            return True
            
        except BadRequest as e:
            error_msg = str(e).lower()
            
            # Handle specific BadRequest cases
            if "message is not modified" in error_msg:
                logging.debug(f"Message {message_id} not modified - same content")
                return True
                
            elif "message to edit not found" in error_msg:
                logging.warning(f"Message {message_id} not found for editing")
                return False
                
            elif "message can't be edited" in error_msg:
                logging.warning(f"Message {message_id} can't be edited (too old or deleted)")
                return False
                
            elif "message is too long" in error_msg:
                # Retry dengan pesan yang lebih pendek
                logging.warning(f"Message too long, retrying with shorter version")
                shorter_text = self._truncate_message(text[:self.max_message_length // 2])
                return await self.safe_edit_message(context, chat_id, message_id, shorter_text, parse_mode)
                
            else:
                logging.error(f"BadRequest error editing message {message_id}: {str(e)}")
                return False
                
        except NetworkError as e:
            logging.error(f"Network error editing message {message_id}: {str(e)}")
            return False
            
        except TimedOut as e:
            logging.error(f"Timeout editing message {message_id}: {str(e)}")
            return False
            
        except Exception as e:
            logging.error(f"Unexpected error editing message {message_id}: {str(e)}")
            return False
    
    async def safe_send_message(self, 
                                context: ContextTypes.DEFAULT_TYPE,
                                chat_id: int,
                                text: str,
                                parse_mode: str = None) -> Optional[int]:
        """
        Safely send message dan return message_id
        """
        try:
            text = self._truncate_message(text.strip())
            
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            
            # Cache initial message
            msg_key = self._get_message_key(chat_id, message.message_id)
            self.message_cache[msg_key] = {
                'hash': self._hash_text(text),
                'last_edit_time': asyncio.get_event_loop().time(),
                'text': text
            }
            
            return message.message_id
            
        except Exception as e:
            logging.error(f"Error sending message to chat {chat_id}: {str(e)}")
            return None
    
    def cleanup_cache(self, max_age_seconds: int = 3600):
        """Cleanup old cache entries"""
        current_time = asyncio.get_event_loop().time()
        keys_to_remove = []
        
        for key, data in self.message_cache.items():
            if current_time - data.get('last_edit_time', 0) > max_age_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.message_cache[key]
        
        if keys_to_remove:
            logging.info(f"Cleaned up {len(keys_to_remove)} old cache entries")


class HandlerMessage:
    def __init__(self):
        self.llm = EnhancedLLMIntegration()
        self.message_manager = MessageManager()
        self._cleanup_task = None
        self._cleanup_started = False
    
    def _ensure_cleanup_task(self):
        """Ensure cleanup task is started when event loop is available"""
        if not self._cleanup_started:
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
                self._cleanup_started = True
                logging.info("Periodic cleanup task started")
            except RuntimeError:
                # No event loop running, will try again later
                pass
    
    async def _periodic_cleanup(self):
        """Periodic cleanup untuk message cache"""
        try:
            while True:
                await asyncio.sleep(1800)  # Cleanup every 30 minutes
                self.message_manager.cleanup_cache()
                logging.debug("Periodic cleanup completed")
        except asyncio.CancelledError:
            logging.info("Periodic cleanup task cancelled")
            raise
        except Exception as e:
            logging.error(f"Error in periodic cleanup: {str(e)}")
    
    def stop_cleanup_task(self):
        """Stop the cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            self._cleanup_started = False
            logging.info("Cleanup task stopped")
    
    # Fungsi Untuk Menjalankan Bot
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Ensure cleanup task is started
        self._ensure_cleanup_task()
        
        text = '''
🤖 Halo! Selamat datang di Virtual Assistant Bot!

Saya asisten digital yang siap membantu Anda mencari informasi tentang:
    🔹 Lowongan magang
    🔹 Peluang pekerjaan
    🔹 Rekomendasi kursus/keterampilan

📢 Penting untuk diketahui:
Saya masih dalam tahap pengembangan aktif dan terus belajar. Saat ini saya memiliki beberapa keterbatasan:
    - Jawaban mungkin belum sempurna (terutama dalam Bahasa Indonesia)
    - Belum bisa memahami semua jenis pertanyaan
    - Kadang merespon dengan kurang akurat

💪 Tim developer saat ini sedang bekerja keras untuk meningkatkan kemampuan saya setiap hari!

💡 Tips: Gunakan kalimat sederhana dan kata kunci jelas untuk hasil terbaik.
            '''
        await self.message_manager.safe_send_message(context, update.effective_chat.id, text)

    # Fungsi Help
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = '''
**📌 Bantuan Penggunaan Bot**

**Perintah Tersedia:**
/start - Untuk memulai bot
/help - Tampilkan menu bantuan
/info - informasi bot telegram

🆘 **Panduan Penggunaan CareerBot:**

**🎯 Untuk Magang:**
• "Cari magang di [bidang] di [lokasi]"
• "Magang IT Jakarta"
• "Internship marketing"

**💼 Untuk Pekerjaan:**
• "Cari kerja [posisi] di [lokasi]"
• "Lowongan developer Jakarta"
• "Pekerjaan remote"

**📚 Untuk Kursus:**
• "Kursus [topik]"
• "Pelatihan Python"
• "Belajar digital marketing"

**💡 Tips:**
• Gunakan kata kunci yang spesifik
• Sebutkan lokasi jika perlu
• Tanyakan hal spesifik yang kamu butuhkan

Ada yang ingin kamu cari sekarang? 🚀
        '''
        await self.message_manager.safe_send_message(context, update.effective_chat.id, text)

    # Fungsi Info
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        info_text = (
"🤖 Informasi Teknis:\n\n"
"Model: SeaLLMs/SeaLLMs-v3-7B-Chat\n"
"Arsitektur: Menggunakan model dari qwen2 dengan 7.62B params\n"
"Library & Teknologi: python-telegram-bot v20 (Library), Inference Providers (Featherless AI)\n\n"
"Model ini dilatih terutama untuk SEA Region.\n"
"Mendukung multibahasa seperti bahasa Inggris, Indonesia, Vietnam, Thai, Tagalog, Malaysia, dsb."
        )
        await self.message_manager.safe_send_message(context, update.effective_chat.id, info_text)

    # Fungsi untuk streaming response dengan edit message
    async def stream_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                initial_text: str = "🤔 Sedang memproses...") -> Optional[int]:
        """
        Create initial message untuk streaming dan return message_id
        """
        return await self.message_manager.safe_send_message(
            context, 
            update.effective_chat.id, 
            initial_text
        )
    
    async def update_streaming_message(self, context: ContextTypes.DEFAULT_TYPE, 
                                        chat_id: int, message_id: int, text: str) -> bool:
        """
        Update streaming message dengan safe edit
        """
        return await self.message_manager.safe_edit_message(
            context, 
            chat_id, 
            message_id, 
            text
        )

    # Fungsi untuk menangani pesan pengguna dengan enhanced handling
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Enhanced message handler dengan optimized edit message
        """
        # Ensure cleanup task is started
        self._ensure_cleanup_task()
        
        # Validasi input dasar
        if not update or not update.message or not update.message.text:
            await self.message_manager.safe_send_message(
                context, 
                update.effective_chat.id, 
                "⚠️ Pesan tidak valid. Silakan kirim pesan teks."
            )
            return
        
        # Validasi user
        if not update.effective_user:
            await self.message_manager.safe_send_message(
                context, 
                update.effective_chat.id, 
                "⚠️ Tidak dapat mengidentifikasi pengguna."
            )
            return
        
        # Initialize context data
        if "streaming_message_id" not in context.chat_data:
            context.chat_data["streaming_message_id"] = None
        
        try:
            user_input = update.message.text.strip()
            
            # Validasi input tidak kosong
            if not user_input:
                await self.message_manager.safe_send_message(
                    context, 
                    update.effective_chat.id, 
                    "⚠️ Pesan tidak boleh kosong. Silakan kirim pertanyaan yang jelas."
                )
                return
            
            # Validasi panjang input
            if len(user_input) > 1000:
                await self.message_manager.safe_send_message(
                    context, 
                    update.effective_chat.id, 
                    "⚠️ Pesan terlalu panjang. Maksimal 1000 karakter."
                )
                return
            
            # Log user input
            logging.info(f"User {update.effective_user.id} sent: {user_input[:100]}...")
            
            # Create initial streaming message
            streaming_msg_id = await self.stream_response(update, context)
            if streaming_msg_id:
                context.chat_data["streaming_message_id"] = streaming_msg_id
            
            # Process dengan EnhancedLLMIntegration
            response = await self.llm.process_user_request(user_input, update, context)
            
            # Validasi response
            if not response or not response.strip():
                fallback_response = "⚠️ Maaf, tidak dapat memproses permintaan Anda saat ini. Silakan coba lagi."
                
                if streaming_msg_id:
                    await self.update_streaming_message(
                        context, 
                        update.effective_chat.id, 
                        streaming_msg_id, 
                        fallback_response
                    )
                else:
                    await self.message_manager.safe_send_message(
                        context, 
                        update.effective_chat.id, 
                        fallback_response
                    )
                return
            
            # Update final response jika ada streaming message
            if streaming_msg_id:
                success = await self.update_streaming_message(
                    context, 
                    update.effective_chat.id, 
                    streaming_msg_id, 
                    response
                )
                
                if not success:
                    # Fallback: send new message
                    await self.message_manager.safe_send_message(
                        context, 
                        update.effective_chat.id, 
                        response
                    )
            
            # Log successful response
            logging.info(f"Response sent to user {update.effective_user.id}: {len(response)} chars")
            
        except NetworkError as e:
            error_msg = "🌐 Masalah koneksi. Silakan coba lagi dalam beberapa saat."
            logging.error(f"Network error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except TimedOut as e:
            error_msg = "⏱️ Permintaan timeout. Silakan coba dengan pertanyaan yang lebih sederhana."
            logging.error(f"Timeout error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except BadRequest as e:
            error_msg = "❌ Format pesan tidak valid. Silakan coba lagi."
            logging.error(f"Bad request for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except ValueError as e:
            error_msg = "⚠️ Input tidak valid. Silakan periksa format pertanyaan Anda."
            logging.error(f"Value error for user {update.effective_user.id}: {str(e)}")
            await self._send_error_message(update, context, error_msg)
            
        except Exception as e:
            error_msg = "🚨 Terjadi kesalahan sistem. Tim teknis sedang memperbaiki."
            logging.error(f"Unexpected error for user {update.effective_user.id}: {str(e)}", exc_info=True)
            await self._send_error_message(update, context, error_msg)
    
    async def _send_error_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error_msg: str):
        """Helper method untuk mengirim pesan error dengan safe handling"""
        try:
            full_error_msg = f"{error_msg}\n\n💡 Gunakan /help untuk panduan atau /start untuk memulai ulang."
            
            # Cek apakah ada streaming message yang bisa di-edit
            streaming_msg_id = context.chat_data.get("streaming_message_id")
            if streaming_msg_id:
                success = await self.update_streaming_message(
                    context, 
                    update.effective_chat.id, 
                    streaming_msg_id, 
                    full_error_msg
                )
                if success:
                    return
            
            # Fallback: send new message
            await self.message_manager.safe_send_message(
                context, 
                update.effective_chat.id, 
                full_error_msg
            )
            
        except Exception as send_error:
            logging.error(f"Failed to send error message: {str(send_error)}")
            # Final fallback: try simple message
            try:
                await self.message_manager.safe_send_message(
                    context, 
                    update.effective_chat.id, 
                    "⚠️ Sistem sedang bermasalah. Silakan coba lagi."
                )
            except Exception as fallback_error:
                logging.error(f"Failed to send fallback message: {str(fallback_error)}")
            
    # Fungsi error handler yang lebih comprehensive
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced error handler dengan safe message handling"""
        
        # Log error dengan detail
        logging.error(
            f'Exception while handling update {update.update_id if update else "Unknown"}: {context.error}',
            exc_info=context.error
        )

        # Jika update tidak valid, tidak bisa mengirim pesan
        if not update or not hasattr(update, 'effective_message') or not update.effective_message:
            logging.error("Invalid update object, cannot send error message to user")
            return

        error = context.error
        user_message = "⚠️ Maaf, terjadi kesalahan."

        # Kategorisasi error berdasarkan tipe
        if isinstance(error, NetworkError):
            user_message = "🌐 Masalah koneksi jaringan. Silakan coba lagi dalam beberapa saat."
        elif isinstance(error, TimedOut):
            user_message = "⏱️ Waktu respons habis. Silakan coba dengan pertanyaan yang lebih sederhana."
        elif isinstance(error, BadRequest):
            user_message = "❌ Format permintaan tidak valid. Silakan periksa input Anda."
        elif isinstance(error, ValueError):
            user_message = "⚠️ Input tidak valid. Silakan coba dengan format yang berbeda."
        elif isinstance(error, IndexError):
            user_message = "📝 Terjadi kesalahan dalam pemrosesan data. Silakan coba lagi."
        elif "rate limit" in str(error).lower():
            user_message = "🚦 Terlalu banyak permintaan. Silakan tunggu sebentar sebelum mencoba lagi."
        elif "timeout" in str(error).lower():
            user_message = "⏱️ Sistem sedang lambat. Silakan coba lagi dalam beberapa saat."
        else:
            user_message = "🚨 Terjadi kesalahan sistem. Tim teknis sedang memperbaiki."

        # Kirim pesan error dengan safe handling
        try:
            full_message = f"{user_message}\n\n💡 Gunakan /help untuk panduan atau /start untuk memulai ulang."
            await self.message_manager.safe_send_message(
                context, 
                update.effective_chat.id, 
                full_message
            )
            
        except Exception as send_error:
            logging.error(f'Failed to send error message to user: {str(send_error)}')

        # Log statistik error untuk monitoring
        error_type = type(error).__name__
        user_id = update.effective_user.id if update.effective_user else "Unknown"
        logging.info(f"Error handled: {error_type} for user {user_id}")