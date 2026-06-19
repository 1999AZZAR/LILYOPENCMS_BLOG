document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuCloseButton = document.getElementById('mobile-menu-close-button');
    const body = document.body;

    function openMobileMenu() {
        if (!mobileMenu || !body) return;
        mobileMenu.classList.remove('hidden');
        body.classList.add('overflow-hidden');
    }

    function closeMobileMenu() {
        if (!mobileMenu || !body) return;
        mobileMenu.classList.add('hidden');
        body.classList.remove('overflow-hidden');
    }

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', openMobileMenu);
        if (mobileMenuCloseButton) {
            mobileMenuCloseButton.addEventListener('click', closeMobileMenu);
        }
        
        // Close on backdrop click
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) closeMobileMenu();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeMobileMenu();
        });
    }
});