document.addEventListener('DOMContentLoaded', function () {
    // Toggle desktop search bar
    const desktopSearchToggle = document.getElementById('desktop-search-toggle');
    const desktopSearchContainer = document.getElementById('desktop-search-container');
  
    if (desktopSearchToggle && desktopSearchContainer) {
      desktopSearchToggle.addEventListener('click', () => {
        desktopSearchContainer.classList.toggle('hidden');
      });
    }
  
    // Toggle mobile search bar
    const mobileSearchToggle = document.getElementById('mobile-search-toggle');
    const mobileSearchContainer = document.getElementById('mobile-search-container');
  
    if (mobileSearchToggle && mobileSearchContainer) {
      mobileSearchToggle.addEventListener('click', () => {
        mobileSearchContainer.classList.toggle('hidden');
      });
    }
});