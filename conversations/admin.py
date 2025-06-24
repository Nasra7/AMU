#conversations/admin.py
from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'started_at', 'last_activity')
    list_filter = ('profile', 'started_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'is_user', 'content', 'timestamp')
    list_filter = ('is_user', 'timestamp')