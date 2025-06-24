from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/<int:profile_id>/', views.chat_interface, name='chat_interface'),
    path('send_message/', views.send_message, name='send_message'),
]