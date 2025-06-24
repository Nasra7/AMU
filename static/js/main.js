document.addEventListener('DOMContentLoaded', function() {
    // Apply saved theme immediately
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
});
