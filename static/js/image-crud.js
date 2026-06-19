let currentImageId = null;
let currentPage = 1; // Keep track of the current page

// Filter elements
const filterVisibility = document.getElementById('filter-visibility');
const filterDescription = document.getElementById('filter-description');
const filterUsage = document.getElementById('filter-usage');

// --- Modal Elements & State ---
const imageManagementModal = document.getElementById('image-management-modal');
const modalImageMgmt = document.getElementById('modal-image-mgmt');
const modalDownloadMgmt = document.getElementById('modal-download-mgmt');
const modalPrevMgmt = document.getElementById('modal-prev-mgmt');
const modalNextMgmt = document.getElementById('modal-next-mgmt');
let currentModalImageIndex = -1;
let galleryImagesDataMgmt = [];

// --- Bulk Selection State ---
let selectedImageIds = new Set();

// --- Bulk Selection UI Logic ---
function updateBulkActionsBarImg() {
    const bar = document.getElementById('bulk-actions-bar-img');
    if (!bar) return;
    if (selectedImageIds.size > 0) {
        bar.classList.remove('hidden');
        document.getElementById('bulk-img-count').textContent = selectedImageIds.size;
    } else {
        bar.classList.add('hidden');
    }
}

function handleSelectAllImages(checked) {
    const checkboxes = document.querySelectorAll('.image-select-checkbox');
    selectedImageIds = new Set();
    checkboxes.forEach(cb => {
        cb.checked = checked;
        if (checked) selectedImageIds.add(Number(cb.value));
    });
    updateBulkActionsBarImg();
}

function handleImageCheckboxChange(e) {
    const id = Number(e.target.value);
    if (e.target.checked) {
        selectedImageIds.add(id);
    } else {
        selectedImageIds.delete(id);
    }
    updateBulkActionsBarImg();
}

// Display images in the grid
function displayImages(images) {
    const imageGrid = document.getElementById('image-grid');
    if (!imageGrid) {
        console.error("Image grid container not found!");
        return;
    }
    imageGrid.innerHTML = ''; // Clear existing images

    galleryImagesDataMgmt = []; // Clear old gallery data before rendering
    if (!images || images.length === 0) {
        imageGrid.innerHTML = '<p class="col-span-full text-center text-gray-500 py-8">Tidak ada gambar ditemukan.</p>';
        return;
    }

    images.forEach((image, index) => { // Add 'index' as the second argument here
        // --- Thumbnail Logic Start (Admin Image Card) ---
        let thumbUrl = '/static/pic/placeholder.png'; // Default placeholder
        const fullImageUrl = image.file_url || image.url || '/static/pic/placeholder.png'; // Keep full URL for potential future use (like modal)

        if (image.filepath) { // Use filepath to construct thumb path
            // Assuming filepath is like 'static/uploads/timestamp_filename.webp'
            const pathWithoutStatic = image.filepath.replace('static/', '', 1);
            const lastDotIndex = pathWithoutStatic.lastIndexOf('.');
            if (lastDotIndex !== -1) {
                const base_path = pathWithoutStatic.substring(0, lastDotIndex);
                const extension = pathWithoutStatic.substring(lastDotIndex);
                // Construct the square thumbnail path
                thumbUrl = `/static/${base_path}_thumb_square${extension}`;
            } else {
                // Fallback to full image URL if path parsing fails
                thumbUrl = fullImageUrl;
            }
        } else {
            // If no filepath, just use the provided URL (might be external)
            thumbUrl = fullImageUrl;
        }
        // --- End Thumbnail Logic ---

        // Store data for the modal
        galleryImagesDataMgmt.push({
            index: index,
            largeSrc: fullImageUrl,
            description: image.description || image.filename || 'Gambar Galeri',
            filename: image.filename || 'download.jpg'
        });

        const imageCard = document.createElement('div');
        // Adjusted classes for a smaller, cleaner look
        imageCard.className = 'bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition group p-4 flex flex-col gap-3';
        // Removed onclick from the card itself
        // imageCard.setAttribute('title', image.description || image.filename || 'Lihat gambar'); // Title moved to image
        imageCard.innerHTML = `
            <img src="${thumbUrl}" onerror="this.onerror=null;this.src='/static/pic/placeholder.png'" class="w-full aspect-square object-cover rounded-md cursor-pointer" alt="${image.description || image.filename || 'Gambar'}" onclick="openImageModalMgmt(${index})" title="${image.description || image.filename || 'Lihat gambar'}">
            <div class="flex flex-col flex-grow">
                <p class="text-sm font-semibold text-gray-800 truncate mb-1" title="${image.filename || 'No filename'}">${image.filename || 'No filename'}</p>
                <p class="text-xs text-gray-500 truncate mb-3" title="${image.description || 'No description'}">${image.description || 'No description'}</p>
                <div class="mt-auto flex justify-between items-center">
                    <span class="px-2 py-1 text-xs font-medium rounded-full ${image.is_visible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${image.is_visible ? 'Visible' : 'Hidden'}
                    </span>
                    <div class="flex space-x-1">
                        <button onclick="event.stopPropagation(); openEditModal(${image.id})" class="p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-300" aria-label="Edit image" title="Edit"><i class="fas fa-edit"></i></button>
                        <button onclick="event.stopPropagation(); toggleVisibility(${image.id}, ${!image.is_visible})" class="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300" aria-label="${image.is_visible ? 'Hide image' : 'Show image'}" title="${image.is_visible ? 'Hide' : 'Show'}"><i class="fas fa-${image.is_visible ? 'eye-slash' : 'eye'}"></i></button>
                        <button onclick="event.stopPropagation(); openDeleteModal(${image.id})" class="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-300" aria-label="Delete image" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            </div>
        `;
        imageGrid.appendChild(imageCard);
    });

    console.log("Collected image data for modal:", galleryImagesDataMgmt); // Debug log
}

