/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Team Members Management JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Handle flash messages
    const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
    messages.forEach(([category, message]) => showToast(category, message));

    // Delete modal handlers
    let deleteForm = null;
    const deleteButtons = document.querySelectorAll('button[value="delete"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            deleteForm = this.closest('form');
            document.getElementById('delete-team-member-modal').classList.remove('hidden');
        });
    });

    document.getElementById('cancel-delete-btn').addEventListener('click', function() {
        document.getElementById('delete-team-member-modal').classList.add('hidden');
        deleteForm = null;
    });

    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
        if (deleteForm) {
            deleteForm.submit();
        }
    });
});
