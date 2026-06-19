document.addEventListener('DOMContentLoaded', function() {
  // Initialize Categories Swiper
  new Swiper('.categories-swiper', {
    slidesPerView: 'auto', // Adjust slides to fit content
    spaceBetween: 10, // Space between slides
    freeMode: true, // Allow free scrolling
    navigation: {
      nextEl: '.categories-swiper .swiper-button-next',
      prevEl: '.categories-swiper .swiper-button-prev',
    },
    breakpoints: {
      // Adjust slidesPerView for different screen sizes
      640: {
        slidesPerView: 4,
      },
      768: {
        slidesPerView: 6,
      },
      1024: {
        slidesPerView: 8,
      },
    },
  });

  // Initialize Tags Swiper
  new Swiper('.tags-swiper', {
    slidesPerView: 'auto', // Adjust slides to fit content
    spaceBetween: 10, // Space between slides
    freeMode: true, // Allow free scrolling
    navigation: {
      nextEl: '.tags-swiper .swiper-button-next',
      prevEl: '.tags-swiper .swiper-button-prev',
    },
    breakpoints: {
      // Adjust slidesPerView for different screen sizes
      640: {
        slidesPerView: 4,
      },
      768: {
        slidesPerView: 6,
      },
      1024: {
        slidesPerView: 8,
      },
    },
  });
});