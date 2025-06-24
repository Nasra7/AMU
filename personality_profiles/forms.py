##personality_profiles/forms.py
from django import forms
from .models import PersonalityProfile

class PersonalityProfileForm(forms.ModelForm):
    class Meta:
        model = PersonalityProfile
        fields = [
            'name', 
            'description', 
            'background_story',
            'gender',
            'age_range',
            'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'background_story': forms.Textarea(attrs={'rows': 6}),
        }
    
    # These fields will be handled separately as they're JSONField in the model
    personality_traits = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Enter personality traits as comma-separated values (e.g., friendly, curious, witty)",
        required=False
    )
    
    speech_patterns = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Describe how this character speaks (e.g., uses lots of slang, speaks formally, etc.)",
        required=False
    )
    
    knowledge_base = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Enter what the character knows about or is an expert in",
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Convert text inputs to JSON format
        personality_traits = cleaned_data.get('personality_traits', '')
        speech_pattern = cleaned_data.get('speech_patterns', '')
        knowledge_base = cleaned_data.get('knowledge_base', '')
        
        cleaned_data['personality_traits'] = {
            'traits': [trait.strip() for trait in personality_traits.split(',') if trait.strip()]
        }
        
        cleaned_data['speech_patterns'] = {
            'description': speech_pattern
        }
        
        cleaned_data['knowledge_base'] = {
            'areas': [area.strip() for area in knowledge_base.split(',') if area.strip()]
        }
        
        return cleaned_data