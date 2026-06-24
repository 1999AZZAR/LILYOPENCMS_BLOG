/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Comprehensive SEO Management JavaScript
// Handles all three SEO types: Articles, Albums, and Root pages

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the page
    initializeComprehensiveSEO();
});

function initializeComprehensiveSEO() {
    // Tab functionality
    initializeTabs();
    
    // Load initial data for each tab
    loadArticlesData();
    loadAlbumsData();
    loadChaptersData();
    loadRootData();
    
    // Load category filters
    loadCategoryFilters();
    
    // Initialize event listeners
    initializeEventListeners();
}

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-white', 'text-gray-800');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active', 'bg-white', 'text-gray-800');
            this.classList.remove('bg-gray-200', 'text-gray-700');
            
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

function initializeEventListeners() {
    // Articles tab events
    document.getElementById('refresh-articles-seo').addEventListener('click', loadArticlesData);
    document.getElementById('search-articles').addEventListener('input', debounce(filterArticles, 300));
    document.getElementById('articles-status-filter').addEventListener('change', filterArticles);
    document.getElementById('articles-seo-status-filter').addEventListener('change', filterArticles);
    document.getElementById('articles-category-filter').addEventListener('change', filterArticles);
    
    // Albums tab events
    document.getElementById('refresh-albums-seo').addEventListener('click', loadAlbumsData);
    document.getElementById('search-albums').addEventListener('input', debounce(filterAlbums, 300));
    document.getElementById('albums-status-filter').addEventListener('change', filterAlbums);
    document.getElementById('albums-seo-status-filter').addEventListener('change', filterAlbums);
    document.getElementById('albums-category-filter').addEventListener('change', filterAlbums);
    
    // Chapters tab events
    document.getElementById('refresh-chapters-seo').addEventListener('click', loadChaptersData);
    document.getElementById('search-chapters').addEventListener('input', debounce(filterChapters, 300));
    document.getElementById('chapters-status-filter').addEventListener('change', filterChapters);
    document.getElementById('chapters-seo-status-filter').addEventListener('change', filterChapters);
    document.getElementById('chapters-category-filter').addEventListener('change', filterChapters);
    
    // Root tab events
    document.getElementById('refresh-root-seo').addEventListener('click', loadRootData);
    document.getElementById('search-root').addEventListener('input', debounce(filterRoot, 300));
    document.getElementById('root-status-filter').addEventListener('change', filterRoot);
    document.getElementById('root-seo-status-filter').addEventListener('change', filterRoot);
    document.getElementById('create-root-seo-btn').addEventListener('click', createRootSEO);
    // root-seo-settings-btn moved to settings.html
    
    // SEO Injection events
    document.getElementById('run-articles-seo-injection').addEventListener('click', () => runSEOInjection('news'));
    document.getElementById('run-albums-seo-injection').addEventListener('click', () => runSEOInjection('albums'));
    document.getElementById('run-chapters-seo-injection').addEventListener('click', () => runSEOInjection('chapters'));
    document.getElementById('run-root-seo-injection').addEventListener('click', () => runSEOInjection('root'));
    
    // Modal events
    document.getElementById('close-seo-modal').addEventListener('click', closeEditModal);
    document.getElementById('cancel-seo-edit').addEventListener('click', closeEditModal);
    document.getElementById('edit-seo-form').addEventListener('submit', handleEditSubmit);
    
    // Confirmation modal events
    document.getElementById('cancel-confirmation').addEventListener('click', closeConfirmationModal);
    document.getElementById('confirm-action').addEventListener('click', executeConfirmedAction);

    // Delegate individual inject buttons
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.inject-seo-btn');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const type = btn.getAttribute('data-type');
            confirmAndInjectSingle(type, id);
        }
    });
}

function loadCategoryFilters() {
    // Load categories for articles filter
    fetchWithCSRF('/api/categories?grouped=true')
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const articlesCategoryFilter = document.getElementById('articles-category-filter');
                const albumsCategoryFilter = document.getElementById('albums-category-filter');
                const chaptersCategoryFilter = document.getElementById('chapters-category-filter');
                
                // Clear existing options except the first one
                articlesCategoryFilter.innerHTML = '<option value="">Semua Kategori</option>';
                albumsCategoryFilter.innerHTML = '<option value="">Semua Kategori</option>';
                chaptersCategoryFilter.innerHTML = '<option value="">Semua Kategori</option>';
                
                // Add category options dynamically supporting both flat and grouped formats
                if (data.length > 0) {
                    const isGrouped = data[0] && typeof data[0] === 'object' && 'group' in data[0] && 'categories' in data[0];
                    if (isGrouped) {
                        data.forEach(groupData => {
                            if (!groupData.group || !groupData.categories) return;
                            const optgroup = document.createElement('optgroup');
                            optgroup.label = groupData.group.name || 'Lainnya';
                            groupData.categories.forEach(category => {
                                ['articles', 'albums', 'chapters'].forEach(type => {
                                    const option = document.createElement('option');
                                    option.value = category.id;
                                    option.textContent = category.name;
                                    const filterEl = document.getElementById(`${type}-category-filter`);
                                    if (filterEl) filterEl.appendChild(option);
                                });
                            });
                        });
                    } else {
                        data.forEach(category => {
                            ['articles', 'albums', 'chapters'].forEach(type => {
                                const option = document.createElement('option');
                                option.value = category.id;
                                option.textContent = category.name;
                                const filterEl = document.getElementById(`${type}-category-filter`);
                                if (filterEl) filterEl.appendChild(option);
                            });
                        });
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

// Articles Management
function loadArticlesData(page = 1) {
    const tableBody = document.getElementById('articles-table-body');
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-xl"></i>
                <p class="mt-2">Memuat artikel...</p>
            </td>
        </tr>
    `;
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        per_page: 20
    });
    
    // Add filters if they exist
    const searchValue = document.getElementById('search-articles').value;
    const statusValue = document.getElementById('articles-status-filter').value;
    const seoStatusValue = document.getElementById('articles-seo-status-filter').value;
    const categoryValue = document.getElementById('articles-category-filter').value;
    
    if (searchValue) params.append('search', searchValue);
    if (statusValue) params.append('status', statusValue);
    if (seoStatusValue) params.append('seo_status', seoStatusValue);
    if (categoryValue) params.append('category', categoryValue);
    
    fetchWithCSRF(`/api/seo/articles?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.articles) {
                renderArticlesTable(data.articles);
                updateArticlesPagination(data.pagination);
                updateArticlesCounts(data.pagination);
            }
        })
        .catch(error => {
            console.error('Error loading articles:', error);
            showToast('Error loading articles data', 'error');
        });
}

