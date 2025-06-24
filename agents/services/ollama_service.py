#modified code of ollama_service.py
import aiohttp
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        
    async def generate(self, prompt, system_prompt=None, context=None, model=None, language=None):
        """
        Generate a response using Ollama API
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            context: Optional context from previous exchanges
            model: The model to use (if None, will select based on language)
            language: The language code ('en' or 'tr')
            
        Returns:
            Tuple of (response text, new context)
        """
        try:
            # Select model based on language if not explicitly provided
            if not model:
                model = "llama3.2" if language == "en" else "qwen2.5"
            
            url = f"{self.base_url}/api/generate"
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
                
            # Add context if provided
            if context:
                payload["context"] = context
            
            logger.info(f"Using model: {model} for request in language: {language}")
            print(f"Using model: {model} for this request in language: {language}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status}, {error_text}")
                        return f"Error communicating with AI service: {response.status}", None
                    
                    response_data = await response.json()
                    
                    # Extract the response text and context
                    response_text = response_data.get("response", "").strip()
                    new_context = response_data.get("context", None)
                    
                    return response_text, new_context
                    
        except Exception as e:
            logger.exception(f"Error in Ollama service: {str(e)}")
            return f"Sorry, there was an error processing your request: {str(e)}", None