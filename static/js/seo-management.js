/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// SEO Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-white', 'text-amber-800');
                btn.classList.add('bg-amber-200', 'text-amber-700');
            });
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active', 'bg-white', 'text-amber-800');
            button.classList.remove('bg-amber-200', 'text-amber-700');
            document.getElementById(targetTab + '-tab').classList.add('active');
            
            // Load data for the selected tab
            if (targetTab === 'articles') {
                loadArticles();
            } else if (targetTab === 'analytics') {
                loadAnalytics();
            } else if (targetTab === 'settings') {
                loadGlobalSettings();
            }
        });
    });

    // Initialize SEO management functionality
    initializeSEOManagement();
});

function initializeSEOManagement() {
    console.log('SEO Management initialized');
    
    // Make functions globally available for onclick handlers
    window.bulkFixMissingMetaDescriptions = bulkFixMissingMetaDescriptions;
    window.bulkFixMissingOGTitles = bulkFixMissingOGTitles;
    window.bulkFixMissingSlugs = bulkFixMissingSlugs;
    window.filterIssuesByPriority = filterIssuesByPriority;
    window.editSeo = editSeo;
    
    console.log('Global functions assigned:', {
        bulkFixMissingMetaDescriptions: typeof window.bulkFixMissingMetaDescriptions,
        bulkFixMissingOGTitles: typeof window.bulkFixMissingOGTitles,
        bulkFixMissingSlugs: typeof window.bulkFixMissingSlugs,
        filterIssuesByPriority: typeof window.filterIssuesByPriority,
        editSeo: typeof window.editSeo
    });
    
    // Load initial data for the active tab
    const activeTab = document.querySelector('.tab-button.active');
    if (activeTab) {
        const targetTab = activeTab.getAttribute('data-tab');
        if (targetTab === 'articles') {
            loadArticles();
        } else if (targetTab === 'analytics') {
            loadAnalytics();
        } else if (targetTab === 'settings') {
            loadGlobalSettings();
        }
    }
    
    // Initialize event listeners
    initializeEventListeners();
}

function initializeEventListeners() {
    // Search and filter functionality
    const searchInput = document.getElementById('search-articles');
    const statusFilter = document.getElementById('status-filter');
    const seoStatusFilter = document.getElementById('seo-status-filter');
    const categoryFilter = document.getElementById('category-filter');
    const refreshButton = document.getElementById('refresh-seo');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => loadArticles(), 500));
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', () => loadArticles());
    }
    
    if (seoStatusFilter) {
        seoStatusFilter.addEventListener('change', () => loadArticles());
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => loadArticles());
    }
    
    if (refreshButton) {
        refreshButton.addEventListener('click', () => loadArticles());
    }
    
    // Modal functionality
    const closeModalBtn = document.getElementById('close-seo-modal');
    const cancelEditBtn = document.getElementById('cancel-seo-edit');
    const editSeoForm = document.getElementById('edit-seo-form');
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeEditModal);
    }
    
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', closeEditModal);
    }
    
    if (editSeoForm) {
        editSeoForm.addEventListener('submit', handleSeoUpdate);
    }
    
    // Add click outside modal to close functionality
    const modal = document.getElementById('edit-seo-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeEditModal();
            }
        });
        
        // Add keyboard support for closing modal
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                closeEditModal();
            }
        });
    }
    
    // Character counters
    const metaDescInput = document.getElementById('edit-meta-description');
    const ogTitleInput = document.getElementById('edit-og-title');
    const ogDescInput = document.getElementById('edit-og-description');
    
    if (metaDescInput) {
        metaDescInput.addEventListener('input', () => updateCharCount('meta-desc-count', metaDescInput, 500));
    }
    
    if (ogTitleInput) {
        ogTitleInput.addEventListener('input', () => updateCharCount('og-title-count', ogTitleInput, 200));
    }
    
    if (ogDescInput) {
        ogDescInput.addEventListener('input', () => updateCharCount('og-desc-count', ogDescInput, 500));
    }
    
    // Global settings forms
    const globalMetaForm = document.getElementById('global-meta-form');
    const globalOgForm = document.getElementById('global-og-form');
    const globalTwitterForm = document.getElementById('global-twitter-form');
    const globalStructuredForm = document.getElementById('global-structured-form');
    
    if (globalMetaForm) {
        globalMetaForm.addEventListener('submit', handleGlobalMetaUpdate);
    }
    
    if (globalOgForm) {
        globalOgForm.addEventListener('submit', handleGlobalOgUpdate);
    }
    
    if (globalTwitterForm) {
        globalTwitterForm.addEventListener('submit', handleGlobalTwitterUpdate);
    }
    
    if (globalStructuredForm) {
        globalStructuredForm.addEventListener('submit', handleGlobalStructuredUpdate);
    }
    
    // Character counting for global settings
    const globalMetaDescInput = document.getElementById('default-meta-description');
    const globalOgDescInput = document.getElementById('default-og-description');
    
    if (globalMetaDescInput) {
        globalMetaDescInput.addEventListener('input', () => {
            updateCharCount('meta-desc-count', globalMetaDescInput, 500);
        });
    }
    
    if (globalOgDescInput) {
        globalOgDescInput.addEventListener('input', () => {
            updateCharCount('og-desc-count', globalOgDescInput, 300);
        });
    }
    
    // Make global functions available
    window.applyGlobalSettings = applyGlobalSettings;
    window.resetGlobalSettings = resetGlobalSettings;
    window.openImageSelector = openImageSelector;
}

