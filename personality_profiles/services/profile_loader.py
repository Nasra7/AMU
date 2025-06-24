# personality_profiles/services/profile_loader.py
import json
from ..models import PersonalityProfile

class ProfileLoader:
    @staticmethod
    def load_from_json(file_path):
        """Load a personality profile from a JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            profile = PersonalityProfile(
                name=data.get("name", ""),
                description=data.get("description", ""),
                background_story=data.get("background_story", ""),
                personality_traits={
                    "traits": data.get("Personality traits", []),
                    "age": data.get("age", ""),
                    "job": data.get("job", "")
                },
                speech_patterns={
                    "speaking_notes": data.get("speaking notes", []),
                    "tone": data.get("tone", "neutral")
                },
                knowledge_base={
                    "hobbies": data.get("hobbies", []),
                    "skills": data.get("skills", [])
                }
            )
            profile.save()
            return profile
        except Exception as e:
            raise Exception(f"Error loading profile from JSON: {str(e)}")

    @staticmethod
    def create_json_template():
        """Create a template JSON structure for a personality profile"""
        template = {
            "name": "Character Name",
            "description": "Physical description",
            "background_story": "Character's background",
            "job": "Character's occupation",
            "age": "Character's age",
            "Personality traits": [
                "trait1",
                "trait2"
            ],
            "hobbies": [
                "hobby1",
                "hobby2"
            ],
            "speaking notes": [
                "note1",
                "note2"
            ],
            "tone": "Character's speaking tone"
        }
        return template