from ..models import Conversation, Message
from datetime import datetime

class ContextManager:
    @staticmethod
    async def create_conversation(profile_id):
        conversation = Conversation.objects.create(
            profile_id=profile_id,
            metadata={'start_time': datetime.now().isoformat()}
        )
        return conversation
    
    @staticmethod
    async def add_message(conversation_id, content, role, context=None):
        message = Message.objects.create(
            conversation_id=conversation_id,
            content=content,
            role=role,
            context=context or {}
        )
        return message
    
    @staticmethod
    async def get_conversation_context(conversation_id, message_limit=5):
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('-timestamp')[:message_limit]
        return list(messages.values())