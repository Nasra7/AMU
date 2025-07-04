#chat/view.py
from asgiref.sync import sync_to_async
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from personality_profiles.models import PersonalityProfile
from conversations.models import Conversation, Message
from django.contrib import messages

from agents.services.response_generator_agent import ResponseGeneratorAgent
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

# Create sync_to_async versions of all database operations
get_profile_async = sync_to_async(get_object_or_404)
create_message_async = sync_to_async(Message.objects.create)
save_conversation_async = sync_to_async(lambda x: x.save())

def index(request):
    try:
        profiles = PersonalityProfile.objects.all().order_by('name')
        return render(request, 'chat/index.html', {
            'profiles': profiles,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        return render(request, 'chat/index.html', {
            'profiles': [],
            'error': 'Unable to load character profiles. Please try again later.'
        })

def chat_interface(request, profile_id=None):
    try:
        # Get conversation_id from query params if available
        conversation_id = request.GET.get('conversation_id')
        
        if conversation_id:
            # Load existing conversation
            conversation = get_object_or_404(Conversation, id=conversation_id)
            profile = conversation.profile
        elif profile_id:
            # Start new conversation with selected profile
            profile = get_object_or_404(PersonalityProfile, id=profile_id)
            conversation = Conversation.objects.create(profile=profile)
        else:
            # Redirect to profile selection if no profile or conversation specified
            return redirect('index')
        
        # Get last 50 messages if any
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')[:50]
        
        return render(request, 'chat/chat_interface.html', {
            'profile': profile,
            'conversation': conversation,
            'messages': messages,
            'error': None
        })
    except ObjectDoesNotExist:
        return render(request, 'chat/index.html', {
            'profiles': PersonalityProfile.objects.all(),
            'error': 'Selected character or conversation not found.'
        })
    except Exception as e:
        logger.error(f"Error in chat_interface view: {str(e)}")
        return render(request, 'chat/index.html', {
            'profiles': PersonalityProfile.objects.all(),
            'error': 'Unable to start chat. Please try again later.'
        })

@csrf_exempt
async def send_message(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        language = data.get('language', 'en')  # Add language parameter with English as default

        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'Message cannot be empty'
            }, status=400)

        if not conversation_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Conversation ID is required'
            }, status=400)

        # Get conversation using sync_to_async
        conversation = await get_profile_async(Conversation, id=conversation_id)
        
        # Save user message using sync_to_async
        user_msg = await create_message_async(
            conversation=conversation,
            content=user_message,
            is_user=True
        )

        # Generate response
        try:
            profile = await sync_to_async(lambda: conversation.profile)()
            agent = ResponseGeneratorAgent(profile, language=language)  # Pass language to agent
            response_text, new_context = await agent.generate_response(
                user_message,
                conversation.context,
                language  # Pass language to generate_response method
            )
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to generate response. Please try again.'
            }, status=500)

        # Save bot message using sync_to_async
        bot_msg = await create_message_async(
            conversation=conversation,
            content=response_text,
            is_user=False,
            context_data=json.dumps(new_context) if isinstance(new_context, dict) else None
        )

        # Update conversation context
        conversation.context = new_context if not isinstance(new_context, dict) else json.dumps(new_context)
        await save_conversation_async(conversation)

        # Format timestamp as string to include in response
        timestamp = await sync_to_async(lambda: bot_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'))()

        return JsonResponse({
            'status': 'success',
            'response': response_text,
            'conversation_id': conversation.id,
            'message_id': bot_msg.id,
            'timestamp': timestamp,
            'language': language  # Include language in response for client-side handling
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in send_message view: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)

# Non-async version for compatibility or fallback
@csrf_exempt
@require_POST
def send_message_sync(request):
    """Synchronous version of send_message for compatibility"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        language = data.get('language', 'en')  # Get language preference, default to English
        
        if not user_message or not conversation_id:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
        
        # Get conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Save user message
        user_message_obj = Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Generate response using agent with specified language
        agent = ResponseGeneratorAgent(conversation.profile, language=language)
        
        # Use asyncio to call the async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response_text, context_data = loop.run_until_complete(
                agent.generate_response(user_message, conversation.context, language)
            )
        finally:
            loop.close()
        
        # Save bot response
        bot_message = Message.objects.create(
            conversation=conversation,
            content=response_text,
            is_user=False,
            context_data=json.dumps(context_data) if isinstance(context_data, dict) else None
        )
        
        # Update conversation context
        conversation.context = context_data if not isinstance(context_data, dict) else json.dumps(context_data)
        conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'response': response_text,
            'conversation_id': conversation.id,
            'message_id': bot_message.id,
            'timestamp': bot_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'language': language
        })
        
    except Exception as e:
        logger.error(f"Error in send_message_sync: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def add_character(request):
    """View for adding a new character profile by regular users"""
    if request.method == 'POST':
        try:
            # Extract form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            name = f"{first_name} {last_name}".strip()
            description = request.POST.get('description')
            background_story = request.POST.get('background_story')
            
            # Convert text areas to JSON for JSONField storage
            personality_traits = {
                "traits": request.POST.get('personality_traits').strip().split(',')
            }
            
            speech_patterns = {
                "patterns": request.POST.get('speech_pattern').strip()
            }
            
            # Parse knowledge base into structured JSON
            knowledge_text = request.POST.get('knowledge_base').strip()
            knowledge_items = knowledge_text.split(',')
            knowledge_base = {}
            
            for item in knowledge_items:
                if ':' in item:
                    key, value = item.split(':', 1)
                    knowledge_base[key.strip()] = value.strip()
                else:
                    # If no level specified, store as general knowledge
                    knowledge_base[item.strip()] = "general"
            
            age_range = request.POST.get('age_range')
            gender = request.POST.get('gender')
            
            # Create new personality profile
            profile = PersonalityProfile(
                name=name,
                description=description,
                background_story=background_story,
                personality_traits=personality_traits,
                speech_patterns=speech_patterns,
                knowledge_base=knowledge_base,
                age_range=age_range,
                gender=gender,
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
                
            profile.save()
            
            messages.success(request, f"Character '{name}' has been created successfully!")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error creating character: {str(e)}")
    
    return render(request, 'chat/new_character.html')