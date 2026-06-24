/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Albums SEO Management JavaScript
// Handles SEO functionality for the albums management page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize SEO tab functionality
    initializeAlbumsSEO();
});

function initializeAlbumsSEO() {
    // Load initial SEO data
    loadAlbumsSEOData();
    
    // Initialize event listeners
    initializeSEOEventListeners();
}

function initializeSEOEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refresh-seo-albums');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAlbumsSEOData);
    }
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-white', 'text-amber-800');
                btn.classList.add('bg-amber-200', 'text-amber-700');
            });
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                content.classList.add('hidden');
            });
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active', 'bg-white', 'text-amber-800');
            this.classList.remove('bg-amber-200', 'text-amber-700');
            
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
                targetContent.classList.remove('hidden');
            }
        });
    });
}

function loadAlbumsSEOData(page = 1) {
    const tableBody = document.getElementById('seo-albums-table-body');
    if (!tableBody) return;
    
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
    
    fetch(`/api/seo/albums-management?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.albums && data.albums.length > 0) {
                renderAlbumsSEOTable(data.albums);
                updateAlbumsSEOPagination(data.pagination);
                updateAlbumsSEOCounts(data.pagination);
            } else {
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
            console.error('Error loading albums SEO data:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-xl mb-2"></i>
                        <p class="mt-2">Error loading albums data</p>
                        <p class="text-sm text-red-400">${error.message}</p>
                    </td>
                </tr>
            `;
            showToast('Error loading albums data: ' + error.message, 'error');
        });
}

function renderAlbumsSEOTable(albums) {
    const tableBody = document.getElementById('seo-albums-table-body');
    if (!tableBody) return;
    
    if (!albums || albums.length === 0) {
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
                <button class="edit-seo-btn text-amber-600 hover:text-amber-900 mr-3" data-id="${album.id}" data-type="album">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to edit buttons
    document.querySelectorAll('.edit-seo-btn[data-type="album"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const albumId = this.getAttribute('data-id');
            openSEOEditModal(albumId);
        });
    });
}

function openSEOEditModal(albumId) {
    // Load album SEO data
    fetch(`/api/seo/albums/${albumId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            populateSEOEditForm(data);
            document.getElementById('seo-edit-modal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error loading album SEO data:', error);
            showToast('Error loading album SEO data: ' + error.message, 'error');
        });
}

function populateSEOEditForm(data) {
    // Populate form fields
    document.getElementById('seo-album-id').value = data.id;
    document.getElementById('seo-meta-description').value = data.meta_description || '';
    document.getElementById('seo-meta-keywords').value = data.meta_keywords || '';
    document.getElementById('seo-seo-slug').value = data.seo_slug || '';
    document.getElementById('seo-canonical-url').value = data.canonical_url || '';
    document.getElementById('seo-og-title').value = data.og_title || '';
    document.getElementById('seo-og-description').value = data.og_description || '';
    document.getElementById('seo-og-image').value = data.og_image || '';
    document.getElementById('seo-meta-author').value = data.meta_author || '';
    document.getElementById('seo-meta-language').value = data.meta_language || 'id';
    document.getElementById('seo-meta-robots').value = data.meta_robots || 'index, follow';
    document.getElementById('seo-structured-data-type').value = data.structured_data_type || 'Book';
}

function closeSEOEditModal() {
    document.getElementById('seo-edit-modal').classList.add('hidden');
    document.getElementById('seo-edit-form').reset();
}

// Add form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const seoEditForm = document.getElementById('seo-edit-form');
    if (seoEditForm) {
        seoEditForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const albumId = document.getElementById('seo-album-id').value;
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData.entries());
            
            // Update album SEO
            fetch(`/api/seo/albums/${albumId}`, {
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
                    closeSEOEditModal();
                    loadAlbumsSEOData();
                } else {
                    showToast('Error updating SEO', 'error');
                }
            })
            .catch(error => {
                console.error('Error updating album SEO:', error);
                showToast('Error updating SEO', 'error');
            });
        });
    }
});

function updateAlbumsSEOPagination(pagination) {
    const controls = document.getElementById('seo-pagination-controls');
    if (!controls) return;
    
    controls.innerHTML = generateSEOPaginationHTML(pagination, 'albums');
}

function updateAlbumsSEOCounts(pagination) {
    const showingStart = document.getElementById('seo-showing-start');
    const showingEnd = document.getElementById('seo-showing-end');
    const total = document.getElementById('seo-total-albums');
    
    if (showingStart) showingStart.textContent = ((pagination.current_page - 1) * pagination.per_page) + 1;
    if (showingEnd) showingEnd.textContent = Math.min(pagination.current_page * pagination.per_page, pagination.total_items);
    if (total) total.textContent = pagination.total_items;
}

function generateSEOPaginationHTML(pagination, type) {
    let html = '';
    
    if (pagination.total_pages <= 1) {
        return html; // No pagination needed
    }
    
    // Previous button
    if (pagination.has_prev) {
        html += `<button class="px-3 py-1 bg-amber-500 text-white rounded hover:bg-amber-600 transition-colors" onclick="loadAlbumsSEOData(${pagination.current_page - 1})">
            <i class="fas fa-chevron-left mr-1"></i>Previous
        </button>`;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.current_page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === pagination.current_page) {
            html += `<span class="px-3 py-1 bg-amber-600 text-white rounded font-medium">${i}</span>`;
        } else {
            html += `<button class="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors" onclick="loadAlbumsSEOData(${i})">${i}</button>`;
        }
    }
    
    // Next button
    if (pagination.has_next) {
        html += `<button class="px-3 py-1 bg-amber-500 text-white rounded hover:bg-amber-600 transition-colors" onclick="loadAlbumsSEOData(${pagination.current_page + 1})">
            Next<i class="fas fa-chevron-right ml-1"></i>
        </button>`;
    }
    
    return html;
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

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
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
