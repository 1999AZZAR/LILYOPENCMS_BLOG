// Navigation Management JavaScript
class NavigationManager {
    constructor() {
        this.currentLocation = 'navbar';
        this.links = [];
        this.editingLink = null;
        this.deletingLink = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadLinks();
    }
    
    bindEvents() {
        // Tab switching
        document.getElementById('navbar-tab').addEventListener('click', () => this.switchTab('navbar'));
        document.getElementById('footer-tab').addEventListener('click', () => this.switchTab('footer'));
        
        // Add link buttons
        document.getElementById('add-link-btn').addEventListener('click', () => this.showAddModal());
        document.getElementById('add-first-link-btn').addEventListener('click', () => this.showAddModal());
        
        // Modal events
        document.getElementById('cancel-btn').addEventListener('click', () => this.hideModal());
        document.getElementById('save-btn').addEventListener('click', () => this.saveLink());
        document.getElementById('cancel-delete-btn').addEventListener('click', () => this.hideDeleteModal());
        document.getElementById('confirm-delete-btn').addEventListener('click', () => this.deleteLink());
        
        // Internal links functionality
        this.bindInternalLinksEvents();
        
        // Modal backdrop clicks
        document.getElementById('link-modal').addEventListener('click', (e) => {
            if (e.target.id === 'link-modal') this.hideModal();
        });
        document.getElementById('delete-modal').addEventListener('click', (e) => {
            if (e.target.id === 'delete-modal') this.hideDeleteModal();
        });
    }
    
    bindInternalLinksEvents() {
        const isExternalCheckbox = document.getElementById('link-external');
        const internalLinkContainer = document.getElementById('internal-link-container');
        const internalLinkSelect = document.getElementById('internal-link-select');
        const urlInput = document.getElementById('link-url');
        
        if (!isExternalCheckbox || !internalLinkContainer || !internalLinkSelect || !urlInput) {
            return;
        }
        
        // Toggle internal link dropdown based on external checkbox
        const toggleInternalLink = () => {
            if (!isExternalCheckbox.checked) {
                internalLinkContainer.classList.remove('hidden');
            } else {
                internalLinkContainer.classList.add('hidden');
                internalLinkSelect.value = '';
            }
        };
        
        isExternalCheckbox.addEventListener('change', toggleInternalLink);
        
        // Auto-fill URL when internal link is selected
        internalLinkSelect.addEventListener('change', function() {
            if (internalLinkSelect.value) {
                urlInput.value = internalLinkSelect.value;
            }
        });
        
        // Initialize state
        toggleInternalLink();
    }
    
    async loadLinks() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/navigation-links');
            if (!response.ok) throw new Error('Failed to load links');
            
