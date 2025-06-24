from elevenlabs.client import ElevenLabs
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from personality_profiles.models import PersonalityProfile

class TTSService:
    def __init__(self, api_key=settings.ELEVENLABS_API_KEY):
        self.client = ElevenLabs(
            api_key=api_key
        )
        self.default_voice_id = settings.ELEVENLABS_DEFAULT_VOICE
        self.default_model_id = "eleven_multilingual_v2"
        
        # Voice mapping based on gender and age range from settings
        voices = settings.ELEVENLABS_VOICE_IDS
        self.voice_mapping = {
            # Male voices
            ('M', 'child'): voices.get('male_child', self.default_voice_id),
            ('M', 'teen'): voices.get('male_teen', self.default_voice_id),
            ('M', 'young_adult'): voices.get('male_young_adult', self.default_voice_id),
            ('M', 'adult'): voices.get('male_adult', self.default_voice_id),
            ('M', 'senior'): voices.get('male_senior', self.default_voice_id),
            
            # Female voices
            ('F', 'child'): voices.get('female_child', self.default_voice_id),
            ('F', 'teen'): voices.get('female_teen', self.default_voice_id),
            ('F', 'young_adult'): voices.get('female_young_adult', self.default_voice_id),
            ('F', 'adult'): voices.get('female_adult', self.default_voice_id),
            ('F', 'senior'): voices.get('female_senior', self.default_voice_id),
        }
    
    def get_voice_id_for_personality(self, personality_id):
        """Get the appropriate voice ID based on personality attributes"""
        try:
            # Get the personality profile
            personality = PersonalityProfile.objects.get(id=personality_id)
            
            # Get gender and age_range
            gender = personality.gender
            age_range = personality.age_range
            
            # Default to adult male if gender or age_range not specified
            if not gender or gender not in ['M', 'F']:
                gender = 'M'
            if not age_range or age_range not in ['child', 'teen', 'young_adult', 'adult', 'senior']:
                age_range = 'adult'
            
            # Lookup voice ID from mapping
            voice_key = (gender, age_range)
            return self.voice_mapping.get(voice_key, self.default_voice_id)
            
        except PersonalityProfile.DoesNotExist:
            # If personality doesn't exist, return default voice
            return self.default_voice_id
        except Exception as e:
            # Handle any other errors
            print(f"Error getting voice ID: {e}")
            return self.default_voice_id
    
    def convert_text_to_audio_file(self, text, personality_id=None):
        """Convert text to audio and save as a file"""
        voice_id = self.default_voice_id
        model_id = self.default_model_id
        
        # Select voice based on personality if personality_id is provided
        if personality_id:
            voice_id = self.get_voice_id_for_personality(personality_id)
        
        # Get audio stream
        audio_stream = self.client.text_to_speech.convert_as_stream(
            text=text,
            voice_id=voice_id,
            model_id=model_id
        )
        
        # Read the stream into bytes
        audio_bytes = b''
        for chunk in audio_stream:
            audio_bytes += chunk
        
        # Generate a unique filename
        filename = f"tts_{uuid.uuid4()}.mp3"
        
        # Path to save in your Django media directory
        media_path = os.path.join('audio', filename)
        
        # Save the file to your storage
        path = default_storage.save(media_path, ContentFile(audio_bytes))
        
        # Get the URL
        url = default_storage.url(path)
        
        return url