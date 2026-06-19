// Social Media Management JavaScript

// Platform icons mapping
const platformIcons = {
    'Facebook': 'fab fa-facebook',
    'Twitter': 'fab fa-twitter',
    'Instagram': 'fab fa-instagram',
    'LinkedIn': 'fab fa-linkedin',
    'YouTube': 'fab fa-youtube',
    'GitHub': 'fab fa-github',
    'Telegram': 'fab fa-telegram',
    'Pinterest': 'fab fa-pinterest',
    'TikTok': 'fab fa-tiktok',
    'WhatsApp': 'fab fa-whatsapp',
    'Discord': 'fab fa-discord',
    'Snapchat': 'fab fa-snapchat',
    'Reddit': 'fab fa-reddit',
    'default': 'fas fa-share-alt'
};

// Function to get platform icon
function getPlatformIcon(platformName) {
    return platformIcons[platformName] || platformIcons.default;
}

let currentDeleteId = null;

// Function to show delete confirmation modal
function showDeleteModal(id) {
    currentDeleteId = id;
    document.getElementById('delete-social-media-modal').classList.remove('hidden');
}

// Function to hide delete confirmation modal
function hideDeleteModal() {
    document.getElementById('delete-social-media-modal').classList.add('hidden');
    currentDeleteId = null;
}

// Function to load all social media links
async function loadSocialMediaLinks() {
    try {
        const response = await fetch('/api/social-media');
        const data = await response.json();
        const container = document.getElementById('social-media-list');
        const emptyState = document.getElementById('empty-state');
        
        container.innerHTML = '';

        if (data.length === 0) {
            container.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }

        container.classList.remove('hidden');
        emptyState.classList.add('hidden');

        data.forEach(item => {
            const template = document.getElementById('social-media-template');
            const clone = template.content.cloneNode(true);
            
            const form = clone.querySelector('form');
            form.querySelector('[name="id"]').value = item.id;
            form.querySelector('[name="name"]').value = item.name;
            form.querySelector('[name="url"]').value = item.url;

            // Update platform display
            const platformName = form.querySelector('.platform-name');
            const platformUrl = form.querySelector('.platform-url');
            const platformIcon = form.querySelector('.platform-icon');
            
            platformName.textContent = item.name;
            platformUrl.textContent = item.url;
            platformIcon.className = getPlatformIcon(item.name);

            // Update ARIA labels with dynamic IDs
            const nameInput = form.querySelector('[name="name"]');
            const urlInput = form.querySelector('[name="url"]');
            nameInput.id = `platform-name-${item.id}`;
            urlInput.id = `platform-url-${item.id}`;
            form.querySelector('label[for="platform-name-{id}"]').setAttribute('for', `platform-name-${item.id}`);
            form.querySelector('label[for="platform-url-{id}"]').setAttribute('for', `platform-url-${item.id}`);

            // Add event listeners
            form.querySelector('.update-btn').addEventListener('click', () => updateSocialMedia(form));
            form.querySelector('.delete-btn').addEventListener('click', () => showDeleteModal(item.id));

            container.appendChild(clone);
        });
    } catch (error) {
        console.error('Error memuat tautan media sosial:', error);
        showToast('error', 'Gagal memuat tautan media sosial');
    }
}

// Function to add new social media
async function addSocialMedia(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Menambahkan...';
    submitBtn.disabled = true;

    const data = {
        name: form.name.value,
        url: form.url.value
    };

    try {
        const response = await fetch('/api/social-media', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Gagal menambahkan media sosial');
        
        form.reset();
        await loadSocialMediaLinks();
        showToast('success', 'Media sosial berhasil ditambahkan');
    } catch (error) {
        console.error('Error menambahkan media sosial:', error);
        showToast('error', 'Gagal menambahkan media sosial');
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Function to update social media
async function updateSocialMedia(form) {
    const updateBtn = form.querySelector('.update-btn');
    const originalText = updateBtn.innerHTML;
    
    // Show loading state
    updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Memperbarui...';
    updateBtn.disabled = true;

    const id = form.querySelector('[name="id"]').value;
    const data = {
        name: form.querySelector('[name="name"]').value,
        url: form.querySelector('[name="url"]').value
    };

    try {
        const response = await fetch(`/api/social-media/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Gagal memperbarui media sosial');
        
        await loadSocialMediaLinks();
        showToast('success', 'Media sosial berhasil diperbarui');
    } catch (error) {
        console.error('Error memperbarui media sosial:', error);
        showToast('error', 'Gagal memperbarui media sosial');
    } finally {
        // Restore button state
        updateBtn.innerHTML = originalText;
        updateBtn.disabled = false;
    }
}

// Function to delete social media
async function deleteSocialMedia() {
    if (!currentDeleteId) return;

    const deleteBtn = document.getElementById('confirm-delete-btn');
    const originalText = deleteBtn.innerHTML;
    
    // Show loading state
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Menghapus...';
    deleteBtn.disabled = true;

    try {
        const response = await fetch(`/api/social-media/${currentDeleteId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Gagal menghapus media sosial');
        
        hideDeleteModal();
        await loadSocialMediaLinks();
        showToast('success', 'Media sosial berhasil dihapus');
    } catch (error) {
        console.error('Error menghapus media sosial:', error);
        showToast('error', 'Gagal menghapus media sosial');
    } finally {
        // Restore button state
        deleteBtn.innerHTML = originalText;
        deleteBtn.disabled = false;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSocialMediaLinks();
    document.getElementById('add-social-media-form').addEventListener('submit', addSocialMedia);
    
    // Add event listeners for delete modal
    document.getElementById('cancel-delete-btn').addEventListener('click', hideDeleteModal);
    document.getElementById('confirm-delete-btn').addEventListener('click', deleteSocialMedia);

    // Handle flash messages
    const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
    messages.forEach(([category, message]) => showToast(category, message));
});