// Patch displayImages to render checkboxes and usage button
const originalDisplayImages = displayImages;
displayImages = function(images) {
    originalDisplayImages(images);
    // Add checkboxes and usage button to each image card
    const imageGrid = document.getElementById('image-grid');
    if (!imageGrid) return;
    const cards = imageGrid.querySelectorAll('.bg-white.border');
    images.forEach((image, idx) => {
        const card = cards[idx];
        if (!card) return;
        // Prevent duplicate checkboxes
        if (!card.querySelector('.image-select-checkbox')) {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'image-select-checkbox rounded border-gray-300 text-yellow-500 focus:ring-yellow-400 mr-2';
            checkbox.value = image.id;
            checkbox.checked = selectedImageIds.has(image.id);
            checkbox.addEventListener('change', handleImageCheckboxChange);
            card.insertBefore(checkbox, card.firstChild);
        }
        // Add Usage button if not present
        if (!card.querySelector('.usage-btn')) {
            const usageBtn = document.createElement('button');
            usageBtn.type = 'button';
            usageBtn.className = 'usage-btn ml-auto px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-300';
            usageBtn.textContent = 'Usage';
            usageBtn.onclick = () => openUsageModal(image.id, image.filename);
            // Place at the bottom right of the card
            card.appendChild(usageBtn);
        }
    });
    // Update select all state
    const selectAll = document.getElementById('select-all-images');
    if (selectAll) {
        selectAll.checked = images.length > 0 && images.every(img => selectedImageIds.has(img.id));
    }
    updateBulkActionsBarImg();
    // Re-attach bulk action button listeners
    const bulkDeleteBtnImg = document.getElementById('bulk-delete-btn-img');
    const bulkVisibilityBtnImg = document.getElementById('bulk-visibility-btn-img');
    if (bulkDeleteBtnImg) {
        bulkDeleteBtnImg.onclick = handleBulkDeleteImages;
    }
    if (bulkVisibilityBtnImg) {
        bulkVisibilityBtnImg.onclick = handleBulkToggleVisibilityImages;
    }
};

// Select all checkbox event
const selectAllImages = document.getElementById('select-all-images');
if (selectAllImages) {
    selectAllImages.addEventListener('change', e => handleSelectAllImages(e.target.checked));
}

