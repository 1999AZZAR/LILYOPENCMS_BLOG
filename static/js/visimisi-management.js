/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Visi Misi Management JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Handle flash messages
    const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
    messages.forEach(([category, message]) => showToast(category, message));

    // Enhanced form validation
    const addForm = document.querySelector('form[action*="visi_misi"]');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const title = this.querySelector('input[name="title"]:checked');
            const content = this.querySelector('textarea[name="content"]');
            const order = this.querySelector('input[name="section_order"]');

            if (!title) {
                e.preventDefault();
                showToast('error', 'Pilih jenis bagian (Visi atau Misi)');
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

    // Enhanced radio button styling
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove active class from all labels
            document.querySelectorAll('label[class*="bg-gradient"]').forEach(label => {
                label.classList.remove('ring-2', 'ring-amber-400');
            });
            
            // Add active class to selected label
            if (this.checked) {
                this.closest('label').classList.add('ring-2', 'ring-amber-400');
            }
        });
    });

    // Auto-focus on first radio button if none selected
    const firstRadio = document.querySelector('input[type="radio"]');
    if (firstRadio && !document.querySelector('input[type="radio"]:checked')) {
        firstRadio.checked = true;
        firstRadio.closest('label').classList.add('ring-2', 'ring-amber-400');
    }

    // Enhanced textarea auto-resize
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});