// Load articles with SEO data
function loadArticles() {
    const tableBody = document.getElementById('articles-table-body');
    if (!tableBody) return;
    
    // Show loading state
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-xl"></i>
                <p class="mt-2">Memuat artikel...</p>
            </td>
        </tr>
    `;
    
    // Get filter values
    const search = document.getElementById('search-articles')?.value || '';
    const status = document.getElementById('status-filter')?.value || '';
    const seoStatus = document.getElementById('seo-status-filter')?.value || '';
    const category = document.getElementById('category-filter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (seoStatus) params.append('seo_status', seoStatus);
    if (category) params.append('category', category);
    params.append('page', '1');
    params.append('per_page', '10');
    
    // Fetch articles
    fetch(`/api/seo/articles?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displayArticles(data.articles, data.pagination);
            loadCategories(); // Load categories for filter
        })
        .catch(error => {
            console.error('Error loading articles:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-xl"></i>
                        <p class="mt-2">Error memuat artikel: ${error.message}</p>
                    </td>
                </tr>
            `;
        });
}

// Display articles in the table
function displayArticles(articles, pagination) {
    const tableBody = document.getElementById('articles-table-body');
    if (!tableBody) return;
    
    if (articles.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-inbox text-xl"></i>
                    <p class="mt-2">Tidak ada artikel ditemukan</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = articles.map(article => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <img class="h-10 w-10 rounded-lg object-cover" 
                             src="${article.image_url || '/static/pic/placeholder.png'}" 
                             alt="${article.title}">
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${article.title}</div>
                        <div class="text-sm text-gray-500">${article.writer}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${article.category_name}</td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeoStatusColor(article.seo_status)}">
                    ${getSeoStatusText(article.seo_status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.meta_description ? 
                    `<span class="text-green-600"><i class="fas fa-check"></i></span>` : 
                    `<span class="text-red-600"><i class="fas fa-times"></i></span>`
                }
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.meta_keywords ? 
                    `<span class="text-green-600"><i class="fas fa-check"></i></span>` : 
                    `<span class="text-red-600"><i class="fas fa-times"></i></span>`
                }
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.og_title && article.og_description ? 
                    `<span class="text-green-600"><i class="fas fa-check"></i></span>` : 
                    `<span class="text-red-600"><i class="fas fa-times"></i></span>`
                }
            </td>
            <td class="px-6 py-4 text-sm font-medium">
                <button onclick="editSeo(${article.id})" 
                        class="text-blue-600 hover:text-blue-900 mr-3">
                    <i class="fas fa-edit"></i> Edit
                </button>
            </td>
        </tr>
    `).join('');
    
    // Update pagination info
    updatePaginationInfo(pagination);
}

// Load analytics data
function loadAnalytics() {
    fetch('/api/seo/metrics')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displayAnalytics(data);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            showToast('Error memuat analitik SEO', 'error');
        });
}

// Display analytics data
function displayAnalytics(data) {
    // Update metric cards
    const completeCount = document.getElementById('complete-seo-count');
    const incompleteCount = document.getElementById('incomplete-seo-count');
    const missingCount = document.getElementById('missing-seo-count');
    const completionRate = document.getElementById('seo-completion-rate');
    
    if (completeCount) completeCount.textContent = data.complete_count || 0;
    if (incompleteCount) incompleteCount.textContent = data.incomplete_count || 0;
    if (missingCount) missingCount.textContent = data.missing_count || 0;
    if (completionRate) completionRate.textContent = `${data.completion_rate || 0}%`;
    
    // Update recent activity
    const recentTotal = document.getElementById('recent-total');
    const recentComplete = document.getElementById('recent-complete');
    const recentCompletionRate = document.getElementById('recent-completion-rate');
    
    if (recentTotal && data.recent_activity) recentTotal.textContent = data.recent_activity.total_recent || 0;
    if (recentComplete && data.recent_activity) recentComplete.textContent = data.recent_activity.complete_recent || 0;
    if (recentCompletionRate && data.recent_activity) recentCompletionRate.textContent = `${data.recent_activity.recent_completion_rate || 0}%`;
    
    // Display field completion chart
    displayFieldCompletion(data.field_completion);
    
    // Display category analysis
    displayCategoryAnalysis(data.category_stats);
    
    // Store issues data for filtering
    if (data.issues) {
        storeIssuesData(data.issues);
    }
    
    // Display SEO issues with priority indicators
    const issuesList = document.getElementById('seo-issues-list');
    if (issuesList && data.issues) {
        if (data.issues.length === 0) {
            issuesList.innerHTML = `
                <div class="text-center text-green-600 py-4">
                    <i class="fas fa-check-circle text-xl"></i>
                    <p class="mt-2">Tidak ada masalah SEO yang perlu diperbaiki</p>
                </div>
            `;
        } else {
            issuesList.innerHTML = data.issues.map(issue => {
                const priorityColor = issue.priority === 'high' ? 'red' : issue.priority === 'medium' ? 'yellow' : 'blue';
                const priorityIcon = issue.priority === 'high' ? 'exclamation-triangle' : issue.priority === 'medium' ? 'exclamation-circle' : 'info-circle';
                
                return `
                    <div class="flex items-center justify-between p-3 bg-${priorityColor}-50 rounded-lg border-l-4 border-${priorityColor}-500">
                        <div class="flex-1">
                            <div class="flex items-center mb-1">
                                <i class="fas fa-${priorityIcon} text-${priorityColor}-600 mr-2"></i>
                                <h4 class="font-medium text-${priorityColor}-900">${issue.title}</h4>
                                <span class="ml-2 px-2 py-1 text-xs font-semibold rounded-full bg-${priorityColor}-100 text-${priorityColor}-800">
                                    ${issue.priority.toUpperCase()}
                                </span>
                            </div>
                            <p class="text-sm text-${priorityColor}-700">${issue.description}</p>
                            <p class="text-xs text-gray-500 mt-1">Kategori: ${issue.category || 'Tidak diketahui'}</p>
                        </div>
                        <button onclick="editSeo(${issue.article_id})" 
                                class="ml-4 px-3 py-1 text-sm bg-${priorityColor}-600 text-white rounded hover:bg-${priorityColor}-700">
                            <i class="fas fa-edit mr-1"></i>Perbaiki
                        </button>
                    </div>
                `;
            }).join('');
        }
    }
}