function renderArticlesTable(articles) {
    const tableBody = document.getElementById('articles-table-body');
    
    if (articles.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    Tidak ada artikel ditemukan
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = articles.map(article => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${article.title}</div>
                <div class="text-sm text-gray-500">${article.writer}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${article.category_name}</td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSEOStatusClass(article.seo_status)}">
                    ${getSEOStatusText(article.seo_status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.meta_description ? article.meta_description.substring(0, 50) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.meta_keywords ? article.meta_keywords.substring(0, 30) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${article.og_title ? '✓' : '✗'}
            </td>
            <td class="px-6 py-4 text-sm font-medium">
                <div class="inline-flex items-center gap-2">
                    <button class="edit-seo-btn px-2 py-1 rounded-md text-blue-600 hover:text-blue-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${article.id}" data-type="article" title="Edit SEO" aria-label="Edit SEO">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="inject-seo-btn px-2 py-1 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${article.id}" data-type="article" title="Inject SEO" aria-label="Inject SEO">
                        <i class="fas fa-magic"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-seo-btn[data-type="article"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const articleId = this.getAttribute('data-id');
            openEditModal(articleId, 'article');
        });
    });
}

// Albums Management
function loadAlbumsData(page = 1) {
    const tableBody = document.getElementById('albums-table-body');
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-xl"></i>
                <p class="mt-2">Memuat album...</p>
            </td>
        </tr>
    `;
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        per_page: 20
    });
    
    // Add filters if they exist
    const searchValue = document.getElementById('search-albums').value;
    const statusValue = document.getElementById('albums-status-filter').value;
    const seoStatusValue = document.getElementById('albums-seo-status-filter').value;
    const categoryValue = document.getElementById('albums-category-filter').value;
    
    if (searchValue) params.append('search', searchValue);
    if (statusValue) params.append('status', statusValue);
    if (seoStatusValue) params.append('seo_status', seoStatusValue);
    if (categoryValue) params.append('category', categoryValue);
    
    fetchWithCSRF(`/api/seo/albums?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.albums) {
                renderAlbumsTable(data.albums);
                updateAlbumsPagination(data.pagination);
                updateAlbumsCounts(data.pagination);
            } else {
                // Handle case where no albums data is returned
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                            Tidak ada album ditemukan
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading albums:', error);
            showToast('Error loading albums data', 'error');
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-xl mb-2"></i>
                        <p class="mt-2">Error loading albums data</p>
                        <p class="text-sm text-red-400">${error.message}</p>
                        <p class="text-xs text-red-300 mt-1">Please check if you are logged in and have proper permissions.</p>
                    </td>
                </tr>
            `;
        });
}

function renderAlbumsTable(albums) {
    const tableBody = document.getElementById('albums-table-body');
    
    if (albums.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    Tidak ada album ditemukan
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = albums.map(album => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${album.title}</div>
                <div class="text-sm text-gray-500">${album.category_name}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${album.category_name}</td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSEOStatusClass(album.seo_status)}">
                    ${getSEOStatusText(album.seo_status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${album.meta_description ? album.meta_description.substring(0, 50) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${album.meta_keywords ? album.meta_keywords.substring(0, 30) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${album.og_title ? '✓' : '✗'}
            </td>
            <td class="px-6 py-4 text-sm font-medium">
                <div class="inline-flex items-center gap-2">
                    <button class="edit-seo-btn px-2 py-1 rounded-md text-blue-600 hover:text-blue-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${album.id}" data-type="album" title="Edit SEO" aria-label="Edit SEO">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="inject-seo-btn px-2 py-1 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${album.id}" data-type="album" title="Inject SEO" aria-label="Inject SEO">
                        <i class="fas fa-magic"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-seo-btn[data-type="album"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const albumId = this.getAttribute('data-id');
            openEditModal(albumId, 'album');
        });
    });
}

// Chapters Management
function loadChaptersData(page = 1) {
    const tableBody = document.getElementById('chapters-table-body');
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-xl"></i>
                <p class="mt-2">Memuat bab...</p>
            </td>
        </tr>
    `;
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        per_page: 20
    });
    
    // Add filters if they exist
    const searchValue = document.getElementById('search-chapters').value;
    const statusValue = document.getElementById('chapters-status-filter').value;
    const seoStatusValue = document.getElementById('chapters-seo-status-filter').value;
    const categoryValue = document.getElementById('chapters-category-filter').value;
    
    if (searchValue) params.append('search', searchValue);
    if (statusValue) params.append('status', statusValue);
    if (seoStatusValue) params.append('seo_status', seoStatusValue);
    if (categoryValue) params.append('category', categoryValue);
    
    fetchWithCSRF(`/api/seo/chapters?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.chapters) {
                renderChaptersTable(data.chapters);
                updateChaptersPagination(data.pagination);
                updateChaptersCounts(data.pagination);
            } else {
                // Handle case where no chapters data is returned
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                            Tidak ada bab ditemukan
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading chapters:', error);
            showToast('Error loading chapters data', 'error');
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-xl mb-2"></i>
                        <p class="mt-2">Error loading chapters data</p>
                        <p class="text-sm text-red-400">${error.message}</p>
                        <p class="text-xs text-red-300 mt-1">Please check if you are logged in and have proper permissions.</p>
                    </td>
                </tr>
            `;
        });
}

