# personality_profiles/management/commands/load_profiles.py
from django.core.management.base import BaseCommand
import os
import json
from personality_profiles.models import PersonalityProfile

class Command(BaseCommand):
    help = 'Load personality profiles from JSON files'

    def handle(self, *args, **options):
        data_dir = os.path.join('personality_profiles', 'data')
        
        # Create directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.stdout.write(self.style.SUCCESS(f'Created directory: {data_dir}'))
        
        # Load all JSON files in the directory
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    # Create or update profile
                    profile, created = PersonalityProfile.objects.update_or_create(
                        name=data.get('name'),
                        defaults={
                            'description': data.get('description', ''),
                            'background_story': data.get('background_story', ''),
                            'personality_traits': {
                                'traits': data.get('Personality traits', []),
                                'age': data.get('age', ''),
                                'job': data.get('job', '')
                            },
                            'speech_patterns': {
                                'speaking_notes': data.get('speaking notes', []),
                                'tone': data.get('tone', 'neutral')
                            },
                            'knowledge_base': {
                                'hobbies': data.get('hobbies', []),
                            }
                        }
                    )
                    
                    action = 'Created' if created else 'Updated'
                    self.stdout.write(
                        self.style.SUCCESS(f'{action} profile: {profile.name}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error loading {filename}: {str(e)}')
                    )