/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Contact Details Management JavaScript

let deleteDetailForm = null;

function openDeleteModal(form) {
    deleteDetailForm = form;
    document.getElementById('delete-confirm-modal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('delete-confirm-modal').classList.add('hidden');
    deleteDetailForm = null;
}

document.addEventListener('DOMContentLoaded', () => {
    // Handle flash messages
    const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
    messages.forEach(([category, message]) => showToast(category, message));

    // Delete confirmation handler
    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
        if (deleteDetailForm) {
            deleteDetailForm.querySelector('input[name="action"]').value = 'delete';
            deleteDetailForm.submit();
        }
    });
});
