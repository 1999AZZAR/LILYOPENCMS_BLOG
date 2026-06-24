/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

function toggleFooter() {
    if (window.innerWidth < 768) {
      document.getElementById('desktop-footer').classList.add('hidden');
      document.getElementById('mobile-footer').classList.remove('hidden');
    } else {
      document.getElementById('desktop-footer').classList.remove('hidden');
      document.getElementById('mobile-footer').classList.add('hidden');
    }
  }

  window.addEventListener('load', toggleFooter);
  window.addEventListener('resize', toggleFooter);
