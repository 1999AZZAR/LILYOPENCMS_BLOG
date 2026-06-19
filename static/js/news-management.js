let editSimplemde = null;
let currentNewsId = null;
let fetchTimeout = null;
let categoryMap = {}; // Store category name-to-id mapping
let currentPage = 1; // Keep track of the current page for news

// --- Filter Elements ---
const searchInput = document.getElementById('search');
const categoryFilter = document.getElementById('category-filter');
const statusFilter = document.getElementById('status-filter');
const premiumFilter = document.getElementById('premium-filter');
const popularityFilter = document.getElementById('popularity-filter');
const shareCountFilter = document.getElementById('share-count-filter');
const userFilter = document.getElementById('user-filter');
const filterFeaturedImage = document.getElementById('filter-featured-image'); // New
const filterExternalLink = document.getElementById('filter-external-link'); // New
const archivedFilter = document.getElementById('archived-filter');

// --- Pagination Helpers (Adapted from image-crud.js) ---

// Helper function to generate page numbers
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

// Helper to create a pagination element
function createPaginationElement(tag, classes, content, ariaLabel = null, title = null, disabled = false, onClick = null) {
    const el = document.createElement(tag);
    el.className = classes;
    el.innerHTML = content;
    if (ariaLabel) el.setAttribute('aria-label', ariaLabel);
    if (title) el.title = title;
    if (disabled) el.setAttribute('aria-disabled', 'true');
    if (onClick && !disabled) el.onclick = () => onClick();
    return el;
}

// Generate pagination controls dynamically
function updatePaginationControls(paginationData) {
    const controlsContainer = document.getElementById('pagination-controls');
    if (!controlsContainer) return;
    controlsContainer.innerHTML = '';

    if (!paginationData || paginationData.total_pages <= 1) return;

    const { page: currentPage, total_pages: totalPages } = paginationData;
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Pagination');
    nav.className = 'flex flex-wrap items-center justify-center mt-8 sm:mt-12 lg:mt-16 gap-2 sm:gap-4 md:gap-6 overflow-x-auto';

    // Get current filter values
    const filters = getCurrentFilters();

    const buttonClasses = 'button button-outline px-2 py-1 sm:px-4 sm:py-2 rounded-md hover:bg-primary/10';
    const disabledClasses = 'button button-outline px-2 py-1 sm:px-4 sm:py-2 rounded-md opacity-50 cursor-not-allowed';
    const currentClasses = 'button button-primary px-2 py-1 sm:px-4 sm:py-2 rounded-md';
    const ellipsisClasses = 'h-10 px-2 inline-flex items-center text-muted-foreground text-base font-medium';

    const firstIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" /></svg>`;
    const prevIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>`;
    const nextIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>`;
    const lastIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 4.5l7.5 7.5-7.5 7.5m6-15l7.5 7.5-7.5 7.5" /></svg>`;

    // First Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, firstIcon, 'Halaman Pertama', 'Halaman Pertama', currentPage <= 1, () => fetchAndDisplayNews(1, filters)));
    // Previous Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, prevIcon, 'Halaman Sebelumnya', 'Halaman Sebelumnya', currentPage <= 1, () => fetchAndDisplayNews(currentPage - 1, filters)));
    // Page Numbers
    generatePageNumbers(currentPage, totalPages).forEach(page_num => {
        if (page_num === null) {
            nav.appendChild(createPaginationElement('span', ellipsisClasses, '...', null, null, true));
        } else if (page_num === currentPage) {
            const el = createPaginationElement('span', currentClasses, page_num, null, `Halaman ${page_num}`, true);
            el.setAttribute('aria-current', 'page');
            nav.appendChild(el);
        } else {
            nav.appendChild(createPaginationElement('button', buttonClasses, page_num, `Ke halaman ${page_num}`, `Ke halaman ${page_num}`, false, () => fetchAndDisplayNews(page_num, filters)));
        }
    });
    // Next Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, nextIcon, 'Halaman Selanjutnya', 'Halaman Selanjutnya', currentPage >= totalPages, () => fetchAndDisplayNews(currentPage + 1, filters)));
    // Last Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, lastIcon, 'Halaman Terakhir', 'Halaman Terakhir', currentPage >= totalPages, () => fetchAndDisplayNews(totalPages, filters)));

    controlsContainer.appendChild(nav);
}

// --- News Fetching and Display ---

// Get current filter values from inputs
function getCurrentFilters() {
    const filters = {
        search: searchInput?.value || '',
        category: categoryFilter?.value || '',
        status: statusFilter?.value || '',
        premium: premiumFilter?.value || '',
        popularity: popularityFilter?.value || '',
        share_count: shareCountFilter?.value || '',
        user: userFilter?.value || '',
        featured_image: filterFeaturedImage?.value || '',
        external_link: filterExternalLink?.value || ''
    };
    // Archived filter logic
    if (archivedFilter) {
        if (archivedFilter.value === 'archived') {
            filters.include_archived = 'true';
            filters.archived = 'true';
        } else if (archivedFilter.value === 'active') {
            filters.include_archived = 'true';
            filters.archived = 'false';
        } else if (archivedFilter.value === '') {
            filters.include_archived = 'true'; // Show all (active + archived)
            // Do not set filters.archived
        }
    }
    return filters;
}

