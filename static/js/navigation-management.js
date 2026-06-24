// Navigation Management JavaScript
class NavigationManager {
    constructor() {
        this.currentLocation = 'navbar';
        this.links = [];
        this.editingLink = null;
        this.deletingLink = null;
        this.selectedLinks = new Set();
        
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
        
        // Copy links button
        const copyBtn = document.getElementById('copy-links-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.showCopyModal());
        }
        
        // Copy modal events
        const cancelCopyBtn = document.getElementById('cancel-copy-btn');
        const confirmCopyBtn = document.getElementById('confirm-copy-btn');
        const copyFrom = document.getElementById('copy-from');
        const copyTo = document.getElementById('copy-to');
        
        if (cancelCopyBtn) cancelCopyBtn.addEventListener('click', () => this.hideCopyModal());
        if (confirmCopyBtn) confirmCopyBtn.addEventListener('click', () => this.copyLinks());
        if (copyFrom) copyFrom.addEventListener('change', () => this.updateCopyPreview());
        if (copyTo) copyTo.addEventListener('change', () => this.updateCopyPreview());
        
        // Bulk action events
        const bulkActivateBtn = document.getElementById('bulk-activate-btn');
        const bulkDeactivateBtn = document.getElementById('bulk-deactivate-btn');
        const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
        const bulkClearBtn = document.getElementById('bulk-clear-btn');
        
        if (bulkActivateBtn) bulkActivateBtn.addEventListener('click', () => this.bulkActivate());
        if (bulkDeactivateBtn) bulkDeactivateBtn.addEventListener('click', () => this.bulkDeactivate());
        if (bulkDeleteBtn) bulkDeleteBtn.addEventListener('click', () => this.showBulkDeleteModal());
        if (bulkClearBtn) bulkClearBtn.addEventListener('click', () => this.clearSelection());
        
        // Bulk delete modal events
        const cancelBulkDeleteBtn = document.getElementById('cancel-bulk-delete-btn');
        const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');
        if (cancelBulkDeleteBtn) cancelBulkDeleteBtn.addEventListener('click', () => this.hideBulkDeleteModal());
        if (confirmBulkDeleteBtn) confirmBulkDeleteBtn.addEventListener('click', () => this.bulkDelete());
        
        // Internal links functionality
        this.bindInternalLinksEvents();
        
        // Modal backdrop clicks
        document.getElementById('link-modal').addEventListener('click', (e) => {
            if (e.target.id === 'link-modal') this.hideModal();
        });
        document.getElementById('delete-modal').addEventListener('click', (e) => {
            if (e.target.id === 'delete-modal') this.hideDeleteModal();
        });
        const copyModal = document.getElementById('copy-modal');
        if (copyModal) {
            copyModal.addEventListener('click', (e) => {
                if (e.target.id === 'copy-modal') this.hideCopyModal();
            });
        }
        const bulkDeleteModal = document.getElementById('bulk-delete-modal');
        if (bulkDeleteModal) {
            bulkDeleteModal.addEventListener('click', (e) => {
                if (e.target.id === 'bulk-delete-modal') this.hideBulkDeleteModal();
            });
        }
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
        const isSelected = this.selectedLinks.has(link.id) ? 'ring-2 ring-blue-500' : '';
        
        return `
            <div class="bg-gradient-to-br from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-300 ${isSelected}" data-link-id="${link.id}">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <input type="checkbox" class="link-checkbox rounded border-gray-300 text-blue-600 focus:ring-blue-500" data-link-id="${link.id}" ${this.selectedLinks.has(link.id) ? 'checked' : ''}>
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
        // Checkbox events
        document.querySelectorAll('.link-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const linkId = parseInt(e.target.dataset.linkId);
                
                if (e.target.checked) {
                    this.selectedLinks.add(linkId);
                } else {
                    this.selectedLinks.delete(linkId);
                }
                
                this.updateBulkActionBar();
                this.renderLinks();
            });
        });
        
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
    
    updateBulkActionBar() {
        const bulkActions = document.getElementById('bulk-actions');
        const selectedCount = document.getElementById('selected-count');
        
        if (!bulkActions) return;
        
        if (this.selectedLinks.size > 0) {
            bulkActions.classList.remove('hidden');
            bulkActions.style.display = 'flex';
            if (selectedCount) selectedCount.textContent = `${this.selectedLinks.size} selected`;
        } else {
            bulkActions.classList.add('hidden');
            bulkActions.style.display = 'none';
        }
    }
    
    clearSelection() {
        this.selectedLinks.clear();
        document.querySelectorAll('.link-checkbox').forEach(cb => { cb.checked = false; });
        this.updateBulkActionBar();
        const bulkActions = document.getElementById('bulk-actions');
        if (bulkActions) {
            bulkActions.classList.add('hidden');
            bulkActions.style.display = 'none';
        }
        this.renderLinks();
    }
    
    showCopyModal() {
        const modal = document.getElementById('copy-modal');
        if (!modal) return;
        modal.classList.remove('hidden');
        const copyFrom = document.getElementById('copy-from');
        const copyTo = document.getElementById('copy-to');
        const overwrite = document.getElementById('copy-overwrite');
        if (copyFrom) copyFrom.value = '';
        if (copyTo) copyTo.value = '';
        if (overwrite) overwrite.checked = false;
        const preview = document.getElementById('copy-preview');
        if (preview) preview.classList.add('hidden');
    }
    
    hideCopyModal() {
        const modal = document.getElementById('copy-modal');
        if (modal) modal.classList.add('hidden');
    }
    
    updateCopyPreview() {
        const copyFrom = document.getElementById('copy-from');
        const copyTo = document.getElementById('copy-to');
        const preview = document.getElementById('copy-preview');
        const previewContent = document.getElementById('copy-preview-content');
        
        if (!copyFrom || !copyTo || !preview || !previewContent) return;
        
        if (copyFrom.value && copyTo.value && copyFrom.value !== copyTo.value) {
            const sourceLinks = this.links.filter(link => link.location === copyFrom.value);
            previewContent.innerHTML = sourceLinks.map(link =>
                `<div class="py-1">• ${link.name} (${link.url})</div>`
            ).join('');
            preview.classList.remove('hidden');
        } else {
            preview.classList.add('hidden');
        }
    }
    
    async copyLinks() {
        const copyFrom = document.getElementById('copy-from');
        const copyTo = document.getElementById('copy-to');
        const overwrite = document.getElementById('copy-overwrite');
        
        if (!copyFrom || !copyTo) return;
        
        if (!copyFrom.value || !copyTo.value || copyFrom.value === copyTo.value) {
            this.showError('Pilih sumber dan tujuan yang berbeda');
            return;
        }
        
        try {
            const response = await fetch('/api/navigation-links/copy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_location: copyFrom.value,
                    to_location: copyTo.value,
                    overwrite: overwrite ? overwrite.checked : false
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to copy links');
            }
            
            const result = await response.json();
            this.hideCopyModal();
            this.showSuccess(`Berhasil menyalin ${result.copied_count} link dari ${copyFrom.value} ke ${copyTo.value}`);
            
            setTimeout(() => window.location.reload(), 1000);
        } catch (error) {
            console.error('Error copying links:', error);
            this.showError(error.message || 'Gagal menyalin link');
        }
    }
    
    showBulkDeleteModal() {
        const modal = document.getElementById('bulk-delete-modal');
        const count = document.getElementById('bulk-delete-count');
        if (!modal) return;
        if (count) count.textContent = this.selectedLinks.size;
        modal.classList.remove('hidden');
    }
    
    hideBulkDeleteModal() {
        const modal = document.getElementById('bulk-delete-modal');
        if (modal) modal.classList.add('hidden');
    }
    
    async bulkActivate() {
        if (this.selectedLinks.size === 0) {
            this.showError('Pilih link yang akan diaktifkan');
            return;
        }
        await this.bulkUpdateStatus(true);
    }
    
    async bulkDeactivate() {
        if (this.selectedLinks.size === 0) {
            this.showError('Pilih link yang akan dinonaktifkan');
            return;
        }
        await this.bulkUpdateStatus(false);
    }
    
    async bulkUpdateStatus(isActive) {
        if (this.selectedLinks.size === 0) return;
        
        try {
            const response = await fetch('/api/navigation-links/bulk-status', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    link_ids: Array.from(this.selectedLinks),
                    is_active: isActive
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update links');
            }
            
            this.showSuccess(`Berhasil ${isActive ? 'mengaktifkan' : 'menonaktifkan'} ${this.selectedLinks.size} link`);
            this.clearSelection();
            
            setTimeout(() => window.location.reload(), 1000);
        } catch (error) {
            console.error('Error updating links:', error);
            this.showError(error.message || 'Gagal mengupdate link');
        }
    }
    
    async bulkDelete() {
        if (this.selectedLinks.size === 0) {
            this.showError('Pilih link yang akan dihapus');
            return;
        }
        
        try {
            const response = await fetch('/api/navigation-links/bulk-delete', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    link_ids: Array.from(this.selectedLinks)
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete links');
            }
            
            this.hideBulkDeleteModal();
            this.showSuccess(`Berhasil menghapus ${this.selectedLinks.size} link`);
            this.clearSelection();
            
            setTimeout(() => window.location.reload(), 1000);
        } catch (error) {
            console.error('Error deleting links:', error);
            this.showError(error.message || 'Gagal menghapus link');
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
            this.inlineToast('success', message);
        }
    }
    
    showError(message) {
        if (typeof showToast === 'function') {
            showToast('error', message);
        } else {
            this.inlineToast('error', 'Error: ' + message);
        }
    }
    
    inlineToast(type, message) {
        const containerId = 'toast-container';
        let container = document.getElementById(containerId);
        if (!container) {
            container = document.createElement('div');
            container.id = containerId;
            container.className = 'fixed top-5 right-5 space-y-2 z-50';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        const bgClass = type === 'error' ? 'bg-sa-critical'
            : type === 'warning' ? 'bg-sa-warning'
            : 'bg-sa-success';
        toast.className = `${bgClass} text-white px-4 py-2 rounded-sa-md shadow-sa-card`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const manager = new NavigationManager();
    
    // Debug helpers for console testing
    window.toggleLinkSelection = (linkId) => {
        const id = parseInt(linkId);
        if (manager.selectedLinks.has(id)) {
            manager.selectedLinks.delete(id);
        } else {
            manager.selectedLinks.add(id);
        }
        manager.updateBulkActionBar();
        manager.renderLinks();
    };
    window.selectAllLinks = () => {
        const locationLinks = manager.links.filter(l => l.location === manager.currentLocation);
        locationLinks.forEach(l => manager.selectedLinks.add(l.id));
        manager.updateBulkActionBar();
        manager.renderLinks();
    };
    window.deselectAllLinks = () => {
        manager.selectedLinks.clear();
        manager.updateBulkActionBar();
        manager.renderLinks();
    };
    window.bulkActivateLinks = () => manager.bulkActivate();
    window.bulkDeactivateLinks = () => manager.bulkDeactivate();
    window.bulkDeleteLinks = () => manager.showBulkDeleteModal();
    window.copyLinks = () => manager.showCopyModal();
}); 