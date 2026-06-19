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