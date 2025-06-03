from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Optional
import os 
from dotenv import load_dotenv

load_dotenv()
DIALOGPT_MODEL = os.getenv('DIALOGPT_MODE')

class DialoGPTManager:
    def __init__(self):
        if True:
            self.tokenizer = AutoTokenizer.from_pretrained(DIALOGPT_MODEL)
            self.model = AutoModelForCausalLM.from_pretrained(DIALOGPT_MODEL)
        else:
            self.tokenizer = None
            self.model = None
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate conversational response using DialoGPT"""
        if not True or not self.model:
            return ""
        
        try:
            # Combine with context if available
            full_prompt = f"{context}\n{prompt}" if context else prompt
            
            inputs = self.tokenizer.encode(
                full_prompt + self.tokenizer.eos_token, 
                return_tensors="pt"
            )
            
            outputs = self.model.generate(
                inputs,
                max_length=150,
                do_sample=True,
                top_k=50,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            response = self.tokenizer.decode(
                outputs[:, inputs.shape[-1]:][0], 
                skip_special_tokens=True
            )
            
            return self._postprocess_response(response)
        
        except Exception as e:
            print(f"DialoGPT Error: {e}")
            return ""
    
    def _postprocess_response(self, text: str) -> str:
        """Clean up DialoGPT output"""
        # Remove incomplete sentences
        if text and text[-1] not in {'.', '!', '?'}:
            last_punct = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
            if last_punct > 0:
                text = text[:last_punct+1]
        
        # Basic safety filtering
        blacklist = ["politik", "rasis", "sara", "porn"]
        if any(bad_word in text.lower() for bad_word in blacklist):
            return "Maaf, saya tidak bisa membahas topik tersebut."
            
        return text.strip()