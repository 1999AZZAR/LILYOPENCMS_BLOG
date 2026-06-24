/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

function showToast(type, message) {
    window.showToast = showToast;
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const iconClassMap = {
      success: 'fas fa-check-circle text-sa-success',
      error: 'fas fa-times-circle text-sa-critical',
      warning: 'fas fa-exclamation-triangle text-sa-warning',
      info: 'fas fa-info-circle text-sa-accent'
    };
    const iconClass = iconClassMap[type] || iconClassMap.info;
    toast.innerHTML =
      `<div class="flex-shrink-0 mt-1"><i class="${iconClass}"></i></div>` +
      `<div class="flex-1 text-sa-fg ml-2">${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.addEventListener('transitionend', () => toast.remove());
    }, 3000);
  }
