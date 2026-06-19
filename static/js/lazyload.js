// Lazy loading for images and loaded class
export function initializeLazyLoad(logger) {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if (logger) logger.log(`Found ${lazyImages.length} lazy images.`);

    // Add event listeners for load/error to add 'loaded' class reliably
    lazyImages.forEach(img => {
        if (img.complete && img.naturalHeight !== 0) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', () => img.classList.add('loaded'), { once: true });
            img.addEventListener('error', () => {
                if (logger) logger.warn('Image failed to load:', img.src);
                img.classList.add('loaded');
            }, { once: true });
        }
    });

    // Use Intersection Observer for optimized loading
    if ("IntersectionObserver" in window) {
        const lazyObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (logger) logger.log('Lazy loading intersecting image:', img.alt || img.src.substring(img.src.lastIndexOf('/') + 1));
                    observer.unobserve(img);
                }
            });
        }, { rootMargin: "0px 0px 200px 0px" });
        lazyImages.forEach(img => lazyObserver.observe(img));
    } else {
        if (logger) logger.warn("IntersectionObserver not supported, relying on browser native lazy-loading and load/error events.");
    }
}