function renderChaptersTable(chapters) {
    const tableBody = document.getElementById('chapters-table-body');
    
    if (chapters.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    Tidak ada bab ditemukan
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = chapters.map(chapter => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${chapter.title}</div>
                <div class="text-sm text-gray-500">Bab ${chapter.chapter_number}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">${chapter.album_title}</td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSEOStatusClass(chapter.seo_status)}">
                    ${getSEOStatusText(chapter.seo_status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${chapter.meta_description ? chapter.meta_description.substring(0, 50) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${chapter.meta_keywords ? chapter.meta_keywords.substring(0, 30) + '...' : 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${chapter.og_title ? '✓' : '✗'}
            </td>
            <td class="px-6 py-4 text-sm font-medium">
                <div class="inline-flex items-center gap-2">
                    <button class="edit-seo-btn px-2 py-1 rounded-md text-blue-600 hover:text-blue-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${chapter.id}" data-type="chapter" title="Edit SEO" aria-label="Edit SEO">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="inject-seo-btn px-2 py-1 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${chapter.id}" data-type="chapter" title="Inject SEO" aria-label="Inject SEO">
                        <i class="fas fa-magic"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-seo-btn[data-type="chapter"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const chapterId = this.getAttribute('data-id');
            openEditModal(chapterId, 'chapter');
        });
    });
}

// Root Pages Management
function loadRootData(page = 1) {
    const tableBody = document.getElementById('root-table-body');
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-xl"></i>
                <p class="mt-2">Memuat halaman root...</p>
            </td>
        </tr>
    `;
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        per_page: 20
    });
    
    // Add filters if they exist
    const searchValue = document.getElementById('search-root').value;
    const statusValue = document.getElementById('root-status-filter').value;
    const seoStatusValue = document.getElementById('root-seo-status-filter').value;
    
    if (searchValue) params.append('search', searchValue);
    if (statusValue) params.append('status', statusValue);
    if (seoStatusValue) params.append('seo_status', seoStatusValue);
    
    const url = `/api/seo/root?${params.toString()}`;
    
    fetchWithCSRF(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.root_entries && data.root_entries.length > 0) {
                renderRootTable(data.root_entries);
                updateRootPagination(data.pagination);
                updateRootCounts(data.pagination);
            } else {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                            Tidak ada halaman root ditemukan
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading root data:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-xl mb-2"></i>
                        <p class="mt-2">Error loading root data</p>
                        <p class="text-sm text-red-400">${error.message}</p>
                    </td>
                </tr>
            `;
            showToast('Error loading root data: ' + error.message, 'error');
        });
}



function renderRootTable(rootData) {
    const tableBody = document.getElementById('root-table-body');
    
    if (!rootData || rootData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    Tidak ada halaman root ditemukan
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = rootData.map(page => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${page.page_name}</div>
                <div class="text-sm text-gray-500">${page.page_identifier}</div>
            </td>
            <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${page.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                    ${page.is_active ? 'Aktif' : 'Tidak Aktif'}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div class="h-2 rounded-full ${getScoreColor(page.seo_score)}" style="width: ${page.seo_score}%"></div>
                    </div>
                    <span class="text-sm font-medium text-gray-900">${page.seo_score}%</span>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${page.meta_title || 'Belum diatur'}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                ${page.meta_description || 'Belum diatur'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${page.updated_at ? new Date(page.updated_at).toLocaleDateString('id-ID') : 'Belum diperbarui'}
            </td>
            <td class="px-6 py-4 text-sm font-medium">
                <div class="inline-flex items-center gap-2">
                    <button class="edit-seo-btn px-2 py-1 rounded-md text-blue-600 hover:text-blue-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${page.id}" data-type="root" title="Edit SEO" aria-label="Edit SEO">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="inject-seo-btn px-2 py-1 rounded-md text-gray-600 hover:text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" data-id="${page.id}" data-type="root" title="Inject SEO" aria-label="Inject SEO">
                        <i class="fas fa-magic"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-seo-btn[data-type="root"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const pageId = this.getAttribute('data-id');
            openEditModal(pageId, 'root');
        });
    });
}

// Filter functions
function filterArticles() {
    // Reload articles with current filters, reset to page 1
    loadArticlesData(1);
}

function filterAlbums() {
    // Reload albums with current filters, reset to page 1
    loadAlbumsData(1);
}

function filterChapters() {
    // Reload chapters with current filters, reset to page 1
    loadChaptersData(1);
}

function filterRoot() {
    // Reload root data with current filters, reset to page 1
    loadRootData(1);
}

// Modal functions
function openEditModal(itemId, itemType) {
    // Validate itemId
    if (!itemId || itemId === 'undefined') {
        console.error('Invalid item ID:', itemId);
        showToast('Invalid item ID', 'error');
        return;
    }
    
    document.getElementById('edit-item-id').value = itemId;
    document.getElementById('edit-item-type').value = itemType;
    
    // Load item data based on type
    if (itemType === 'article') {
        loadArticleData(itemId);
    } else if (itemType === 'album') {
        loadAlbumData(itemId);
    } else if (itemType === 'chapter') {
        loadChapterData(itemId);
    } else if (itemType === 'root') {
        loadRootPageData(itemId);
    }
    
    document.getElementById('edit-seo-modal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('edit-seo-modal').classList.add('hidden');
    document.getElementById('edit-seo-form').reset();
}

function loadArticleData(articleId) {
    fetchWithCSRF(`/api/seo/articles/${articleId}`)
        .then(response => response.json())
        .then(data => {
            populateEditForm(data, 'article');
        })
        .catch(error => {
            console.error('Error loading article data:', error);
            showToast('Error loading article data', 'error');
        });
}

function loadAlbumData(albumId) {
    fetchWithCSRF(`/api/seo/albums/${albumId}`)
        .then(response => response.json())
        .then(data => {
            populateEditForm(data, 'album');
        })
        .catch(error => {
            console.error('Error loading album data:', error);
            showToast('Error loading album data', 'error');
        });
}

function loadChapterData(chapterId) {
    fetchWithCSRF(`/api/seo/chapters/${chapterId}`)
        .then(response => response.json())
        .then(data => {
            populateEditForm(data, 'chapter');
        })
        .catch(error => {
            console.error('Error loading chapter data:', error);
            showToast('Error loading chapter data', 'error');
        });
}

function loadRootPageData(rootId) {
    // Check if rootId is valid
    if (!rootId || rootId === 'undefined') {
        console.error('Invalid root ID:', rootId);
        showToast('Invalid root page ID', 'error');
        return;
    }
    
    // Load root SEO data from API
    fetchWithCSRF(`/api/seo/root/${rootId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            populateEditForm(data, 'root');
        })
        .catch(error => {
            console.error('Error loading root data:', error);
            showToast('Error loading root data: ' + error.message, 'error');
        });
}

function populateEditForm(data, type) {
    if (type === 'chapter') {
        document.getElementById('edit-item-title').textContent = `${data.title} (Bab ${data.chapter_number})`;
        document.getElementById('edit-item-category').textContent = `${data.album} - ${data.category}`;
    } else {
        document.getElementById('edit-item-title').textContent = data.title || 'N/A';
        document.getElementById('edit-item-category').textContent = data.category || 'N/A';
    }
    
    // Populate form fields
    document.getElementById('edit-meta-title').value = data.meta_title || '';
    document.getElementById('edit-meta-description').value = data.meta_description || '';
    document.getElementById('edit-meta-keywords').value = data.meta_keywords || '';
    document.getElementById('edit-og-title').value = data.og_title || '';
    document.getElementById('edit-og-description').value = data.og_description || '';
    document.getElementById('edit-og-image').value = data.og_image || '';
    document.getElementById('edit-canonical-url').value = data.canonical_url || '';
    document.getElementById('edit-seo-slug').value = data.seo_slug || '';
    document.getElementById('edit-twitter-card').value = data.twitter_card || '';
    document.getElementById('edit-twitter-title').value = data.twitter_title || '';
    document.getElementById('edit-twitter-description').value = data.twitter_description || '';
    document.getElementById('edit-twitter-image').value = data.twitter_image || '';
    document.getElementById('edit-meta-author').value = data.meta_author || '';
    document.getElementById('edit-meta-language').value = data.meta_language || 'id';
    document.getElementById('edit-meta-robots').value = data.meta_robots || 'index, follow';
    document.getElementById('edit-structured-data-type').value = data.structured_data_type || 'Article';
    
    // Update character counts
    updateCharacterCounts();
    
    // Update preview
    updatePreview(data);
}

function handleEditSubmit(event) {
    event.preventDefault();
    
    const itemId = document.getElementById('edit-item-id').value;
    const itemType = document.getElementById('edit-item-type').value;
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Submit based on type
    if (itemType === 'article') {
        updateArticleSEO(itemId, data);
    } else if (itemType === 'album') {
        updateAlbumSEO(itemId, data);
    } else if (itemType === 'chapter') {
        updateChapterSEO(itemId, data);
    } else if (itemType === 'root') {
        updateRootSEO(itemId, data);
    }
}

function updateArticleSEO(articleId, data) {
    fetchWithCSRF(`/api/seo/articles/${articleId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showToast(result.message, 'success');
            closeEditModal();
            loadArticlesData();
        } else {
            showToast('Error updating SEO', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating article SEO:', error);
        showToast('Error updating SEO', 'error');
    });
}

function updateAlbumSEO(albumId, data) {
    fetchWithCSRF(`/api/seo/albums/${albumId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showToast(result.message, 'success');
            closeEditModal();
            loadAlbumsData();
        } else {
            showToast('Error updating SEO', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating album SEO:', error);
        showToast('Error updating SEO', 'error');
    });
}

function updateChapterSEO(chapterId, data) {
    fetchWithCSRF(`/api/seo/chapters/${chapterId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showToast(result.message, 'success');
            closeEditModal();
            loadChaptersData();
        } else {
            showToast('Error updating SEO', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating chapter SEO:', error);
        showToast('Error updating SEO', 'error');
    });
}

function updateRootSEO(rootId, data) {
    fetchWithCSRF(`/api/seo/root/${rootId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            showToast(result.message, 'success');
            closeEditModal();
            loadRootData();
        } else {
            showToast('Error updating SEO', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating root SEO:', error);
        showToast('Error updating SEO', 'error');
    });
}

// Utility functions
function getSEOStatusClass(status) {
    switch (status) {
        case 'complete': return 'bg-green-100 text-green-800';
        case 'incomplete': return 'bg-yellow-100 text-yellow-800';
        case 'missing': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getSEOStatusText(status) {
    switch (status) {
        case 'complete': return 'Lengkap';
        case 'incomplete': return 'Tidak Lengkap';
        case 'missing': return 'Hilang';
        default: return 'Unknown';
    }
}

function getScoreColor(score) {
    if (score >= 80) return 'bg-green-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
}

function updateCharacterCounts() {
    const metaTitle = document.getElementById('edit-meta-title');
    const metaDesc = document.getElementById('edit-meta-description');
    const ogTitle = document.getElementById('edit-og-title');
    const ogDesc = document.getElementById('edit-og-description');
    
    if (metaTitle) {
        document.getElementById('meta-title-count').textContent = `${metaTitle.value.length}/200`;
    }
    document.getElementById('meta-desc-count').textContent = `${metaDesc.value.length}/500`;
    document.getElementById('og-title-count').textContent = `${ogTitle.value.length}/200`;
    document.getElementById('og-desc-count').textContent = `${ogDesc.value.length}/500`;
    
    // Add event listeners for real-time counting
    if (metaTitle) {
        metaTitle.addEventListener('input', function() {
            document.getElementById('meta-title-count').textContent = `${this.value.length}/200`;
        });
    }
    
    metaDesc.addEventListener('input', function() {
        document.getElementById('meta-desc-count').textContent = `${this.value.length}/500`;
    });
    
    ogTitle.addEventListener('input', function() {
        document.getElementById('og-title-count').textContent = `${this.value.length}/200`;
    });
    
    ogDesc.addEventListener('input', function() {
        document.getElementById('og-desc-count').textContent = `${this.value.length}/500`;
    });
}

function updatePreview(data) {
    document.getElementById('preview-url').textContent = `https://example.com/${data.seo_slug || 'page'}`;
    document.getElementById('preview-title').textContent = data.og_title || data.title || 'Judul Artikel';
    document.getElementById('preview-description').textContent = data.meta_description || 'Deskripsi artikel akan muncul di sini...';
    
    // Calculate SEO score
    const score = calculateSEOScore(data);
    document.getElementById('seo-score').textContent = score;
}

function calculateSEOScore(data) {
    let score = 0;
    const fields = [
        'meta_description', 'meta_keywords', 'og_title', 
        'og_description', 'og_image', 'seo_slug'
    ];
    
    fields.forEach(field => {
        if (data[field] && data[field].trim()) {
            score += 16.67; // 100 / 6 fields
        }
    });
    
    return Math.round(score);
}

function createRootSEO() {
    // Open modal for creating new root SEO
    document.getElementById('edit-item-id').value = '';
    document.getElementById('edit-item-type').value = 'root';
    
    // Clear form
    document.getElementById('edit-seo-form').reset();
    
    // Update modal title
    document.querySelector('#edit-seo-modal h3').textContent = 'Buat SEO Root Baru';
    
    // Show modal
    document.getElementById('edit-seo-modal').classList.remove('hidden');
    
    // Update form submission handler for create vs edit
    const form = document.getElementById('edit-seo-form');
    form.onsubmit = function(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        // Create new root SEO
        fetchWithCSRF('/api/seo/root', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.message) {
                showToast(result.message, 'success');
                closeEditModal();
                loadRootData();
            } else {
                showToast('Error creating SEO', 'error');
            }
        })
        .catch(error => {
            console.error('Error creating root SEO:', error);
            showToast('Error creating SEO', 'error');
        });
    };
}

function closeConfirmationModal() {
    document.getElementById('confirmation-modal').classList.add('hidden');
}

function executeConfirmedAction() {
    // Implement confirmed action
    closeConfirmationModal();
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const bgColor = type === 'success' ? 'bg-green-500' : 
                   type === 'error' ? 'bg-red-500' : 
                   type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
    
    toast.className = `${bgColor} text-white px-4 py-2 rounded-lg shadow-lg`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

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

// SEO Injection Functions
function runSEOInjection(type) {
    const buttonMap = {
        'news': 'run-articles-seo-injection',
        'albums': 'run-albums-seo-injection',
        'chapters': 'run-chapters-seo-injection',
        'root': 'run-root-seo-injection'
    };
    
    const typeLabels = {
        'news': 'Artikel',
        'albums': 'Album',
        'chapters': 'Bab',
        'root': 'Halaman Root'
    };
    
    const button = document.getElementById(buttonMap[type]);
    const originalText = button.innerHTML;
    
    // Show confirmation dialog
    // Custom confirm modal using our confirmation modal instead of system confirm
    const message = `⚠️ PERHATIAN: SEO Injection akan menghapus semua data SEO yang ada dan membuat ulang berdasarkan konten ${typeLabels[type]}.\n\n` +
      'Ini akan:\n' +
      '• Menghapus semua meta description, keywords, OG tags yang ada\n' +
      '• Membuat ulang SEO data berdasarkan konten dengan pembersihan markdown\n' +
      '• Mengatur is_seo_lock = false untuk semua item\n\n' +
      `Apakah Anda yakin ingin melanjutkan untuk ${typeLabels[type]}?`;

    const modal = document.getElementById('confirmation-modal');
    if (modal) {
        document.getElementById('confirmation-message').textContent = message;
        modal.classList.remove('hidden');
        // Temporarily override confirm action
        const confirmBtn = document.getElementById('confirm-action');
        const cancelBtn = document.getElementById('cancel-confirmation');
        const originalConfirmHandler = confirmBtn.onclick;
        const originalCancelHandler = cancelBtn.onclick;
        confirmBtn.onclick = () => {
            modal.classList.add('hidden');
            // restore handlers
            confirmBtn.onclick = originalConfirmHandler;
            cancelBtn.onclick = originalCancelHandler;
            proceedInjection();
        };
        cancelBtn.onclick = () => {
            modal.classList.add('hidden');
            confirmBtn.onclick = originalConfirmHandler;
            cancelBtn.onclick = originalCancelHandler;
        };
        return; // wait for user choice
    }
    
    // Fallback to direct proceed if modal not found
    proceedInjection();

    function proceedInjection() {
    
    // Disable button and show loading state
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Menjalankan SEO Injection...';
    
    // Show progress toast
    showToast(`🚀 Memulai SEO Injection untuk ${typeLabels[type]}...`, 'info');
    
    // Make API call to run SEO injection
    fetchWithCSRF('/api/seo/inject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            type: type,
            clean_markdown: true // Enable markdown cleaning for better SEO
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Show success message with results
        const result = data.result;
        let message = `✅ SEO Injection untuk ${typeLabels[type]} selesai!\n\n`;
        
        if (result.total_updated > 0) {
            message += `📊 Hasil:\n`;
            message += `• Total item diperbarui: ${result.total_updated}\n`;
            message += `• Total item terkunci: ${result.total_locked}\n`;
            message += `• Total error: ${result.total_errors}\n`;
            message += `• Durasi: ${result.duration_seconds.toFixed(2)} detik\n\n`;
        }
        
        message += `🔄 Memuat ulang data...`;
        
        showToast(message, 'success');
        
        // Reload data based on type
        setTimeout(() => {
            switch(type) {
                case 'news':
                    loadArticlesData();
                    break;
                case 'albums':
                    loadAlbumsData();
                    break;
                case 'chapters':
                    loadChaptersData();
                    break;
                case 'root':
                    loadRootData();
                    break;
            }
        }, 2000);
        
    })
    .catch(error => {
        console.error('SEO Injection error:', error);
        showToast(`❌ Error untuk ${typeLabels[type]}: ${error.message}`, 'error');
    })
    .finally(() => {
        // Re-enable button
        button.disabled = false;
        button.innerHTML = originalText;
    });
    }
}

function confirmAndInjectSingle(type, id) {
    const typeLabels = {
        'article': 'Artikel',
        'album': 'Album',
        'chapter': 'Bab',
        'root': 'Halaman Root'
    };
    const modal = document.getElementById('confirmation-modal');
    const message = `Injeksi SEO akan menghasilkan dan mengisi bidang SEO untuk ${typeLabels[type]}. Lanjutkan?`;
    if (modal) {
        document.getElementById('confirmation-message').textContent = message;
        modal.classList.remove('hidden');
        const confirmBtn = document.getElementById('confirm-action');
        const cancelBtn = document.getElementById('cancel-confirmation');
        const originalConfirm = confirmBtn.onclick;
        const originalCancel = cancelBtn.onclick;
        confirmBtn.onclick = () => {
            modal.classList.add('hidden');
            confirmBtn.onclick = originalConfirm;
            cancelBtn.onclick = originalCancel;
            injectSingle(type, id);
        };
        cancelBtn.onclick = () => {
            modal.classList.add('hidden');
            confirmBtn.onclick = originalConfirm;
            cancelBtn.onclick = originalCancel;
        };
    } else {
        injectSingle(type, id);
    }
}

function injectSingle(type, id) {
    const urlMap = {
        'article': `/api/seo/articles/${id}/inject`,
        'album': `/api/seo/albums/${id}/inject`,
        'chapter': `/api/seo/chapters/${id}/inject`,
        'root': `/api/seo/root/${id}/inject`
    };
    const labelMap = {
        'article': 'Artikel',
        'album': 'Album',
        'chapter': 'Bab',
        'root': 'Halaman Root'
    };
    const url = urlMap[type];
    if (!url) return;
    showToast(`Memproses injeksi SEO untuk ${labelMap[type]}...`, 'info');
    fetchWithCSRF(url, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json'
        }
    })
    .then(r => r.json().then(j => ({ ok: r.ok, body: j })))
    .then(({ ok, body }) => {
        if (!ok) {
            console.error('Server response:', body);
            throw new Error(body.error || body.details || 'Gagal injeksi');
        }
        showToast(body.message || 'SEO injected', 'success');
        // Reload respective table
        switch(type) {
            case 'article':
                loadArticlesData();
                break;
            case 'album':
                loadAlbumsData();
                break;
            case 'chapter':
                loadChaptersData();
                break;
            case 'root':
                loadRootData();
                break;
        }
    })
    .catch(err => {
        console.error('Inject error:', err);
        console.error('Error details:', err);
        showToast('Gagal injeksi SEO: ' + err.message, 'error');
    });
}

function getSEOInjectionStatus() {
    fetchWithCSRF('/api/seo/inject/status', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error getting SEO status:', data.error);
            return;
        }
        
        // Update status display if needed
        const status = data.result;
        
        // You can add UI elements to show the SEO health percentage
        if (status.seo_health_percentage !== undefined) {
            // Update any status indicators in the UI
        }
    })
    .catch(error => {
        console.error('Error getting SEO status:', error);
    });
}

