#conversations/views.py
import django.conf
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from django.conf import settings
from conversations.services.txt_to_speech import TTSService

@require_POST
@csrf_exempt  # If you're calling this from JS with CSRF token, you can remove this
def txt_to_speech(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        personality_id = data.get('personality_id')
        
        if not text:
            return JsonResponse({'success': False, 'error': 'No text provided'})
        
        tts_service = TTSService()
        audio_url = tts_service.convert_text_to_audio_file(text, personality_id)
        
        return JsonResponse({
            'success': True,
            'audio_url': audio_url
        })
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def delete_audio(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({'success': False, 'error': 'No filename provided'})
        
        # Ensure we're only deleting files from the audio directory
        if not filename.startswith('tts_') or not filename.endswith('.mp3'):
            return JsonResponse({'success': False, 'error': 'Invalid filename format'})
        
        # Construct the path to the file
        media_path = os.path.join('audio', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, media_path)
        
        # Check if file exists and delete it
        if os.path.exists(full_path):
            os.remove(full_path)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'File not found'})
    
    except Exception as e:
        print(f"Delete Audio Error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})