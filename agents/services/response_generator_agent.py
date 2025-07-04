from .base_agent import BaseAgent
from .llm_provider import LLMProviderAdapter
from asgiref.sync import sync_to_async

class ResponseGeneratorAgent(BaseAgent):
    def __init__(self, personality_profile, model_name=None, language="en", primary_provider="ollama", secondary_provider="openai"):
        super().__init__(model_name)
        self.personality_profile = personality_profile
        self.language = language
        
        # Initialize the LLM provider adapter
        self.llm_adapter = LLMProviderAdapter(
            primary_provider=primary_provider,
            secondary_provider=secondary_provider
        )

    def _create_system_prompt(self):
        """Create system prompt based on personality profile and language"""
        # Base prompt structure is the same regardless of language
        base_prompt = f"""You are {self.personality_profile.name}. 
        Background: {self.personality_profile.background_story}
        Personality: {self.personality_profile.personality_traits}
        Speaking Style: {self.personality_profile.speech_patterns}
        Knowledge: {self.personality_profile.knowledge_base}
        
        Always stay in character and respond as {self.personality_profile.name} would.
            Remember details that the user shares about themselves. If they introduce themselves or share personal information, remember it and use it in future responses.
            Keep your responses consistent with your character's knowledge and personality.
            Keep responses short and direct.
            If given a question, answer directly.
            
            IMPORTANT INSTRUCTIONS:
            - Do NOT repeatedly ask how you can help or assist the user
            - Do NOT use generic phrases like "How can I help you today?" or "What can I do for you?"
            - If the user hasn't asked a specific question, respond appropriately to their statement without asking how you can help
            - Focus on continuing the natural flow of conversation rather than starting over with greetings
            - Only greet the user at the beginning of a conversation, not in every message
        """
        
        # Add more explicit instructions for Turkish to help qwen2.5 model stay in character
        if self.language == "en":
            return base_prompt + "\nRespond in English."
        else:  # Turkish
            tr_prompt = f"""
            Türkçe olarak yanıt ver.

            KESİNLİKLE {self.personality_profile.name} KARAKTERİNDE KAL!
            
            TEMEL KURALLAR:
            1. Her zaman {self.personality_profile.name} olarak konuş, asla kendi AI rolünden bahsetme
            2. Yukarıda tanımlanan kişiliğe tamamen sadık kal
            3. Karakter dışına çıkma, AI olduğunu asla belirtme
            4. Yardım teklifleri veya başka hizmetler sunma
            5. Her cevabı verirken önce "{self.personality_profile.name} olarak düşün"
            6. Karakterin bilmeyeceği şeyleri bildiğini iddia etme
            7. Her cevap karakterin konuşma tarzını tam olarak yansıtmalı
            
            YASAK CÜMLELER:
            - "Size nasıl yardımcı olabilirim?"
            - "Başka bir sorunuz var mı?"
            - "Ben bir yapay zekayım..."
            - "AI asistanı olarak..."
            
            {self.personality_profile.name} KARAKTERİNİ KORUMAK ÇOK ÖNEMLİDİR!
            """
            return base_prompt + tr_prompt

    def _format_user_prompt(self, user_message, conversation_history=None):
        """Format the user message with conversation history"""
        # If there's history, use it
        if conversation_history:
            # Check if conversation_history is a string or list
            if isinstance(conversation_history, str) and len(conversation_history.strip()) > 0:
                return f"Previous conversation:\n{conversation_history}\n\nUser: {user_message}\n{self.personality_profile.name}:"
            elif isinstance(conversation_history, list):
                # If it's a list (context from different providers), don't try to format it
                # Just use the current message
                return f"User: {user_message}\n{self.personality_profile.name}:"
        # Otherwise just use the current message
        return f"User: {user_message}\n{self.personality_profile.name}:"

    async def process(self, user_message, conversation_history=None, language=None, provider=None):
        """Process user message and generate response"""
        try:
            # Update language if provided
            if language:
                self.language = language
                
            system_prompt = self._create_system_prompt()
            formatted_prompt = self._format_user_prompt(user_message, conversation_history)

            # If conversation_history is already a list, it might be a valid context
            # Otherwise, pass None as context
            context_to_pass = conversation_history if isinstance(conversation_history, list) else None
            
            # Determine model based on language (let providers handle this)
            model = None
            
            response, new_context = await self.llm_adapter.generate(
                prompt=formatted_prompt,
                system_prompt=system_prompt,
                context=context_to_pass,
                model=model,
                language=self.language,
                provider=provider
            )
            
            return response, new_context
        except Exception as e:
            raise Exception(f"Error in response generation: {str(e)}")

    async def generate_response(self, user_message, conversation_history=None, language=None, provider=None):
        """Main method to generate responses"""
        return await self.process(user_message, conversation_history, language, provider)
    
    def get_available_providers(self):
        """Get available providers"""
        return self.llm_adapter.get_available_providers()
    
    def set_primary_provider(self, provider_name):
        """Set primary provider"""
        self.llm_adapter.set_primary_provider(provider_name)
    
    def set_secondary_provider(self, provider_name):
        """Set secondary provider"""
        self.llm_adapter.set_secondary_provider(provider_name)