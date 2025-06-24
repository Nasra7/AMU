# conversations/models.py
from django.db import models
from personality_profiles.models import PersonalityProfile

class Conversation(models.Model):
    profile = models.ForeignKey(PersonalityProfile, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    context = models.JSONField(default=dict)

    def __str__(self):
        return f"Conversation with {self.profile.name} at {self.started_at}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    context_data = models.JSONField(default=dict, null=True, blank=True)  # Add this field
    
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.content[:50]}"