// Fetch and display news with pagination and filters
async function fetchAndDisplayNews(page = 1, filters = null) {
    currentPage = page;
    if (filters === null) {
        filters = getCurrentFilters();
    }

    const newsList = document.getElementById('news-list');
    const paginationControls = document.getElementById('pagination-controls');

    // Show loading state
    if (newsList) newsList.innerHTML = '<p class="col-span-full text-center text-gray-500 py-8">Memuat berita...</p>';
    if (paginationControls) paginationControls.innerHTML = ''; // Clear old controls

    try {
        const url = new URL('/api/news', window.location.origin);
        url.searchParams.append('page', page);
        // Append filter parameters
        for (const [key, value] of Object.entries(filters)) {
            if (value) { // Only append if filter has a value
                url.searchParams.append(key, value);
            }
        }

        console.debug('Fetching news with URL:', url.toString());
        const response = await fetch(url);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to fetch news (Status: ${response.status})`);
        }

        const data = await response.json();
        console.debug('News API response:', data);
        displayNews(data.items); // Display items for the current page
        updatePaginationControls(data); // Generate pagination controls

    } catch (error) {
        console.error('Error fetching news:', error);
        if (newsList) {
            newsList.innerHTML = `<p class="col-span-full text-center text-red-500 py-8">Gagal memuat berita: ${error.message}</p>`;
        }
    }
}

// Debounce fetchNews to prevent rapid API calls
function debounceFetchNews() {
    if (fetchTimeout) {
        clearTimeout(fetchTimeout);
    }
    // Fetch page 1 when filters change
    fetchTimeout = setTimeout(() => fetchAndDisplayNews(1), 300);
}

// Display news based on filters and search
function displayNews(news) {
    const newsList = document.getElementById('news-list');
    if (!newsList) {
        console.error("News list container not found");
        return;
    }
    newsList.innerHTML = '';

    if (!news || news.length === 0) {
        newsList.innerHTML = '<p class="col-span-full text-center text-gray-600 py-8">Tidak ada artikel ditemukan.</p>';
        return;
    }

    news.forEach(article => {
        // --- Thumbnail Logic Start (Admin News Card) ---
        let thumbUrl = '/static/pic/placeholder.png'; // Default placeholder
        if (article.image && article.image.file_url) {
            let imagePath = article.image.file_url;
            if (imagePath.startsWith('http')) {
                const urlParts = new URL(imagePath);
                const staticIndex = urlParts.pathname.indexOf('/static/');
                if (staticIndex !== -1) {
                    imagePath = urlParts.pathname.substring(staticIndex + 1);
                }
            }
            const pathWithoutStatic = imagePath.replace('static/', '', 1);
            const lastDotIndex = pathWithoutStatic.lastIndexOf('.');
            if (lastDotIndex !== -1) {
                const base_path = pathWithoutStatic.substring(0, lastDotIndex);
                const extension = pathWithoutStatic.substring(lastDotIndex);
                thumbUrl = `/static/${base_path}_thumb_square${extension}`;
            } else {
                 thumbUrl = imagePath.startsWith('/') ? imagePath : '/' + imagePath; // Use full path if parsing fails
            }
        }
        // --- End Thumbnail Logic ---
        const categoryName = article.category || 'Tidak ada kategori';
        console.debug(`Artikel ${article.id}: category=${article.category}, category_id=${article.category_id}`);

        const newsCard = document.createElement('div');
        newsCard.className = 'bg-white border border-gray-200 rounded-xl shadow-md hover:shadow-lg transition p-6 flex flex-col sm:flex-row gap-4 relative'; // Responsive layout
        newsCard.innerHTML = `
            <div class="absolute top-4 right-4 z-10">
                <input type="checkbox" class="news-item-checkbox rounded border-gray-300 text-yellow-500 focus:ring-yellow-400" value="${article.id}" onchange="handleNewsItemSelect(this)" aria-label="Pilih artikel ${article.title || 'Tanpa judul'}">
            </div>
            <div class="w-full sm:w-36 h-36 sm:h-auto flex-shrink-0">
                <img src="${thumbUrl}" onerror="this.onerror=null;this.src='/static/pic/placeholder.png'" class="w-full h-full object-cover rounded-lg" alt="Gambar artikel">
            </div>
            <div class="flex flex-col justify-between flex-grow">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-1 pr-8">${article.title || 'Tanpa judul'}</h3>
                    <div class="flex flex-wrap items-center gap-x-2 text-sm text-gray-600 mb-1">
                        <span>${categoryName}</span>
                        ${article.is_news ? '<span class="text-yellow-600 bg-yellow-100 px-2 py-0.5 rounded-full text-xs">Kanal Info</span>' : ''}
                        ${article.is_main_news ? '<span class="text-purple-600 bg-purple-100 px-2 py-0.5 rounded-full text-xs">Utama</span>' : ''}
                    </div>
                    <div class="flex flex-wrap items-center gap-x-2 text-xs text-gray-500 mb-1">
                        <span>${new Date(article.date).toLocaleDateString()}</span>
                        <span class="px-2 py-0.5 rounded-full ${article.is_visible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">${article.is_visible ? 'Terlihat' : 'Tersembunyi'}</span>
                    </div>
                    <div class="flex items-center text-xs text-gray-500">
                        <span><i class="fas fa-eye mr-1"></i> ${article.read_count || 0}</span>
                        <span class="mx-2">|</span>
                        <span><i class="fas fa-share-alt mr-1"></i> ${article.total_shares || 0}</span>
                    </div>
                </div>
                <div class="mt-4 flex space-x-2 justify-end">
                    <button onclick="openEditModal(${article.id})" class="p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-600 rounded-full focus:outline-none focus:ring-2 focus:ring-yellow-300" aria-label="Edit artikel" title="Edit"><i class="fas fa-edit"></i></button>
                    <button onclick="toggleVisibility(${article.id}, ${!article.is_visible})" class="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-300" aria-label="${article.is_visible ? 'Sembunyikan artikel' : 'Tampilkan artikel'}" title="${article.is_visible ? 'Sembunyikan' : 'Tampilkan'}"><i class="fas fa-${article.is_visible ? 'eye-slash' : 'eye'}"></i></button>
                    <button onclick="duplicateNews(${article.id})" class="p-2 bg-green-100 hover:bg-green-200 text-green-600 rounded-full focus:outline-none focus:ring-2 focus:ring-green-300" aria-label="Duplikat artikel" title="Duplikat"><i class="fas fa-copy"></i></button>
                    <button onclick="toggleArchive(${article.id}, ${article.is_archived})" class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-300" aria-label="${article.is_archived ? 'Unarchive' : 'Archive'} artikel" title="${article.is_archived ? 'Unarchive' : 'Archive'}"><i class="fas fa-archive"></i></button>
                    <button onclick="openDeleteModal(${article.id})" class="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-full focus:outline-none focus:ring-2 focus:ring-red-300" aria-label="Hapus artikel" title="Hapus"><i class="fas fa-trash"></i></button>
                </div>
                ${article.is_archived ? '<span class="ml-2 text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">Arsip</span>' : ''}
            </div>
        `;
        newsList.appendChild(newsCard);
    });
}

// --- Category Fetching ---

// Fetch and populate categories
async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) {
            throw new Error(`Failed to fetch categories (Status: ${response.status})`);
        }

        const categories = await response.json();
        console.debug('Categories API response:', categories);
        const editCategoryDropdown = document.getElementById('edit-news-category');
        const filterCategoryDropdown = document.getElementById('category-filter');

        if (!editCategoryDropdown || !filterCategoryDropdown) {
            console.error("Category dropdowns not found");
            return;
        }

        // Update categoryMap (name to id)
        categoryMap = {};
        categories.forEach(category => {
            categoryMap[category.name] = category.id;
        });
        console.debug('Updated categoryMap:', categoryMap);

        editCategoryDropdown.innerHTML = '<option value="" disabled selected>Pilih kategori...</option>';
        filterCategoryDropdown.innerHTML = '<option value="">Semua Kategori</option>'; // Changed default text

        categories.forEach(category => {
            const editOption = document.createElement('option');
            editOption.value = category.id;
            editOption.textContent = category.name;
            editCategoryDropdown.appendChild(editOption);

            const filterOption = document.createElement('option');
            filterOption.value = category.id;
            filterOption.textContent = category.name;
            filterCategoryDropdown.appendChild(filterOption);
        });
    } catch (error) {
        console.error('Error fetching categories:', error);
        const newsList = document.getElementById('news-list');
        if (newsList) {
            newsList.innerHTML = `<p class="text-red-400">Error loading categories: ${error.message}</p>`;
        }
    }
}

// --- SimpleMDE and Modals ---

// Initialize SimpleMDE for edit modal
function initializeSimpleMDE() {
    if (editSimplemde) return; // Prevent re-initialization
    const editElem = document.getElementById("edit-news-content");
    if (!editElem) {
        console.error("Edit news content textarea not found");
        return;
    }
    editSimplemde = new SimpleMDE({
        element: editElem, spellChecker: true, autofocus: true,
        placeholder: "Tulis artikel Anda di sini...",
        autosave: { enabled: true, uniqueId: "edit-news-content-autosave", delay: 1000 },
        toolbar: false, // Use custom toolbar
        renderingConfig: { singleLineBreaks: false, codeSyntaxHighlighting: true },
    });
    // Custom toolbar event bindings
    document.querySelectorAll('#custom-toolbar button[data-cmd]').forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            switch (cmd) {
                case 'bold': SimpleMDE.toggleBold(editSimplemde); break;
                case 'italic': SimpleMDE.toggleItalic(editSimplemde); break;
                case 'heading': SimpleMDE.toggleHeadingSmaller(editSimplemde); break;
                case 'quote': SimpleMDE.toggleBlockquote(editSimplemde); break;
                case 'unordered-list': SimpleMDE.toggleUnorderedList(editSimplemde); break;
                case 'ordered-list': SimpleMDE.toggleOrderedList(editSimplemde); break;
                case 'link': openLinkInsertModal(editSimplemde); break; // Assumes function exists
                case 'image': openImageInsertModalEdit(); break; // Assumes function exists
                case 'preview': SimpleMDE.togglePreview(editSimplemde); break;
                case 'guide': window.open('https://www.markdownguide.org/cheat-sheet/', '_blank'); break;
            }
        });
    });
}

// Open Edit Modal
async function openEditModal(id) {
    currentNewsId = id;
    initializeSimpleMDE();

    try {
        const response = await fetch(`/api/news/${id}`);
        if (!response.ok) throw new Error(`Failed to load article (Status: ${response.status})`);
        const article = await response.json();
        console.debug('Article data for edit:', article);

        // Populate form fields
        document.getElementById('edit-news-id').value = article.id;
        document.getElementById('edit-news-title').value = article.title || '';
        document.getElementById('edit-news-writer').value = article.writer || '';
        document.getElementById('edit-news-tagar').value = article.tagar || '';
        document.getElementById('edit-news-date').value = article.date ? article.date.split('T')[0] : '';
        document.getElementById('edit-news-external-source').value = article.external_source || '';
        document.getElementById('edit-news-image-id').value = article.image ? article.image.id : '';
        document.getElementById('edit-news-premium').checked = article.is_news || false; // Changed from premium to is_news
        document.getElementById('edit-news-main').checked = article.is_main_news || false;
        document.getElementById('edit-news-is-premium').checked = article.is_premium || false;
        
        // Set category (use category_id directly from API response)
        const categoryDropdown = document.getElementById('edit-news-category');
        if (categoryDropdown) {
            const categoryIdToSet = article.category_id;
            console.debug(`Attempting to set category dropdown to ID: ${categoryIdToSet}`);
            // Check if the option actually exists before setting
            if (categoryIdToSet && categoryDropdown.querySelector(`option[value="${categoryIdToSet}"]`)) {
                categoryDropdown.value = categoryIdToSet;
            } else {
                console.warn(`Category ID ${categoryIdToSet} not found in dropdown options or is null/undefined. Setting to default.`);
                categoryDropdown.value = ''; // Set to default/placeholder value
            }
        }
        if (editSimplemde) editSimplemde.value(article.content || '');

        // Sync featured image preview
        const preview = document.getElementById('featured-preview-edit');
        if (preview) {
            if (article.image && article.image.file_url) {
                preview.src = article.image.file_url.startsWith('http') ? article.image.file_url : `/${article.image.file_url}`;
                preview.classList.remove('hidden');
            } else {
                preview.src = ''; // Clear src
                preview.classList.add('hidden');
            }
        }

        document.getElementById('edit-modal')?.classList.remove('hidden');

    } catch (error) {
        console.error('Error loading article:', error);
        showToast('error', `Gagal memuat artikel: ${error.message}`); // Assumes showToast exists
    }
}

// Close Edit Modal
function closeEditModal() {
    document.getElementById('edit-modal')?.classList.add('hidden');
    if (editSimplemde) {
        editSimplemde.clearAutosavedValue();
        // Consider destroying or detaching if performance is an issue
        // editSimplemde.toTextArea();
        // editSimplemde = null;
    }
}

// Open Delete Modal
function openDeleteModal(id) {
    currentNewsId = id;
    document.getElementById('delete-modal')?.classList.remove('hidden');
}

// Close Delete Modal
function closeDeleteModal() {
    document.getElementById('delete-modal')?.classList.add('hidden');
}

// Open Link Insert Modal (Placeholder - adapt if needed)
function openLinkInsertModal(editorInstance) {
    const modal = document.getElementById('link-insert-modal');
    const textInput = document.getElementById('link-text');
    const urlInput = document.getElementById('link-url');
    const insertBtn = document.getElementById('insert-link-btn');
    const cancelBtn = document.getElementById('cancel-link-btn');

    if (!modal || !textInput || !urlInput || !insertBtn || !cancelBtn) return;

    // Pre-fill text if something is selected
    textInput.value = editorInstance.codemirror.getSelection() || '';
    urlInput.value = 'https://';

    const insertHandler = () => {
        const text = textInput.value.trim();
        const url = urlInput.value.trim();
        if (url) {
            editorInstance.codemirror.replaceSelection(`[${text || url}](${url})`);
        }
        closeLinkModal();
    };

    const closeLinkModal = () => {
        modal.classList.add('hidden');
        insertBtn.removeEventListener('click', insertHandler); // Clean up listener
        cancelBtn.removeEventListener('click', closeLinkModal);
    };

    insertBtn.addEventListener('click', insertHandler);
    cancelBtn.addEventListener('click', closeLinkModal);

    modal.classList.remove('hidden');
    urlInput.focus();
}

// Open Image Insert Modal for Editing News (Placeholder - adapt if needed)
function openImageInsertModalEdit() {
    const modal = document.getElementById('image-insert-modal-edit');
    if (!modal) return;
    modal.classList.remove('hidden');
    // Add logic to load library images, handle URL input, etc.
    // Example: Populate library section
    // Fetch the first page of images for the content insert modal
    fetchAndDisplayContentImages(1);

    // Handle radio button toggle
    document.querySelectorAll('input[name="image-source-edit"]').forEach(radio => {
        radio.onchange = (e) => {
            document.getElementById('image-library-section-edit').style.display = e.target.value === 'library' ? 'grid' : 'none';
            document.getElementById('image-url-section-edit').style.display = e.target.value === 'url' ? 'block' : 'none';
        };
    });
    // Trigger change to set initial state
    document.querySelector('input[name="image-source-edit"]:checked').dispatchEvent(new Event('change'));
}

function closeImageInsertModalEdit() {
    document.getElementById('image-insert-modal-edit')?.classList.add('hidden');
}

function insertImageFromUrlEdit(url, alt = '') {
    if (editSimplemde && url) {
        editSimplemde.codemirror.replaceSelection(`![${alt}](${url})`); // Use !alt format
    }
    closeImageInsertModalEdit();
}

// --- CRUD Operations ---

// Edit News Form Submission
const editForm = document.getElementById('edit-news-form');
if (editForm) {
    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const isPublishButton = e.submitter && e.submitter.name === 'publish';
        const data = {
            title: document.getElementById('edit-news-title')?.value.trim() || '',
            content: editSimplemde ? editSimplemde.value().trim() : '',
            tagar: document.getElementById('edit-news-tagar')?.value.trim() || '',
            date: document.getElementById('edit-news-date')?.value || '',
            category: document.getElementById('edit-news-category')?.value || '', // Send category ID
            is_news: document.getElementById('edit-news-premium')?.checked || false, // Changed from premium to is_news
            is_main_news: document.getElementById('edit-news-main')?.checked || false,
            is_premium: document.getElementById('edit-news-is-premium')?.checked || false,
            is_visible: isPublishButton, // Set visibility based on button clicked
            writer: document.getElementById('edit-news-writer')?.value.trim() || '',
            external_source: document.getElementById('edit-news-external-source')?.value.trim() || '',
            image_id: document.getElementById('edit-news-image-id')?.value || ''
        };

        try {
            console.debug('Sending PUT request with data:', data);
            const response = await fetch(`/api/news/${currentNewsId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            const responseData = await response.json();
            if (!response.ok) throw new Error(responseData.error || `Failed to update article (Status: ${response.status})`);

            showToast('success', `Artikel ${isPublishButton ? 'diterbitkan' : 'disimpan sebagai draf'} berhasil!`);
            closeEditModal();
            fetchAndDisplayNews(currentPage); // Refresh current page
        } catch (error) {
            console.error('Error updating article:', error);
            showToast('error', `Gagal memperbarui artikel: ${error.message}`);
        }
    });
}

