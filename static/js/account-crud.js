/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

document.addEventListener('DOMContentLoaded', () => {
    const passwordForm = document.getElementById('change-password-form');
    const passwordStatus = document.getElementById('password-status');
    const ownedNewsList = document.getElementById('owned-news-list');
    const ownedPaginationControls = document.getElementById('owned-pagination-controls');

    let currentOwnedPage = 1; // Track current page for owned news
    let newsIdToDelete = null; // Track which news item to delete

    // --- Password Change Logic ---
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

            if (newPassword !== confirmPassword) {
                passwordStatus.innerHTML = '<p class="text-red-500">Kata sandi baru tidak cocok.</p>';
                return;
            }
            if (!csrfToken) {
                passwordStatus.innerHTML = '<p class="text-red-500">Token CSRF tidak ditemukan.</p>';
                return;
            }

            passwordStatus.innerHTML = '<p class="text-gray-400">Mengubah kata sandi...</p>';

            try {
                const response = await fetch('/api/account/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword,
                        confirm_password: confirmPassword,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Gagal mengubah kata sandi.');
                }

                passwordStatus.innerHTML = '<p class="text-green-500">Kata sandi berhasil diubah.</p>';
                passwordForm.reset();
                if (typeof showToast === 'function') showToast('success', 'Kata sandi berhasil diubah!');

            } catch (error) {
                console.error('Error changing password:', error);
                passwordStatus.innerHTML = `<p class="text-red-500">Gagal mengubah kata sandi: ${error.message}</p>`;
                if (typeof showToast === 'function') showToast('error', `Gagal mengubah kata sandi: ${error.message}`);
            }
        });
    }

    // --- Pagination Helpers ---
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
        const el = document.createElement(tag);
        el.className = classes;
        el.innerHTML = content;
        if (ariaLabel) el.setAttribute('aria-label', ariaLabel);
        if (title) el.title = title;
        if (disabled) el.setAttribute('aria-disabled', 'true');
        if (onClick && !disabled) el.onclick = () => onClick();
        return el;
    }

    function updateOwnedPaginationControls(paginationData) {
        if (!ownedPaginationControls) return;
        ownedPaginationControls.innerHTML = '';
        if (!paginationData || paginationData.total_pages <= 1) return;

        const { page: currentPage, total_pages: totalPages } = paginationData;
        const nav = document.createElement('nav');
        nav.setAttribute('aria-label', 'Owned News Pagination');
        nav.className = 'flex flex-wrap items-center justify-center mt-4 gap-2 overflow-x-auto';

        // Use consistent styles from news-management.js / image-crud.js
        const buttonClasses = 'px-3 py-2 text-sm font-medium text-amber-700 bg-white border border-amber-300 rounded-md hover:bg-amber-50 focus:outline-none focus:ring-2 focus:ring-amber-500';
        const disabledClasses = 'px-3 py-2 text-sm font-medium text-gray-400 bg-gray-100 border border-gray-200 rounded-md cursor-not-allowed';
        const currentClasses = 'px-3 py-2 text-sm font-medium text-white bg-amber-600 border border-amber-600 rounded-md';
        const ellipsisClasses = 'px-3 py-2 text-sm font-medium text-gray-500';
        const firstIcon = `&laquo;`, prevIcon = `&lsaquo;`, nextIcon = `&rsaquo;`, lastIcon = `&raquo;`;

        nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, firstIcon, 'First Page', 'First Page', currentPage <= 1, () => fetchOwnedNews(1)));
        nav.appendChild(createPaginationElement(currentPage > 1 ? 'button' : 'span', currentPage > 1 ? buttonClasses : disabledClasses, prevIcon, 'Previous Page', 'Previous Page', currentPage <= 1, () => fetchOwnedNews(currentPage - 1)));
        generatePageNumbers(currentPage, totalPages, 1, 1).forEach(page_num => {
            if (page_num === null) nav.appendChild(createPaginationElement('span', ellipsisClasses, '...', null, null, true));
            else if (page_num === currentPage) {
                const el = createPaginationElement('span', currentClasses, page_num, null, `Page ${page_num}`, true);
                el.setAttribute('aria-current', 'page');
                nav.appendChild(el);
            } else nav.appendChild(createPaginationElement('button', buttonClasses, page_num, `Go to page ${page_num}`, `Go to page ${page_num}`, false, () => fetchOwnedNews(page_num)));
        });
        nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, nextIcon, 'Next Page', 'Next Page', currentPage >= totalPages, () => fetchOwnedNews(currentPage + 1)));
        nav.appendChild(createPaginationElement(currentPage < totalPages ? 'button' : 'span', currentPage < totalPages ? buttonClasses : disabledClasses, lastIcon, 'Last Page', 'Last Page', currentPage >= totalPages, () => fetchOwnedNews(totalPages)));
        ownedPaginationControls.appendChild(nav);
    }

    // --- Owned News Fetching and Rendering ---
    async function fetchOwnedNews(page = 1) {
        if (!ownedNewsList) return;

        currentOwnedPage = page;
        ownedNewsList.innerHTML = '<p class="text-gray-400 col-span-full text-center">Memuat artikel Anda...</p>';
        if (ownedPaginationControls) ownedPaginationControls.innerHTML = '';

        try {
            const isNews = document.getElementById('owned-premium-filter')?.value || '';
            const status = document.getElementById('owned-status-filter')?.value || '';
            const hasImage = document.getElementById('owned-filter-featured-image')?.value || '';
            const hasLink = document.getElementById('owned-filter-external-link')?.value || '';
            const search = document.getElementById('owned-search')?.value || '';
            
            const params = new URLSearchParams({
                page: page,
                is_news: isNews,
                status: status,
                has_image: hasImage,
                has_link: hasLink,
                search: search
            });

            const response = await fetch(`/api/news/owned?${params}`);
            if (!response.ok) throw new Error('Failed to fetch owned news');
            
            const data = await response.json();
            console.log('API Response:', data); // Debug log
            
            // Fix: Use 'items' instead of 'news' based on API response
            renderOwnedNews(data.items, data);
        } catch (error) {
            console.error('Error fetching owned news:', error);
            ownedNewsList.innerHTML = `<p class="text-red-500 col-span-full text-center">Gagal memuat artikel: ${error.message}</p>`;
            if (typeof showToast === 'function') {
                showToast('error', `Gagal memuat artikel: ${error.message}`);
            }
        }
    }

    function renderOwnedNews(newsItems, paginationData) {
        if (!ownedNewsList) return;

        // Update article count
        const articlesCountElement = document.getElementById('articles-count');
        if (articlesCountElement) {
            articlesCountElement.textContent = paginationData?.total_items || newsItems?.length || 0;
        }

        if (!newsItems || newsItems.length === 0) {
            ownedNewsList.innerHTML = '<p class="text-gray-400 col-span-full text-center">Tidak ada artikel yang cocok dengan filter Anda atau Anda belum membuat artikel.</p>';
            return;
        }

        const placeholderImg = '/static/pic/placeholder.png';

        ownedNewsList.innerHTML = newsItems.map(news => {
            console.log("Rendering news item:", news.id, "Image data:", news.image); // DEBUG: Check image data
            let squareThumbUrl = placeholderImg;
            if (news.image && news.image.filepath) {
                const pathWithoutStatic = news.image.filepath.replace('static/', '', 1);
                const lastDotIndex = pathWithoutStatic.lastIndexOf('.');
                if (lastDotIndex !== -1) {
                    const base_path = pathWithoutStatic.substring(0, lastDotIndex);
                    const extension = pathWithoutStatic.substring(lastDotIndex);
                    squareThumbUrl = `/static/${base_path}_thumb_square${extension}`;
                } else {
                    squareThumbUrl = news.image.file_url || placeholderImg;
                }
            } else if (news.image && news.image.url) {
                 squareThumbUrl = news.image.url;
            }

            const visibilityClass = news.is_visible ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
            const visibilityText = news.is_visible ? 'Terlihat' : 'Draf';
            const premiumClass = news.is_news ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800';
            const premiumText = news.is_news ? 'Artikel' : 'Berita';

            // Use the card structure similar to news-management.js
            return `
            <div class="bg-white border border-gray-200 rounded-xl shadow-md hover:shadow-lg transition p-6 flex flex-col sm:flex-row gap-4">
                <div class="w-40 h-40 flex-shrink-0 bg-gray-200 rounded-lg overflow-hidden">
                    <img src="${squareThumbUrl}"
                         alt="Thumbnail for ${news.title || 'artikel'}"
                         class="w-full h-full object-cover"
                         onerror="this.onerror=null; this.src='${placeholderImg}';">
                </div>
                <div class="flex flex-col justify-between flex-grow">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">${news.title || 'Tanpa Judul'}</h3>
                        <div class="flex flex-wrap items-center gap-x-2 text-sm text-gray-600 mb-1">
                            <span>${news.category || 'Tanpa Kategori'}</span>
                            <span class="px-2 py-0.5 rounded-full text-xs ${premiumClass}">${premiumText}</span>
                        </div>
                        <div class="flex flex-wrap items-center gap-x-2 text-xs text-gray-500 mb-1">
                            ${news.date ? new Date(news.date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Tanggal tidak ada'}
                            <span class="px-2 py-0.5 rounded-full ${visibilityClass}">${visibilityText}</span>
                        </div>
                        <div class="flex items-center text-xs text-gray-500 mt-1">
                            <span><i class="fas fa-eye mr-1"></i> ${news.read_count || 0}</span>
                            ${news.total_shares !== undefined ? `<span class="mx-2">|</span><span><i class="fas fa-share-alt mr-1"></i> ${news.total_shares}</span>` : ''}
                        </div>
                    </div>
                    <div class="mt-4 flex space-x-2 justify-end">
                        <button onclick="toggleVisibility(${news.id}, ${!news.is_visible})" class="w-8 h-8 flex items-center justify-center bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-300" aria-label="${news.is_visible ? 'Sembunyikan artikel' : 'Tampilkan artikel'}" title="${news.is_visible ? 'Sembunyikan' : 'Tampilkan'}"><i class="fas fa-${news.is_visible ? 'eye-slash' : 'eye'}"></i></button>
                        <button data-news-id="${news.id}" class="delete-owned-news-btn w-8 h-8 flex items-center justify-center bg-red-100 hover:bg-red-200 text-red-600 rounded-full focus:outline-none focus:ring-2 focus:ring-red-300" aria-label="Hapus artikel" title="Hapus"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            </div>
            `;
        }).join('');

        // Update pagination controls
        updateOwnedPaginationControls(paginationData);
        attachDeleteListeners();
    }

    // --- Delete News Logic ---
    const deleteModal = document.getElementById('delete-modal');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

    function openDeleteModal(newsId) {
        if (!deleteModal) return;
        newsIdToDelete = newsId;
        deleteModal.classList.remove('hidden');
        deleteModal.classList.add('flex');
    }

    window.closeDeleteModal = function() { // Make globally accessible
        if (!deleteModal) return;
        newsIdToDelete = null;
        deleteModal.classList.add('hidden');
        deleteModal.classList.remove('flex');
    }

    function attachDeleteListeners() {
        document.querySelectorAll('.delete-owned-news-btn').forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            newButton.addEventListener('click', () => {
                const newsId = newButton.getAttribute('data-news-id');
                openDeleteModal(newsId);
            });
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {
            if (!newsIdToDelete) return;

            try {
                // Use the correct general delete endpoint
                const response = await fetch(`/api/news/${newsIdToDelete}`, {
                    method: 'DELETE',
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Gagal menghapus artikel.' }));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }

                if (typeof showToast === 'function') showToast('success', 'Artikel berhasil dihapus.');
                // Refresh the current page after delete
                fetchOwnedNews(currentOwnedPage);

            } catch (error) {
                console.error('Error deleting news:', error);
                if (typeof showToast === 'function') showToast('error', `Gagal menghapus artikel: ${error.message}`);
            } finally {
                closeDeleteModal();
            }
        });
    }

    // --- Toggle Visibility Function (Re-added) ---
    window.toggleVisibility = async function(newsId, isVisible) { // Make globally accessible
        try {
            const response = await fetch(`/api/news/${newsId}/visibility`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_visible: isVisible }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Gagal mengubah visibilitas (Status: ${response.status})`);
            }
            fetchOwnedNews(currentOwnedPage); // Refresh current page
            if (typeof showToast === 'function') showToast('success', 'Visibilitas berhasil diubah!');
        } catch (error) {
            console.error('Error toggling visibility:', error);
            if (typeof showToast === 'function') showToast('error', `Gagal mengubah visibilitas: ${error.message}`);
        }
    }

    // --- Filter Event Listeners ---
    const filterInputs = [
        'owned-search',
        'owned-status-filter',
        'owned-premium-filter',
        'owned-filter-featured-image',
        'owned-filter-external-link'
    ];

    filterInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            const eventType = (input.tagName === 'INPUT' && input.type === 'text') ? 'input' : 'change';
            let debounceTimer;
            input.addEventListener(eventType, () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    fetchOwnedNews(1); // Reset to page 1 on filter change
                }, 300);
            });
        }
    });

    // --- Delete Account Logic ---
    const deleteAccountModal = document.getElementById('delete-account-modal');
    const confirmDeleteAccountBtn = document.getElementById('confirm-delete-account-btn');

    window.openDeleteAccountModal = function() { // Make globally accessible
        if (deleteAccountModal) {
            deleteAccountModal.classList.remove('hidden');
            deleteAccountModal.classList.add('flex');
        }
    }

    window.closeDeleteAccountModal = function() { // Make globally accessible
        if (deleteAccountModal) {
            deleteAccountModal.classList.add('hidden');
            deleteAccountModal.classList.remove('flex');
        }
    }

    if (confirmDeleteAccountBtn) {
        confirmDeleteAccountBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/account/delete', {
                    method: 'DELETE',
                });

                if (!response.ok) {
                     const errorData = await response.json().catch(() => ({ error: 'Gagal menghapus akun.' }));
                    throw new Error(errorData.error || 'Gagal menghapus akun.');
                }

                // Redirect to logout or login page after successful deletion
                window.location.href = '/logout';

            } catch (error) {
                console.error('Error deleting account:', error);
                if (typeof showToast === 'function') showToast('error', `Gagal menghapus akun: ${error.message}`);
                closeDeleteAccountModal();
            }
        });
    }

    // --- Update Account Stats ---
    async function updateAccountStats() {
        try {
            const response = await fetch('/api/news/owned?page=1&per_page=1000'); // Get all articles for stats
            if (response.ok) {
                const data = await response.json();
                const articles = data.items || [];
                
                const totalArticles = data.total_items || articles.length;
                const visibleArticles = articles.filter(article => article.is_visible).length;
                const totalReads = articles.reduce((sum, article) => sum + (article.read_count || 0), 0);
                
                // Update stats display
                const totalArticlesElement = document.getElementById('total-articles');
                const visibleArticlesElement = document.getElementById('visible-articles');
                const totalReadsElement = document.getElementById('total-reads');
                
                if (totalArticlesElement) totalArticlesElement.textContent = totalArticles;
                if (visibleArticlesElement) visibleArticlesElement.textContent = visibleArticles;
                if (totalReadsElement) totalReadsElement.textContent = totalReads;
            }
        } catch (error) {
            console.error('Error updating account stats:', error);
        }
    }

    // --- Initial Load ---
    fetchOwnedNews(1);
    updateAccountStats();

}); // End DOMContentLoaded

// Change password form submission
document.getElementById('change-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        current_password: document.getElementById('current-password').value.trim(),
        new_password: document.getElementById('new-password').value.trim(),
        confirm_password: document.getElementById('confirm-password').value.trim(),
    };

    try {
        const response = await fetch('/api/account/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to change password');
        }

        showToast('success', 'Password berhasil diubah!');
        document.getElementById('change-password-form').reset();
    } catch (error) {
        console.error(error);
        showToast('error', `Gagal mengubah kata sandi: ${error.message}`);
    }
});

// Open delete account modal
function openDeleteAccountModal() {
    document.getElementById('delete-account-modal').classList.remove('hidden');
}

// Close delete account modal
function closeDeleteAccountModal() {
    document.getElementById('delete-account-modal').classList.add('hidden');
}

// Delete account
document.getElementById('confirm-delete-account-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/account/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Failed to delete account');

        window.location.href = '/logout'; // Redirect to logout after deletion
    } catch (error) {
        console.error(error);
        showToast('error', error.message);
    }
});

// Initial fetch
fetchOwnedNews();
