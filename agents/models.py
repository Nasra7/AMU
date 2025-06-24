from django.db import models
from personality_profiles.models import PersonalityProfile

class Agent(models.Model):
    name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=50)  # data_collector, profile_builder, response_generator
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.agent_type}: {self.name}"

class AgentTask(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)  # pending, running, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)