// Display field completion chart
function displayFieldCompletion(fieldCompletion) {
    const chartContainer = document.getElementById('field-completion-chart');
    if (!chartContainer || !fieldCompletion) return;
    
    const fieldLabels = {
        'meta_description': 'Meta Description',
        'meta_keywords': 'Meta Keywords',
        'og_title': 'OG Title',
        'og_description': 'OG Description',
        'og_image': 'OG Image',
        'seo_slug': 'SEO Slug',
        'canonical_url': 'Canonical URL',
        'twitter_card': 'Twitter Card'
    };
    
    const fieldIcons = {
        'meta_description': 'fas fa-tag',
        'meta_keywords': 'fas fa-key',
        'og_title': 'fas fa-heading',
        'og_description': 'fas fa-align-left',
        'og_image': 'fas fa-image',
        'seo_slug': 'fas fa-link',
        'canonical_url': 'fas fa-external-link-alt',
        'twitter_card': 'fab fa-twitter'
    };
    
    chartContainer.innerHTML = Object.entries(fieldCompletion).map(([field, percentage]) => {
        const color = percentage >= 80 ? 'green' : percentage >= 50 ? 'yellow' : 'red';
        const icon = fieldIcons[field] || 'fas fa-chart-bar';
        const label = fieldLabels[field] || field;
        
        return `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <i class="${icon} text-${color}-600 mr-3"></i>
                    <span class="font-medium text-gray-700">${label}</span>
                </div>
                <div class="flex items-center">
                    <div class="w-24 bg-gray-200 rounded-full h-2 mr-3">
                        <div class="bg-${color}-500 h-2 rounded-full" style="width: ${percentage}%"></div>
                    </div>
                    <span class="text-sm font-semibold text-${color}-600">${percentage}%</span>
                </div>
            </div>
        `;
    }).join('');
}