// Helper function to generate page numbers like Flask-SQLAlchemy's iter_pages
// (Simplified version for demonstration)
function generatePageNumbers(currentPage, totalPages, edgeCount = 1, currentCount = 2) {
    if (totalPages <= 1) return [];

    const pages = new Set();
    // Add edge pages
    for (let i = 1; i <= Math.min(edgeCount, totalPages); i++) pages.add(i);
    for (let i = Math.max(1, totalPages - edgeCount + 1); i <= totalPages; i++) pages.add(i);

    // Add pages around current page
    for (let i = Math.max(1, currentPage - currentCount); i <= Math.min(totalPages, currentPage + currentCount); i++) pages.add(i);

    const sortedPages = Array.from(pages).sort((a, b) => a - b);
    const result = [];
    let lastPage = 0;

    for (const page of sortedPages) {
        if (page > lastPage + 1) {
            result.push(null); // Represents ellipsis '...'
        }
        result.push(page);
        lastPage = page;
    }
    return result;
}

// Helper to create a pagination button/link/span
function createPaginationElement(tag, classes, content, ariaLabel = null, title = null, disabled = false, onClick = null) {
    const el = document.createElement(tag);
    el.className = classes;
    el.innerHTML = content; // Use innerHTML to allow SVG content
    if (ariaLabel) el.setAttribute('aria-label', ariaLabel);
    if (title) el.title = title;
    if (disabled) el.setAttribute('aria-disabled', 'true');
    if (onClick && !disabled) el.onclick = () => onClick(); // Wrap onClick to ensure it's called correctly
    return el;
}

// Generate pagination controls dynamically
function updatePaginationControls(paginationData) {
    const controlsContainer = document.getElementById('pagination-controls');
    if (!controlsContainer) return;

    controlsContainer.innerHTML = ''; // Clear existing controls

    if (!paginationData || paginationData.total_pages <= 1) {
        return; // No controls needed for 0 or 1 page
    }

    const { page: currentPage, total_pages: totalPages } = paginationData;

    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Pagination');
    // Use classes from pagination.html
    nav.className = 'flex flex-wrap items-center justify-center mt-8 sm:mt-12 lg:mt-16 gap-2 sm:gap-4 md:gap-6 overflow-x-auto';

    // Get current filter values to preserve them in pagination links
    const currentVisibility = filterVisibility ? filterVisibility.value : 'all';
    const currentDescription = filterDescription ? filterDescription.value : 'all';
    const currentUsage = filterUsage ? filterUsage.value : 'all';

    const buttonClasses = 'button button-outline px-2 py-1 sm:px-4 sm:py-2 rounded-md hover:bg-primary/10';
    const disabledClasses = 'button button-outline px-2 py-1 sm:px-4 sm:py-2 rounded-md opacity-50 cursor-not-allowed';
    const currentClasses = 'button button-primary px-2 py-1 sm:px-4 sm:py-2 rounded-md';
    const ellipsisClasses = 'h-10 px-2 inline-flex items-center text-muted-foreground text-base font-medium'; // Match height roughly

    const firstIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" /></svg>`;
    const prevIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>`;
    const nextIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>`;
    const lastIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 4.5l7.5 7.5-7.5 7.5m6-15l7.5 7.5-7.5 7.5" /></svg>`;

    // First Page Button
    nav.appendChild(createPaginationElement(
        currentPage > 1 ? 'button' : 'span',
        currentPage > 1 ? buttonClasses : disabledClasses,
        firstIcon,
        'Halaman Pertama', 'Halaman Pertama', currentPage <= 1,
        () => fetchAndDisplayImages(1, currentVisibility, currentDescription, currentUsage) // Pass filters
    ));

    // Previous Page Button
    nav.appendChild(createPaginationElement(
        currentPage > 1 ? 'button' : 'span',
        currentPage > 1 ? buttonClasses : disabledClasses,
        prevIcon,
        'Halaman Sebelumnya', 'Halaman Sebelumnya', currentPage <= 1,
        () => fetchAndDisplayImages(currentPage - 1, currentVisibility, currentDescription, currentUsage) // Pass filters
    ));

    // Page Numbers
    const pageNumbers = generatePageNumbers(currentPage, totalPages);
    pageNumbers.forEach(page_num => {
        if (page_num === null) {
            nav.appendChild(createPaginationElement('span', ellipsisClasses, '...', null, null, true));
        } else if (page_num === currentPage) {
            nav.appendChild(createPaginationElement('span', currentClasses, page_num, null, `Halaman ${page_num}`, true));
            nav.lastChild.setAttribute('aria-current', 'page');
        } else {
            nav.appendChild(createPaginationElement(
                'button', buttonClasses, page_num,
                `Ke halaman ${page_num}`, `Ke halaman ${page_num}`, false,
                () => fetchAndDisplayImages(page_num, currentVisibility, currentDescription, currentUsage) // Pass filters
            ));
        }
    });

    // Next Page Button
    nav.appendChild(createPaginationElement(
        currentPage < totalPages ? 'button' : 'span',
        currentPage < totalPages ? buttonClasses : disabledClasses,
        nextIcon,
        'Halaman Selanjutnya', 'Halaman Selanjutnya', currentPage >= totalPages,
        () => fetchAndDisplayImages(currentPage + 1, currentVisibility, currentDescription, currentUsage) // Pass filters
    ));

    // Last Page Button
    nav.appendChild(createPaginationElement(
        currentPage < totalPages ? 'button' : 'span',
        currentPage < totalPages ? buttonClasses : disabledClasses,
        lastIcon,
        'Halaman Terakhir', 'Halaman Terakhir', currentPage >= totalPages,
        () => fetchAndDisplayImages(totalPages, currentVisibility, currentDescription, currentUsage) // Pass filters
    ));

    controlsContainer.appendChild(nav);
}

