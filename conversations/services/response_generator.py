from agents.services.response_generator_agent import ResponseGeneratorAgent
from personality_profiles.services.profile_manager import ProfileManager

class ResponseGenerator:
    """Service for generating responses to user messages"""
    
    def __init__(self):
        self.profile_manager = ProfileManager()
        
    async def generate_response(self, user_message, personality_id, conversation_history=None):
        """
        Generate a response to a user message
        
        Args:
            user_message (str): The user's message
            personality_id (int): The ID of the personality to use
            conversation_history (str, optional): Previous conversation history
            
        Returns:
            tuple: (text_response, audio_url)
        """
        try:
            # Get the personality profile
            personality_profile = self.profile_manager.get_profile(personality_id)
            
            if not personality_profile:
                raise Exception(f"Personality profile with ID {personality_id} not found")
            
            # Create the agent
            agent = ResponseGeneratorAgent(personality_profile)
            
            # Generate the response
            response, context, audio_url = await agent.generate_response(user_message, conversation_history)
            
            return {
                "text": response,
                "audio_url": audio_url,
                "context": context
            }
            
        except Exception as e:
            print(f"Error in response generation: {str(e)}")
            return {
                "text": "I'm sorry, I couldn't generate a response at this time.",
                "audio_url": None,
                "context": None
            }