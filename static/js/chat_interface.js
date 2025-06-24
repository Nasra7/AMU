document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const profileId = document.getElementById('profileId').value;
    const conversationId = document.getElementById('conversationId').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const languageToggle = document.getElementById('languageToggle');
    
    // Current language - default to English
    let currentLanguage = "en";

    // Add audio element for TTS if it doesn't exist
    if (!document.getElementById('speech-audio')) {
        const audioElement = document.createElement('audio');
        audioElement.id = 'speech-audio';
        audioElement.style.display = 'none';
        document.body.appendChild(audioElement);
    }
    
    const audioElement = document.getElementById('speech-audio');
    let currentlyPlayingButton = null;
    let isProcessing = false;

    // Set up language toggle button
    if (languageToggle) {
        languageToggle.addEventListener('click', function() {
            // Toggle language
            if (currentLanguage === "en") {
                currentLanguage = "tr";
                languageToggle.textContent = "EN";
                languageToggle.title = "Switch to English";
            } else {
                currentLanguage = "en";
                languageToggle.textContent = "TR";
                languageToggle.title = "Switch to Turkish";
            }
            
            // Show language change notification
            const langMessage = currentLanguage === "en" ? 
                "Switched to English (using Llama3.2)" : 
                "Switched to Turkish (using Qwen)";
            
            showNotification(langMessage);
        });
    }

    function showLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'flex justify-start loading-message';
        loadingDiv.innerHTML = `
            <div class="max-w-[70%] p-3 rounded-lg bot-message">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return loadingDiv;
    }

    function appendMessage(content, isUser, messageId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `max-w-[70%] p-3 rounded-lg chat-message ${isUser ? 'user-message' : 'bot-message'}`;
        bubble.textContent = content;
        
        // Add speak button for bot messages
        if (!isUser) {
            const buttonDiv = document.createElement('div');
            buttonDiv.className = 'mt-2 text-right';
            
            const speakButton = document.createElement('button');
            speakButton.className = 'speak-button text-sm px-2 py-1 bg-blue-400 text-white rounded hover:bg-blue-500';
            speakButton.dataset.messageId = messageId || Date.now().toString();
            speakButton.dataset.text = content;
            speakButton.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            
            // Add event listener to the speak button
            speakButton.addEventListener('click', handleSpeakButtonClick);
            
            buttonDiv.appendChild(speakButton);
            bubble.appendChild(buttonDiv);
        }
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'flex justify-center my-2';
        errorDiv.innerHTML = `
            <div class="p-2 rounded text-sm error-message" style="background-color: #ffeded; color: #d32f2f;">
                ${message}
            </div>
        `;
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        setTimeout(() => errorDiv.remove(), 5000);
    }

    function showNotification(message) {
        const notifDiv = document.createElement('div');
        notifDiv.className = 'flex justify-center my-2';
        notifDiv.innerHTML = `
            <div class="p-2 rounded text-sm notification-message" style="background-color: #e3f2fd; color: #1565c0;">
                ${message}
            </div>
        `;
        chatMessages.appendChild(notifDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        setTimeout(() => notifDiv.remove(), 5000);
    }

    // Function to handle speak button clicks
    function handleSpeakButtonClick() {
        const messageText = this.dataset.text;
        const messageId = this.dataset.messageId;
        
        // If this button is already speaking, stop it
        if (this.classList.contains('speaking')) {
            audioElement.pause();
            this.classList.remove('speaking');
            this.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            currentlyPlayingButton = null;
            return;
        }
        
        // If another button is speaking, stop it
        if (currentlyPlayingButton) {
            currentlyPlayingButton.classList.remove('speaking');
            currentlyPlayingButton.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            audioElement.pause();
        }
        
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        
        // Request speech from the API with language parameter
        fetch('/api/tts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                text: messageText,
                personality_id: profileId,
                language: currentLanguage
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            this.disabled = false;
            
            if (data.success) {
                // Mark this button as speaking
                this.classList.add('speaking');
                this.innerHTML = '<i class="fas fa-volume-up"></i> Stop';
                currentlyPlayingButton = this;
                
                // Set the audio source and play
                audioElement.src = data.audio_url;
                
                // Try playing
                const playPromise = audioElement.play();
                
                // Handle play promise
                if (playPromise !== undefined) {
                    playPromise.catch(err => {
                        console.error('Playback failed:', err);
                        showError('Failed to play audio. Please try again.');
                        
                        // Reset button state
                        this.classList.remove('speaking');
                        this.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
                        currentlyPlayingButton = null;
                    });
                }
                
                // Handle audio ending
                audioElement.onended = function() {
                    if (currentlyPlayingButton) {
                        currentlyPlayingButton.classList.remove('speaking');
                        currentlyPlayingButton.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
                        currentlyPlayingButton = null;
                    }
                };
            } else {
                console.error('TTS Error:', data.error);
                showError('Error generating speech. Please try again.');
                this.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            }
        })
        .catch(error => {
            console.error('TTS API Error:', error);
            showError('Error communicating with speech service. Please try again.');
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
        });
    }

    // Setup speak buttons for existing messages
    function setupExistingSpeakButtons() {
        document.querySelectorAll('.speak-button').forEach(button => {
            button.removeEventListener('click', handleSpeakButtonClick);  // Remove any existing listeners
            button.addEventListener('click', handleSpeakButtonClick);
        });
    }
    
    // Call this to initialize the speak buttons for existing messages
    setupExistingSpeakButtons();

    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (isProcessing) return;
        
        const message = messageInput.value.trim();
        if (!message) return;

        isProcessing = true;
        messageInput.disabled = true;
        
        // Append user message
        appendMessage(message, true);
        const loadingIndicator = showLoadingIndicator();

        messageInput.value = '';

        try {
            const response = await fetch('/send_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin',  // Important for CSRF
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId,
                    language: currentLanguage  // Send the current language preference
                })
            });

            loadingIndicator.remove();

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                // Use message ID if available in the response, otherwise use timestamp
                const messageId = data.message_id || Date.now().toString();
                appendMessage(data.response, false, messageId);
            } else {
                showError(data.message || 'Failed to get response');
            }
        } catch (error) {
            loadingIndicator.remove();
            showError('Failed to send message. Please try again.');
            console.error('Error:', error);
        } finally {
            isProcessing = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    });

    // Handle audio play errors
    audioElement.addEventListener('error', function() {
        console.error('Audio error:', this.error);
        if (currentlyPlayingButton) {
            currentlyPlayingButton.classList.remove('speaking');
            currentlyPlayingButton.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            currentlyPlayingButton = null;
            showError('Failed to play the audio. Please try again.');
        }
    });

    // Handle audio ending
    audioElement.onended = function() {
        if (currentlyPlayingButton) {
            currentlyPlayingButton.classList.remove('speaking');
            currentlyPlayingButton.innerHTML = '<i class="fas fa-volume-up"></i> Speak';
            
            // Extract the filename from the audio URL
            const audioUrl = audioElement.src;
            const filename = audioUrl.substring(audioUrl.lastIndexOf('/') + 1);
            
            // Call endpoint to delete the file
            fetch('/api/delete_audio/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    filename: filename
                })
            }).catch(error => {
                console.error('Error deleting audio file:', error);
            });
            
            currentlyPlayingButton = null;
        }
    };

    // Add reconnection handling
    window.addEventListener('online', function() {
        showNotification('Connection restored. You can continue chatting.');
    });

    window.addEventListener('offline', function() {
        showError('Connection lost. Please check your internet connection.');
    });
});