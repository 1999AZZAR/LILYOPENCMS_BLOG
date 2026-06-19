document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const themeToggleMobile = document.getElementById('theme-toggle-mobile');
  const body = document.body;

  // Function to set the theme
  function setTheme(theme) {
    if (theme === 'light') {
      body.classList.add('light-theme');
      body.classList.remove('dark-theme');
      themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
      if (themeToggleMobile) {
        themeToggleMobile.innerHTML = '<i class="fas fa-sun"></i>';
      }
    } else {
      body.classList.add('dark-theme');
      body.classList.remove('light-theme');
      themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
      if (themeToggleMobile) {
        themeToggleMobile.innerHTML = '<i class="fas fa-moon"></i>';
      }
    }
    localStorage.setItem('theme', theme);
    updateUIForTheme(theme);
    updateLogoForTheme(theme);
    updateImageFallbackForTheme(theme);
  }

  // Function to toggle the theme
  function toggleTheme() {
    if (body.classList.contains('light-theme')) {
      setTheme('dark');
    } else {
      setTheme('light');
    }
  }

  // Function to update UI components based on the theme
  function updateUIForTheme(theme) {
    const cards = document.querySelectorAll('.card, .team-card, .error-card');
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');

    cards.forEach(card => {
      if (theme === 'light') {
        card.classList.add('light-theme');
        card.classList.remove('dark-theme');
      } else {
        card.classList.add('dark-theme');
        card.classList.remove('light-theme');
      }
    });

    buttons.forEach(button => {
      if (theme === 'light') {
        button.classList.add('light-theme');
        button.classList.remove('dark-theme');
      } else {
        button.classList.add('dark-theme');
        button.classList.remove('light-theme');
      }
    });
  }

  // Function to update the logo based on the theme
  function updateLogoForTheme(theme) {
    const logoElement = document.getElementById('theme-logo');
    if (logoElement) {
      if (theme === 'light') {
        logoElement.src = "/static/pic/logo.png";
      } else {
        logoElement.src = "/static/pic/logo.png";
      }
    }
  }

  // Function to update the image fallback based on the theme
  function updateImageFallbackForTheme(theme) {
    const newsCards = document.querySelectorAll('.news-card');
    newsCards.forEach(card => {
      const imageElement = card.querySelector('img');
      const hasActualImage = card.dataset.hasImage === "true";

      if (!hasActualImage && imageElement) {
        if (theme === 'light') {
          imageElement.src = "/static/pic/logo.png";
        } else {
          imageElement.src = "/static/pic/logo.png";
        }
      }
    });
  }

  // Event listeners for theme toggle buttons
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  if (themeToggleMobile) {
    themeToggleMobile.addEventListener('click', toggleTheme);
  }

  // Set theme on page load
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setTheme(savedTheme);
  } else {
    const systemTheme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    setTheme(systemTheme); // Follow system theme by default
  }

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'light' : 'dark');
    }
  });

  // Optional: Add smooth transition for theme change
  body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
});
