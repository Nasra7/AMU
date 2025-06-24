// Script for image preview and form validation
document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const imageUpload = document.getElementById('image-upload');
    const previewImage = document.getElementById('preview-image');
    const previewPlaceholder = document.getElementById('preview-placeholder');
    let imageSelected = false;
    
    imageUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                previewPlaceholder.classList.add('hidden');
                imageSelected = true;
            }
            
            reader.readAsDataURL(this.files[0]);
        }
    });

    // Form validation and submission handler
    const form = document.getElementById('character-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission
        
        // Perform validation
        if (validateForm()) {
            // Create FormData object
            const formData = new FormData(form);
            
            // Submit the form using fetch API
            fetch(form.action, {
                method: form.method,
                body: formData,
                credentials: 'same-origin', // Include cookies for CSRF token
            })
            .then(response => {
                if (response.ok) {
                    showSuccessAnimation();
                    // Reset form after successful submission
                    setTimeout(() => {
                        form.reset();
                        imageSelected = false;
                        document.getElementById('preview-image').classList.add('hidden');
                        document.getElementById('preview-placeholder').classList.remove('hidden');
                        resetValidationStyles();
                    }, 500);
                } else {
                    console.error('Form submission failed');
                    alert('There was an error submitting the form. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                alert('There was an error submitting the form. Please try again.');
            });
        }
    });

    // Function to validate all form fields
    function validateForm() {
        let isValid = true;
        
        // Required fields to validate (add any additional required fields here)
        const requiredFields = [
            { id: 'first_name', label: 'First Name' },
            { id: 'age_range', label: 'Age Range' },
            { id: 'gender', label: 'Gender' },
            { id: 'description', label: 'Description' },
            { id: 'background_story', label: 'Background Story' },
            { id: 'personality_traits', label: 'Personality Traits' },
            { id: 'speech_pattern', label: 'Speech Pattern' },
            { id: 'knowledge_base', label: 'Knowledge Base' }
        ];
        
        // Check if image is required and validate
        if (!imageSelected) {
            const imagePreview = document.getElementById('image-preview');
            imagePreview.classList.add('border-red-500');
            isValid = false;
            showError('image-preview', 'Profile photo is required');
        } else {
            resetFieldValidation('image-preview');
        }
        
        // Validate all required text fields
        requiredFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!element.value.trim()) {
                element.classList.add('border-red-500');
                isValid = false;
                showError(field.id, `${field.label} is required`);
            } else {
                resetFieldValidation(field.id);
            }
        });
        
        // If not valid, scroll to the first error
        if (!isValid) {
            const firstError = document.querySelector('.border-red-500');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        return isValid;
    }
    
    // Function to show error message for a field
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        
        // Check if error message already exists
        let errorElement = field.parentElement.querySelector('.error-message');
        
        if (!errorElement) {
            // Create error message element
            errorElement = document.createElement('p');
            errorElement.className = 'error-message text-red-500 text-xs mt-1';
            errorElement.textContent = message;
            
            // Add it after the field
            field.parentElement.appendChild(errorElement);
        }
    }
    
    // Function to reset validation styling for a specific field
    function resetFieldValidation(fieldId) {
        const field = document.getElementById(fieldId);
        field.classList.remove('border-red-500');
        
        // Remove error message if it exists
        const errorElement = field.parentElement.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    // Function to reset all validation styles
    function resetValidationStyles() {
        // Remove all error borders
        document.querySelectorAll('.border-red-500').forEach(element => {
            element.classList.remove('border-red-500');
        });
        
        // Remove all error messages
        document.querySelectorAll('.error-message').forEach(element => {
            element.remove();
        });
    }

    function showSuccessAnimation() {
        // Show the overlay
        const overlay = document.getElementById('success-overlay');
        overlay.classList.remove('hidden');
        
        // Animate the circle
        anime({
            targets: '#success-circle',
            strokeDashoffset: [anime.setDashoffset, 0],
            easing: 'easeInOutSine',
            duration: 1500,
            delay: 300
        });
        
        // Animate the checkmark
        anime({
            targets: '#success-check',
            strokeDashoffset: [anime.setDashoffset, 0],
            easing: 'easeInOutSine',
            duration: 700,
            delay: 1000
        });
        
        // Setup close button
        document.getElementById('close-overlay').addEventListener('click', function() {
            overlay.classList.add('hidden');
        });
    }
});