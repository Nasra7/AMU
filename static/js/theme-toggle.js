document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (!themeToggle) {
        console.error("Theme toggle element not found!");
        return;
    }
    
    // Function to set theme
    function setTheme(themeName) {
        console.log("Setting theme to:", themeName);
        localStorage.setItem('theme', themeName);
        document.documentElement.setAttribute('data-theme', themeName);
        console.log("data-theme attribute is now:", document.documentElement.getAttribute('data-theme'));
    }
    
    // Initialize the toggle based on saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log("Initial theme from localStorage:", savedTheme);
    setTheme(savedTheme);
    themeToggle.checked = savedTheme === 'dark';
    
    // Event listener for the toggle switch
    themeToggle.addEventListener('change', function() {
        console.log("Toggle changed. Checked:", this.checked);
        if (this.checked) {
            setTheme('dark');
        } else {
            setTheme('light');
        }
    });
    
    console.log("Theme toggle initialized successfully");
});