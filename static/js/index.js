// Index page functionality
export function initializeIndex() {
    const logger = {
        log: (...args) => console.log('[IndexPage]', ...args),
        warn: (...args) => console.warn('[IndexPage]', ...args),
        error: (...args) => console.error('[IndexPage]', ...args)
    };

    // Initialize Featured News Swiper
    const swiperContainer = document.querySelector('.featured-swiper');
    if (swiperContainer && swiperContainer.querySelector('.swiper-slide')) {
        logger.log("Initializing Featured Swiper...");
        try {
            const swiper = new Swiper('.featured-swiper', {
                loop: swiperContainer.querySelectorAll('.swiper-slide').length > 1,
                effect: 'fade',
                fadeEffect: { crossFade: true },
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                    pauseOnMouseEnter: true
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev'
                },
                keyboard: { enabled: true },
                a11y: {
                    prevSlideMessage: 'Slide sebelumnya',
                    nextSlideMessage: 'Slide berikutnya',
                    paginationBulletMessage: 'Ke slide {{index}}',
                },
            });
            logger.log("Featured Swiper initialized successfully.");
        } catch(e) {
            logger.error("Featured Swiper initialization failed:", e);
        }
    } else if (swiperContainer) {
        logger.log("Featured Swiper container found, but no slides. Hiding controls.");
        const controls = ['.swiper-button-next', '.swiper-button-prev', '.swiper-pagination'];
        controls.forEach(sel => {
            const el = swiperContainer.querySelector(sel);
            if (el) el.style.display = 'none';
        });
    } else {
        logger.log("Featured Swiper container not found.");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeIndex();
});