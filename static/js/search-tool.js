// Search and Filter Functionality
class SearchTool {
  constructor() {
    this.initializeElements();
    if (this.hasRequiredElements()) {
      this.initializeEventListeners();
    }
  }

  initializeElements() {
    // Search elements
    this.desktopSearch = document.getElementById('desktop-search');
    this.mobileSearch = document.getElementById('mobile-search');
    this.desktopClear = document.querySelector('[data-target="desktop-search"]');
    this.mobileClear = document.querySelector('[data-target="mobile-search"]');
    
    // Filter elements
    this.filtersBtn = document.getElementById('mobile-filters-btn');
    this.filtersModal = document.getElementById('mobile-filters-modal');
    this.closeFiltersBtn = document.getElementById('close-filters-btn');
    this.modalContent = this.filtersModal?.querySelector('.bg-gray-900');
    
    // Suggestions containers
    this.desktopSuggestions = document.getElementById('desktop-search-suggestions');
    this.mobileSuggestions = document.getElementById('mobile-search-suggestions');

    // Loading spinner
    this.loadingSpinner = document.getElementById('loading-spinner');
  }

  hasRequiredElements() {
    return (this.desktopSearch || this.mobileSearch) && 
           (this.desktopClear || this.mobileClear);
  }

  initializeEventListeners() {
    // Initialize search bars
    if (this.desktopSearch && this.desktopClear) {
      this.initializeSearchBar(this.desktopSearch, this.desktopClear, this.desktopSuggestions);
    }
    if (this.mobileSearch && this.mobileClear) {
      this.initializeSearchBar(this.mobileSearch, this.mobileClear, this.mobileSuggestions);
    }

    // Initialize filters modal
    if (this.filtersBtn && this.filtersModal && this.closeFiltersBtn && this.modalContent) {
      this.initializeFiltersModal();
    }

    // Initialize form submission loading
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', () => this.showLoading());
    });
  }

  initializeSearchBar(searchInput, clearButton, suggestionsContainer) {
    searchInput.addEventListener('input', () => {
      if (searchInput.value) {
        clearButton.classList.remove('hidden');
        if (searchInput.value.length >= 3) {
          this.showSuggestions(searchInput.value, suggestionsContainer);
        }
      } else {
        clearButton.classList.add('hidden');
        suggestionsContainer?.classList.add('hidden');
      }
    });

    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      clearButton.classList.add('hidden');
      suggestionsContainer?.classList.add('hidden');
      searchInput.focus();
    });
  }

  showSuggestions(query, container) {
    if (!container) return;
    
    // Here you can implement the suggestions logic
    // For example, making an API call to get search suggestions
    container.classList.remove('hidden');
    // Add your suggestion implementation here
  }

  initializeFiltersModal() {
    this.filtersBtn.addEventListener('click', () => {
      this.filtersModal.classList.remove('hidden');
    });

    this.closeFiltersBtn.addEventListener('click', () => {
      this.filtersModal.classList.add('hidden');
    });

    // Close modal when clicking outside
    this.filtersModal.addEventListener('click', (e) => {
      if (e.target === this.filtersModal) {
        this.filtersModal.classList.add('hidden');
      }
    });
  }

  showLoading() {
    this.loadingSpinner?.classList.remove('hidden');
  }

  hideLoading() {
    this.loadingSpinner?.classList.add('hidden');
  }
}

// Initialize search tool when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new SearchTool();
});
