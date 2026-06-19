// Featured image modal logic
function initializeFeaturedImageModal(logger) {
    // Make functions globally available
    window.initializeFeaturedImageModal = initializeFeaturedImageModal;
    
    const trigger = document.getElementById('featured-image-trigger');
    const modal = document.getElementById('featured-image-modal');
    const modalImg = document.getElementById('modal-featured-image');
    const downloadBtn = document.getElementById('modal-featured-download');
    
    if (!trigger || !modal || !modalImg || !downloadBtn) {
        if (logger) logger.warn("Featured image modal elements not found. Fullscreen feature disabled.");
        return;
    }
    trigger.addEventListener('click', (event) => {
        event.preventDefault();
        const mainImg = trigger.querySelector('img');
        if (!mainImg) {
            if (logger) logger.warn("No image found in featured image trigger");
            return;
        }
        const imgSrc = mainImg.src;
        const imgAlt = mainImg.alt || 'Featured Image';
        let filename = 'featured_image.jpg';
        try {
            const urlParts = new URL(imgSrc);
            const pathParts = urlParts.pathname.split('/');
            const potentialFilename = pathParts[pathParts.length - 1];
            if (potentialFilename && potentialFilename.includes('.')) {
                filename = potentialFilename.split('?')[0];
            }
        } catch (e) {
            if (logger) logger.warn("Could not parse image URL for filename, using default.");
        }
        modalImg.src = imgSrc;
        modalImg.alt = imgAlt;
        downloadBtn.href = imgSrc;
        downloadBtn.download = filename;
        modal.classList.remove('hidden');
        requestAnimationFrame(() => {
            modal.classList.add('opacity-100');
        });
        document.body.style.overflow = 'hidden';
        if (logger) logger.log("Featured image modal opened");
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
            window.closeFeaturedImageModal();
        }
    });
    window.closeFeaturedImageModal = function() {
        if (!modal) return;
        modal.classList.remove('opacity-100');
        setTimeout(() => modal.classList.add('hidden'), 300);
        document.body.style.overflow = '';
        if (logger) logger.log("Featured image modal closed");
    };
    
    // Also add the click outside function
    window.closeFeaturedImageModalOnClickOutside = function(event) {
        if (event.target === modal) {
            window.closeFeaturedImageModal();
        }
    };
}
