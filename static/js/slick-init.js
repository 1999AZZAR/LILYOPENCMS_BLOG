// Slick carousel initialization
function initializeSlick(logger) {
    if (typeof $ === 'undefined' || typeof $.fn.slick === 'undefined') {
        if (logger) logger.error("Slick Carousel requires jQuery and slick.min.js. Make sure they are loaded correctly in base.html before this script.");
        $('.related-news-carousel-wrapper .slick-prev, .related-news-carousel-wrapper .slick-next').hide();
        return;
    }
    const slickElement = $('.related-news-carousel');
    
    if (slickElement.length) {
        if (slickElement.children().length === 0) {
            if (logger) logger.log("Slick Carousel: No slides found inside .related-news-carousel. Skipping initialization.");
            $('.related-news-carousel-wrapper .slick-prev, .related-news-carousel-wrapper .slick-next').hide();
            return;
        }
        if (logger) logger.log("Initializing Slick Carousel on:", slickElement);
        try {
            slickElement.slick({
                dots: false,
                infinite: false,
                speed: 400,
                slidesToShow: 4,
                slidesToScroll: 1,
                variableWidth: false,
                centerMode: false,
                prevArrow: $('.related-news-carousel-wrapper .slick-prev'),
                nextArrow: $('.related-news-carousel-wrapper .slick-next'),
                responsive: [
                    { breakpoint: 1280, settings: { slidesToShow: 3, slidesToScroll: 1 } },
                    { breakpoint: 1024, settings: { slidesToShow: 2, slidesToScroll: 1 } },
                    { breakpoint: 768, settings: { slidesToShow: 2, slidesToScroll: 1 } },
                    { breakpoint: 640, settings: { slidesToShow: 1, slidesToScroll: 1 } }
                ]
            });
            const updateArrows = (slick) => {
                const prevArrow = slick.options.prevArrow;
                const nextArrow = slick.options.nextArrow;
                const currentSlide = slick.currentSlide;
                const slideCount = slick.slideCount;
                const slidesToShow = slick.options.slidesToShow;
                if (currentSlide === 0) {
                    $(prevArrow).addClass('slick-disabled').attr('aria-disabled', 'true');
                } else {
                    $(prevArrow).removeClass('slick-disabled').attr('aria-disabled', 'false');
                }
                if (currentSlide >= slideCount - slidesToShow) {
                    $(nextArrow).addClass('slick-disabled').attr('aria-disabled', 'true');
                } else {
                    $(nextArrow).removeClass('slick-disabled').attr('aria-disabled', 'false');
                }
            };
            slickElement.on('init reInit afterChange breakpoint', function(event, slick) {
                updateArrows(slick);
            });
            const slickInstance = slickElement.slick('getSlick');
            if (slickInstance) updateArrows(slickInstance);
            if (logger) logger.log("Slick initialized successfully.");
        } catch (e) {
            if (logger) logger.error("Slick initialization failed:", e);
            $('.related-news-carousel-wrapper .slick-prev, .related-news-carousel-wrapper .slick-next').hide();
        }
    } else {
        if (logger) logger.warn("Slick Carousel target '.related-news-carousel' not found in the DOM.");
        $('.related-news-carousel-wrapper .slick-prev, .related-news-carousel-wrapper .slick-next').hide();
    }
}