// Delete Article
const deleteBtn = document.getElementById('confirm-delete-btn');
if (deleteBtn) {
    deleteBtn.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/news/${currentNewsId}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                // Try to parse error if DELETE returns JSON body on failure
                let errorMsg = `Failed to delete article (Status: ${response.status})`;
                try { const errorData = await response.json(); errorMsg = errorData.error || errorMsg; } catch (e) {}
                throw new Error(errorMsg);
            }
            // If response is 204 No Content, response.json() will fail, which is expected on success

            closeDeleteModal();
            // Decide whether to refresh current page or go to page 1
            // Let's refresh current page, but might need adjustment if it becomes empty
            fetchAndDisplayNews(currentPage);
            showToast('success', 'Artikel berhasil dihapus!');
        } catch (error) {
            console.error('Error deleting article:', error);
            showToast('error', `Gagal menghapus artikel: ${error.message}`);
        }
    });
}

// Toggle News Visibility
async function toggleVisibility(newsId, isVisible) {
    try {
        const response = await fetch(`/api/news/${newsId}/visibility`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_visible: isVisible }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to toggle visibility (Status: ${response.status})`);
        }
        fetchAndDisplayNews(currentPage); // Refresh current page
        showToast('success', 'Visibilitas berhasil diubah!');
    } catch (error) {
        console.error('Error toggling visibility:', error);
        showToast('error', `Gagal mengubah visibilitas: ${error.message}`);
    }
}

async function duplicateNews(newsId) {
    try {
        const response = await fetch(`/api/news/${newsId}/duplicate`, {
            method: 'POST',
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Gagal menduplikat artikel');
        showToast('success', 'Artikel berhasil diduplikat!');
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        showToast('error', error.message);
    }
}
async function toggleArchive(newsId, isArchived) {
    try {
        const url = isArchived ? `/api/news/${newsId}/unarchive` : `/api/news/${newsId}/archive`;
        const response = await fetch(url, {
            method: 'PATCH',
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Gagal mengubah status arsip');
        showToast('success', isArchived ? 'Artikel dipulihkan dari arsip!' : 'Artikel diarsipkan!');
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        showToast('error', error.message);
    }
}

// --- Content Image Insert Modal Pagination ---

// Generate pagination controls for the content image insert modal
function updateContentImagePaginationControls(paginationData) {
    const controlsContainer = document.getElementById('content-image-pagination-controls');
    if (!controlsContainer) return;
    controlsContainer.innerHTML = '';

    if (!paginationData || paginationData.total_pages <= 1) return;

    const { page: currentPage, total_pages: totalPages } = paginationData;
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Content Image Pagination');
    // Use smaller buttons/spacing for modal context
    nav.className = 'flex flex-wrap items-center justify-center mt-4 gap-2 overflow-x-auto';

    const buttonClasses = 'button button-outline px-3 py-1 rounded-md hover:bg-primary/10 text-sm';
    const disabledClasses = 'button button-outline px-3 py-1 rounded-md opacity-50 cursor-not-allowed text-sm';
    const currentClasses = 'button button-primary px-3 py-1 rounded-md text-sm';
    const ellipsisClasses = 'h-8 px-1 inline-flex items-center text-muted-foreground text-sm font-medium'; // Match height

    // Simplified Icons for smaller buttons
    const firstIcon = `&laquo;`;
    const prevIcon = `&lsaquo;`;
    const nextIcon = `&rsaquo;`;
    const lastIcon = `&raquo;`;

    // First Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, firstIcon, 'First Page', 'First Page', currentPage <= 1, () => fetchAndDisplayContentImages(1)));
    // Previous Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, prevIcon, 'Previous Page', 'Previous Page', currentPage <= 1, () => fetchAndDisplayContentImages(currentPage - 1)));
    // Page Numbers
    generatePageNumbers(currentPage, totalPages, 1, 1).forEach(page_num => { // Show fewer page numbers
        if (page_num === null) {
            nav.appendChild(createPaginationElement('span', ellipsisClasses, '...', null, null, true));
        } else if (page_num === currentPage) {
            const el = createPaginationElement('span', currentClasses, page_num, null, `Page ${page_num}`, true);
            el.setAttribute('aria-current', 'page');
            nav.appendChild(el);
        } else {
            nav.appendChild(createPaginationElement('button', buttonClasses, page_num, `Go to page ${page_num}`, `Go to page ${page_num}`, false, () => fetchAndDisplayContentImages(page_num)));
        }
    });
    // Next Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, nextIcon, 'Next Page', 'Next Page', currentPage >= totalPages, () => fetchAndDisplayContentImages(currentPage + 1)));
    // Last Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, lastIcon, 'Last Page', 'Last Page', currentPage >= totalPages, () => fetchAndDisplayContentImages(totalPages)));

    controlsContainer.appendChild(nav);
}

// Fetch and display images for the content insert modal
async function fetchAndDisplayContentImages(page = 1) {
    const librarySection = document.getElementById('image-library-section-edit');
    const paginationContainer = document.getElementById('content-image-pagination-controls');
    if (!librarySection || !paginationContainer) return;

    librarySection.innerHTML = '<p class="col-span-full text-center text-gray-500 py-4">Loading images...</p>'; // Placeholder
    paginationContainer.innerHTML = ''; // Clear old pagination

    try {
        const response = await fetch(`/api/images?page=${page}`); // Uses default per_page from API
        if (!response.ok) throw new Error('Failed to load content images');
        const data = await response.json();

        librarySection.innerHTML = data.items.map(img => `
            <div class="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition p-3 flex flex-col gap-2 group cursor-pointer hover:border-yellow-400" onclick="insertImageFromUrlEdit('${img.file_url || img.url}', '${img.filename || ''}')">
                <img src="${img.file_url || img.url}" onerror="this.onerror=null;this.src='/static/pic/placeholder.png'" class="w-full aspect-square object-cover rounded-lg mb-2 shadow-sm group-hover:shadow-md">
                <p class="hidden">${img.filename || 'No name'}</p>
                <button class="select-image-create bg-yellow-500 text-gray-900 py-1 rounded-lg font-semibold">Select</button>
            </div>
        `).join('');
        updateContentImagePaginationControls(data); // Render pagination for this modal
    } catch (err) {
        librarySection.innerHTML = '<p class="col-span-full text-center text-red-500 py-4">Error loading images.</p>';
        console.error("Content image load error:", err);
    }
}


// --- Image Gallery Pagination ---

// Generate pagination controls for the gallery modal
function updateGalleryPaginationControls(paginationData) {
    const controlsContainer = document.getElementById('gallery-pagination-controls');
    if (!controlsContainer) return;
    controlsContainer.innerHTML = '';

    if (!paginationData || paginationData.total_pages <= 1) return;

    const { page: currentPage, total_pages: totalPages } = paginationData;
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Gallery Pagination');
    // Use smaller buttons/spacing for modal context
    nav.className = 'flex flex-wrap items-center justify-center mt-4 gap-2 overflow-x-auto';

    const buttonClasses = 'button button-outline px-3 py-1 rounded-md hover:bg-primary/10 text-sm';
    const disabledClasses = 'button button-outline px-3 py-1 rounded-md opacity-50 cursor-not-allowed text-sm';
    const currentClasses = 'button button-primary px-3 py-1 rounded-md text-sm';
    const ellipsisClasses = 'h-8 px-1 inline-flex items-center text-muted-foreground text-sm font-medium'; // Match height

    // Simplified Icons for smaller buttons
    const firstIcon = `&laquo;`;
    const prevIcon = `&lsaquo;`;
    const nextIcon = `&rsaquo;`;
    const lastIcon = `&raquo;`;

    // First Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, firstIcon, 'First Page', 'First Page', currentPage <= 1, () => fetchAndDisplayGalleryImages(1)));
    // Previous Page
    nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, prevIcon, 'Previous Page', 'Previous Page', currentPage <= 1, () => fetchAndDisplayGalleryImages(currentPage - 1)));
    // Page Numbers
    generatePageNumbers(currentPage, totalPages, 1, 1).forEach(page_num => { // Show fewer page numbers
        if (page_num === null) {
            nav.appendChild(createPaginationElement('span', ellipsisClasses, '...', null, null, true));
        } else if (page_num === currentPage) {
            const el = createPaginationElement('span', currentClasses, page_num, null, `Page ${page_num}`, true);
            el.setAttribute('aria-current', 'page');
            nav.appendChild(el);
        } else {
            nav.appendChild(createPaginationElement('button', buttonClasses, page_num, `Go to page ${page_num}`, `Go to page ${page_num}`, false, () => fetchAndDisplayGalleryImages(page_num)));
        }
    });
    // Next Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, nextIcon, 'Next Page', 'Next Page', currentPage >= totalPages, () => fetchAndDisplayGalleryImages(currentPage + 1)));
    // Last Page
    nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, lastIcon, 'Last Page', 'Last Page', currentPage >= totalPages, () => fetchAndDisplayGalleryImages(totalPages)));

    controlsContainer.appendChild(nav);
}

// Fetch and display images for the gallery modal
async function fetchAndDisplayGalleryImages(page = 1) {
    const galleryContainer = document.getElementById('gallery-images-edit');
    const paginationContainer = document.getElementById('gallery-pagination-controls');
    if (!galleryContainer || !paginationContainer) return;

    galleryContainer.innerHTML = '<p class="col-span-full text-center text-gray-500 py-4">Loading gallery...</p>';
    paginationContainer.innerHTML = ''; // Clear old pagination

    try {
        const response = await fetch(`/api/images?page=${page}`); // Uses default per_page from API
        if (!response.ok) throw new Error('Failed to load gallery images');
        const data = await response.json();

        galleryContainer.innerHTML = data.items.map(img => `
            <div class="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition p-3 flex flex-col gap-2 group cursor-pointer hover:border-yellow-400" onclick="selectImageFromGalleryEdit('${img.id}', '${img.file_url || img.url}')">
                <img src="${img.file_url || img.url}" onerror="this.onerror=null;this.src='/static/pic/placeholder.png'" class="w-full aspect-square object-cover rounded-lg mb-2 shadow-sm group-hover:shadow-md">
                <p class="hidden">${img.filename || 'No name'}</p>
                <button class="select-image-create bg-yellow-500 text-gray-900 py-1 rounded-lg font-semibold">Select</button>
            </div>
        `).join('');
        updateGalleryPaginationControls(data); // Render pagination
    } catch (err) {
        galleryContainer.innerHTML = '<p class="col-span-full text-center text-red-500 py-4">Error loading gallery.</p>';
        console.error("Gallery load error:", err);
    }
}


// Open Image Gallery for Edit Modal (Placeholder - adapt if needed)
function openImageGalleryEdit() {
    const modal = document.getElementById('image-gallery-modal-edit');
    modal.classList.remove('hidden');
    // Load images into #gallery-images-edit
    const galleryContainer = document.getElementById('gallery-images-edit');
    // Fetch the first page of images initially
    fetchAndDisplayGalleryImages(1);
}

function closeImageGalleryEdit() {
    document.getElementById('image-gallery-modal-edit')?.classList.add('hidden');
}

function selectImageFromGalleryEdit(imageId, imageUrl) {
    document.getElementById('edit-news-image-id').value = imageId;
    const preview = document.getElementById('featured-preview-edit');
    if (preview) {
        preview.src = imageUrl;
        preview.classList.remove('hidden');
    }
    closeImageGalleryEdit();
}

// Clear Featured Image Button Logic (Edit Modal)
const clearEditBtn = document.getElementById('clear-featured-image-edit-btn');
if (clearEditBtn) {
    clearEditBtn.addEventListener('click', () => {
        document.getElementById('edit-news-image-id').value = ''; // Clear the hidden input
        const preview = document.getElementById('featured-preview-edit');
        if (preview) {
            preview.src = ''; // Clear the preview source
            preview.classList.add('hidden'); // Hide the preview
        }
        showToast('info', 'Gambar unggulan dihapus.');
    });
}

// Upload inside Edit Gallery Modal (Placeholder - adapt if needed)
const editUploadBtn = document.getElementById('edit-upload-btn');
if (editUploadBtn) {
    editUploadBtn.addEventListener('click', async () => {
        // Add logic to handle file/URL upload similar to image-crud.js
        console.warn('Upload inside gallery not fully implemented yet.');
        // On success, call openImageGalleryEdit() to refresh the gallery
    });
}

// Bulk archive/unarchive
const bulkArchiveBtn = document.getElementById('bulk-archive');
if (bulkArchiveBtn) {
    bulkArchiveBtn.addEventListener('click', async () => {
        if (selectedNewsIds.size === 0) { showToast('warning', 'Tidak ada artikel yang dipilih'); return; }
        await bulkArchiveUnarchive(true);
    });
}
const bulkUnarchiveBtn = document.getElementById('bulk-unarchive');
if (bulkUnarchiveBtn) {
    bulkUnarchiveBtn.addEventListener('click', async () => {
        if (selectedNewsIds.size === 0) { showToast('warning', 'Tidak ada artikel yang dipilih'); return; }
        await bulkArchiveUnarchive(false);
    });
}
async function bulkArchiveUnarchive(archive = true) {
    try {
        const url = archive ? '/api/news/bulk-archive' : '/api/news/bulk-unarchive';
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: Array.from(selectedNewsIds) })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Gagal mengubah status arsip massal');
        showToast('success', data.message || (archive ? 'Artikel diarsipkan!' : 'Artikel dipulihkan dari arsip!'));
        selectedNewsIds.clear();
        updateBulkActionsBar();
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        showToast('error', error.message);
    }
}

// --- Initialization ---

document.addEventListener('DOMContentLoaded', async () => {
    const newsListContainer = document.getElementById('news-list');
    if (newsListContainer) {
        // Add event listeners to filters
        [searchInput, categoryFilter, statusFilter, premiumFilter, popularityFilter, shareCountFilter, userFilter, filterFeaturedImage, filterExternalLink, archivedFilter].forEach(el => { // Added new filters
            if (el) {
                el.addEventListener(el.id === 'search' ? 'input' : 'change', debounceFetchNews);
            }
        });

        // Show user filter for superuser or admin (assuming this logic is correct)
        // This should ideally be controlled by a variable passed from the template if needed
        // if (isUserAdminOrSuperuser) { // Replace with actual check if available
        //     if (userFilter) userFilter.parentElement.style.display = 'block';
        // }

        // Fetch categories first, then initial news data
        await fetchCategories();
        await fetchAndDisplayNews(1); // Fetch page 1 on load

        // Attach listeners for modal close buttons (if not handled by inline onclick)
        document.querySelector('#edit-modal button[onclick="closeEditModal()"]')?.addEventListener('click', closeEditModal);
        document.querySelector('#delete-modal button[onclick="closeDeleteModal()"]')?.addEventListener('click', closeDeleteModal);
        document.getElementById('close-image-insert-edit')?.addEventListener('click', closeImageInsertModalEdit);
        document.querySelector('#image-gallery-modal-edit button[onclick="closeImageGalleryEdit()"]')?.addEventListener('click', closeImageGalleryEdit);
        document.getElementById('cancel-link-btn')?.addEventListener('click', () => document.getElementById('link-insert-modal')?.classList.add('hidden'));

        // Initialize bulk operations
        initBulkOperations();

    } else {
        console.error("News list container (#news-list) not found. Cannot initialize news management.");
    }
});

// ==================== BULK OPERATIONS ====================

let selectedNewsIds = new Set();

function initBulkOperations() {
    // Select All checkbox
    const selectAllCheckbox = document.getElementById('select-all-news');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', handleSelectAll);
    }

    // Bulk action buttons
    const bulkDeleteBtn = document.getElementById('bulk-delete');
    const bulkToggleVisibilityBtn = document.getElementById('bulk-toggle-visibility');
    const bulkCategorySelect = document.getElementById('bulk-category-select');

    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', handleBulkDelete);
    }

    if (bulkToggleVisibilityBtn) {
        bulkToggleVisibilityBtn.addEventListener('click', handleBulkToggleVisibility);
    }

    if (bulkCategorySelect) {
        bulkCategorySelect.addEventListener('change', handleBulkCategoryChange);
        // Populate categories
        populateBulkCategorySelect();
    }

    // Bulk delete modal
    const cancelBulkDeleteBtn = document.getElementById('cancel-bulk-delete-btn');
    const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');

    if (cancelBulkDeleteBtn) {
        cancelBulkDeleteBtn.addEventListener('click', closeBulkDeleteModal);
    }

    if (confirmBulkDeleteBtn) {
        confirmBulkDeleteBtn.addEventListener('click', confirmBulkDelete);
    }
}

function handleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all-news');
    const newsCheckboxes = document.querySelectorAll('.news-item-checkbox');
    
    if (selectAllCheckbox.checked) {
        // Select all
        newsCheckboxes.forEach(checkbox => {
            checkbox.checked = true;
            selectedNewsIds.add(parseInt(checkbox.value));
        });
    } else {
        // Deselect all
        newsCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        selectedNewsIds.clear();
    }
    
    updateBulkActionsBar();
}

function handleNewsItemSelect(checkbox) {
    const newsId = parseInt(checkbox.value);
    
    if (checkbox.checked) {
        selectedNewsIds.add(newsId);
    } else {
        selectedNewsIds.delete(newsId);
        // Uncheck select all if not all items are selected
        const selectAllCheckbox = document.getElementById('select-all-news');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = false;
        }
    }
    
    updateBulkActionsBar();
}

function updateBulkActionsBar() {
    const bulkActionsBar = document.getElementById('bulk-actions-bar');
    const selectedCountSpan = document.getElementById('selected-count');
    const selectAllCheckbox = document.getElementById('select-all-news');
    
    if (selectedNewsIds.size > 0) {
        bulkActionsBar?.classList.remove('hidden');
        if (selectedCountSpan) {
            selectedCountSpan.textContent = `${selectedNewsIds.size} dipilih`;
        }
    } else {
        bulkActionsBar?.classList.add('hidden');
    }
    
    // Update select all checkbox state
    const newsCheckboxes = document.querySelectorAll('.news-item-checkbox');
    const totalItems = newsCheckboxes.length;
    const selectedItems = selectedNewsIds.size;
    
    if (selectAllCheckbox && totalItems > 0) {
        if (selectedItems === totalItems) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedItems > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }
}

function populateBulkCategorySelect() {
    const bulkCategorySelect = document.getElementById('bulk-category-select');
    if (!bulkCategorySelect) return;
    
    // Clear existing options except the first one
    while (bulkCategorySelect.children.length > 1) {
        bulkCategorySelect.removeChild(bulkCategorySelect.lastChild);
    }
    
    // Add categories from the global categoryMap
    Object.entries(categoryMap).forEach(([categoryName, categoryId]) => {
        const option = document.createElement('option');
        option.value = categoryId;
        option.textContent = categoryName;
        bulkCategorySelect.appendChild(option);
    });
}

async function handleBulkDelete() {
    if (selectedNewsIds.size === 0) {
        showToast('warning', 'Tidak ada artikel yang dipilih');
        return;
    }
    
    const bulkDeleteCount = document.getElementById('bulk-delete-count');
    if (bulkDeleteCount) {
        bulkDeleteCount.textContent = selectedNewsIds.size;
    }
    
    const bulkDeleteModal = document.getElementById('bulk-delete-modal');
    if (bulkDeleteModal) {
        bulkDeleteModal.classList.remove('hidden');
    }
}

function closeBulkDeleteModal() {
    const bulkDeleteModal = document.getElementById('bulk-delete-modal');
    if (bulkDeleteModal) {
        bulkDeleteModal.classList.add('hidden');
    }
}

async function confirmBulkDelete() {
    if (selectedNewsIds.size === 0) return;
    try {
        const response = await fetch('/api/news/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: Array.from(selectedNewsIds) })
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Gagal menghapus artikel (Status: ${response.status})`);
        }
        const result = await response.json();
        showToast('success', result.message || 'Artikel berhasil dihapus');
        // Clear selections and refresh
        selectedNewsIds.clear();
        updateBulkActionsBar();
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        console.error('Bulk delete error:', error);
        showToast('error', error.message || 'Terjadi kesalahan saat menghapus artikel');
    } finally {
        closeBulkDeleteModal();
    }
}

