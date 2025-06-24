# personality_profiles/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PersonalityProfile

@admin.register(PersonalityProfile)
class PersonalityProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'gender', 'age_range', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('gender', 'age_range')
    readonly_fields = ('created_at', 'updated_at', 'display_large_image')
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.image.url)
        return "No Image"
    
    display_image.short_description = 'Profile Picture'
    
    def display_large_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="max-height: 300px; object-fit: contain;" />', obj.image.url)
        return "No Image"
    
    display_large_image.short_description = 'Character Image Preview'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image', 'display_large_image', 'gender', 'age_range')
        }),
        ('Character Details', {
            'fields': ('background_story', 'personality_traits', 'speech_patterns', 'knowledge_base')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )