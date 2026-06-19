// Gallery page functionality
export function initializeGallery() {
    const galleryModal = document.getElementById('gallery-modal');
    const modalImage = document.getElementById('modal-image');
    const modalDownloadButton = document.getElementById('modal-download-button');
    const modalPrevButton = document.getElementById('modal-prev-button');
    const modalNextButton = document.getElementById('modal-next-button');
    const imageGridContainer = document.getElementById('image-grid-container');

    let currentImageIndex = -1;
    let galleryImagesData = [];

    // Function to gather image data from the grid
    function collectImageData() {
        galleryImagesData = [];
        if (imageGridContainer) {
            const imageElements = imageGridContainer.querySelectorAll('[data-large-src]');
            imageElements.forEach(el => {
                galleryImagesData.push({
                    index: parseInt(el.dataset.index, 10),
                    largeSrc: el.dataset.largeSrc,
                    description: el.dataset.description,
                    filename: el.dataset.filename
                });
            });
        }
    }

    function openImageModal(index) {
        if (galleryImagesData.length === 0) {
            console.error("Image data not collected yet.");
            return;
        }
        if (index < 0 || index >= galleryImagesData.length) {
            console.error("Invalid image index:", index);
            return;
        }

        currentImageIndex = index;
        const imageData = galleryImagesData[currentImageIndex];

        if (!imageData) {
            console.error("Image data not found for index:", index);
            return;
        }

        // Update modal content
        modalImage.src = imageData.largeSrc;
        modalImage.alt = imageData.description;
        document.getElementById('modal-description').textContent = imageData.description;
        modalDownloadButton.href = imageData.largeSrc;
        modalDownloadButton.download = imageData.filename;

        // Show/hide prev/next buttons
        modalPrevButton.disabled = currentImageIndex <= 0;
        modalNextButton.disabled = currentImageIndex >= galleryImagesData.length - 1;

        // Show modal
        galleryModal.classList.remove('hidden');
        galleryModal.setAttribute('aria-hidden', 'false');
        requestAnimationFrame(() => {
            galleryModal.classList.add('opacity-100');
        });

        document.body.style.overflow = 'hidden';
        document.body.setAttribute('aria-hidden', 'true');
    }

    function closeImageModal() {
        galleryModal.classList.remove('opacity-100');
        setTimeout(() => {
            galleryModal.classList.add('hidden');
            galleryModal.setAttribute('aria-hidden', 'true');
            modalImage.src = "";
        }, 300);

        document.body.style.overflow = '';
        document.body.removeAttribute('aria-hidden');
    }

    // Close modal if clicking on the backdrop
    function closeImageModalOnClickOutside(event) {
        if (event.target === galleryModal) {
            closeImageModal();
        }
    }

    function showNextImage() {
        if (currentImageIndex < galleryImagesData.length - 1) {
            openImageModal(currentImageIndex + 1);
        }
    }

    function showPrevImage() {
        if (currentImageIndex > 0) {
            openImageModal(currentImageIndex - 1);
        }
    }

    // Keyboard navigation
    document.addEventListener('keydown', (event) => {
        if (!galleryModal.classList.contains('hidden')) {
            switch (event.key) {
                case 'Escape':
                    closeImageModal();
                    break;
                case 'ArrowRight':
                    showNextImage();
                    break;
                case 'ArrowLeft':
                    showPrevImage();
                    break;
            }
        }
    });

    // Initialize
    collectImageData();
    
    // Make functions globally available
    window.openImageModal = openImageModal;
    window.closeImageModal = closeImageModal;
    window.closeImageModalOnClickOutside = closeImageModalOnClickOutside;
    window.showNextImage = showNextImage;
    window.showPrevImage = showPrevImage;
}

document.addEventListener('DOMContentLoaded', initializeGallery);