// Pagination functions
function updateArticlesPagination(pagination) {
    const controls = document.getElementById('articles-pagination-controls');
    controls.innerHTML = generatePaginationHTML(pagination, 'articles');
}

function updateArticlesCounts(pagination) {
    document.getElementById('articles-showing-start').textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    document.getElementById('articles-showing-end').textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    document.getElementById('articles-total').textContent = pagination.total_items;
}

function updateAlbumsPagination(pagination) {
    const controls = document.getElementById('albums-pagination-controls');
    controls.innerHTML = generatePaginationHTML(pagination, 'albums');
}

function updateAlbumsCounts(pagination) {
    document.getElementById('albums-showing-start').textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    document.getElementById('albums-showing-end').textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    document.getElementById('albums-total').textContent = pagination.total_items;
}

function updateChaptersPagination(pagination) {
    const controls = document.getElementById('chapters-pagination-controls');
    controls.innerHTML = generatePaginationHTML(pagination, 'chapters');
}

function updateChaptersCounts(pagination) {
    document.getElementById('chapters-showing-start').textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    document.getElementById('chapters-showing-end').textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    document.getElementById('chapters-total').textContent = pagination.total_items;
}

function updateRootPagination(pagination) {
    const controls = document.getElementById('root-pagination-controls');
    controls.innerHTML = generatePaginationHTML(pagination, 'root');
}

