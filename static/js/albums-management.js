/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Albums Management JavaScript
(() => {
    'use strict';

    // Global variables
    let selectedNews = [];
    let tempSelectedNews = [];
    let currentAlbumId = null;
    let categories = [];
    let images = [];
    let newsArticles = [];
    let currentTab = 'albums';

    // Initialize the page
    function init() {
        loadCategories();
        loadImages();
        loadNewsArticles();
        setupTabEventListeners();
        loadAlbums();
        setupEventListeners();
        setupBulkEventListeners();
    }

    // Setup tab event listeners
    function setupTabEventListeners() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
    }

    // Switch between tabs
    function switchTab(tabName) {
        // Hide all tab contents
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.add('hidden');
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.classList.remove('active', 'bg-white', 'text-amber-800');
            button.classList.add('bg-amber-200', 'text-amber-700');
        });

        // Show selected tab content
        const selectedTab = document.getElementById(`${tabName}-tab`);
        if (selectedTab) {
            selectedTab.classList.remove('hidden');
            selectedTab.classList.add('active');
        }

        // Add active class to selected tab button
        const selectedButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (selectedButton) {
            selectedButton.classList.add('active', 'bg-white', 'text-amber-800');
            selectedButton.classList.remove('bg-amber-200', 'text-amber-700');
        }

        currentTab = tabName;

        // Load appropriate content based on tab
        switch (tabName) {
            case 'albums':
                loadAlbums();
                break;
            case 'seo':
                loadSEOAlbums();
                break;
        }
    }

    // Setup event listeners
    function setupEventListeners() {
        // Filter inputs
        const searchFilter = document.getElementById('filter-search');
        const categoryFilter = document.getElementById('filter-category');
        const statusFilter = document.getElementById('filter-status');
        const premiumFilter = document.getElementById('filter-premium');

        if (searchFilter) {
            searchFilter.addEventListener('input', debounce(applyFilters, 500));
        }
        if (categoryFilter) {
            categoryFilter.addEventListener('change', applyFilters);
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', applyFilters);
        }
        if (premiumFilter) {
            premiumFilter.addEventListener('change', applyFilters);
        }

        // Album form
        const albumForm = document.getElementById('album-form');
        if (albumForm) {
            albumForm.addEventListener('submit', handleAlbumSubmit);
        }

        // Image picker modals
        const headerImageCloseAlbum = document.getElementById('header-image-close-album');
        const headerUploadBtnAlbum = document.getElementById('header-upload-btn-album');
        const clearFeaturedImageBtnAlbum = document.getElementById('clear-featured-image-btn-album');

        if (headerImageCloseAlbum) {
            headerImageCloseAlbum.addEventListener('click', closeImageHeaderModalAlbum);
        }
        if (headerUploadBtnAlbum) {
            headerUploadBtnAlbum.addEventListener('click', uploadHeaderImageAlbum);
        }
        if (clearFeaturedImageBtnAlbum) {
            clearFeaturedImageBtnAlbum.addEventListener('click', clearHeaderImageAlbum);
        }

        // Add event listener for opening image picker
        const openImageHeaderBtn = document.querySelector('button[onclick="openImageHeaderModalAlbum()"]');
        if (openImageHeaderBtn) {
            openImageHeaderBtn.addEventListener('click', openImageHeaderModalAlbum);
        }

        // News picker modal
        const newsSearch = document.getElementById('news-search');
        if (newsSearch) {
            newsSearch.addEventListener('input', debounce(filterNewsPicker, 300));
        }
    }

    // Load categories for dropdowns
    async function loadCategories() {
        try {
            const response = await fetch('/api/categories');
            if (!response.ok) throw new Error('Failed to fetch categories');

            const categoriesData = await response.json();
            categories = categoriesData || [];
            populateCategoryDropdowns();
        } catch (error) {
            console.error('Error loading categories:', error);
            showToast('Error loading categories', 'error');
        }
    }

    // Load images for image picker
    async function loadImages() {
        try {
            const response = await fetch('/api/images?visible=true');
            const data = await response.json();
            
            console.log('Images API response:', data);
            
            if (data.items) {
                images = data.items;
                populateImageDropdowns();
            } else {
                console.error('Images API error:', data);
                showToast('Error loading images', 'error');
            }
        } catch (error) {
            console.error('Error loading images:', error);
            showToast('Error loading images', 'error');
        }
    }

    // Load news articles for news picker
    async function loadNewsArticles() {
        try {
            const response = await fetch('/api/news?visible=true');
            const data = await response.json();
            
            console.log('News API response:', data);
            
            if (data.items) {
                newsArticles = data.items;
                populateNewsDropdown();
            } else {
                console.error('News API error:', data);
                showToast('Error loading news articles', 'error');
            }
        } catch (error) {
            console.error('Error loading news articles:', error);
            showToast('Error loading news articles', 'error');
        }
    }

    // Populate category dropdowns
    function populateCategoryDropdowns() {
        const filterCategory = document.getElementById('filter-category');
        const albumCategory = document.getElementById('album-category');
        
        if (filterCategory) {
            filterCategory.innerHTML = '<option value="">Semua Kategori</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                filterCategory.appendChild(option);
            });
        }
        
        if (albumCategory) {
            albumCategory.innerHTML = '<option value="">Pilih kategori...</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                albumCategory.appendChild(option);
            });
        }
    }

    // Populate image dropdowns
    function populateImageDropdowns() {
        // This will be used by the image picker modal
        window.albumImages = images;
        console.log('Images loaded for picker:', images.length);
    }

    // Populate news dropdown
    function populateNewsDropdown() {
        // This will be used by the news picker modal
        window.newsArticles = newsArticles;
        console.log('News articles loaded for picker:', newsArticles.length);
    }

    // Load albums for albums tab
    async function loadAlbums(page = 1) {
        const searchFilter = document.getElementById('filter-search');
        const categoryFilter = document.getElementById('filter-category');
        const statusFilter = document.getElementById('filter-status');
        const premiumFilter = document.getElementById('filter-premium');
        
        const search = searchFilter ? searchFilter.value : '';
        const category = categoryFilter ? categoryFilter.value : '';
        const status = statusFilter ? statusFilter.value : '';
        const premium = premiumFilter ? premiumFilter.value : '';
        
        const params = new URLSearchParams({
            page: page,
            per_page: 12,
            search: search,
            category: category,
            status: status,
            premium: premium
        });
        
        try {
            const response = await fetch(`/api/albums?${params}`);
            const data = await response.json();
            
            if (data.items) {
                displayAlbums(data.items);
                renderPagination('pagination', { currentPage: data.page, totalPages: data.total_pages }, loadAlbums);
                
                if (data.items.length === 0) {
                    showEmptyState();
                } else {
                    hideEmptyState();
                }
            } else {
                showToast(data.message || 'Error loading albums', 'error');
            }
        } catch (error) {
            console.error('Error loading albums:', error);
            showToast('Error loading albums', 'error');
        }
    }

    // Load SEO albums
    async function loadSEOAlbums(page = 1) {
        try {
            const response = await fetch(`/api/albums?page=${page}&per_page=20`);
            if (!response.ok) throw new Error('Failed to fetch albums');

            const data = await response.json();
            const albums = data.items || [];
            
            displaySEOAlbums(albums);
            renderPagination('seo-pagination-controls', { currentPage: data.page, totalPages: data.total_pages }, loadSEOAlbums);
            
            // Update SEO count info
            const start = data.total > 0 ? (data.page - 1) * 20 + 1 : 0;
            const end = Math.min(data.page * 20, data.total);
            document.getElementById('seo-showing-start').textContent = start;
            document.getElementById('seo-showing-end').textContent = end;
            document.getElementById('seo-total-albums').textContent = data.total;

        } catch (error) {
            console.error('Error loading SEO albums:', error);
            showToast('Error loading SEO albums', 'error');
        }
    }

    // Display albums in grid
    function displayAlbums(albums) {
        const grid = document.getElementById('albums-grid');
        const emptyState = document.getElementById('empty-state');
        
        if (!grid) return;
        
        if (!albums || albums.length === 0) {
            grid.innerHTML = '';
            showEmptyState();
            return;
        }
        
        hideEmptyState();
        grid.innerHTML = albums.map(album => createAlbumCard(album)).join('');
    }

    // Create album card HTML with iconified buttons
    function createAlbumCard(album) {
        const badges = [];
        if (album.is_premium) badges.push('<span class="album-badge badge-premium">Premium</span>');
        if (album.is_archived) badges.push('<span class="album-badge badge-archived">Archived</span>');
        if (!album.is_visible) badges.push('<span class="album-badge badge-hidden">Hidden</span>');
        if (album.is_completed) badges.push('<span class="album-badge badge-completed">Completed</span>');
        if (album.is_hiatus) badges.push('<span class="album-badge badge-hiatus">Hiatus</span>');
        
        // Fix image rendering - handle different image data structures
        let coverImageSrc = '';
        if (album.cover_image) {
            if (album.cover_image.file_url) {
                coverImageSrc = album.cover_image.file_url;
            } else if (album.cover_image.url) {
                coverImageSrc = album.cover_image.url;
            } else if (album.cover_image.filepath) {
                coverImageSrc = album.cover_image.filepath;
            } else if (album.cover_image.filename) {
                coverImageSrc = `/static/uploads/${album.cover_image.filename}`;
            }
        }
        
        const coverImage = coverImageSrc ? 
            `<img src="${coverImageSrc}" alt="Cover" class="w-full h-48 object-cover">` :
            '<div class="w-full h-48 bg-gradient-to-br from-amber-100 to-yellow-100 flex items-center justify-center"><i class="fas fa-book-open text-4xl text-amber-400"></i></div>';
        
        const chapters = album.chapters ? album.chapters.map(chapter => 
            `<div class="chapter-item bg-white rounded-lg p-3 border border-amber-200 hover:border-amber-300 transition-all duration-200 mb-2">
                <div class="flex items-center w-full">
                    <div class="flex items-center gap-3 flex-1 min-w-0">
                        <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-amber-100 to-yellow-100 rounded-lg flex-shrink-0">
                            <span class="text-sm font-bold text-amber-600">${chapter.chapter_number}</span>
                        </div>
                        <div class="flex-1 min-w-0 pr-4">
                            <h5 class="text-sm font-medium text-amber-800 line-clamp-1">${chapter.chapter_title}</h5>
                            <p class="text-xs text-amber-500 line-clamp-1">${chapter.news ? chapter.news.title : 'Original article'}</p>
                        </div>
                    </div>
                    <div class="flex gap-1 flex-shrink-0">
                        <button onclick="window.editChapter(${album.id}, ${chapter.id}, '${chapter.chapter_title}', ${chapter.chapter_number}, '${chapter.news ? chapter.news.title : ''}')" class="text-blue-600 hover:text-blue-800 hover:bg-blue-100 rounded-lg transition-all duration-200" title="Edit Chapter">
                            <i class="fas fa-edit text-sm"></i>
                        </button>
                        <button onclick="window.removeChapter(${album.id}, ${chapter.id}, '${chapter.chapter_title}')" class="text-red-600 hover:text-red-800 hover:bg-red-100 rounded-lg transition-all duration-200" title="Remove Chapter">
                            <i class="fas fa-trash text-sm"></i>
                        </button>
                    </div>
                </div>
            </div>`
        ).join('') : '';
        
        return `
            <div class="album-card" data-album-id="${album.id}">
                <input type="checkbox" class="album-checkbox hidden" data-album-id="${album.id}">
                
                <div class="relative">
                    ${coverImage}
                    <div class="absolute top-3 left-3 flex gap-2">
                        ${badges.join('')}
                    </div>
                    
                    <div class="album-actions">
                        <button onclick="window.editAlbum(${album.id})" class="action-btn edit" title="Edit Album">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="window.toggleAlbumVisibility(${album.id})" class="action-btn visibility ${!album.is_visible ? 'is-hidden' : ''}" title="${album.is_visible ? 'Hide Album' : 'Show Album'}">
                            <i class="fas fa-${album.is_visible ? 'eye' : 'eye-slash'}"></i>
                        </button>
                        <button onclick="window.toggleAlbumType(${album.id})" class="action-btn type ${album.is_premium ? 'premium' : ''}" title="${album.is_premium ? 'Set to Regular' : 'Set to Premium'}">
                            <i class="fas fa-${album.is_premium ? 'crown' : 'star'}"></i>
                        </button>
                        <button onclick="window.${album.is_archived ? 'unarchiveAlbum' : 'archiveAlbum'}(${album.id})" class="action-btn archive" title="${album.is_archived ? 'Unarchive Album' : 'Archive Album'}">
                            <i class="fas fa-${album.is_archived ? 'folder-open' : 'archive'}"></i>
                        </button>
                        <button onclick="window.deleteAlbum(${album.id})" class="action-btn delete" title="Delete Album">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <div class="p-6 space-y-4 flex-1 flex flex-col">
                    <div class="space-y-2">
                        <h3 class="text-xl font-bold text-amber-800 line-clamp-2 leading-tight">${album.title}</h3>
                        <p class="text-sm text-amber-600 line-clamp-2">${album.description || 'No description'}</p>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4 py-3 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg">
                        <div class="text-center">
                            <div class="flex items-center justify-center mb-1">
                                <i class="fas fa-user text-amber-500 mr-2"></i>
                                <span class="text-xs text-amber-600">Author</span>
                            </div>
                            <p class="text-sm font-medium text-amber-800">${album.author ? album.author.username : 'Unknown'}</p>
                        </div>
                        <div class="text-center">
                            <div class="flex items-center justify-center mb-1">
                                <i class="fas fa-folder text-amber-500 mr-2"></i>
                                <span class="text-xs text-amber-600">Category</span>
                            </div>
                            <p class="text-sm font-medium text-amber-800">${album.category ? album.category.name : 'Unknown'}</p>
                        </div>
                        <div class="text-center">
                            <div class="flex items-center justify-center mb-1">
                                <i class="fas fa-list text-amber-500 mr-2"></i>
                                <span class="text-xs text-amber-600">Chapters</span>
                            </div>
                            <p class="text-sm font-medium text-amber-800">${album.total_chapters || 0}</p>
                        </div>
                        <div class="text-center">
                            <div class="flex items-center justify-center mb-1">
                                <i class="fas fa-eye text-amber-500 mr-2"></i>
                                <span class="text-xs text-amber-600">Reads</span>
                            </div>
                            <p class="text-sm font-medium text-amber-800">${album.total_reads || 0}</p>
                        </div>
                    </div>
                    
                    <div class="space-y-2 flex-1">
                        <div class="flex items-center justify-between">
                            <h4 class="text-sm font-semibold text-amber-800">
                                <i class="fas fa-book-open mr-2"></i>Chapters
                            </h4>
                            <span class="text-xs text-amber-500 bg-amber-100 px-2 py-1 rounded-full">${album.total_chapters || 0} total</span>
                        </div>
                        <div class="chapter-list bg-amber-50 rounded-lg p-3 h-48 overflow-y-auto">
                            ${chapters || '<p class="text-xs text-amber-500 italic text-center py-2">No chapters yet</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // --- REFACTOR: Unified Pagination Logic ---

    /**
     * Creates an array of page numbers for pagination, with ellipses for gaps.
     * @param {number} currentPage The current active page.
     * @param {number} totalPages The total number of pages.
     * @returns {Array<number|string>} An array of page numbers and '...' for gaps.
     */
    function getPaginationRange(currentPage, totalPages) {
        let delta = totalPages <= 7 ? 7 : (currentPage > 4 && currentPage < totalPages - 3) ? 2 : 4;
        const range = {
            start: Math.round(currentPage - delta / 2),
            end: Math.round(currentPage + delta / 2)
        };

        if (range.start - 1 === 1 || range.end + 1 === totalPages) {
            range.start += 1;
            range.end += 1;
        }

        let pages = currentPage > delta ?
            getRange(Math.min(range.start, totalPages - delta), Math.min(range.end, totalPages)) :
            getRange(1, Math.min(totalPages, delta + 1));

        const withDots = (value, pair) => (pages.length + 1 !== totalPages ? pair : [value]);

        if (pages[0] !== 1) {
            pages = withDots(1, [1, '...']).concat(pages);
        }

        if (pages[pages.length - 1] < totalPages) {
            pages = pages.concat(withDots(totalPages, ['...', totalPages]));
        }

        return pages;
    }

    function getRange(start, end) {
        return Array.from({ length: end - start + 1 }, (_, i) => i + start);
    }
    
    /**
     * Renders pagination controls in a specified container.
     * @param {string} containerId - The ID of the element to render pagination into.
     * @param {object} paginationData - Object with currentPage and totalPages.
     * @param {function} onPageChange - Callback function to execute when a page is clicked.
     */
    function renderPagination(containerId, { currentPage, totalPages }, onPageChange) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        if (totalPages <= 1) return;

        const nav = document.createElement('nav');
        nav.className = 'flex items-center justify-center space-x-2';
        nav.setAttribute('aria-label', 'Pagination');

        // Helper to create a button
        const createButton = (content, page, { isEnabled = true, isIcon = false, isActive = false, title = '' } = {}) => {
            const button = document.createElement('button');
            const activeClasses = 'bg-gradient-to-r from-amber-600 to-yellow-600 text-white shadow-lg';
            const defaultClasses = 'group bg-gradient-to-r from-amber-300 to-yellow-300 hover:from-amber-400 hover:to-yellow-400 text-amber-800 shadow-md hover:shadow-lg transform hover:-translate-y-0.5';
            const iconClasses = 'group bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white shadow-md hover:shadow-lg transform hover:-translate-y-0.5';
            
            button.className = `px-4 py-2 rounded-xl font-semibold focus:outline-none focus:ring-2 focus:ring-amber-300 transition-all duration-300 ${isIcon ? iconClasses : (isActive ? activeClasses : defaultClasses)}`;
            button.innerHTML = content;
            button.disabled = !isEnabled;
            if (title) button.title = title;
            if (isEnabled) {
                button.addEventListener('click', () => onPageChange(page));
            } else {
                 button.classList.add('opacity-50', 'cursor-not-allowed');
            }
            return button;
        };

        // Previous Button
        nav.appendChild(createButton('<i class="fas fa-chevron-left group-hover:scale-110 transition-transform"></i>', currentPage - 1, { isEnabled: currentPage > 1, isIcon: true, title: 'Previous Page' }));

        // Page Numbers
        getPaginationRange(currentPage, totalPages).forEach(page => {
            if (page === '...') {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'px-3 py-2 text-amber-600';
                ellipsis.textContent = '...';
                nav.appendChild(ellipsis);
            } else {
                nav.appendChild(createButton(page, page, { isActive: page === currentPage, title: `Go to page ${page}` }));
            }
        });

        // Next Button
        nav.appendChild(createButton('<i class="fas fa-chevron-right group-hover:scale-110 transition-transform"></i>', currentPage + 1, { isEnabled: currentPage < totalPages, isIcon: true, title: 'Next Page' }));
        
        container.appendChild(nav);
    }
    
    // --- End of Pagination Refactor ---


    // Apply filters
    function applyFilters() {
        loadAlbums(1); // Reset to first page on filter change
    }

    // Clear filters
    function clearFilters() {
        const searchFilter = document.getElementById('filter-search');
        const categoryFilter = document.getElementById('filter-category');
        const statusFilter = document.getElementById('filter-status');
        const premiumFilter = document.getElementById('filter-premium');
        
        if (searchFilter) searchFilter.value = '';
        if (categoryFilter) categoryFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        if (premiumFilter) premiumFilter.value = '';
        
        applyFilters();
    }

    // Show loading state for individual album cards
    function showAlbumCardLoading(albumId) {
        const card = document.querySelector(`[data-album-id="${albumId}"]`);
        if (card) {
            const overlay = document.createElement('div');
            overlay.className = 'absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-20';
            overlay.innerHTML = `
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-500"></div>
            `;
            card.appendChild(overlay);
        }
    }

    // Show/hide empty state
    function showEmptyState() {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) emptyState.style.display = 'block';
    }

    function hideEmptyState() {
        const emptyState = document.getElementById('empty-state');
        if (emptyState) emptyState.style.display = 'none';
    }

    // Album modal functions
    function openAlbumModal(albumId = null) {
        currentAlbumId = albumId;
        
        const modal = document.getElementById('album-modal');
        const title = document.getElementById('album-modal-title');
        const form = document.getElementById('album-form');
        
        if (!modal || !title || !form) return;
        
        if (albumId) {
            // Edit mode - load existing album data
            title.textContent = 'Edit Album';
            loadAlbumForEdit(albumId);
        } else {
            // Create mode - reset form completely
            title.textContent = 'Buat Album Baru';
            form.reset();
            
            // Clear all form fields explicitly
            const albumIdInput = document.getElementById('album-id');
            const coverImageId = document.getElementById('album-cover-image-id');
            const coverPreview = document.getElementById('featured-preview-album');
            const selectedNewsList = document.getElementById('selected-news-list');
            const premiumInput = document.getElementById('album-premium');
            const completedInput = document.getElementById('album-completed');
            const hiatusInput = document.getElementById('album-hiatus');
            
            if (albumIdInput) albumIdInput.value = '';
            if (coverImageId) coverImageId.value = '';
            if (coverPreview) {
                coverPreview.src = '';
                coverPreview.classList.add('hidden');
            }
            if (selectedNewsList) {
                selectedNewsList.innerHTML = '<p class="text-sm text-amber-500 italic">Belum ada artikel dipilih</p>';
            }
            if (premiumInput) premiumInput.checked = false;
            if (completedInput) completedInput.checked = false;
            if (hiatusInput) hiatusInput.checked = false;
            
            // Clear selected news arrays
            selectedNews = [];
            tempSelectedNews = [];
        }
        
        modal.classList.remove('hidden');
    }

    function closeAlbumModal() {
        const modal = document.getElementById('album-modal');
        if (modal) modal.classList.add('hidden');
        currentAlbumId = null;
        selectedNews = [];
        tempSelectedNews = [];
    }

    // Load album for editing
    async function loadAlbumForEdit(albumId) {
        try {
            const response = await fetch(`/api/albums/${albumId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const album = await response.json();
            
            // Get form elements
            const albumIdInput = document.getElementById('album-id');
            const titleInput = document.getElementById('album-title');
            const descInput = document.getElementById('album-description');
            const categoryInput = document.getElementById('album-category');
            const premiumInput = document.getElementById('album-premium');
            const completedInput = document.getElementById('album-completed');
            const hiatusInput = document.getElementById('album-hiatus');
            const coverImageId = document.getElementById('album-cover-image-id');
            const coverPreview = document.getElementById('featured-preview-album');
            
            // Populate form fields with album data
            if (albumIdInput) albumIdInput.value = album.id;
            if (titleInput) titleInput.value = album.title;
            if (descInput) descInput.value = album.description || '';
            if (categoryInput) categoryInput.value = album.category ? album.category.id : '';
            if (premiumInput) premiumInput.checked = album.is_premium;
            if (completedInput) completedInput.checked = album.is_completed;
            if (hiatusInput) hiatusInput.checked = album.is_hiatus;
            
            // Handle cover image
            if (album.cover_image && coverImageId && coverPreview) {
                coverImageId.value = album.cover_image.id;
                // Fix image preview - handle different image data structures
                let coverImageSrc = '';
                if (album.cover_image.file_url) {
                    coverImageSrc = album.cover_image.file_url;
                } else if (album.cover_image.url) {
                    coverImageSrc = album.cover_image.url;
                } else if (album.cover_image.filepath) {
                    coverImageSrc = album.cover_image.filepath;
                } else if (album.cover_image.filename) {
                    coverImageSrc = `/static/uploads/${album.cover_image.filename}`;
                }
                if (coverImageSrc) {
                    coverPreview.src = coverImageSrc;
                    coverPreview.classList.remove('hidden');
                }
            } else {
                // Clear image if no cover image
                if (coverImageId) coverImageId.value = '';
                if (coverPreview) {
                    coverPreview.src = '';
                    coverPreview.classList.add('hidden');
                }
            }
            
            // Load selected news/chapters
            if (album.chapters && album.chapters.length > 0) {
                selectedNews = album.chapters.map(chapter => ({
                    id: chapter.news.id,
                    title: chapter.news.title,
                    chapter_number: chapter.chapter_number
                }));
                displaySelectedNews();
            } else {
                // Clear selected news if no chapters
                selectedNews = [];
                displaySelectedNews();
            }
            
            // Load SEO fields
            const metaDescInput = document.getElementById('album-meta-description');
            const metaKeywordsInput = document.getElementById('album-meta-keywords');
            const seoSlugInput = document.getElementById('album-seo-slug');
            const canonicalUrlInput = document.getElementById('album-canonical-url');
            const ogTitleInput = document.getElementById('album-og-title');
            const ogDescInput = document.getElementById('album-og-description');
            const ogImageInput = document.getElementById('album-og-image');
            const metaAuthorInput = document.getElementById('album-meta-author');
            const metaLanguageInput = document.getElementById('album-meta-language');
            const metaRobotsInput = document.getElementById('album-meta-robots');
            const structuredDataTypeInput = document.getElementById('album-structured-data-type');
            
            if (metaDescInput) metaDescInput.value = album.meta_description || '';
            if (metaKeywordsInput) metaKeywordsInput.value = album.meta_keywords || '';
            if (seoSlugInput) seoSlugInput.value = album.seo_slug || '';
            if (canonicalUrlInput) canonicalUrlInput.value = album.canonical_url || '';
            if (ogTitleInput) ogTitleInput.value = album.og_title || '';
            if (ogDescInput) ogDescInput.value = album.og_description || '';
            if (ogImageInput) ogImageInput.value = album.og_image || '';
            if (metaAuthorInput) metaAuthorInput.value = album.meta_author || '';
            if (metaLanguageInput) metaLanguageInput.value = album.meta_language || 'id';
            if (metaRobotsInput) metaRobotsInput.value = album.meta_robots || 'index, follow';
            if (structuredDataTypeInput) structuredDataTypeInput.value = album.structured_data_type || 'Book';
            
            console.log('Album loaded for editing:', album);
            
        } catch (error) {
            console.error('Error loading album:', error);
            showToast('Error loading album: ' + error.message, 'error');
        }
    }

    // Handle album form submission
    async function handleAlbumSubmit(e) {
        e.preventDefault();
        
        if (selectedNews.length === 0) {
            showToast('Pilih minimal satu artikel untuk album', 'error');
            return;
        }
        
        const titleInput = document.getElementById('album-title');
        const descInput = document.getElementById('album-description');
        const categoryInput = document.getElementById('album-category');
        const premiumInput = document.getElementById('album-premium');
        const coverImageId = document.getElementById('album-cover-image-id');
        
        const completedInput = document.getElementById('album-completed');
        const hiatusInput = document.getElementById('album-hiatus');
        
        // Get SEO form elements
        const metaDescInput = document.getElementById('album-meta-description');
        const metaKeywordsInput = document.getElementById('album-meta-keywords');
        const seoSlugInput = document.getElementById('album-seo-slug');
        const canonicalUrlInput = document.getElementById('album-canonical-url');
        const ogTitleInput = document.getElementById('album-og-title');
        const ogDescInput = document.getElementById('album-og-description');
        const ogImageInput = document.getElementById('album-og-image');
        const metaAuthorInput = document.getElementById('album-meta-author');
        const metaLanguageInput = document.getElementById('album-meta-language');
        const metaRobotsInput = document.getElementById('album-meta-robots');
        const structuredDataTypeInput = document.getElementById('album-structured-data-type');
        
        const formData = {
            title: titleInput ? titleInput.value : '',
            description: descInput ? descInput.value : '',
            category_id: categoryInput ? categoryInput.value : '',
            is_premium: premiumInput ? premiumInput.checked : false,
            is_completed: completedInput ? completedInput.checked : false,
            is_hiatus: hiatusInput ? hiatusInput.checked : false,
            cover_image_id: coverImageId ? coverImageId.value || null : null,
            // SEO Fields
            meta_description: metaDescInput ? metaDescInput.value : '',
            meta_keywords: metaKeywordsInput ? metaKeywordsInput.value : '',
            seo_slug: seoSlugInput ? seoSlugInput.value : '',
            canonical_url: canonicalUrlInput ? canonicalUrlInput.value : '',
            og_title: ogTitleInput ? ogTitleInput.value : '',
            og_description: ogDescInput ? ogDescInput.value : '',
            og_image: ogImageInput ? ogImageInput.value : '',
            meta_author: metaAuthorInput ? metaAuthorInput.value : '',
            meta_language: metaLanguageInput ? metaLanguageInput.value : 'id',
            meta_robots: metaRobotsInput ? metaRobotsInput.value : 'index, follow',
            structured_data_type: structuredDataTypeInput ? structuredDataTypeInput.value : 'Book',
            chapters: selectedNews.map((news, index) => ({
                news_id: news.id,
                chapter_number: index + 1,
                chapter_title: news.title
            }))
        };
        
        try {
            const url = currentAlbumId ? `/api/albums/${currentAlbumId}` : '/api/albums';
            const method = currentAlbumId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast(currentAlbumId ? 'Album berhasil diperbarui' : 'Album berhasil dibuat', 'success');
                closeAlbumModal();
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error saving album', 'error');
            }
        } catch (error) {
            console.error('Error saving album:', error);
            showToast('Error saving album', 'error');
        }
    }

    // Album cover image modal functions (using exact same system as news creation)
    async function loadHeaderLibraryAlbum(page = 1) {
        const container = document.getElementById('header-image-library-album');
        const paginationContainer = document.getElementById('header-image-pagination-controls-album');
        if (!container || !paginationContainer) return;

        container.innerHTML = '<p class="col-span-full text-center text-gray-500 py-4">Loading images...</p>'; // Loading state
        paginationContainer.innerHTML = ''; // Clear old pagination

        try {
            const response = await fetch(`/api/images?page=${page}&per_page=12`); // Fetch paginated images
            if (!response.ok) throw new Error('Failed to load header images');
            const data = await response.json();
            const imgs = data.items || [];

            container.innerHTML = imgs.map(image => {
                 // --- Thumbnail Logic (Featured Image Modal Grid) ---
                const placeholderImg = '/static/pic/placeholder.png';
                const fullImageUrl = image.file_url || image.url || '/static/pic/placeholder.png';
                let squareThumbUrl = placeholderImg; // For the grid display
                let landscapeThumbUrl = placeholderImg; // For the preview after selection

                if (image.filepath) {
                    const pathWithoutStatic = image.filepath.replace('static/', '', 1);
                    const lastDotIndex = pathWithoutStatic.lastIndexOf('.');
                    if (lastDotIndex !== -1) {
                        const base_path = pathWithoutStatic.substring(0, lastDotIndex);
                        const extension = pathWithoutStatic.substring(lastDotIndex);
                        squareThumbUrl = `/static/${base_path}_thumb_square${extension}`; // Use square for grid
                        landscapeThumbUrl = `/static/${base_path}_thumb_landscape${extension}`; // Use landscape for preview data
                    } else {
                        squareThumbUrl = fullImageUrl; // Fallback
                        landscapeThumbUrl = fullImageUrl; // Fallback
                    }
                } else {
                    squareThumbUrl = fullImageUrl; // Fallback for external URLs
                    landscapeThumbUrl = fullImageUrl; // Fallback for external URLs
                }
                // --- End Thumbnail Logic ---
                return `
                <div class="p-2 group cursor-pointer border border-transparent hover:border-yellow-400 rounded-lg transition duration-150">
                    <img src="${squareThumbUrl}" onerror="this.onerror=null;this.src='${placeholderImg}'" alt="${image.filename || 'Image'}" class="w-full aspect-square object-cover rounded-lg mb-2 shadow-sm group-hover:shadow-md" loading="lazy">
                    <button class="select-header-album mt-2 w-full bg-yellow-500 text-gray-900 py-1 rounded-lg font-semibold" data-thumb-url="${landscapeThumbUrl}" data-id="${image.id}">Select</button>
                </div>
                `;
            }).join('');

            // Re-attach listeners
            container.querySelectorAll('.select-header-album').forEach(btn => {
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
                newBtn.addEventListener('click', () => {
                    const preview = document.getElementById('featured-preview-album');
                    const imageIdInput = document.getElementById('album-cover-image-id');
                    if (preview && imageIdInput) {
                        preview.src = newBtn.dataset.thumbUrl; // Use the landscape thumb URL for preview
                        imageIdInput.value = newBtn.dataset.id; // Set the hidden input value
                        preview.classList.remove('hidden');
                    }
                    closeImageHeaderModalAlbum();
                });
            });

            // Update pagination controls
            updateHeaderImagePaginationControlsAlbum(data);
        } catch (err) {
            console.error('Error loading header images:', err);
            container.innerHTML = '<p class="col-span-full text-center text-red-500 py-4">Error loading images.</p>';
        }
    }

    function openImageHeaderModalAlbum() {
        console.log("Attempting to open featured image modal (#image-header-modal-album)"); // Debug log
        const modal = document.getElementById('image-header-modal-album');
        if (modal) {
            modal.classList.remove('hidden');
            loadHeaderLibraryAlbum(1); // Load first page when opening
        } else {
            console.error("Featured image modal (#image-header-modal-album) not found.");
        }
    }

    function closeImageHeaderModalAlbum() {
        const modal = document.getElementById('image-header-modal-album');
        if (modal) modal.classList.add('hidden');
    }

    function clearHeaderImageAlbum() {
        const coverImageId = document.getElementById('album-cover-image-id');
        const coverPreview = document.getElementById('featured-preview-album');
        
        if (coverImageId) coverImageId.value = '';
        if (coverPreview) {
            coverPreview.src = '';
            coverPreview.classList.add('hidden');
        }
    }

    async function uploadHeaderImageAlbum() {
        const fileInput = document.getElementById('header-upload-file-album');
        const urlInput = document.getElementById('header-upload-url-album');
        const nameInput = document.getElementById('header-upload-name-album');
        const urlValue = urlInput.value.trim();
        const nameValue = nameInput.value.trim();
        const fd = new FormData();

        if (fileInput.files.length) {
            fd.append('file', fileInput.files[0]);
        } else if (urlValue) {
            fd.append('url', urlValue);
        } else {
            if (typeof showToast === 'function') showToast('warning', 'Pilih berkas atau masukkan URL.');
            return; // No file or URL provided
        }
        if (nameValue) fd.append('name', nameValue);
        fd.append('is_visible', 'true'); // Make uploaded header images visible by default?

        try {
            const resp = await fetch('/api/images', { method: 'POST', body: fd });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || 'Upload failed');

            // Clear inputs after successful upload
            nameInput.value = '';
            fileInput.value = ''; // Clear file input
            urlInput.value = ''; // Clear URL input

            // Reload the image library
            loadHeaderLibraryAlbum(1);

            if (typeof showToast === 'function') showToast('success', 'Gambar berhasil diunggah!');
        } catch (error) {
            console.error('Upload error:', error);
            if (typeof showToast === 'function') showToast('error', 'Gagal mengunggah gambar: ' + error.message);
        }
    }

    // Pagination helper functions (copied from news-create.js)
    function generatePageNumbers(currentPage, totalPages, edgeCount = 1, currentCount = 2) {
        if (totalPages <= 1) return [];
        const pages = new Set();
        for (let i = 1; i <= Math.min(edgeCount, totalPages); i++) pages.add(i);
        for (let i = Math.max(1, totalPages - edgeCount + 1); i <= totalPages; i++) pages.add(i);
        for (let i = Math.max(1, currentPage - currentCount); i <= Math.min(totalPages, currentPage + currentCount); i++) pages.add(i);
        const sortedPages = Array.from(pages).sort((a, b) => a - b);
        const result = [];
        let lastPage = 0;
        for (const page of sortedPages) {
            if (page > lastPage + 1) result.push(null); // Ellipsis
            result.push(page);
            lastPage = page;
        }
        return result;
    }

    function createPaginationElement(tag, classes, content, ariaLabel = null, title = null, disabled = false, onClick = null) {
        const element = document.createElement(tag);
        element.className = classes;
        element.textContent = content;
        if (ariaLabel) element.setAttribute('aria-label', ariaLabel);
        if (title) element.setAttribute('title', title);
        if (disabled) element.disabled = true;
        if (onClick) element.addEventListener('click', onClick);
        return element;
    }

    function updateHeaderImagePaginationControlsAlbum(paginationData) {
        const container = document.getElementById('header-image-pagination-controls-album');
        if (!container || !paginationData) return;

        const { page, total_pages } = paginationData;
        if (total_pages <= 1) {
            container.innerHTML = '';
            return;
        }

        const pageNumbers = generatePageNumbers(page, total_pages);
        container.innerHTML = '';

        // Previous button
        const prevBtn = createPaginationElement(
            'button',
            'px-3 py-1 mx-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed',
            '←',
            'Previous page',
            'Previous page',
            page <= 1,
            page > 1 ? () => loadHeaderLibraryAlbum(page - 1) : null
        );
        container.appendChild(prevBtn);

        // Page numbers
        pageNumbers.forEach(pageNum => {
            if (pageNum === null) {
                // Ellipsis
                const ellipsis = createPaginationElement('span', 'px-3 py-1 mx-1', '...');
                container.appendChild(ellipsis);
            } else {
                const pageBtn = createPaginationElement(
                    'button',
                    `px-3 py-1 mx-1 rounded ${pageNum === page ? 'bg-yellow-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`,
                    pageNum.toString(),
                    `Page ${pageNum}`,
                    `Go to page ${pageNum}`,
                    false,
                    () => loadHeaderLibraryAlbum(pageNum)
                );
                container.appendChild(pageBtn);
            }
        });

        // Next button
        const nextBtn = createPaginationElement(
            'button',
            'px-3 py-1 mx-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed',
            '→',
            'Next page',
            'Next page',
            page >= total_pages,
            page < total_pages ? () => loadHeaderLibraryAlbum(page + 1) : null
        );
        container.appendChild(nextBtn);
    }

    // News picker modal functions
    function openNewsPickerModal() {
        const modal = document.getElementById('news-picker-modal');
        if (!modal) return;
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Populate category filter
        populateNewsPickerCategoryFilter();
        
        // Load news articles
        loadNewsPicker();
        
        // Add event listeners for filters
        setupNewsPickerEventListeners();
    }
    
    function populateNewsPickerCategoryFilter() {
        const categoryFilter = document.getElementById('news-category-filter');
        if (!categoryFilter) return;
        
        // Clear existing options except the first one
        categoryFilter.innerHTML = '<option value="">Semua Kategori</option>';
        
        // Add category options
        if (window.categories && window.categories.length > 0) {
            window.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categoryFilter.appendChild(option);
            });
        }
    }
    
    function setupNewsPickerEventListeners() {
        const searchInput = document.getElementById('news-search');
        const categoryFilter = document.getElementById('news-category-filter');
        const statusFilter = document.getElementById('news-status-filter');
        
        // Debounced search
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                filterNewsPicker();
            }, 300));
        }
        
        // Category filter
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                filterNewsPicker();
            });
        }
        
        // Status filter
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                filterNewsPicker();
            });
        }
    }

    function closeNewsPickerModal() {
        const modal = document.getElementById('news-picker-modal');
        const searchInput = document.getElementById('news-search');
        const categoryFilter = document.getElementById('news-category-filter');
        const statusFilter = document.getElementById('news-status-filter');
        
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
        if (searchInput) searchInput.value = '';
        if (categoryFilter) categoryFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        tempSelectedNews = [];
    }

    async function loadNewsPicker(page = 1) {
        const list = document.getElementById('news-picker-list');
        const paginationContainer = document.getElementById('news-picker-pagination');
        if (!list || !paginationContainer) return;
        
        list.innerHTML = '<p class="text-center text-amber-600 py-4">Memuat artikel...</p>';
        paginationContainer.innerHTML = '';
        
        try {
            // Get filter values
            const searchQuery = document.getElementById('news-search')?.value || '';
            const categoryFilter = document.getElementById('news-category-filter')?.value || '';
            const statusFilter = document.getElementById('news-status-filter')?.value || '';
            
            // Build query parameters
            const params = new URLSearchParams({
                page: page,
                per_page: 10
            });
            
            if (searchQuery) params.append('search', searchQuery);
            if (categoryFilter) params.append('category', categoryFilter);
            if (statusFilter) params.append('status', statusFilter);
            
            const response = await fetch(`/api/news?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to load news articles');
            
            const data = await response.json();
            const news = data.items || [];
            
            console.log('Loading news for picker:', news);
            
            if (news.length === 0) {
                list.innerHTML = '<p class="text-center text-amber-600 py-4">Tidak ada artikel tersedia</p>';
                paginationContainer.innerHTML = '';
                return;
            }
            
            list.innerHTML = news.map(article => {
                const isSelected = selectedNews.some(n => n.id === article.id);
                const isTempSelected = tempSelectedNews.some(n => n.id === article.id);
                const isChecked = isSelected || isTempSelected;
                
                return `
                    <div class="flex items-center p-3 bg-white border border-amber-200 rounded-lg hover:border-amber-400 transition-all duration-300">
                        <input type="checkbox" id="news-${article.id}" value="${article.id}" ${isChecked ? 'checked' : ''} class="rounded border-amber-300 text-amber-500 focus:ring-amber-400">
                        <label for="news-${article.id}" class="ml-3 flex-1 cursor-pointer">
                            <div class="font-medium text-amber-800">${article.title}</div>
                            <div class="text-sm text-amber-600">${article.category ? article.category.name : 'Unknown'} • ${article.writer || 'Unknown'} • ${article.is_visible ? 'Tampilkan' : 'Sembunyikan'}</div>
                        </label>
                    </div>
                `;
            }).join('');
            
            // Add event listeners to checkboxes
            list.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const newsId = parseInt(this.value);
                    const selectedArticle = news.find(n => n.id === newsId);
                    
                    if (this.checked) {
                        tempSelectedNews.push({
                            id: selectedArticle.id,
                            title: selectedArticle.title
                        });
                    } else {
                        tempSelectedNews = tempSelectedNews.filter(n => n.id !== selectedArticle.id);
                    }
                });
            });
            
            // Generate pagination
             renderPagination('news-picker-pagination', { currentPage: data.page, totalPages: data.total_pages }, loadNewsPicker);
            
        } catch (error) {
            console.error('Error loading news picker:', error);
            list.innerHTML = '<p class="text-center text-red-600 py-4">Error memuat artikel</p>';
        }
    }

    function filterNewsPicker() {
        // Reload with current filters
        loadNewsPicker(1);
    }
    
    function clearNewsFilters() {
        const searchInput = document.getElementById('news-search');
        const categoryFilter = document.getElementById('news-category-filter');
        const statusFilter = document.getElementById('news-status-filter');
        
        if (searchInput) searchInput.value = '';
        if (categoryFilter) categoryFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        
        loadNewsPicker(1);
    }

    function confirmNewsSelection() {
        selectedNews = [...tempSelectedNews];
        displaySelectedNews();
        closeNewsPickerModal();
    }

    function displaySelectedNews() {
        const list = document.getElementById('selected-news-list');
        if (!list) return;
        
        if (selectedNews.length === 0) {
            list.innerHTML = '<p class="text-sm text-amber-500 italic">Belum ada artikel dipilih</p>';
            return;
        }
        
        list.innerHTML = selectedNews.map((news, index) => `
            <div class="flex items-center justify-between p-2 bg-amber-100 rounded border border-amber-200">
                <div class="flex items-center">
                    <span class="text-sm font-medium text-amber-700 mr-2">Chapter ${news.chapter_number || (index + 1)}:</span>
                    <span class="text-sm text-amber-800">${news.title}</span>
                </div>
                <button onclick="window.removeSelectedNews(${index})" class="text-red-500 hover:text-red-700 text-sm">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    function removeSelectedNews(index) {
        selectedNews.splice(index, 1);
        displaySelectedNews();
    }

    // Album actions
    async function editAlbum(albumId) {
        openAlbumModal(albumId);
    }

    async function toggleAlbumVisibility(albumId) {
        showAlbumCardLoading(albumId);
        const currentPage = document.querySelector('#pagination button.bg-gradient-to-r.from-amber-600')?.textContent || 1;
        
        try {
            const response = await fetch(`/api/albums/${albumId}/visibility`, {
                method: 'PATCH'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Album visibility updated successfully', 'success');
                loadAlbums(currentPage);
            } else {
                showToast(data.error || data.message || 'Error toggling visibility', 'error');
                loadAlbums(currentPage); // Reload to restore original state
            }
        } catch (error) {
            console.error('Error toggling visibility:', error);
            showToast('Error toggling visibility', 'error');
            loadAlbums(currentPage); // Reload to restore original state
        }
    }

    // Toggle album type (premium/regular)
    async function toggleAlbumType(albumId) {
        showAlbumCardLoading(albumId);
        const currentPage = document.querySelector('#pagination button.bg-gradient-to-r.from-amber-600')?.textContent || 1;
        
        try {
            const response = await fetch(`/api/albums/${albumId}/type`, {
                method: 'PATCH'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Album type updated successfully', 'success');
                loadAlbums(currentPage);
            } else {
                showToast(data.error || data.message || 'Error toggling type', 'error');
                loadAlbums(currentPage); // Reload to restore original state
            }
        } catch (error) {
            console.error('Error toggling type:', error);
            showToast('Error toggling type', 'error');
            loadAlbums(currentPage); // Reload to restore original state
        }
    }

    function deleteAlbum(albumId) {
        showConfirmModal(
            'Apakah Anda yakin ingin menghapus album ini?',
            'Tindakan ini tidak dapat dibatalkan.',
            () => executeDeleteAlbum(albumId)
        );
    }

    async function executeDeleteAlbum(albumId) {
        showAlbumCardLoading(albumId);
        
        try {
            const response = await fetch(`/api/albums/${albumId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Album berhasil dihapus', 'success');
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error deleting album', 'error');
                loadAlbums(); // Reload to restore original state
            }
        } catch (error) {
            console.error('Error deleting album:', error);
            showToast('Error deleting album', 'error');
            loadAlbums(); // Reload to restore original state
        }
    }

    // Confirmation modal functions
    function showConfirmModal(title, message, action) {
        const modal = document.getElementById('confirm-modal');
        const titleEl = document.getElementById('confirm-modal-title');
        const messageEl = document.getElementById('confirm-modal-message');
        const actionBtn = document.getElementById('confirm-modal-action');
        
        if (!modal || !titleEl || !messageEl || !actionBtn) return;
        
        titleEl.textContent = title;
        messageEl.textContent = message;
        
        actionBtn.onclick = () => {
            action();
            closeConfirmModal();
        };
        
        modal.classList.remove('hidden');
    }

    function closeConfirmModal() {
        const modal = document.getElementById('confirm-modal');
        if (modal) modal.classList.add('hidden');
    }

    // Utility functions
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

    // Chapter management functions
    function editChapter(albumId, chapterId, currentTitle, chapterNumber, newsTitle) {
        const modal = document.getElementById('chapter-edit-modal');
        const titleInput = document.getElementById('chapter-edit-title-input');
        const numberInput = document.getElementById('chapter-edit-number');
        const newsTitleInput = document.getElementById('chapter-edit-news-title');
        const chapterIdInput = document.getElementById('chapter-edit-id');
        const albumIdInput = document.getElementById('chapter-edit-album-id');
        
        if (modal && titleInput && numberInput && newsTitleInput && chapterIdInput && albumIdInput) {
            titleInput.value = currentTitle;
            numberInput.value = chapterNumber;
            newsTitleInput.value = newsTitle;
            chapterIdInput.value = chapterId;
            albumIdInput.value = albumId;
            
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    function closeChapterEditModal() {
        const modal = document.getElementById('chapter-edit-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    async function saveChapterEdit() {
        const chapterId = document.getElementById('chapter-edit-id').value;
        const albumId = document.getElementById('chapter-edit-album-id').value;
        const title = document.getElementById('chapter-edit-title-input').value;
        const number = document.getElementById('chapter-edit-number').value;
        
        if (!title || !number) {
            showToast('Judul dan nomor chapter harus diisi', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/albums/${albumId}/chapters/${chapterId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chapter_title: title,
                    chapter_number: parseInt(number)
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Chapter berhasil diperbarui', 'success');
                closeChapterEditModal();
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error updating chapter', 'error');
            }
        } catch (error) {
            console.error('Error updating chapter:', error);
            showToast('Error updating chapter', 'error');
        }
    }

    function removeChapter(albumId, chapterId, chapterTitle) {
        showConfirmModal(
            `Apakah Anda yakin ingin menghapus chapter "${chapterTitle}"?`,
            'Tindakan ini tidak dapat dibatalkan.',
            () => executeRemoveChapter(albumId, chapterId)
        );
    }

    async function executeRemoveChapter(albumId, chapterId) {
        try {
            const response = await fetch(`/api/albums/${albumId}/chapters/${chapterId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Chapter berhasil dihapus', 'success');
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error removing chapter', 'error');
            }
        } catch (error) {
            console.error('Error removing chapter:', error);
            showToast('Error removing chapter', 'error');
        }
    }

    // Archive/Unarchive functions
    async function archiveAlbum(albumId) {
        try {
            const response = await fetch(`/api/albums/${albumId}/archive`, {
                method: 'PATCH'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Album berhasil diarsipkan', 'success');
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error archiving album', 'error');
            }
        } catch (error) {
            console.error('Error archiving album:', error);
            showToast('Error archiving album', 'error');
        }
    }

    async function unarchiveAlbum(albumId) {
        try {
            const response = await fetch(`/api/albums/${albumId}/unarchive`, {
                method: 'PATCH'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('Album berhasil unarsipkan', 'success');
                loadAlbums();
            } else {
                showToast(data.error || data.message || 'Error unarchiving album', 'error');
            }
        } catch (error) {
            console.error('Error unarchiving album:', error);
            showToast('Error unarchiving album', 'error');
        }
    }

    // Bulk operations
    let selectedAlbums = [];
    let isBulkMode = false;

    function toggleBulkMode() {
        isBulkMode = !isBulkMode;
        const bulkActions = document.getElementById('bulk-actions');
        const checkboxes = document.querySelectorAll('.album-checkbox');
        const selectAllCheckbox = document.getElementById('select-all-albums');
        
        if (isBulkMode) {
            bulkActions.classList.add('show');
            checkboxes.forEach(checkbox => checkbox.classList.remove('hidden'));
            if (selectAllCheckbox) selectAllCheckbox.checked = false;
            selectedAlbums = [];
            updateSelectedCount();
        } else {
            bulkActions.classList.remove('show');
            checkboxes.forEach(checkbox => {
                checkbox.classList.add('hidden');
                checkbox.checked = false;
            });
            selectedAlbums = [];
            updateSelectedCount();
        }
    }

    function exitBulkMode() {
        isBulkMode = false;
        const bulkActions = document.getElementById('bulk-actions');
        const checkboxes = document.querySelectorAll('.album-checkbox');
        const selectAllCheckbox = document.getElementById('select-all-albums');
        
        bulkActions.classList.remove('show');
        checkboxes.forEach(checkbox => {
            checkbox.classList.add('hidden');
            checkbox.checked = false;
        });
        if (selectAllCheckbox) selectAllCheckbox.checked = false;
        selectedAlbums = [];
        updateSelectedCount();
    }

    function updateSelectedCount() {
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = `(${selectedAlbums.length} dipilih)`;
        }
    }

    function handleAlbumSelection(albumId, isChecked) {
        if (isChecked) {
            if (!selectedAlbums.includes(albumId)) {
                selectedAlbums.push(albumId);
            }
        } else {
            selectedAlbums = selectedAlbums.filter(id => id !== albumId);
        }
        updateSelectedCount();
    }

    function handleSelectAll(isChecked) {
        const checkboxes = document.querySelectorAll('.album-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            const albumId = checkbox.dataset.albumId;
            if (isChecked) {
                if (!selectedAlbums.includes(albumId)) {
                    selectedAlbums.push(albumId);
                }
            } else {
                selectedAlbums = selectedAlbums.filter(id => id !== albumId);
            }
        });
        updateSelectedCount();
    }

    async function bulkArchive() {
        if (selectedAlbums.length === 0) {
            showToast('Pilih album terlebih dahulu', 'error');
            return;
        }
        
        showConfirmModal(
            `Arsipkan ${selectedAlbums.length} album?`,
            'Album yang diarsipkan akan disembunyikan dari tampilan publik.',
            () => executeBulkOperation('archive')
        );
    }

    async function bulkUnarchive() {
        if (selectedAlbums.length === 0) {
            showToast('Pilih album terlebih dahulu', 'error');
            return;
        }
        
        showConfirmModal(
            `Unarsipkan ${selectedAlbums.length} album?`,
            'Album akan ditampilkan kembali.',
            () => executeBulkOperation('unarchive')
        );
    }

    async function bulkHide() {
        if (selectedAlbums.length === 0) {
            showToast('Pilih album terlebih dahulu', 'error');
            return;
        }
        
        showConfirmModal(
            `Sembunyikan ${selectedAlbums.length} album?`,
            'Album akan disembunyikan dari tampilan publik.',
            () => executeBulkOperation('hide')
        );
    }

    async function bulkShow() {
        if (selectedAlbums.length === 0) {
            showToast('Pilih album terlebih dahulu', 'error');
            return;
        }
        
        showConfirmModal(
            `Tampilkan ${selectedAlbums.length} album?`,
            'Album akan ditampilkan kembali.',
            () => executeBulkOperation('show')
        );
    }

    async function bulkDelete() {
        if (selectedAlbums.length === 0) {
            showToast('Pilih album terlebih dahulu', 'error');
            return;
        }
        
        showConfirmModal(
            `Hapus ${selectedAlbums.length} album?`,
            'Tindakan ini tidak dapat dibatalkan.',
            () => executeBulkOperation('delete')
        );
    }

    async function executeBulkOperation(operation) {
        try {
            const promises = selectedAlbums.map(albumId => {
                let url, method;
                
                switch (operation) {
                    case 'archive':
                        url = `/api/albums/${albumId}/archive`;
                        method = 'PATCH';
                        break;
                    case 'unarchive':
                        url = `/api/albums/${albumId}/unarchive`;
                        method = 'PATCH';
                        break;
                    case 'hide':
                        url = `/api/albums/${albumId}/visibility`;
                        method = 'PATCH';
                        break;
                    case 'show':
                        url = `/api/albums/${albumId}/visibility`;
                        method = 'PATCH';
                        break;
                    case 'delete':
                        url = `/api/albums/${albumId}`;
                        method = 'DELETE';
                        break;
                }
                
                return fetch(url, { method });
            });
            
            const responses = await Promise.all(promises);
            const failedCount = responses.filter(r => !r.ok).length;
            const successCount = responses.length - failedCount;
            
            if (failedCount === 0) {
                showToast(`${operation} berhasil untuk ${successCount} album`, 'success');
            } else {
                showToast(`${operation} berhasil untuk ${successCount} album, gagal untuk ${failedCount} album`, 'warning');
            }
            
            exitBulkMode();
            loadAlbums();
            
        } catch (error) {
            console.error('Error executing bulk operation:', error);
            showToast('Error executing bulk operation', 'error');
        }
    }

    // Setup bulk operation event listeners
    function setupBulkEventListeners() {
        const selectAllCheckbox = document.getElementById('select-all-albums');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                handleSelectAll(this.checked);
            });
        }

        // Delegate event listeners for album checkboxes
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('album-checkbox')) {
                const albumId = e.target.dataset.albumId;
                handleAlbumSelection(albumId, e.target.checked);
            }
        });

        // Chapter edit form submission
        const chapterEditForm = document.getElementById('chapter-edit-form');
        if (chapterEditForm) {
            chapterEditForm.addEventListener('submit', function(e) {
                e.preventDefault();
                saveChapterEdit();
            });
        }
    }

    // SEO Functions
    function displaySEOAlbums(albums) {
        const tbody = document.getElementById('seo-albums-table-body');
        if (!tbody) return;

        if (albums.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        <i class="fas fa-inbox text-xl mb-2"></i>
                        <p>No albums to display</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = albums.map(album => createSEOAlbumRow(album)).join('');
    }

    function createSEOAlbumRow(album) {
        const seoStatus = getSEOStatus(album);
        const seoStatusClass = getSEOStatusClass(seoStatus);
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <img class="h-10 w-10 rounded-lg object-cover" src="${album.cover_image ? (album.cover_image.file_url || album.cover_image.url || album.cover_image.filepath || '/static/pic/placeholder.png') : '/static/pic/placeholder.png'}" alt="${album.title}">
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${album.title}</div>
                            <div class="text-sm text-gray-500">${album.author ? album.author.username : 'Unknown'}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${album.category ? album.category.name : 'Unknown'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${seoStatusClass}">
                        ${seoStatus}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${album.meta_description ? (album.meta_description.length > 50 ? album.meta_description.substring(0, 50) + '...' : album.meta_description) : 'None'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${album.meta_keywords ? (album.meta_keywords.length > 30 ? album.meta_keywords.substring(0, 30) + '...' : album.meta_keywords) : 'None'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${album.og_title ? '✓' : '✗'} / ${album.og_description ? '✓' : '✗'} / ${album.og_image ? '✓' : '✗'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="editAlbumSEO(${album.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="viewAlbumSEO(${album.id})" class="text-green-600 hover:text-green-900">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    function getSEOStatus(album) {
        const hasMetaDesc = album.meta_description && album.meta_description.trim().length > 0;
        const hasKeywords = album.meta_keywords && album.meta_keywords.trim().length > 0;
        const hasOGTitle = album.og_title && album.og_title.trim().length > 0;
        const hasOGDesc = album.og_description && album.og_description.trim().length > 0;
        const hasOGImage = album.og_image && album.og_image.trim().length > 0;
        const hasSlug = album.seo_slug && album.seo_slug.trim().length > 0;

        const totalFields = 6;
        const filledFields = [hasMetaDesc, hasKeywords, hasOGTitle, hasOGDesc, hasOGImage, hasSlug].filter(Boolean).length;

        if (filledFields === 0) return 'Missing';
        if (filledFields < totalFields / 2) return 'Incomplete';
        return 'Complete';
    }

    function getSEOStatusClass(status) {
        switch (status) {
            case 'Complete': return 'bg-green-100 text-green-800';
            case 'Incomplete': return 'bg-yellow-100 text-yellow-800';
            case 'Missing': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // SEO Modal Functions
    function openSEOEditModal(albumId) {
        const modal = document.getElementById('seo-edit-modal');
        const albumIdInput = document.getElementById('seo-album-id');
        
        if (modal && albumIdInput) {
            albumIdInput.value = albumId;
            modal.classList.remove('hidden');
            loadAlbumSEO(albumId);
        }
    }

    function closeSEOEditModal() {
        const modal = document.getElementById('seo-edit-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    async function loadAlbumSEO(albumId) {
        try {
            const response = await fetch(`/api/albums/${albumId}`);
            if (!response.ok) throw new Error('Failed to fetch album');
            
            const album = await response.json();
            
            // Populate SEO fields
            const metaDescInput = document.getElementById('seo-meta-description');
            const metaKeywordsInput = document.getElementById('seo-meta-keywords');
            const seoSlugInput = document.getElementById('seo-seo-slug');
            const canonicalUrlInput = document.getElementById('seo-canonical-url');
            const ogTitleInput = document.getElementById('seo-og-title');
            const ogDescInput = document.getElementById('seo-og-description');
            const ogImageInput = document.getElementById('seo-og-image');
            const metaAuthorInput = document.getElementById('seo-meta-author');
            const metaLanguageInput = document.getElementById('seo-meta-language');
            const metaRobotsInput = document.getElementById('seo-meta-robots');
            const structuredDataTypeInput = document.getElementById('seo-structured-data-type');
            
            if (metaDescInput) metaDescInput.value = album.meta_description || '';
            if (metaKeywordsInput) metaKeywordsInput.value = album.meta_keywords || '';
            if (seoSlugInput) seoSlugInput.value = album.seo_slug || '';
            if (canonicalUrlInput) canonicalUrlInput.value = album.canonical_url || '';
            if (ogTitleInput) ogTitleInput.value = album.og_title || '';
            if (ogDescInput) ogDescInput.value = album.og_description || '';
            if (ogImageInput) ogImageInput.value = album.og_image || '';
            if (metaAuthorInput) metaAuthorInput.value = album.meta_author || '';
            if (metaLanguageInput) metaLanguageInput.value = album.meta_language || 'id';
            if (metaRobotsInput) metaRobotsInput.value = album.meta_robots || 'index, follow';
            if (structuredDataTypeInput) structuredDataTypeInput.value = album.structured_data_type || 'Book';
            
        } catch (error) {
            console.error('Error loading album SEO:', error);
            showToast('Error loading album SEO', 'error');
        }
    }

    // SEO Form Submit Handler
    function handleSEOFormSubmit(e) {
        e.preventDefault();
        
        const albumId = document.getElementById('seo-album-id').value;
        const formData = {
            meta_description: document.getElementById('seo-meta-description').value,
            meta_keywords: document.getElementById('seo-meta-keywords').value,
            seo_slug: document.getElementById('seo-seo-slug').value,
            canonical_url: document.getElementById('seo-canonical-url').value,
            og_title: document.getElementById('seo-og-title').value,
            og_description: document.getElementById('seo-og-description').value,
            og_image: document.getElementById('seo-og-image').value,
            meta_author: document.getElementById('seo-meta-author').value,
            meta_language: document.getElementById('seo-meta-language').value,
            meta_robots: document.getElementById('seo-meta-robots').value,
            structured_data_type: document.getElementById('seo-structured-data-type').value
        };

        updateAlbumSEO(albumId, formData);
    }

    async function updateAlbumSEO(albumId, seoData) {
        try {
            const response = await fetch(`/api/albums/${albumId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(seoData)
            });

            if (!response.ok) throw new Error('Failed to update album SEO');

            showToast('Album SEO updated successfully', 'success');
            closeSEOEditModal();
            loadSEOAlbums(); // Refresh the SEO table
            
        } catch (error) {
            console.error('Error updating album SEO:', error);
            showToast('Error updating album SEO', 'error');
        }
    }

    // Make functions globally available
    window.openAlbumModal = openAlbumModal;
    window.closeAlbumModal = closeAlbumModal;
    window.openImageHeaderModalAlbum = openImageHeaderModalAlbum;
    window.closeImageHeaderModalAlbum = closeImageHeaderModalAlbum;
    window.openNewsPickerModal = openNewsPickerModal;
    window.closeNewsPickerModal = closeNewsPickerModal;
    window.editAlbum = editAlbum;
    window.toggleAlbumVisibility = toggleAlbumVisibility;
    window.toggleAlbumType = toggleAlbumType;
    window.deleteAlbum = deleteAlbum;
    window.applyFilters = applyFilters;
    window.clearFilters = clearFilters;
    window.loadHeaderLibraryAlbum = loadHeaderLibraryAlbum;
    window.loadNewsPicker = loadNewsPicker;
    window.removeSelectedNews = removeSelectedNews;
    window.confirmNewsSelection = confirmNewsSelection;
    window.closeConfirmModal = closeConfirmModal;
    window.clearNewsFilters = clearNewsFilters;
    
    // New functions
    window.editChapter = editChapter;
    window.closeChapterEditModal = closeChapterEditModal;
    window.removeChapter = removeChapter;
    window.archiveAlbum = archiveAlbum;
    window.unarchiveAlbum = unarchiveAlbum;
    window.toggleBulkMode = toggleBulkMode;
    window.exitBulkMode = exitBulkMode;
    window.bulkArchive = bulkArchive;
    window.bulkUnarchive = bulkUnarchive;
    window.bulkHide = bulkHide;
    window.bulkShow = bulkShow;
    window.bulkDelete = bulkDelete;
    
    // Tab and SEO functions
    window.switchTab = switchTab;
    window.loadSEOAlbums = loadSEOAlbums;
    window.openSEOEditModal = openSEOEditModal;
    window.closeSEOEditModal = closeSEOEditModal;
    window.editAlbumSEO = openSEOEditModal;
    window.viewAlbumSEO = (albumId) => {
        // For now, just open the SEO edit modal
        openSEOEditModal(albumId);
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