// Fetch images and then display them
async function fetchAndDisplayImages(page = 1, visibility = 'all', description = 'all', usage = 'all') {
    visibility = filterVisibility ? filterVisibility.value : visibility;
    description = filterDescription ? filterDescription.value : description;
    usage = filterUsage ? filterUsage.value : usage;

    currentPage = page;
    const imageGrid = document.getElementById('image-grid');
    const controlsContainer = document.getElementById('pagination-controls');

    if (imageGrid) imageGrid.innerHTML = '<p class="col-span-full text-center text-gray-500 py-8">Loading images...</p>';
    if (controlsContainer) controlsContainer.innerHTML = '';

    try {
        const apiUrl = new URL('/api/images', window.location.origin);
        apiUrl.searchParams.append('page', page);
        apiUrl.searchParams.append('visibility', visibility);
        apiUrl.searchParams.append('description', description);
        apiUrl.searchParams.append('usage', usage);

        const response = await fetch(apiUrl.toString());
        if (!response.ok) {
            throw new Error('Failed to fetch images');
        }
        const data = await response.json();
        displayImages(data.items);
        updatePaginationControls(data);
    } catch (error) {
        console.error('Error fetching images:', error);
        if (imageGrid) imageGrid.innerHTML = '<p class="col-span-full text-center text-red-500 py-8">Failed to load images.</p>';
    }
}

// Add Image
document.getElementById('add-image-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('name', document.getElementById('image-name').value || '');
    formData.append('description', document.getElementById('image-description').value || '');
    formData.append('file', document.getElementById('image-file').files[0]);
    formData.append('url', document.getElementById('image-url').value || '');

    try {
        const response = await fetch('/api/images', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error('Failed to upload image');

        showToast('success', 'Image uploaded successfully!');
        fetchAndDisplayImages(1); // Refresh the image grid, go to page 1
        document.getElementById('add-image-form').reset();
    } catch (error) {
        console.error(error);
        showToast('error', `Failed to upload image: ${error.message}`);
    }
});

