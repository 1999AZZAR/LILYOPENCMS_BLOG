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