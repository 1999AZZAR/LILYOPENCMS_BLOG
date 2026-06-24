/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

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
