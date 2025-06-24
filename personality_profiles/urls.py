#personality_profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/create/', views.profile_create, name='profile_create'),
    path('profiles/<int:profile_id>/', views.profile_detail, name='profile_detail'),
    path('profiles/<int:profile_id>/edit/', views.profile_edit, name='profile_edit'),
    path('profiles/<int:profile_id>/delete/', views.profile_delete, name='profile_delete'),
]