function updateRootCounts(pagination) {
    document.getElementById('root-showing-start').textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    document.getElementById('root-showing-end').textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    document.getElementById('root-total').textContent = pagination.total_items;
}

function generatePaginationHTML(pagination, type) {
    let html = '';
    
    if (pagination.total_pages <= 1) {
        return html; // No pagination needed
    }
    
    // Previous button
    if (pagination.has_prev) {
        html += `<button class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors" onclick="load${type.charAt(0).toUpperCase() + type.slice(1)}Data(${pagination.current_page - 1})">
            <i class="fas fa-chevron-left mr-1"></i>Previous
        </button>`;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.current_page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === pagination.current_page) {
            html += `<span class="px-3 py-1 bg-blue-700 text-white rounded font-medium">${i}</span>`;
        } else {
            html += `<button class="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors" onclick="load${type.charAt(0).toUpperCase() + type.slice(1)}Data(${i})">${i}</button>`;
        }
    }
    
    // Next button
    if (pagination.has_next) {
        html += `<button class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors" onclick="load${type.charAt(0).toUpperCase() + type.slice(1)}Data(${pagination.current_page + 1})">
            Next<i class="fas fa-chevron-right ml-1"></i>
        </button>`;
    }
    
    return html;
}

// Root SEO Settings Functions
function openRootSEOSettings() {
    // Load brand information first
    loadBrandInformation();
    
    // Show the modal
    const modal = document.getElementById('root-seo-settings-modal');
    modal.classList.remove('hidden');
    
    // Add event listeners for the modal
    document.getElementById('close-root-seo-settings').addEventListener('click', closeRootSEOSettings);
    document.getElementById('cancel-root-seo-settings').addEventListener('click', closeRootSEOSettings);
    document.getElementById('root-seo-settings-form').addEventListener('submit', handleRootSEOSettingsSubmit);
}