            this.links = await response.json();
            this.renderLinks();
        } catch (error) {
            console.error('Error loading links:', error);
            this.showError('Gagal memuat link navigasi');
        } finally {
            this.hideLoading();
        }
    }
    
    switchTab(location) {
        this.currentLocation = location;
        
        // Update tab styles
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active', 'border-amber-500');
            tab.classList.add('border-transparent');
        });
        const activeTab = document.querySelector(`[data-location="${location}"]`);
        activeTab.classList.add('active', 'border-amber-500');
        activeTab.classList.remove('border-transparent');
        
        this.renderLinks();
    }
    
    renderLinks() {
        const container = document.getElementById('links-container');
        const emptyState = document.getElementById('empty-state');
        
        const locationLinks = this.links.filter(link => link.location === this.currentLocation);
        
        if (locationLinks.length === 0) {
            container.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }
        
        emptyState.classList.add('hidden');
        
        // Sort by order
        locationLinks.sort((a, b) => a.order - b.order);
        
        container.innerHTML = locationLinks.map(link => this.createLinkCard(link)).join('');
        
        // Bind card events
        this.bindCardEvents();
    }
    
    createLinkCard(link) {
        const statusClass = link.is_active ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-600';
        const statusText = link.is_active ? 'Aktif' : 'Nonaktif';
        const externalIcon = link.is_external ? '<svg class="w-4 h-4 ml-1 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>' : '';
        
        return `
            <div class="bg-gradient-to-br from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-300" data-link-id="${link.id}">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="flex items-center mb-2">
                            <h3 class="text-lg font-semibold text-amber-800">${link.name}</h3>
                            ${externalIcon}
                        </div>
                        <p class="text-sm text-amber-600 mb-2">${link.url}</p>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-1 text-xs rounded-full ${statusClass}">${statusText}</span>
                            <span class="text-xs text-amber-600">Urutan: ${link.order}</span>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button class="edit-link-btn p-2 text-amber-600 hover:text-amber-800 hover:bg-amber-100 rounded-md transition-all duration-300" title="Edit">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button class="delete-link-btn p-2 text-amber-600 hover:text-red-500 hover:bg-red-50 rounded-md transition-all duration-300" title="Hapus">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindCardEvents() {
        // Edit buttons
        document.querySelectorAll('.edit-link-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const linkId = e.target.closest('[data-link-id]').dataset.linkId;
                const link = this.links.find(l => l.id == linkId);
                if (link) this.showEditModal(link);
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-link-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const linkId = e.target.closest('[data-link-id]').dataset.linkId;
                const link = this.links.find(l => l.id == linkId);
                if (link) this.showDeleteModal(link);
            });
        });
    }
    
    showAddModal() {
        this.editingLink = null;
        document.getElementById('modal-title').textContent = 'Tambah Link Baru';
        document.getElementById('link-form').reset();
        document.getElementById('link-location').value = this.currentLocation;
        document.getElementById('link-order').value = '0';
        document.getElementById('link-active').checked = true;
        document.getElementById('link-external').checked = false;
        
        // Reset internal links dropdown
        const internalLinkSelect = document.getElementById('internal-link-select');
        if (internalLinkSelect) {
            internalLinkSelect.value = '';
        }
        
        // Show/hide internal links container based on external checkbox
        const internalLinkContainer = document.getElementById('internal-link-container');
        if (internalLinkContainer) {
            internalLinkContainer.classList.remove('hidden');
        }
        
        this.showModal();
    }
    
    showEditModal(link) {
        this.editingLink = link;
        document.getElementById('modal-title').textContent = 'Edit Link';
        document.getElementById('link-id').value = link.id;
        document.getElementById('link-name').value = link.name;
        document.getElementById('link-url').value = link.url;
        document.getElementById('link-location').value = link.location;
        document.getElementById('link-order').value = link.order;
        document.getElementById('link-active').checked = link.is_active;
        document.getElementById('link-external').checked = link.is_external;
        
        // Handle internal links dropdown
        const internalLinkSelect = document.getElementById('internal-link-select');
        const internalLinkContainer = document.getElementById('internal-link-container');
        
        if (internalLinkSelect && internalLinkContainer) {
            // Reset dropdown
            internalLinkSelect.value = '';
            
            // Show/hide based on external checkbox
            if (link.is_external) {
                internalLinkContainer.classList.add('hidden');
            } else {
                internalLinkContainer.classList.remove('hidden');
            }
        }
        
        this.showModal();
    }
    
    showModal() {
        document.getElementById('link-modal').classList.remove('hidden');
    }
    
    hideModal() {
        document.getElementById('link-modal').classList.add('hidden');
        this.editingLink = null;
        
        // Reset internal links dropdown
        const internalLinkSelect = document.getElementById('internal-link-select');
        const internalLinkContainer = document.getElementById('internal-link-container');
        if (internalLinkSelect) {
            internalLinkSelect.value = '';
        }
        if (internalLinkContainer) {
            internalLinkContainer.classList.add('hidden');
        }
    }
    
    showDeleteModal(link) {
        this.deletingLink = link;
        document.getElementById('delete-modal').classList.remove('hidden');
    }
    
    hideDeleteModal() {
        document.getElementById('delete-modal').classList.add('hidden');
        this.deletingLink = null;
    }
    
    async saveLink() {
        try {
            const formData = new FormData(document.getElementById('link-form'));
            const data = {
                name: formData.get('name'),
                url: formData.get('url'),
                location: formData.get('location'),
                order: parseInt(formData.get('order')) || 0,
                is_active: formData.get('is_active') === 'on',
                is_external: formData.get('is_external') === 'on'
            };
            
            // Validate required fields
            if (!data.name || !data.url || !data.location) {
                this.showError('Semua field wajib diisi');
                return;
            }
            
            const url = this.editingLink 
                ? `/api/navigation-links/${this.editingLink.id}`
                : '/api/navigation-links';
            
            const method = this.editingLink ? 'PUT' : 'POST';
            
            // Show loading state
            const saveBtn = document.getElementById('save-btn');
            const originalText = saveBtn.textContent;
            saveBtn.textContent = 'Menyimpan...';
            saveBtn.disabled = true;
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to save link');
            }
            
            this.hideModal();
            this.showSuccess(this.editingLink ? 'Link berhasil diperbarui' : 'Link berhasil ditambahkan');
            
            // Reload the page to reflect navigation changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('Error saving link:', error);
            this.showError(error.message || 'Gagal menyimpan link');
        } finally {
            // Reset button state
            const saveBtn = document.getElementById('save-btn');
            saveBtn.textContent = 'Simpan';
            saveBtn.disabled = false;
        }
    }
    
    async deleteLink() {
        if (!this.deletingLink) return;
        
        try {
            const response = await fetch(`/api/navigation-links/${this.deletingLink.id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete link');
            }
            
            this.hideDeleteModal();
            this.showSuccess('Link berhasil dihapus');
            
            // Reload the page to reflect navigation changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('Error deleting link:', error);
            this.showError(error.message);
        }
    }
    
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }
    
    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }
    
    showSuccess(message) {
        if (typeof showToast === 'function') {
            showToast('success', message);
        } else {
            alert(message);
        }
    }
    
    showError(message) {
        if (typeof showToast === 'function') {
            showToast('error', message);
        } else {
            alert('Error: ' + message);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NavigationManager();
}); 