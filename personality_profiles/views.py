# personality_profiles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PersonalityProfile
from .forms import PersonalityProfileForm
from conversations.models import Conversation

def profile_list(request):
    profiles = PersonalityProfile.objects.all().order_by('name')
    return render(request, 'personality_profiles/profile_list.html', {
        'profiles': profiles
    })

def profile_detail(request, profile_id):
    profile = get_object_or_404(PersonalityProfile, id=profile_id)
    # Get conversations with this profile for the current user
    conversations = Conversation.objects.filter(profile=profile).order_by('-last_activity')
    
    return render(request, 'personality_profiles/profile_detail.html', {
        'profile': profile,
        'conversations': conversations
    })

@login_required
def profile_create(request):
    if request.method == 'POST':
        form = PersonalityProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            # Set JSON fields from cleaned data
            profile.personality_traits = form.cleaned_data['personality_traits']
            profile.speech_patterns = form.cleaned_data['speech_patterns']
            profile.knowledge_base = form.cleaned_data['knowledge_base']
            profile.save()
            
            messages.success(request, f"Profile '{profile.name}' created successfully!")
            return redirect('profile_detail', profile_id=profile.id)
    else:
        form = PersonalityProfileForm()
    
    return render(request, 'personality_profiles/profile_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
def profile_edit(request, profile_id):
    profile = get_object_or_404(PersonalityProfile, id=profile_id)
    
    if request.method == 'POST':
        form = PersonalityProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            # Set JSON fields from cleaned data
            profile.personality_traits = form.cleaned_data['personality_traits']
            profile.speech_patterns = form.cleaned_data['speech_patterns']
            profile.knowledge_base = form.cleaned_data['knowledge_base']
            profile.save()
            
            messages.success(request, f"Profile '{profile.name}' updated successfully!")
            return redirect('profile_detail', profile_id=profile.id)
    else:
        # Pre-populate the JSON fields for editing
        initial_data = {
            'personality_traits': ', '.join(profile.personality_traits.get('traits', [])),
            'speech_patterns': profile.speech_patterns.get('description', ''),
            'knowledge_base': ', '.join(profile.knowledge_base.get('areas', []))
        }
        form = PersonalityProfileForm(instance=profile, initial=initial_data)
    
    return render(request, 'personality_profiles/profile_form.html', {
        'form': form,
        'profile': profile,
        'action': 'Edit'
    })

@login_required
def profile_delete(request, profile_id):
    profile = get_object_or_404(PersonalityProfile, id=profile_id)
    
    if request.method == 'POST':
        profile_name = profile.name
        profile.delete()
        messages.success(request, f"Profile '{profile_name}' has been deleted.")
        return redirect('profile_list')
    
    return render(request, 'personality_profiles/profile_confirm_delete.html', {
        'profile': profile
    })