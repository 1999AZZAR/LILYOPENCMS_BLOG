// Root SEO Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let currentSeoId = null;
    let isEditMode = false;

    // Initialize
    initializeEventListeners();
    updateAnalytics();

    function initializeEventListeners() {
        // Create SEO button
        document.getElementById('create-seo-btn').addEventListener('click', openCreateModal);
        
        // Modal controls
        document.getElementById('cancel-btn').addEventListener('click', closeModal);
        document.getElementById('seo-form').addEventListener('submit', handleFormSubmit);
        
        // Delete modal controls
        document.getElementById('cancel-delete').addEventListener('click', closeDeleteModal);
        document.getElementById('confirm-delete').addEventListener('click', confirmDelete);
        
        // Action buttons
        document.getElementById('bulk-edit-btn').addEventListener('click', openBulkEdit);
        document.getElementById('export-btn').addEventListener('click', exportData);
        document.getElementById('refresh-btn').addEventListener('click', refreshData);
        
        // Filters
        document.getElementById('seo-status-filter').addEventListener('change', filterTable);
        document.getElementById('page-status-filter').addEventListener('change', filterTable);
        document.getElementById('search-filter').addEventListener('input', filterTable);
        
        // Select all checkbox
        document.getElementById('select-all').addEventListener('change', toggleSelectAll);
        
        // SEO status cards
        document.querySelectorAll('[data-seo-status]').forEach(card => {
            card.addEventListener('click', () => filterByStatus(card.dataset.seoStatus));
        });
        
        // Form field listeners for SEO score calculation
        const seoFields = ['meta-title', 'meta-description', 'meta-keywords', 'og-title', 'og-description', 'og-image', 'canonical-url', 'schema-markup'];
        seoFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', calculateSeoScore);
            }
        });
    }

    // Modal Management
    function openCreateModal() {
        isEditMode = false;
        currentSeoId = null;
        document.getElementById('modal-title').textContent = 'Buat SEO Baru';
        document.getElementById('seo-form').reset();
        document.getElementById('page-identifier').readOnly = false;
        showModal();
    }

    function openEditModal(seoId) {
        isEditMode = true;
        currentSeoId = seoId;
        document.getElementById('modal-title').textContent = 'Edit SEO';
        document.getElementById('page-identifier').readOnly = true;
        
        // Fetch SEO data
        fetch(`/settings/root-seo/${seoId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateForm(data.data);
                    showModal();
                } else {
                    showToast('Error loading SEO data', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error loading SEO data', 'error');
            });
    }

    function populateForm(data) {
        document.getElementById('seo-id').value = data.id;
        document.getElementById('page-identifier').value = data.page_identifier;
        document.getElementById('page-name').value = data.page_name;
        document.getElementById('is-active').checked = data.is_active;
        document.getElementById('meta-title').value = data.meta_title || '';
        document.getElementById('meta-description').value = data.meta_description || '';
        document.getElementById('meta-keywords').value = data.meta_keywords || '';
        document.getElementById('og-title').value = data.og_title || '';
        document.getElementById('og-description').value = data.og_description || '';
        document.getElementById('og-image').value = data.og_image || '';
        document.getElementById('og-type').value = data.og_type || 'website';
        document.getElementById('twitter-card').value = data.twitter_card || 'summary_large_image';
        document.getElementById('twitter-title').value = data.twitter_title || '';
        document.getElementById('twitter-description').value = data.twitter_description || '';
        document.getElementById('twitter-image').value = data.twitter_image || '';
        document.getElementById('canonical-url').value = data.canonical_url || '';
        document.getElementById('meta-author').value = data.meta_author || '';
        document.getElementById('meta-language').value = data.meta_language || 'id';
        document.getElementById('meta-robots').value = data.meta_robots || 'index, follow';
        document.getElementById('structured-data-type').value = data.structured_data_type || 'WebPage';
        document.getElementById('schema-markup').value = data.schema_markup || '';
        document.getElementById('google-analytics-id').value = data.google_analytics_id || '';
        document.getElementById('facebook-pixel-id').value = data.facebook_pixel_id || '';
        
        calculateSeoScore();
    }

    function showModal() {
        document.getElementById('seo-modal').classList.remove('hidden');
    }

    function closeModal() {
        document.getElementById('seo-modal').classList.add('hidden');
        document.getElementById('seo-form').reset();
        currentSeoId = null;
        isEditMode = false;
    }

    function closeDeleteModal() {
        document.getElementById('delete-modal').classList.add('hidden');
    }

    // Form Handling
    function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (key === 'is_active') {
                data[key] = true;
            } else {
                data[key] = value;
            }
        }
        
        // Add checkbox value
        data.is_active = document.getElementById('is-active').checked;
        
        const url = isEditMode ? `/settings/root-seo/${currentSeoId}` : '/settings/root-seo/create';
        const method = isEditMode ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showToast(result.message, 'success');
                closeModal();
                refreshData();
            } else {
                showToast(result.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error saving SEO data', 'error');
        });
    }

    // Delete functionality
    function deleteSeo(seoId) {
        currentSeoId = seoId;
        document.getElementById('delete-modal').classList.remove('hidden');
    }

    function confirmDelete() {
        if (!currentSeoId) return;
        
        fetch(`/settings/root-seo/${currentSeoId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showToast(result.message, 'success');
                closeDeleteModal();
                refreshData();
            } else {
                showToast(result.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error deleting SEO data', 'error');
        });
    }

    // SEO Score Calculation
    function calculateSeoScore() {
        const fields = [
            'meta-title',
            'meta-description', 
            'meta-keywords',
            'og-title',
            'og-description',
            'og-image',
            'canonical-url',
            'schema-markup'
        ];
        
        let score = 0;
        const totalFields = fields.length;
        
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && field.value.trim()) {
                score++;
            }
        });
        
        const percentage = Math.round((score / totalFields) * 100);
        const scoreDisplay = document.getElementById('seo-score-display');
        const scoreBar = document.getElementById('seo-score-bar');
        
        if (scoreDisplay) scoreDisplay.textContent = `${percentage}%`;
        if (scoreBar) {
            scoreBar.style.width = `${percentage}%`;
            if (percentage >= 80) {
                scoreBar.className = 'h-3 rounded-full bg-green-500';
            } else if (percentage >= 40) {
                scoreBar.className = 'h-3 rounded-full bg-yellow-500';
            } else {
                scoreBar.className = 'h-3 rounded-full bg-red-500';
            }
        }
    }

    // Table Management
    function refreshData() {
        location.reload();
    }

    function filterTable() {
        const statusFilter = document.getElementById('seo-status-filter').value;
        const pageStatusFilter = document.getElementById('page-status-filter').value;
        const searchFilter = document.getElementById('search-filter').value.toLowerCase();
        
        const rows = document.querySelectorAll('#root-seo-table-body tr');
        
        rows.forEach(row => {
            let show = true;
            
            // Status filter
            if (statusFilter) {
                const seoScore = parseInt(row.querySelector('.text-sm.font-medium.text-gray-900').textContent);
                if (statusFilter === 'complete' && seoScore < 80) show = false;
                if (statusFilter === 'incomplete' && (seoScore >= 80 || seoScore < 40)) show = false;
                if (statusFilter === 'missing' && seoScore >= 40) show = false;
            }
            
            // Page status filter
            if (pageStatusFilter) {
                const statusText = row.querySelector('.inline-flex').textContent.trim();
                if (pageStatusFilter === 'active' && statusText !== 'Aktif') show = false;
                if (pageStatusFilter === 'inactive' && statusText !== 'Tidak Aktif') show = false;
            }
            
            // Search filter
            if (searchFilter) {
                const pageName = row.querySelector('.text-sm.font-medium.text-gray-900').textContent.toLowerCase();
                const pageIdentifier = row.querySelector('.text-sm.text-gray-500').textContent.toLowerCase();
                if (!pageName.includes(searchFilter) && !pageIdentifier.includes(searchFilter)) {
                    show = false;
                }
            }
            
            row.style.display = show ? '' : 'none';
        });
    }

    function filterByStatus(status) {
        document.getElementById('seo-status-filter').value = status;
        filterTable();
    }

    function toggleSelectAll() {
        const selectAll = document.getElementById('select-all');
        const checkboxes = document.querySelectorAll('.seo-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll.checked;
        });
    }

    // Bulk Operations
    function openBulkEdit() {
        const selectedIds = getSelectedIds();
        if (selectedIds.length === 0) {
            showToast('Pilih setidaknya satu item untuk diedit', 'warning');
            return;
        }
        
        // Implement bulk edit functionality
        showToast('Fitur edit massal akan segera hadir', 'info');
    }

    function getSelectedIds() {
        const checkboxes = document.querySelectorAll('.seo-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Export functionality
    function exportData() {
        window.location.href = '/settings/root-seo/export';
    }

    // Analytics
    function updateAnalytics() {
        fetch('/settings/root-seo/analytics')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateAnalyticsDisplay(data.data);
                }
            })
            .catch(error => {
                console.error('Error updating analytics:', error);
            });
    }

    function updateAnalyticsDisplay(data) {
        // Update card counts
        if (document.getElementById('total-pages')) {
            document.getElementById('total-pages').textContent = data.total_pages;
        }
        if (document.getElementById('active-pages')) {
            document.getElementById('active-pages').textContent = data.active_pages;
        }
        if (document.getElementById('complete-seo')) {
            document.getElementById('complete-seo').textContent = data.complete_seo;
        }
        if (document.getElementById('complete-seo-count')) {
            document.getElementById('complete-seo-count').textContent = data.complete_seo;
        }
        if (document.getElementById('incomplete-seo-count')) {
            document.getElementById('incomplete-seo-count').textContent = data.incomplete_seo;
        }
        if (document.getElementById('missing-seo-count')) {
            document.getElementById('missing-seo-count').textContent = data.missing_seo;
        }
        if (document.getElementById('avg-seo-score')) {
            document.getElementById('avg-seo-score').textContent = `${data.avg_score}%`;
        }
    }

    // Event delegation for dynamic elements
    document.addEventListener('click', function(e) {
        // Edit buttons
        if (e.target.closest('.edit-seo-btn')) {
            const seoId = e.target.closest('.edit-seo-btn').dataset.seoId;
            openEditModal(seoId);
        }
        
        // Delete buttons
        if (e.target.closest('.delete-seo-btn')) {
            const seoId = e.target.closest('.delete-seo-btn').dataset.seoId;
            deleteSeo(seoId);
        }
    });

    // Toast notifications
    function showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium ${
            type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Initialize SEO score calculation
    calculateSeoScore();
});