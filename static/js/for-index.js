document.addEventListener('DOMContentLoaded', function () {
    // Function to set uniform height for cards in a group
    function setUniformHeight(groupSelector) {
        const group = document.querySelector(groupSelector);
        if (!group) return;

        const cards = group.querySelectorAll('.news-card');
        let maxHeight = 0;

        // Reset heights to auto to calculate the natural height
        cards.forEach(card => {
        card.style.height = 'auto';
        });

        // Find the tallest card
        cards.forEach(card => {
        const cardHeight = card.offsetHeight;
        if (cardHeight > maxHeight) {
            maxHeight = cardHeight;
        }
        });

        // Apply the tallest height to all cards
        cards.forEach(card => {
        card.style.height = `${maxHeight}px`;
        });
    }

    // Only set uniform height on desktop
    if (window.innerWidth >= 768) {
        setUniformHeight('[data-group="latest-news"]');
        setUniformHeight('[data-group="popular-news"]');

        // Recalculate on window resize
        window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) {
            setUniformHeight('[data-group="latest-news"]');
            setUniformHeight('[data-group="popular-news"]');
        }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    new Swiper('.featured-swiper', {
        slidesPerView: 1, // Show only one slide at a time
        spaceBetween: 30, // Space between slides
        loop: true, // Infinite loop
        autoplay: {
        delay: 3500, // Auto-slide every 3.5 seconds
        disableOnInteraction: false, // Allow autoplay to continue after user interaction
        },
        navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
        },
        pagination: {
        el: '.swiper-pagination',
        clickable: true,
        },
    });
});
