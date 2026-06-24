/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

document.addEventListener('DOMContentLoaded', function () {
    // Toggle desktop search bar
    const desktopSearchToggle = document.getElementById('desktop-search-toggle');
    const desktopSearchContainer = document.getElementById('desktop-search-container');
  
    if (desktopSearchToggle && desktopSearchContainer) {
      desktopSearchToggle.addEventListener('click', () => {
        desktopSearchContainer.classList.toggle('hidden');
      });
    }
  
    // Toggle mobile search bar
    const mobileSearchToggle = document.getElementById('mobile-search-toggle');
    const mobileSearchContainer = document.getElementById('mobile-search-container');
  
    if (mobileSearchToggle && mobileSearchContainer) {
      mobileSearchToggle.addEventListener('click', () => {
        mobileSearchContainer.classList.toggle('hidden');
      });
    }
});
