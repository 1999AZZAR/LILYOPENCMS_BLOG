/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Custom logging utility for development
const logger = {
  log: (...args) => console.log("[LOG]", ...args),
  warn: (...args) => console.warn("[WARN]", ...args),
  error: (...args) => console.error("[ERROR]", ...args)
};

// Global variables for gallery functionality
let galleryImagesData = [];
let currentImageIndex = -1;

// Function to collect image data from the gallery
document.addEventListener('DOMContentLoaded', function() {
  // Get references to modal elements
  const galleryModal = document.getElementById('gallery-modal');
  const modalImage = galleryModal ? galleryModal.querySelector('img') : null;
  const modalCaption = galleryModal ? galleryModal.querySelector('figcaption') : null;
  const modalPrevButton = galleryModal ? galleryModal.querySelector('[data-action="prev"]') : null;
  const modalNextButton = galleryModal ? galleryModal.querySelector('[data-action="next"]') : null;
  const modalCloseButton = galleryModal ? galleryModal.querySelector('[data-action="close"]') : null;

  // Initialize Featured News Swiper if it exists
  const swiperContainer = document.querySelector('.featured-swiper');
  if (swiperContainer && swiperContainer.querySelector('.swiper-slide')) {
    const swiper = new Swiper('.featured-swiper', {
      // Optional parameters
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      effect: 'fade',
      fadeEffect: {
        crossFade: true
      },
      speed: 1000,
      // Navigation arrows
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      // If we need pagination
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
    });
  }

  // --- Gallery Modal Functions ---
  
  // Function to scan the grid and store image data in the galleryImagesData array
  function collectImageData() {
    const imageGrid = document.getElementById('latest-image-grid-container');
    if (!imageGrid) return;

    const imageElements = imageGrid.querySelectorAll('img');
    galleryImagesData = [];

    imageElements.forEach((img, index) => {
      const container = img.closest('a');
      if (container) {
        galleryImagesData.push({
          src: img.src,
          alt: img.alt,
          title: container.getAttribute('aria-label') || '',
          index: index
        });
      }
    });

    logger.log(`Collected ${galleryImagesData.length} images for gallery`);
  }


  // Function to open the modal and display the image at the given index
  window.openImageModal = function(index) {
    if (!galleryModal || !galleryImagesData.length || index < 0 || index >= galleryImagesData.length) {
      logger.warn(`Invalid index or no images available for modal: ${index}`);
      return;
    }

    const imageData = galleryImagesData[index];
    currentImageIndex = index;

    // Update modal content
    if (modalImage) {
      modalImage.src = imageData.src;
      modalImage.alt = imageData.alt;
      modalImage.loading = 'eager';
    }

    if (modalCaption) {
      modalCaption.textContent = imageData.alt;
    }

    // Update navigation buttons
    if (modalPrevButton) {
      modalPrevButton.style.display = currentImageIndex > 0 ? 'block' : 'none';
    }
    if (modalNextButton) {
      modalNextButton.style.display = currentImageIndex < galleryImagesData.length - 1 ? 'block' : 'none';
    }

    // Display the modal
    galleryModal.classList.remove('hidden');
    galleryModal.classList.add('flex');
    requestAnimationFrame(() => {
      galleryModal.classList.add('opacity-100');
    });

    // Prevent scrolling on the main page
    document.body.style.overflow = 'hidden';
    logger.log(`Opened modal for image index: ${currentImageIndex}`);
  }


  // Function to close the modal
  window.closeImageModal = function() {
    if (!galleryModal) return;
    
    galleryModal.classList.remove('opacity-100');
    setTimeout(() => {
      galleryModal.classList.add('hidden');
      galleryModal.classList.remove('flex');
      if (modalImage) modalImage.src = "";
    }, 300);

    document.body.style.overflow = '';
    logger.log("Closed image modal.");
  }

  // Function to close the modal if the click occurs on the backdrop
  window.closeImageModalOnClickOutside = function(event) {
    if (galleryModal && event.target === galleryModal) {
      closeImageModal();
    }
  }

  // Function to navigate to the next image
  window.showNextImage = function() {
    if (currentImageIndex < galleryImagesData.length - 1) {
      openImageModal(currentImageIndex + 1);
    }
  }

  // Function to navigate to the previous image
  window.showPrevImage = function() {
    if (currentImageIndex > 0) {
      openImageModal(currentImageIndex - 1);
    }
  }

  // Keyboard navigation for modal
  document.addEventListener('keydown', function(event) {
    if (galleryModal && !galleryModal.classList.contains('hidden')) {
      if (event.key === 'Escape') {
        closeImageModal();
      } else if (event.key === 'ArrowRight') {
        showNextImage();
      } else if (event.key === 'ArrowLeft') {
        showPrevImage();
      }
    }
  });

  // Initialize the gallery
  collectImageData();

  // Add event listeners for modal buttons
  if (modalCloseButton) {
    modalCloseButton.addEventListener('click', closeImageModal);
  }
  if (modalPrevButton) {
    modalPrevButton.addEventListener('click', (e) => {
      e.stopPropagation();
      showPrevImage();
    });
  }
  if (modalNextButton) {
    modalNextButton.addEventListener('click', (e) => {
      e.stopPropagation();
      showNextImage();
    });
  }
});
