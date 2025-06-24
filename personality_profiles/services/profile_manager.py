#personaliy_profiles/services/profile_manager.py
from ..models import PersonalityProfile, ProfileAttribute

class ProfileManager:
    @staticmethod
    async def create_profile(name, profile_type, data_sources):
        profile = PersonalityProfile.objects.create(
            name=name,
            profile_type=profile_type,
            data_sources=data_sources,
            behavioral_patterns={},
            speech_patterns={}
        )
        return profile
    
    @staticmethod
    async def update_profile(profile_id, attributes):
        profile = PersonalityProfile.objects.get(id=profile_id)
        for attr_type, value in attributes.items():
            ProfileAttribute.objects.create(
                profile=profile,
                attribute_type=attr_type,
                value=value['value'],
                confidence_score=value.get('confidence_score', 1.0),
                source=value.get('source', 'system')
            )
        return profile