// Open Edit Modal
async function openEditModal(id) {
    currentImageId = id;
    try {
        const response = await fetch(`/api/images/${id}`);
        if (!response.ok) {
            throw new Error('Failed to fetch image details for editing');
        }
        const image = await response.json();

        document.getElementById('edit-id').value = image.id;
        document.getElementById('edit-image-name').value = image.filename || '';
        document.getElementById('edit-image-description').value = image.description || '';
        // Reset file/url inputs
        document.getElementById('edit-image-file').value = '';
        document.getElementById('edit-image-url').value = '';
        // You might want to show the current image preview here if needed

    } catch (error) {
        showToast('error', `Error loading image details: ${error.message}`);
    }
    document.getElementById('edit-modal').classList.remove('hidden');
}

// Close Edit Modal
function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
}

// Edit Image
document.getElementById('edit-image-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const editFile = document.getElementById('edit-image-file').files[0];
    const editUrl = document.getElementById('edit-image-url').value.trim();

    // Validation: Ensure either file or URL is provided if source is changed
    // (Backend should handle validation if no new source is provided)
    // if (!editFile && !editUrl) {
    //     showToast('warning', 'Please provide a new image file or URL to update.');
    //     return;
    // }

    const formData = new FormData();
    formData.append('name', document.getElementById('edit-image-name').value || '');
    formData.append('description', document.getElementById('edit-image-description').value || '');

    try {
        const response = await fetch(`/api/images/${currentImageId}`, {
            method: 'PUT',
            body: formData,
        });

        if (!response.ok) throw new Error('Failed to update image');

        showToast('success', 'Image updated successfully!');
        fetchAndDisplayImages(currentPage); // Refresh the current page
        setTimeout(() => closeEditModal(), 1500);
    } catch (error) {
        console.error(error);
        showToast('error', `Failed to update image: ${error.message}`);
    }
});

// Open Delete Modal
function openDeleteModal(id) {
    currentImageId = id;
    document.getElementById('delete-modal').classList.remove('hidden');
}

// Close Delete Modal
function closeDeleteModal() {
    document.getElementById('delete-modal').classList.add('hidden');
}