function closeRootSEOSettings() {
    const modal = document.getElementById('root-seo-settings-modal');
    modal.classList.add('hidden');
}

function loadBrandInformation() {
    // Fetch root SEO settings from the server
    fetchWithCSRF('/admin/api/root-seo-settings')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const brandInfo = data.brand_identity;
                const settings = data.settings;
                
                // Populate brand information fields
                document.getElementById('brand-name').value = brandInfo.brand_name || 'LilyOpenCMS';
                document.getElementById('website-url').value = brandInfo.website_url || 'https://hystory.id';
                
                // Populate settings fields
                populateSettingsFields(settings);
                
                // Update template placeholders with actual brand name
                updateTemplatePlaceholders(brandInfo.brand_name || 'LilyOpenCMS');
            } else {
                console.error('Failed to load root SEO settings:', data.error);
                // Set defaults
                document.getElementById('brand-name').value = 'LilyOpenCMS';
                document.getElementById('website-url').value = 'https://hystory.id';
            }
        })
        .catch(error => {
            console.error('Error loading root SEO settings:', error);
            // Set defaults on error
            document.getElementById('brand-name').value = 'LilyOpenCMS';
            document.getElementById('website-url').value = 'https://lilycms.com';
        });
}

function populateSettingsFields(settings) {
    // Populate all the settings fields with the loaded data
    const fields = [
        'home_meta_title', 'home_meta_description', 'home_meta_keywords',
        'about_meta_title', 'about_meta_description', 'about_meta_keywords',
        'news_meta_title', 'news_meta_description', 'news_meta_keywords',
        'albums_meta_title', 'albums_meta_description', 'albums_meta_keywords',
        'default_og_image', 'default_og_type', 'default_twitter_card',
        'default_twitter_image', 'default_language', 'default_meta_robots'
    ];
    
    fields.forEach(fieldName => {
        const element = document.getElementById(fieldName.replace(/_/g, '-'));
        if (element && settings[fieldName]) {
            element.value = settings[fieldName];
        }
    });
}

