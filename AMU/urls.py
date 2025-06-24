from django.contrib import admin
from django.urls import path, include
from chat import views
from conversations.views import txt_to_speech, delete_audio
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('chat/<int:profile_id>/', views.chat_interface, name='chat_interface'),
    path('send_message/', views.send_message, name='send_message'),
    path('api/tts/', txt_to_speech, name='txt_to_speech'),
    path('api/delete_audio/', delete_audio, name='delete_audio'),

    path('chat/', include('chat.urls')),
    path('', include('personality_profiles.urls')),
    path('add-character/', views.add_character, name='add_character'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

