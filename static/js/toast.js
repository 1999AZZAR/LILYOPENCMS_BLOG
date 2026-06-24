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