function updateTemplatePlaceholders(brandName) {
    // Update meta title templates with actual brand name
    const homeTitle = document.getElementById('home-meta-title');
    const aboutTitle = document.getElementById('about-meta-title');
    const newsTitle = document.getElementById('news-meta-title');
    const albumsTitle = document.getElementById('albums-meta-title');
    
    if (homeTitle && homeTitle.value.includes('{brand_name}')) {
        homeTitle.value = homeTitle.value.replace('{brand_name}', brandName);
    }
    if (aboutTitle && aboutTitle.value.includes('{brand_name}')) {
        aboutTitle.value = aboutTitle.value.replace('{brand_name}', brandName);
    }
    if (newsTitle && newsTitle.value.includes('{brand_name}')) {
        newsTitle.value = newsTitle.value.replace('{brand_name}', brandName);
    }
    if (albumsTitle && albumsTitle.value.includes('{brand_name}')) {
        albumsTitle.value = albumsTitle.value.replace('{brand_name}', brandName);
    }
}

function handleRootSEOSettingsSubmit(event) {
    event.preventDefault();
    
    // Collect form data
    const formData = new FormData(event.target);
    const settings = {
        // Brand information
        brand_name: document.getElementById('brand-name').value,
        website_url: document.getElementById('website-url').value,
        
        // Page templates
        home_meta_title: formData.get('home_meta_title'),
        home_meta_description: formData.get('home_meta_description'),
        home_meta_keywords: formData.get('home_meta_keywords'),
        
        about_meta_title: formData.get('about_meta_title'),
        about_meta_description: formData.get('about_meta_description'),
        about_meta_keywords: formData.get('about_meta_keywords'),
        
        news_meta_title: formData.get('news_meta_title'),
        news_meta_description: formData.get('news_meta_description'),
        news_meta_keywords: formData.get('news_meta_keywords'),
        
        albums_meta_title: formData.get('albums_meta_title'),
        albums_meta_description: formData.get('albums_meta_description'),
        albums_meta_keywords: formData.get('albums_meta_keywords'),
        
        // Open Graph defaults
        default_og_image: formData.get('default_og_image'),
        default_og_type: formData.get('default_og_type'),
        
        // Twitter Card defaults
        default_twitter_card: formData.get('default_twitter_card'),
        default_twitter_image: formData.get('default_twitter_image'),
        
        // Schema markup settings
        default_language: formData.get('default_language'),
        default_meta_robots: formData.get('default_meta_robots')
    };
    
    // Save settings to server
    saveRootSEOSettings(settings);
}

function saveRootSEOSettings(settings) {
    // Show loading state
    const submitBtn = document.querySelector('#root-seo-settings-form button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Menyimpan...';
    submitBtn.disabled = true;
    
    fetchWithCSRF('/admin/api/root-seo-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Pengaturan Root SEO berhasil disimpan!', 'success');
            closeRootSEOSettings();
        } else {
            showToast('Gagal menyimpan pengaturan: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error saving root SEO settings:', error);
        showToast('Terjadi kesalahan saat menyimpan pengaturan', 'error');
    })
    .finally(() => {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function getCSRFToken() {
    // Get CSRF token from meta tag or cookie
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                  document.cookie.split('; ').find(row => row.startsWith('csrf_token='))?.split('=')[1];
    return token || '';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2 max-w-md`;
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-auto text-white hover:text-gray-200">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}