async function handleBulkToggleVisibility() {
    if (selectedNewsIds.size === 0) {
        showToast('warning', 'Tidak ada artikel yang dipilih');
        return;
    }
    // Show the styled modal
    const modal = document.getElementById('bulk-visibility-modal');
    const countSpan = document.getElementById('bulk-visibility-count');
    const showBtn = document.getElementById('bulk-visibility-show-btn');
    const hideBtn = document.getElementById('bulk-visibility-hide-btn');
    const cancelBtn = document.getElementById('cancel-bulk-visibility-btn');
    if (!modal || !countSpan || !showBtn || !hideBtn || !cancelBtn) return;
    countSpan.textContent = selectedNewsIds.size;
    modal.classList.remove('hidden');

    // Remove previous listeners to avoid stacking
    showBtn.onclick = null;
    hideBtn.onclick = null;
    cancelBtn.onclick = null;

    showBtn.onclick = () => bulkSetVisibility(true);
    hideBtn.onclick = () => bulkSetVisibility(false);
    cancelBtn.onclick = () => modal.classList.add('hidden');
}

async function bulkSetVisibility(isVisible) {
    const modal = document.getElementById('bulk-visibility-modal');
    try {
        const response = await fetch('/api/news/bulk-visibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: Array.from(selectedNewsIds), is_visible: isVisible })
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Gagal memperbarui visibilitas (Status: ${response.status})`);
        }
        const result = await response.json();
        showToast('success', result.message || 'Visibilitas artikel berhasil diperbarui');
        // Clear selections and refresh
        selectedNewsIds.clear();
        updateBulkActionsBar();
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        console.error('Bulk toggle visibility error:', error);
        showToast('error', error.message || 'Terjadi kesalahan saat memperbarui visibilitas');
    } finally {
        if (modal) modal.classList.add('hidden');
    }
}

async function handleBulkCategoryChange() {
    const bulkCategorySelect = document.getElementById('bulk-category-select');
    const categoryId = bulkCategorySelect?.value;
    if (!categoryId || selectedNewsIds.size === 0) {
        bulkCategorySelect.value = ''; // Reset selection
        return;
    }
    // Show the styled modal
    const modal = document.getElementById('bulk-category-modal');
    const countSpan = document.getElementById('bulk-category-count');
    const nameSpan = document.getElementById('bulk-category-name');
    const confirmBtn = document.getElementById('confirm-bulk-category-btn');
    const cancelBtn = document.getElementById('cancel-bulk-category-btn');
    if (!modal || !countSpan || !nameSpan || !confirmBtn || !cancelBtn) return;
    countSpan.textContent = selectedNewsIds.size;
    // Find the category name from the select options
    const selectedOption = bulkCategorySelect.options[bulkCategorySelect.selectedIndex];
    nameSpan.textContent = selectedOption ? selectedOption.textContent : '-';
    modal.classList.remove('hidden');

    // Remove previous listeners to avoid stacking
    confirmBtn.onclick = null;
    cancelBtn.onclick = null;

    confirmBtn.onclick = async () => {
        await bulkSetCategory(categoryId, modal, bulkCategorySelect);
    };
    cancelBtn.onclick = () => {
        modal.classList.add('hidden');
        bulkCategorySelect.value = '';
    };
}

async function bulkSetCategory(categoryId, modal, bulkCategorySelect) {
    try {
        const response = await fetch('/api/news/bulk-category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: Array.from(selectedNewsIds), category_id: parseInt(categoryId) })
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Gagal memperbarui kategori (Status: ${response.status})`);
        }
        const result = await response.json();
        showToast('success', result.message || 'Kategori artikel berhasil diperbarui');
        // Clear selections and refresh
        selectedNewsIds.clear();
        updateBulkActionsBar();
        await fetchAndDisplayNews(currentPage);
    } catch (error) {
        console.error('Bulk category change error:', error);
        showToast('error', error.message || 'Terjadi kesalahan saat memperbarui kategori');
    } finally {
        if (modal) modal.classList.add('hidden');
        if (bulkCategorySelect) bulkCategorySelect.value = '';
    }
}