// Display category analysis
function displayCategoryAnalysis(categoryStats) {
    const analysisContainer = document.getElementById('category-analysis');
    if (!analysisContainer || !categoryStats) return;
    
    // Sort categories by completion rate (descending)
    const sortedCategories = Object.entries(categoryStats).sort((a, b) => b[1].completion_rate - a[1].completion_rate);
    
    analysisContainer.innerHTML = sortedCategories.map(([category, stats]) => {
        const color = stats.completion_rate >= 80 ? 'green' : stats.completion_rate >= 50 ? 'yellow' : 'red';
        
        return `
            <div class="border border-gray-200 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium text-gray-900">${category}</h4>
                    <span class="text-sm font-semibold text-${color}-600">${stats.completion_rate}%</span>
                </div>
                <div class="flex justify-between text-xs text-gray-500 mb-2">
                    <span>Total: ${stats.total}</span>
                    <span>Lengkap: ${stats.complete}</span>
                    <span>Tidak lengkap: ${stats.incomplete}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-${color}-500 h-2 rounded-full" style="width: ${stats.completion_rate}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

// Load global settings
function loadGlobalSettings() {
    fetch('/api/seo/global-settings')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Populate form fields
            const metaDescField = document.getElementById('default-meta-description');
            const metaKeywordsField = document.getElementById('default-meta-keywords');
            const ogTitleField = document.getElementById('default-og-title');
            const ogDescField = document.getElementById('default-og-description');
            const ogImageField = document.getElementById('default-og-image');
            
            if (metaDescField) metaDescField.value = data.default_meta_description || '';
            if (metaKeywordsField) metaKeywordsField.value = data.default_meta_keywords || '';
            if (ogTitleField) ogTitleField.value = data.default_og_title || '';
            if (ogDescField) ogDescField.value = data.default_og_description || '';
            if (ogImageField) ogImageField.value = data.default_og_image || '';
        })
        .catch(error => {
            console.error('Error loading global settings:', error);
            showToast('Error memuat pengaturan global', 'error');
        });
}

// Load categories for filter
function loadCategories() {
    fetch('/api/seo/categories')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(categories => {
            const categoryFilter = document.getElementById('category-filter');
            if (categoryFilter) {
                const currentValue = categoryFilter.value;
                categoryFilter.innerHTML = '<option value="">Semua Kategori</option>' +
                    categories.map(cat => `<option value="${cat.name}">${cat.name}</option>`).join('');
                categoryFilter.value = currentValue;
            }
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

// Edit SEO for an article
function editSeo(articleId) {
    console.log('=== EDIT SEO CALLED ===', articleId);
    fetch(`/api/seo/articles/${articleId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(article => {
            console.log('Article loaded for editing:', article.title);
            // Populate modal fields
            document.getElementById('edit-article-id').value = article.id;
            document.getElementById('edit-article-title').textContent = article.title;
            document.getElementById('edit-article-category').textContent = article.category_name;
            
            // SEO fields
            document.getElementById('edit-meta-description').value = article.meta_description || '';
            document.getElementById('edit-meta-keywords').value = article.meta_keywords || '';
            document.getElementById('edit-og-title').value = article.og_title || '';
            document.getElementById('edit-og-description').value = article.og_description || '';
            document.getElementById('edit-og-image').value = article.og_image || '';
            document.getElementById('edit-canonical-url').value = article.canonical_url || '';
            document.getElementById('edit-seo-slug').value = article.seo_slug || '';
            
            // Twitter fields
            document.getElementById('edit-twitter-card').value = article.twitter_card || '';
            document.getElementById('edit-twitter-title').value = article.twitter_title || '';
            document.getElementById('edit-twitter-description').value = article.twitter_description || '';
            document.getElementById('edit-twitter-image').value = article.twitter_image || '';
            
            // Advanced fields
            document.getElementById('edit-meta-author').value = article.meta_author || '';
            document.getElementById('edit-meta-language').value = article.meta_language || 'id';
            document.getElementById('edit-meta-robots').value = article.meta_robots || 'index, follow';
            document.getElementById('edit-structured-data-type').value = article.structured_data_type || 'Article';
            
            // Update character counts
            updateCharCount('meta-desc-count', document.getElementById('edit-meta-description'), 500);
            updateCharCount('og-title-count', document.getElementById('edit-og-title'), 200);
            updateCharCount('og-desc-count', document.getElementById('edit-og-description'), 500);
            
            // Update preview
            updatePreview(article);
            
            // Hide all other modals first
            hideAllModals();
            
            // Show modal
            const editModal = document.getElementById('edit-seo-modal');
            editModal.classList.remove('hidden');
            editModal.style.display = 'block';
            console.log('Edit modal should now be visible');
        })
        .catch(error => {
            console.error('Error loading article for editing:', error);
            showToast('Error memuat data artikel', 'error');
        });
}

// Handle SEO update
function handleSeoUpdate(event) {
    event.preventDefault();
    
    const articleId = document.getElementById('edit-article-id').value;
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch(`/api/seo/articles/${articleId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        showToast('SEO berhasil diperbarui', 'success');
        closeEditModal();
        loadArticles(); // Refresh the articles list
    })
    .catch(error => {
        console.error('Error updating SEO:', error);
        showToast('Error memperbarui SEO', 'error');
    });
}

// Handle global meta settings update
function handleGlobalMetaUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/seo/global-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        showToast('Pengaturan meta global berhasil disimpan', 'success');
    })
    .catch(error => {
        console.error('Error updating global meta settings:', error);
        showToast('Error menyimpan pengaturan meta global', 'error');
    });
}

// Handle global OG settings update
function handleGlobalOgUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/seo/global-og', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        showToast('Pengaturan Open Graph global berhasil disimpan', 'success');
    })
    .catch(error => {
        console.error('Error updating global OG settings:', error);
        showToast('Error menyimpan pengaturan Open Graph global', 'error');
    });
}

// Handle global Twitter settings update
function handleGlobalTwitterUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/seo/global-twitter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        showToast('Pengaturan Twitter Card global berhasil disimpan', 'success');
    })
    .catch(error => {
        console.error('Error updating global Twitter settings:', error);
        showToast('Error menyimpan pengaturan Twitter Card global', 'error');
    });
}

// Handle global structured data settings update
function handleGlobalStructuredUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/seo/global-structured', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        showToast('Pengaturan Structured Data global berhasil disimpan', 'success');
    })
    .catch(error => {
        console.error('Error updating global structured data settings:', error);
        showToast('Error menyimpan pengaturan Structured Data global', 'error');
    });
}

// Apply global settings to all articles
function applyGlobalSettings() {
    showConfirmationModal(
        'Apakah Anda yakin ingin menerapkan pengaturan global ke semua artikel? Tindakan ini akan memperbarui artikel yang belum memiliki pengaturan SEO.',
        () => {
            fetch('/api/seo/apply-global-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                showToast(`Berhasil menerapkan pengaturan global ke ${result.updated_count} artikel`, 'success');
                loadAnalytics(); // Refresh analytics
            })
            .catch(error => {
                console.error('Error applying global settings:', error);
                showToast('Error menerapkan pengaturan global', 'error');
            });
        }
    );
}

// Reset global settings
function resetGlobalSettings() {
    showConfirmationModal(
        'Apakah Anda yakin ingin mereset semua pengaturan global ke nilai default?',
        () => {
            // Reset all form fields
            document.getElementById('default-meta-description').value = '';
            document.getElementById('default-meta-keywords').value = '';
            document.getElementById('default-meta-author').value = '';
            document.getElementById('default-meta-robots').value = 'index, follow';
            document.getElementById('default-og-title').value = '';
            document.getElementById('default-og-description').value = '';
            document.getElementById('default-og-image').value = '';
            document.getElementById('default-twitter-card').value = 'summary';
            document.getElementById('default-twitter-title').value = '';
            document.getElementById('default-twitter-description').value = '';
            document.getElementById('default-structured-data-type').value = 'Article';
            document.getElementById('default-canonical-url').value = '';
            document.getElementById('default-meta-language').value = 'id';
            
            // Hide image preview
            document.getElementById('og-image-preview').classList.add('hidden');
            
            showToast('Pengaturan global telah direset', 'success');
        }
    );
}

// Open image selector modal
function openImageSelector(targetField) {
    // Hide all other modals first
    hideAllModals();
    
    window.currentImageTarget = targetField;
    const modal = document.getElementById('image-selector-modal');
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    
    // Load image library
    loadImageLibrary();
    
    // Setup event listeners
    setupImageSelectorEvents();
}

// Load image library for selector
function loadImageLibrary(page = 1) {
    fetch(`/api/images?page=${page}&per_page=12`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('image-library-section-selector');
            container.innerHTML = '';
            
            if (data.items && data.items.length > 0) {
                data.items.forEach(image => {
                    const imageCard = document.createElement('div');
                    imageCard.className = 'bg-white rounded-lg shadow-md p-2 cursor-pointer hover:shadow-lg transition-shadow duration-200';
                    imageCard.innerHTML = `
                        <img src="${image.file_url || image.url}" alt="${image.description || 'Image'}" class="w-full h-24 object-cover rounded mb-2">
                        <p class="text-xs text-gray-600 truncate">${image.filename || 'Untitled'}</p>
                    `;
                    imageCard.onclick = () => selectImageFromLibrary(image.file_url || image.url, image.description);
                    container.appendChild(imageCard);
                });
            } else {
                container.innerHTML = `
                    <div class="col-span-3 text-center text-gray-500 py-8">
                        <i class="fas fa-images text-4xl mb-4"></i>
                        <p>Tidak ada gambar tersedia</p>
                    </div>
                `;
            }
            
            // Update pagination
            updateImageSelectorPagination({
                current_page: data.page,
                total_pages: data.total_pages,
                total_items: data.total_items
            });
        })
        .catch(error => {
            console.error('Error loading image library:', error);
            showToast('Error memuat perpustakaan gambar', 'error');
        });
}

// Select image from library
function selectImageFromLibrary(url, altText) {
    const targetField = window.currentImageTarget;
    document.getElementById(targetField).value = url;
    
    // Show preview if it's OG image
    if (targetField === 'default-og-image') {
        const preview = document.getElementById('og-image-preview');
        preview.src = url;
        preview.classList.remove('hidden');
    }
    
    // Close modal
    hideAllModals();
    showToast('Gambar berhasil dipilih', 'success');
}

// Setup image selector events
function setupImageSelectorEvents() {
    // Radio button change
    document.querySelectorAll('input[name="image-source-selector"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const librarySection = document.getElementById('image-library-section-selector');
            const urlSection = document.getElementById('image-url-section-selector');
            
            if (this.value === 'library') {
                librarySection.classList.remove('hidden');
                urlSection.classList.add('hidden');
            } else {
                librarySection.classList.add('hidden');
                urlSection.classList.remove('hidden');
            }
        });
    });
    
    // Select image button
    document.getElementById('select-image-btn').onclick = () => {
        const urlInput = document.getElementById('image-url-input-selector');
        const url = urlInput.value.trim();
        
        if (!url) {
            showToast('Masukkan URL gambar', 'error');
            return;
        }
        
        const targetField = window.currentImageTarget;
        document.getElementById(targetField).value = url;
        
        // Show preview if it's OG image
        if (targetField === 'default-og-image') {
            const preview = document.getElementById('og-image-preview');
            preview.src = url;
            preview.classList.remove('hidden');
        }
        
        // Close modal
        document.getElementById('image-selector-modal').classList.add('hidden');
        showToast('Gambar berhasil dipilih', 'success');
    };
    
    // Close button
    document.getElementById('close-image-selector').onclick = () => {
        document.getElementById('image-selector-modal').classList.add('hidden');
    };
}

// Update image selector pagination
function updateImageSelectorPagination(pagination) {
    const container = document.getElementById('image-selector-pagination-controls');
    container.innerHTML = '';
    
    if (pagination.total_pages <= 1) return;
    
    const ul = document.createElement('ul');
    ul.className = 'flex justify-center space-x-1';
    
    // Previous button
    if (pagination.current_page > 1) {
        const prevLi = document.createElement('li');
        prevLi.innerHTML = `<button onclick="loadImageLibrary(${pagination.current_page - 1})" class="px-3 py-2 text-sm bg-white border border-amber-300 text-amber-700 rounded-lg hover:bg-amber-50">Previous</button>`;
        ul.appendChild(prevLi);
    }
    
    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        const li = document.createElement('li');
        const buttonClass = i === pagination.current_page 
            ? 'px-3 py-2 text-sm bg-amber-500 text-white rounded-lg' 
            : 'px-3 py-2 text-sm bg-white border border-amber-300 text-amber-700 rounded-lg hover:bg-amber-50';
        li.innerHTML = `<button onclick="loadImageLibrary(${i})" class="${buttonClass}">${i}</button>`;
        ul.appendChild(li);
    }
    
    // Next button
    if (pagination.current_page < pagination.total_pages) {
        const nextLi = document.createElement('li');
        nextLi.innerHTML = `<button onclick="loadImageLibrary(${pagination.current_page + 1})" class="px-3 py-2 text-sm bg-white border border-amber-300 text-amber-700 rounded-lg hover:bg-amber-50">Next</button>`;
        ul.appendChild(nextLi);
    }
    
    container.appendChild(ul);
}

// Close edit modal
function closeEditModal() {
    hideAllModals();
    // Reset form when closing
    document.getElementById('edit-seo-form').reset();
}

// Update character count
function updateCharCount(elementId, input, maxLength) {
    const countElement = document.getElementById(elementId);
    if (countElement && input) {
        const currentLength = input.value.length;
        countElement.textContent = `${currentLength}/${maxLength}`;
        
        if (currentLength > maxLength) {
            countElement.classList.add('text-red-600');
        } else {
            countElement.classList.remove('text-red-600');
        }
    }
}

// Update preview
function updatePreview(article) {
    const previewUrl = document.getElementById('preview-url');
    const previewTitle = document.getElementById('preview-title');
    const previewDescription = document.getElementById('preview-description');
    
    if (previewUrl) previewUrl.textContent = `https://example.com/${article.seo_slug || 'article'}`;
    if (previewTitle) previewTitle.textContent = article.og_title || article.title;
    if (previewDescription) previewDescription.textContent = article.og_description || article.meta_description || 'Deskripsi artikel akan muncul di sini...';
}

// Update pagination info
function updatePaginationInfo(pagination) {
    const showingStart = document.getElementById('showing-start');
    const showingEnd = document.getElementById('showing-end');
    const totalArticles = document.getElementById('total-articles');
    const paginationControls = document.getElementById('pagination-controls');
    
    if (showingStart) showingStart.textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    if (showingEnd) showingEnd.textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    if (totalArticles) totalArticles.textContent = pagination.total_items;
    
    // Generate pagination controls using the same style as pagination.html
    if (paginationControls) {
        let controls = '';
        
        // First page button
        if (pagination.current_page > 1) {
            controls += `<button onclick="changePage(1)" class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-amber-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-400/20 focus:border-amber-400" aria-label="Ke halaman pertama" title="Ke halaman pertama">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" />
                </svg>
            </button>`;
        } else {
            controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-400 opacity-50 cursor-not-allowed" aria-disabled="true" aria-label="Ke halaman pertama (tidak tersedia)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" />
                </svg>
            </span>`;
        }
        
        // Previous button
        if (pagination.has_prev) {
            controls += `<button onclick="changePage(${pagination.current_page - 1})" class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-amber-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-400/20 focus:border-amber-400" aria-label="Ke halaman sebelumnya" title="Ke halaman sebelumnya">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                </svg>
            </button>`;
        } else {
            controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-400 opacity-50 cursor-not-allowed" aria-disabled="true" aria-label="Halaman sebelumnya (tidak tersedia)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                </svg>
            </span>`;
        }
        
        // Page numbers
        const leftEdge = 1;
        const rightEdge = 1;
        const leftCurrent = 2;
        const rightCurrent = 2;
        
        for (let i = Math.max(1, pagination.current_page - leftCurrent); i <= Math.min(pagination.total_pages, pagination.current_page + rightCurrent); i++) {
            if (i === 1 || i === pagination.total_pages || (i >= pagination.current_page - leftCurrent && i <= pagination.current_page + rightCurrent)) {
                if (i === pagination.current_page) {
                    controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-amber-600 text-white font-semibold shadow-sm text-sm" aria-current="page" title="Halaman ${i}">${i}</span>`;
                } else {
                    controls += `<button onclick="changePage(${i})" class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-amber-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-400/20 focus:border-amber-400 text-sm" aria-label="Ke halaman ${i}" title="Ke halaman ${i}">${i}</button>`;
                }
            } else if (i === pagination.current_page - leftCurrent - 1 || i === pagination.current_page + rightCurrent + 1) {
                controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 text-gray-400 text-sm" aria-hidden="true">...</span>`;
            }
        }
        
        // Next button
        if (pagination.has_next) {
            controls += `<button onclick="changePage(${pagination.current_page + 1})" class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-amber-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-400/20 focus:border-amber-400" aria-label="Ke halaman selanjutnya" title="Ke halaman selanjutnya">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                </svg>
            </button>`;
        } else {
            controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-400 opacity-50 cursor-not-allowed" aria-disabled="true" aria-label="Halaman selanjutnya (tidak tersedia)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                </svg>
            </span>`;
        }
        
        // Last page button
        if (pagination.current_page < pagination.total_pages) {
            controls += `<button onclick="changePage(${pagination.total_pages})" class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-amber-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-400/20 focus:border-amber-400" aria-label="Ke halaman terakhir" title="Ke halaman terakhir">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 4.5l7.5 7.5-7.5 7.5m6-15l7.5 7.5-7.5 7.5" />
                </svg>
            </button>`;
        } else {
            controls += `<span class="inline-flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-300 bg-white text-gray-400 opacity-50 cursor-not-allowed" aria-disabled="true" aria-label="Ke halaman terakhir (tidak tersedia)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 4.5l7.5 7.5-7.5 7.5m6-15l7.5 7.5-7.5 7.5" />
                </svg>
            </span>`;
        }
        
        paginationControls.innerHTML = controls;
    }
}

// Change page
function changePage(page) {
    // Store current filter values
    const search = document.getElementById('search-articles')?.value || '';
    const status = document.getElementById('status-filter')?.value || '';
    const seoStatus = document.getElementById('seo-status-filter')?.value || '';
    const category = document.getElementById('category-filter')?.value || '';
    
    // Build query parameters with new page
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (seoStatus) params.append('seo_status', seoStatus);
    if (category) params.append('category', category);
    params.append('page', page.toString());
    params.append('per_page', '10');
    
    // Fetch articles with new page
    const tableBody = document.getElementById('articles-table-body');
    if (tableBody) {
        // Show loading state
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-spinner fa-spin text-xl"></i>
                    <p class="mt-2">Memuat artikel...</p>
                </td>
            </tr>
        `;
    }
    
    fetch(`/api/seo/articles?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displayArticles(data.articles, data.pagination);
        })
        .catch(error => {
            console.error('Error loading articles:', error);
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 text-center text-red-500">
                            <i class="fas fa-exclamation-triangle text-xl"></i>
                            <p class="mt-2">Error memuat artikel: ${error.message}</p>
                        </td>
                    </tr>
                `;
            }
        });
}

// Get SEO status color
function getSeoStatusColor(status) {
    switch (status) {
        case 'complete':
            return 'bg-green-100 text-green-800';
        case 'incomplete':
            return 'bg-yellow-100 text-yellow-800';
        case 'missing':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

// Get SEO status text
function getSeoStatusText(status) {
    switch (status) {
        case 'complete':
            return 'Lengkap';
        case 'incomplete':
            return 'Tidak Lengkap';
        case 'missing':
            return 'Hilang';
        default:
            return 'Tidak Diketahui';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Modal management system
function hideAllModals() {
    console.log('hideAllModals called');
    const modals = [
        'edit-seo-modal',
        'confirmation-modal', 
        'image-selector-modal'
    ];
    
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            console.log(`Hiding modal: ${modalId}`);
            modal.classList.add('hidden');
            modal.style.display = 'none';
        } else {
            console.log(`Modal not found: ${modalId}`);
        }
    });
}

// Show confirmation modal
function showConfirmationModal(message, onConfirm) {
    console.log('showConfirmationModal called with message:', message);
    console.log('onConfirm function:', typeof onConfirm);
    
    // Hide all other modals first
    hideAllModals();
    
    const modal = document.getElementById('confirmation-modal');
    const messageElement = document.getElementById('confirmation-message');
    const confirmButton = document.getElementById('confirm-action');
    const cancelButton = document.getElementById('cancel-confirmation');
    
    console.log('Modal elements found:', {
        modal: !!modal,
        messageElement: !!messageElement,
        confirmButton: !!confirmButton,
        cancelButton: !!cancelButton
    });
    
    if (!modal || !messageElement || !confirmButton || !cancelButton) {
        console.error('Some modal elements not found!');
        return;
    }
    
    // Set message
    messageElement.textContent = message;
    
    // Show modal
    modal.classList.remove('hidden');
    modal.style.display = 'block';
    console.log('Confirmation modal should now be visible');
    
    // Handle confirm
    const handleConfirm = () => {
        console.log('Confirm button clicked');
        hideAllModals();
        onConfirm();
        // Clean up event listeners
        confirmButton.removeEventListener('click', handleConfirm);
        cancelButton.removeEventListener('click', handleCancel);
        modal.removeEventListener('click', handleModalClick);
        document.removeEventListener('keydown', handleKeydown);
    };
    
    // Handle cancel
    const handleCancel = () => {
        console.log('Cancel button clicked');
        hideAllModals();
        // Clean up event listeners
        confirmButton.removeEventListener('click', handleConfirm);
        cancelButton.removeEventListener('click', handleCancel);
        modal.removeEventListener('click', handleModalClick);
        document.removeEventListener('keydown', handleKeydown);
    };
    
    // Handle click outside modal
    const handleModalClick = (e) => {
        if (e.target === modal) {
            handleCancel();
        }
    };
    
    // Handle escape key
    const handleKeydown = (e) => {
        if (e.key === 'Escape') {
            handleCancel();
        }
    };
    
    // Add event listeners
    confirmButton.addEventListener('click', handleConfirm);
    cancelButton.addEventListener('click', handleCancel);
    modal.addEventListener('click', handleModalClick);
    document.addEventListener('keydown', handleKeydown);
    
    console.log('Event listeners added to confirmation modal');
}

// Bulk fix missing meta descriptions
function bulkFixMissingMetaDescriptions() {
    console.log('=== BULK FIX META DESCRIPTIONS CALLED ===');
    console.log('Function called from:', new Error().stack);
    console.log('showConfirmationModal function exists:', typeof showConfirmationModal);
    console.log('confirmation-modal element exists:', !!document.getElementById('confirmation-modal'));
    
    showConfirmationModal(
        'Apakah Anda yakin ingin menambahkan meta description otomatis untuk semua artikel yang belum memilikinya?',
        () => {
            console.log('Confirmation accepted, making API call');
            fetch('/api/seo/bulk-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'add_meta_descriptions',
                    field: 'meta_description'
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                showToast(`Berhasil menambahkan meta description untuk ${result.updated_count} artikel`, 'success');
                loadAnalytics(); // Refresh analytics
            })
            .catch(error => {
                console.error('Error bulk updating meta descriptions:', error);
                showToast('Error memperbarui meta descriptions', 'error');
            });
        }
    );
}

// Bulk fix missing OG titles
function bulkFixMissingOGTitles() {
    showConfirmationModal(
        'Apakah Anda yakin ingin menambahkan Open Graph titles otomatis untuk semua artikel yang belum memilikinya?',
        () => {
            fetch('/api/seo/bulk-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'add_og_titles',
                    field: 'og_title'
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                showToast(`Berhasil menambahkan OG titles untuk ${result.updated_count} artikel`, 'success');
                loadAnalytics(); // Refresh analytics
            })
            .catch(error => {
                console.error('Error bulk updating OG titles:', error);
                showToast('Error memperbarui OG titles', 'error');
            });
        }
    );
}

// Bulk fix missing SEO slugs
function bulkFixMissingSlugs() {
    showConfirmationModal(
        'Apakah Anda yakin ingin generate SEO slugs otomatis untuk semua artikel yang belum memilikinya?',
        () => {
            fetch('/api/seo/bulk-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'add_seo_slugs',
                    field: 'seo_slug'
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(result => {
                showToast(`Berhasil menambahkan SEO slugs untuk ${result.updated_count} artikel`, 'success');
                loadAnalytics(); // Refresh analytics
            })
            .catch(error => {
                console.error('Error bulk updating SEO slugs:', error);
                showToast('Error memperbarui SEO slugs', 'error');
            });
        }
    );
}

// Filter issues by priority
function filterIssuesByPriority(priority) {
    const issuesList = document.getElementById('seo-issues-list');
    if (!issuesList) return;
    
    // Store current issues data globally for filtering
    if (!window.currentIssuesData) {
        showToast('Data issues belum dimuat', 'error');
        return;
    }
    
    let filteredIssues = window.currentIssuesData;
    
    if (priority !== 'all') {
        filteredIssues = window.currentIssuesData.filter(issue => issue.priority === priority);
    }
    
    if (filteredIssues.length === 0) {
        issuesList.innerHTML = `
            <div class="text-center text-gray-500 py-4">
                <i class="fas fa-inbox text-xl"></i>
                <p class="mt-2">Tidak ada masalah ${priority === 'all' ? '' : priority + ' priority'} yang ditemukan</p>
            </div>
        `;
        return;
    }
    
    issuesList.innerHTML = filteredIssues.map(issue => {
        const priorityColor = issue.priority === 'high' ? 'red' : issue.priority === 'medium' ? 'yellow' : 'blue';
        const priorityIcon = issue.priority === 'high' ? 'exclamation-triangle' : issue.priority === 'medium' ? 'exclamation-circle' : 'info-circle';
        
        return `
            <div class="flex items-center justify-between p-3 bg-${priorityColor}-50 rounded-lg border-l-4 border-${priorityColor}-500">
                <div class="flex-1">
                    <div class="flex items-center mb-1">
                        <i class="fas fa-${priorityIcon} text-${priorityColor}-600 mr-2"></i>
                        <h4 class="font-medium text-${priorityColor}-900">${issue.title}</h4>
                        <span class="ml-2 px-2 py-1 text-xs font-semibold rounded-full bg-${priorityColor}-100 text-${priorityColor}-800">
                            ${issue.priority.toUpperCase()}
                        </span>
                    </div>
                    <p class="text-sm text-${priorityColor}-700">${issue.description}</p>
                    <p class="text-xs text-gray-500 mt-1">Kategori: ${issue.category || 'Tidak diketahui'}</p>
                </div>
                <button onclick="editSeo(${issue.article_id})" 
                        class="ml-4 px-3 py-1 text-sm bg-${priorityColor}-600 text-white rounded hover:bg-${priorityColor}-700">
                    <i class="fas fa-edit mr-1"></i>Perbaiki
                </button>
            </div>
        `;
    }).join('');
}

// Store issues data globally for filtering
function storeIssuesData(issues) {
    window.currentIssuesData = issues;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