// Confirm Delete
async function confirmDelete() {
    try {
        const response = await fetch(`/api/images/${currentImageId}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Failed to delete image');

        showToast('success', 'Image deleted successfully!');
        fetchAndDisplayImages(currentPage); // Refresh the current page
        closeDeleteModal();
    } catch (error) {
        console.error(error);
        showToast('error', `Failed to delete image: ${error.message}`);
    }
}

// Toggle Visibility
async function toggleVisibility(id, isVisible) {
    try {
        const response = await fetch(`/api/images/${id}/visibility`, {
            method: 'PATCH',
            body: JSON.stringify({ is_visible: isVisible }),
        });

        if (!response.ok) {
            throw new Error('Failed to toggle visibility');
        }

        // Refresh the image grid after toggling visibility
        fetchAndDisplayImages(currentPage); // Refresh the current page
        showToast('success', isVisible ? 'Gambar ditampilkan!' : 'Gambar tersembunyi!');
    } catch (error) {
        console.error(error);
        showToast('error', 'Failed to toggle visibility');
    }
}

// --- Image Management Modal Logic ---

function openImageModalMgmt(index) {
    if (!imageManagementModal || !modalImageMgmt || !modalDownloadMgmt || !modalPrevMgmt || !modalNextMgmt) {
        console.error("Modal elements for image management not found.");
        return;
    }
    if (index < 0 || index >= galleryImagesDataMgmt.length) {
        console.error(`Invalid image index requested: ${index}. Available: 0-${galleryImagesDataMgmt.length - 1}`);
        return;
    }

    currentModalImageIndex = index;
    const imageData = galleryImagesDataMgmt[currentModalImageIndex];

    if (!imageData) {
        console.error(`Image data unexpectedly not found for index: ${index}`);
        return;
    }

    // Update modal content
    modalImageMgmt.src = imageData.largeSrc;
    modalImageMgmt.alt = imageData.description;
    modalDownloadMgmt.href = imageData.largeSrc;
    modalDownloadMgmt.download = imageData.filename;

    // Update navigation buttons state
    modalPrevMgmt.disabled = currentModalImageIndex === 0;
    modalNextMgmt.disabled = currentModalImageIndex === galleryImagesDataMgmt.length - 1;

    // Show modal with fade effect
    imageManagementModal.classList.remove('hidden');
    requestAnimationFrame(() => {
        imageManagementModal.classList.add('opacity-100');
    });
    document.body.style.overflow = 'hidden'; // Prevent body scroll
    console.log(`Opened management modal for image index: ${currentModalImageIndex}`);
}

// Make close function global for onclick attribute and Escape key
window.closeImageModalMgmt = function() {
    if (!imageManagementModal) return;
    imageManagementModal.classList.remove('opacity-100');
    setTimeout(() => {
        imageManagementModal.classList.add('hidden');
        if (modalImageMgmt) modalImageMgmt.src = ""; // Clear image src
    }, 300); // Match transition duration
    document.body.style.overflow = ''; // Restore body scroll
    console.log("Closed management image modal.");
}

// Make global for backdrop click
window.closeImageModalMgmtOnClickOutside = function(event) {
    if (imageManagementModal && event.target === imageManagementModal) {
        closeImageModalMgmt();
    }
}

// Make global for button clicks
window.showNextImageMgmt = function() {
    if (currentModalImageIndex < galleryImagesDataMgmt.length - 1) {
        openImageModalMgmt(currentModalImageIndex + 1);
    }
}

// Make global for button clicks
window.showPrevImageMgmt = function() {
    if (currentModalImageIndex > 0) {
        openImageModalMgmt(currentModalImageIndex - 1);
    }
}

// --- Bulk Delete Modal Logic ---
const bulkDeleteModalImg = document.getElementById('bulk-delete-modal-img');
const confirmBulkDeleteBtnImg = document.getElementById('confirm-bulk-delete-btn-img');
const cancelBulkDeleteBtnImg = document.getElementById('cancel-bulk-delete-btn-img');

async function handleBulkDeleteImages() {
    if (selectedImageIds.size === 0) return;
    // Show modal
    if (bulkDeleteModalImg) {
        document.getElementById('bulk-delete-count-img').textContent = selectedImageIds.size;
        bulkDeleteModalImg.classList.remove('hidden');
    }
}
if (confirmBulkDeleteBtnImg) {
    confirmBulkDeleteBtnImg.onclick = async function() {
        try {
            const response = await fetch('/api/images/bulk-delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: Array.from(selectedImageIds) })
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Gagal menghapus gambar (Status: ${response.status})`);
            }
            showToast('success', 'Gambar berhasil dihapus!');
            selectedImageIds.clear();
            updateBulkActionsBarImg();
            fetchAndDisplayImages(currentPage);
        } catch (error) {
            showToast('error', error.message);
        }
        bulkDeleteModalImg.classList.add('hidden');
    };
}
if (cancelBulkDeleteBtnImg) {
    cancelBulkDeleteBtnImg.onclick = function() {
        bulkDeleteModalImg.classList.add('hidden');
    };
}

// --- Bulk Visibility Modal Logic ---
const bulkVisibilityModalImg = document.getElementById('bulk-visibility-modal-img');
const showBulkVisibilityBtnImg = document.getElementById('bulk-visibility-show-btn-img');
const hideBulkVisibilityBtnImg = document.getElementById('bulk-visibility-hide-btn-img');
const cancelBulkVisibilityBtnImg = document.getElementById('cancel-bulk-visibility-btn-img');

async function handleBulkToggleVisibilityImages() {
    if (selectedImageIds.size === 0) return;
    // Show modal
    if (bulkVisibilityModalImg) {
        document.getElementById('bulk-visibility-count-img').textContent = selectedImageIds.size;
        bulkVisibilityModalImg.classList.remove('hidden');
    }
}
if (showBulkVisibilityBtnImg) {
    showBulkVisibilityBtnImg.onclick = async function() {
        await bulkSetVisibilityImages(true);
        bulkVisibilityModalImg.classList.add('hidden');
    };
}
if (hideBulkVisibilityBtnImg) {
    hideBulkVisibilityBtnImg.onclick = async function() {
        await bulkSetVisibilityImages(false);
        bulkVisibilityModalImg.classList.add('hidden');
    };
}
if (cancelBulkVisibilityBtnImg) {
    cancelBulkVisibilityBtnImg.onclick = function() {
        bulkVisibilityModalImg.classList.add('hidden');
    };
}

