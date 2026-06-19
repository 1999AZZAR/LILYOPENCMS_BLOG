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