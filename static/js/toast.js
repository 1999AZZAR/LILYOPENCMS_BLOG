// Unified toast display logic
function showToast(type, message) {
    // Make function globally available
    window.showToast = showToast;
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const iconClassMap = {
      success: 'fas fa-check-circle text-green-500',
      error: 'fas fa-times-circle text-red-500',
      warning: 'fas fa-exclamation-triangle text-yellow-400',
      info: 'fas fa-info-circle text-blue-400'
    };
    const iconClass = iconClassMap[type] || iconClassMap.info;
    toast.innerHTML =
      `<div class="flex-shrink-0 mt-1"><i class="${iconClass}"></i></div>` +
      `<div class="flex-1 text-gray-700 ml-2">${message}</div>`;
    container.appendChild(toast);
    // auto-dismiss
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.addEventListener('transitionend', () => toast.remove());
    }, 3000);
  }