async function bulkSetVisibilityImages(isVisible) {
    try {
        const response = await fetch('/api/images/bulk-visibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: Array.from(selectedImageIds), is_visible: isVisible })
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Gagal mengubah visibilitas gambar (Status: ${response.status})`);
        }
        showToast('success', isVisible ? 'Gambar ditampilkan!' : 'Gambar disembunyikan!');
        selectedImageIds.clear();
        updateBulkActionsBarImg();
        fetchAndDisplayImages(currentPage);
    } catch (error) {
        showToast('error', error.message);
    }
    updateBulkActionsBarImg();
}

// --- Bulk Actions Bar Button Events ---
const bulkDeleteBtnImg = document.getElementById('bulk-delete-btn-img');
const bulkVisibilityBtnImg = document.getElementById('bulk-visibility-btn-img');
if (bulkDeleteBtnImg) {
    bulkDeleteBtnImg.onclick = handleBulkDeleteImages;
}
if (bulkVisibilityBtnImg) {
    bulkVisibilityBtnImg.onclick = handleBulkToggleVisibilityImages;
}

// --- Event Listeners for Filters ---
if (filterVisibility) {
    filterVisibility.addEventListener('change', () => {
        fetchAndDisplayImages(1); // Reset to page 1 when filter changes
    });
}
if (filterDescription) {
    filterDescription.addEventListener('change', () => {
        fetchAndDisplayImages(1); // Reset to page 1 when filter changes
    });
}
if (filterUsage) {
    filterUsage.addEventListener('change', () => {
        fetchAndDisplayImages(1); // Reset to page 1 when filter changes
    });
}

// Fetch initial page of images on page load
fetchAndDisplayImages(1);

// Keyboard navigation for the management modal
document.addEventListener('keydown', function(event) {
    if (imageManagementModal && !imageManagementModal.classList.contains('hidden')) {
        if (event.key === 'Escape') {
            closeImageModalMgmt();
        } else if (event.key === 'ArrowRight') {
            showNextImageMgmt();
        } else if (event.key === 'ArrowLeft') {
            showPrevImageMgmt();
        }
    }
});

// Usage Modal Logic
const usageModal = document.getElementById('usage-modal');
const usageModalFilename = document.getElementById('usage-modal-filename');
const usageModalList = document.getElementById('usage-modal-list');
const closeUsageModalBtn = document.getElementById('close-usage-modal-btn');

function openUsageModal(imageId, filename) {
    usageModalFilename.textContent = `Gambar: ${filename}`;
    usageModalList.innerHTML = '<div class="text-gray-500">Memuat data penggunaan...</div>';
    usageModal.classList.remove('hidden');
    fetch(`/api/images/${imageId}/usage`)
        .then(res => res.json())
        .then(data => {
            if (data.news && data.news.length > 0) {
                const list = document.createElement('ul');
                data.news.forEach(news => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="${news.url}" target="_blank" class="text-blue-600 hover:underline">${news.title}</a>`;
                    list.appendChild(li);
                });
                usageModalList.innerHTML = '<div class="font-semibold mb-2">Digunakan di artikel:</div>';
                usageModalList.appendChild(list);
            } else {
                usageModalList.innerHTML = '<div class="text-gray-500">Gambar ini tidak digunakan di artikel manapun.</div>';
            }
        })
        .catch(() => {
            usageModalList.innerHTML = '<div class="text-red-500">Gagal memuat data penggunaan.</div>';
        });
}
if (closeUsageModalBtn) {
    closeUsageModalBtn.onclick = function() {
        usageModal.classList.add('hidden');
    };
}
