// Media Guidelines Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Handle flash messages
    const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
    messages.forEach(([category, message]) => showToast(category, message));

    // Enhanced form validation
    const addForm = document.querySelector('form[action*="media_guidelines"]');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const title = this.querySelector('input[name="title"]');
            const content = this.querySelector('textarea[name="content"]');
            const order = this.querySelector('input[name="section_order"]');

            if (!title.value.trim()) {
                e.preventDefault();
                showToast('error', 'Judul tidak boleh kosong');
                title.focus();
                return;
            }

            if (!content.value.trim()) {
                e.preventDefault();
                showToast('error', 'Konten tidak boleh kosong');
                content.focus();
                return;
            }

            if (!order.value || order.value < 1) {
                e.preventDefault();
                showToast('error', 'Urutan harus berupa angka positif');
                order.focus();
                return;
            }
        });
    }

    // Enhanced textarea auto-resize
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Enhanced input focus effects
    const inputs = document.querySelectorAll('input[type="text"], input[type="number"], textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('ring-2', 'ring-amber-400');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('ring-2', 'ring-amber-400');
        });
    });

    // Auto-focus on first input when adding new section
    const newTitleInput = document.getElementById('new-title');
    if (newTitleInput) {
        newTitleInput.focus();
    }

    // Enhanced checkbox styling
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (this.checked) {
                label.classList.add('text-amber-800', 'font-semibold');
            } else {
                label.classList.remove('text-amber-800', 'font-semibold');
            }
        });
    });
});