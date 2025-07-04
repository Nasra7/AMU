import aiohttp
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

def get_setting(setting_name, default_value=None):
    """Safely get Django settings with fallback to environment variables"""
    try:
        from django.conf import settings
        return getattr(settings, setting_name, default_value)
    except Exception:
        # If Django settings aren't configured, try environment variables
        env_name = setting_name
        return os.environ.get(env_name, default_value)

class LLMProviderBase(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt, system_prompt=None, context=None, model=None, language=None):
        pass

class OllamaProvider(LLMProviderBase):
    """Ollama provider implementation"""
    
    def __init__(self):
        self.base_url = get_setting("OLLAMA_BASE_URL", "http://localhost:11434")
        
    async def generate(self, prompt, system_prompt=None, context=None, model=None, language=None):
        try:
            # Select model based on language if not explicitly provided
            if not model:
                model = "llama3.2" if language == "en" else "qwen2.5"
            
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            if context:
                payload["context"] = context
            
            logger.info(f"Ollama - Using model: {model} for language: {language}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status}, {error_text}")
                        raise Exception(f"Ollama API error: {response.status}")
                    
                    response_data = await response.json()
                    response_text = response_data.get("response", "").strip()
                    new_context = response_data.get("context", None)
                    
                    return response_text, new_context
                    
        except Exception as e:
            logger.exception(f"Error in Ollama provider: {str(e)}")
            raise

class OpenAIProvider(LLMProviderBase):
    """OpenAI provider implementation"""
    
    def __init__(self):
        self.api_key = get_setting("OPENAI_API_KEY", None)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            raise Exception("OPENAI_API_KEY not found in settings or environment variables")
    
    async def generate(self, prompt, system_prompt=None, context=None, model=None, language=None):
        try:
            # Select model based on language if not explicitly provided
            if not model:
                model = "gpt-4o-mini" if language == "en" else "gpt-4o-mini"
            
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add context if provided (convert context to conversation history)
            if context and isinstance(context, list):
                # Convert context to messages if it's a list
                for ctx_item in context[-5:]:  # Only use last 5 exchanges
                    if isinstance(ctx_item, dict):
                        messages.append(ctx_item)
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"OpenAI - Using model: {model} for language: {language}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status}, {error_text}")
                        raise Exception(f"OpenAI API error: {response.status}")
                    
                    response_data = await response.json()
                    response_text = response_data["choices"][0]["message"]["content"].strip()
                    
                    # Create new context (for OpenAI, we'll maintain a simple message history)
                    new_context = messages + [{"role": "assistant", "content": response_text}]
                    
                    return response_text, new_context
                    
        except Exception as e:
            logger.exception(f"Error in OpenAI provider: {str(e)}")
            raise

class LLMProviderAdapter:
    """Adapter that manages multiple LLM providers with fallback"""
    
    def __init__(self, primary_provider="ollama", secondary_provider="openai"):
        self.providers = {}
        self.primary_provider = primary_provider
        self.secondary_provider = secondary_provider
        
        # Initialize providers
        try:
            self.providers["ollama"] = OllamaProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama provider: {e}")
            
        try:
            self.providers["openai"] = OpenAIProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {e}")
    
    async def generate(self, prompt, system_prompt=None, context=None, model=None, language=None, provider=None):
        """
        Generate response using specified provider or with fallback
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            context: Optional context from previous exchanges
            model: The model to use
            language: The language code ('en' or 'tr')
            provider: Specific provider to use (overrides primary/secondary logic)
            
        Returns:
            Tuple of (response text, new context)
        """
        # Determine which provider to use
        if provider:
            providers_to_try = [provider]
        else:
            providers_to_try = [self.primary_provider, self.secondary_provider]
        
        last_error = None
        
        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue
                
            try:
                logger.info(f"Attempting to use provider: {provider_name}")
                response, new_context = await self.providers[provider_name].generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    context=context,
                    model=model,
                    language=language
                )
                logger.info(f"Successfully used provider: {provider_name}")
                return response, new_context
                
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
        
        # If all providers failed
        if last_error:
            return f"Sorry, there was an error processing your request: {str(last_error)}", None
        else:
            return "Sorry, no available providers to process your request.", None
    
    def get_available_providers(self):
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def set_primary_provider(self, provider_name):
        """Set the primary provider"""
        if provider_name in self.providers:
            self.primary_provider = provider_name
        else:
            raise ValueError(f"Provider {provider_name} not available")
    
    def set_secondary_provider(self, provider_name):
        """Set the secondary provider"""
        if provider_name in self.providers:
            self.secondary_provider = provider_name
        else:
            raise ValueError(f"Provider {provider_name} not available")