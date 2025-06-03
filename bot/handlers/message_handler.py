from telegram import Update
from telegram.ext import ContextTypes
from bot.modules.response_generator import ResponseGenerator
from bot.utils.logger import log_interaction, get_current_time
import logging

response_generator = ResponseGenerator()
user_contexts = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message handler"""
    user_id = update.effective_user.id
    user_input = update.message.text
    
    # Get or create user context
    context_data = user_contexts.get(user_id, {})
    
    # Generate response
    response = response_generator.generate_response(user_input, context_data)
    
    # Send response
    await update.message.reply_text(response['text'], parse_mode="Markdown")
    
    # Log interaction
    log_interaction(user_id, user_input, response['text'], response['source'])
    
    # Update context
    context_data['last_interaction'] = get_current_time()
    user_contexts[user_id] = context_data

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logging.error(f"Update {update} caused error {context.error}")
