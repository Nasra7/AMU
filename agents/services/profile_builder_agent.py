from .base_agent import BaseAgent
import json

class ProfileBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__("ProfileBuilder", "profile_builder")
    
    async def process_task(self, task_data):
        # Extract personality traits and patterns
        traits_prompt = f"""
        Analyze the following data and extract key personality traits and patterns:
        {json.dumps(task_data['raw_data'])}
        Focus on:
        1. Communication style
        2. Behavioral patterns
        3. Common phrases or expressions
        4. Decision-making patterns
        """
        
        analysis = await self.ollama_service.generate_response(traits_prompt)
        
        return {
            'status': 'success',
            'profile_data': {
                'traits': analysis,
                'confidence_score': 0.85,  # You might want to implement proper scoring
                'source_data': task_data['raw_data']
            }
        }
