# personality_profiles/models.py
from django.db import models

class PersonalityProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    AGE_RANGE_CHOICES = [
        ('child', 'Child (0-12)'),
        ('teen', 'Teenager (13-19)'),
        ('young_adult', 'Young Adult (20-35)'),
        ('adult', 'Adult (36-50)'),
        ('senior', 'Senior (51+)'),
        ('unknown', 'Unknown/Not specified')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    background_story = models.TextField()
    personality_traits = models.JSONField()
    speech_patterns = models.JSONField()
    knowledge_base = models.JSONField()
    
    image = models.ImageField(upload_to='character_images/', null=True, blank=True)
    
    # New fields
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    age_range = models.CharField(
        max_length=15,
        choices=AGE_RANGE_CHOICES,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name