# # terminal_chat.py
import asyncio
import os
import django
from asgiref.sync import sync_to_async

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AMU.settings')
django.setup()

from personality_profiles.models import PersonalityProfile
from agents.services.response_generator_agent import ResponseGeneratorAgent
from conversations.models import Conversation, Message

# Create sync_to_async versions of database operations
get_all_profiles = sync_to_async(lambda: list(PersonalityProfile.objects.all()))
create_conversation = sync_to_async(Conversation.objects.create)
create_message = sync_to_async(Message.objects.create)
save_conversation = sync_to_async(lambda x: x.save())
get_conversation_messages = sync_to_async(lambda conv: list(Message.objects.filter(conversation=conv).order_by('timestamp')))

async def display_profile_info(profile):
    """Display the character's information before starting chat"""
    print("\n" + "="*50)
    print(f"Character Profile: {profile.name}")
    print("="*50)
    print(f"Description: {profile.description}")
    print(f"Background: {profile.background_story}")
    print(f"Personality: {profile.personality_traits}")
    print(f"Speech Patterns: {profile.speech_patterns}")
    print("="*50 + "\n")

async def build_conversation_history(conversation):
    """Build a conversation history string from messages"""
    messages = await get_conversation_messages(conversation)
    history = ""
    
    for msg in messages:
        sender = "User" if msg.is_user else conversation.profile.name
        history += f"{sender}: {msg.content}\n"
    
    return history

async def chat_session():
    try:
        # Get and display available profiles
        profiles = await get_all_profiles()
        print("\nAvailable characters:")
        for idx, profile in enumerate(profiles, 1):
            print(f"{idx}. {profile.name}")
        
        # Let user choose a profile
        while True:
            try:
                choice = int(input("\nChoose a character number: "))
                if 1 <= choice <= len(profiles):
                    profile = profiles[choice-1]
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Display chosen profile info
        await display_profile_info(profile)
        
        # Create a new conversation
        conversation = await create_conversation(profile=profile)
        
        # Create response generator
        agent = ResponseGeneratorAgent(profile)
        
        print("Chat started! Type 'quit' to exit or 'info' to see character details again.\n")
        
        while True:
            # Get user input
            user_message = input("You: ").strip()
            
            if user_message.lower() == 'quit':
                break
            
            if user_message.lower() == 'info':
                await display_profile_info(profile)
                continue
            
            # Save user message
            await create_message(
                conversation=conversation,
                content=user_message,
                is_user=True
            )
            
            print(f"\n{profile.name} is typing...")
            
            try:
                # Build conversation history
                conversation_history = await build_conversation_history(conversation)
                
                # Generate response with full history context
                response_text, new_context = await agent.generate_response(
                    user_message,
                    conversation_history
                )
                
                await create_message(
                    conversation=conversation,
                    content=response_text,
                    is_user=False
                )
                
                # Update conversation context
                conversation.context = new_context
                await save_conversation(conversation)
                
                print(f"{profile.name}: {response_text}\n")
                
            except Exception as e:
                print(f"Error generating response: {str(e)}\n")
                
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("\nInitializing chat interface...")
    asyncio.run(chat_session())
