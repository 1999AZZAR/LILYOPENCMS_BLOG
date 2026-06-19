// YouTube Management JavaScript
// (CSRF token logic can be removed if not needed)

let currentPage = 1;
let perPage = 12;
let totalPages = 1;
let totalItems = 0;
let searchQuery = '';
let currentEditId = null;
let currentDeleteId = null;
let selectedVideoIds = new Set();

const filterVisibilityVideo = document.getElementById('filter-visibility-video');

function showEditModal(id, link) {
    currentEditId = id;
    document.getElementById('edit-video-link').value = link;
    document.getElementById('edit-video-modal').classList.remove('hidden');
}
function hideEditModal() {
    document.getElementById('edit-video-modal').classList.add('hidden');
    currentEditId = null;
}
function showDeleteModal(id) {
    currentDeleteId = id;
    document.getElementById('delete-video-modal').classList.remove('hidden');
}
function hideDeleteModal() {
    document.getElementById('delete-video-modal').classList.add('hidden');
    currentDeleteId = null;
}

async function fetchVideos(page = 1, perPageVal = 12, query = '', visibility = 'all') {
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: perPageVal,
            q: query,
            visibility: filterVisibilityVideo ? filterVisibilityVideo.value : visibility
        });
        const response = await fetch(`/api/youtube_videos?${params}`);
        if (!response.ok) throw new Error('Gagal memuat video');
        const data = await response.json();
        currentPage = page;
        perPage = perPageVal;
        totalPages = data.pages;
        totalItems = data.total;
        updatePaginationControls();
        renderManageVideos(data.items);
    } catch (e) {
        showToast('error', 'Gagal memuat video: ' + e.message);
    }
}

async function updateVideo(id, link) {
    try {
        const res = await fetch(`/api/youtube_videos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link }),
        });
        if (!res.ok) throw new Error('Gagal memperbarui video');
        fetchVideos(currentPage, perPage, searchQuery);
        showToast('success', 'Video berhasil diperbarui!');
    } catch (e) {
        showToast('error', e.message);
    }
}

async function deleteVideo(id) {
    try {
        const res = await fetch(`/api/youtube_videos/${id}`, {
            method: 'DELETE' });
        if (!res.ok) throw new Error('Gagal menghapus video');
        fetchVideos(currentPage, perPage, searchQuery);
        showToast('success', 'Video berhasil dihapus!');
    } catch (e) {
        showToast('error', e.message);
    }
}

async function toggleVisibility(id, isVisible) {
    try {
        const res = await fetch(`/api/youtube_videos/${id}/visibility`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_visible: isVisible }),
        });
        if (!res.ok) throw new Error('Gagal memperbarui visibilitas video');
        fetchVideos(currentPage, perPage, searchQuery);
        showToast('success', 'Visibilitas video diperbarui!');
    } catch (e) {
        showToast('error', e.message);
    }
}

function updatePaginationControls() {
    document.getElementById('page-info').textContent = `Halaman ${currentPage} dari ${totalPages} (${totalItems} video)`;
    const pageSelector = document.getElementById('page-selector');
    pageSelector.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === currentPage) option.selected = true;
        pageSelector.appendChild(option);
    }
    const perPageSelector = document.getElementById('per-page-selector');
    perPageSelector.value = perPage;
    document.getElementById('first-page').disabled = currentPage === 1;
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === totalPages;
    document.getElementById('last-page').disabled = currentPage === totalPages;
}

function renderManageVideos(videos) {
    const list = document.getElementById('video-list');
    if (!videos.length) {
        list.innerHTML = '<div class="text-center py-6 text-gray-500">Tidak ada video ditemukan</div>';
        return;
    }
    list.innerHTML = '';
    videos.forEach(v => {
        const row = document.createElement('div');
        row.className = 'flex flex-row-reverse items-center bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition mb-2 gap-4';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'video-select-checkbox rounded border-gray-300 text-yellow-500 focus:ring-yellow-400 ml-3';
        checkbox.value = v.id;
        checkbox.checked = selectedVideoIds.has(v.id);
        checkbox.addEventListener('change', handleVideoCheckboxChange);
        row.appendChild(checkbox);
        const thumb = document.createElement('img');
        thumb.src = `https://img.youtube.com/vi/${v.youtube_id}/hqdefault.jpg`;
        thumb.className = 'w-32 h-20 object-cover rounded-lg shadow-sm border';
        thumb.loading = 'lazy';
        row.appendChild(thumb);
        const info = document.createElement('div');
        info.className = 'flex flex-col flex-1 min-w-0';
        const title = document.createElement('div');
        title.textContent = v.title || v.youtube_id;
        title.className = 'text-gray-900 font-semibold text-base truncate mb-1';
        info.appendChild(title);
        const linkEl = document.createElement('a');
        linkEl.href = v.link;
        linkEl.textContent = 'Tonton';
        linkEl.target = '_blank';
        linkEl.className = 'text-blue-500 underline hover:text-blue-600 text-sm mb-1';
        info.appendChild(linkEl);
        const statusBadge = document.createElement('span');
        statusBadge.textContent = v.is_visible ? 'Tampil' : 'Tersembunyi';
        statusBadge.className = v.is_visible
            ? 'inline-block px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 mb-1'
            : 'inline-block px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 mb-1';
        info.appendChild(statusBadge);
        row.appendChild(info);
        const btns = document.createElement('div');
        btns.className = 'flex flex-col gap-2 items-end';
        const editBtn = document.createElement('button');
        editBtn.innerHTML = '<i class="fas fa-pen"></i>';
        editBtn.className = 'bg-yellow-500 text-gray-900 p-2 rounded-full hover:bg-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-300';
        editBtn.onclick = () => showEditModal(v.id, v.link);
        const delBtn = document.createElement('button');
        delBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
        delBtn.className = 'bg-red-500 text-white p-2 rounded-full hover:bg-red-400 focus:outline-none focus:ring-2 focus:ring-red-300';
        delBtn.onclick = () => showDeleteModal(v.id);
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = `<i class="fas ${v.is_visible ? 'fa-eye-slash' : 'fa-eye'}"></i>`;
        toggleBtn.className = v.is_visible
            ? 'bg-gray-300 text-gray-800 p-2 rounded-full hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-300'
            : 'bg-green-500 text-white p-2 rounded-full hover:bg-green-400 focus:outline-none focus:ring-2 focus:ring-green-300';
        toggleBtn.onclick = () => toggleVisibility(v.id, !v.is_visible);
        btns.appendChild(editBtn);
        btns.appendChild(delBtn);
        btns.appendChild(toggleBtn);
        row.appendChild(btns);
        list.appendChild(row);
    });
    // Update select all state
    const selectAll = document.getElementById('select-all-videos');
    if (selectAll) {
        selectAll.checked = videos.length > 0 && videos.every(v => selectedVideoIds.has(v.id));
    }
    updateBulkActionsBarVideo();
    attachSelectAllListener();
}

function updateBulkActionsBarVideo() {
    const bar = document.getElementById('bulk-actions-bar-video');
    if (!bar) return;
    if (selectedVideoIds.size > 0) {
        bar.classList.remove('hidden');
        document.getElementById('bulk-video-count').textContent = selectedVideoIds.size;
    } else {
        bar.classList.add('hidden');
    }
}

function handleSelectAllVideos(checked) {
    const checkboxes = document.querySelectorAll('.video-select-checkbox');
    selectedVideoIds = new Set();
    checkboxes.forEach(cb => {
        cb.checked = checked;
        if (checked) selectedVideoIds.add(Number(cb.value));
    });
    updateBulkActionsBarVideo();
}

function handleVideoCheckboxChange(e) {
    const id = Number(e.target.value);
    if (e.target.checked) {
        selectedVideoIds.add(id);
    } else {
        selectedVideoIds.delete(id);
    }
    updateBulkActionsBarVideo();
}

function attachSelectAllListener() {
    const selectAll = document.getElementById('select-all-videos');
    if (selectAll) {
        selectAll.onchange = function() {
            handleSelectAllVideos(this.checked);
        };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Pagination and search controls
    document.getElementById('page-selector').addEventListener('change', () => {
        fetchVideos(parseInt(pageSelector.value), perPage, searchQuery);
    });
    document.getElementById('per-page-selector').addEventListener('change', () => {
        perPage = parseInt(perPageSelector.value);
        fetchVideos(1, perPage, searchQuery);
    });
    document.getElementById('search-btn').addEventListener('click', () => {
        searchQuery = document.getElementById('search-input').value.trim();
        fetchVideos(1, perPage, searchQuery);
    });
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchQuery = document.getElementById('search-input').value.trim();
            fetchVideos(1, perPage, searchQuery);
        }
    });
    document.getElementById('first-page').addEventListener('click', () => {
        fetchVideos(1, perPage, searchQuery);
    });
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) fetchVideos(currentPage - 1, perPage, searchQuery);
    });
    document.getElementById('next-page').addEventListener('click', () => {
        if (currentPage < totalPages) fetchVideos(currentPage + 1, perPage, searchQuery);
    });
    document.getElementById('last-page').addEventListener('click', () => {
        fetchVideos(totalPages, perPage, searchQuery);
    });
    document.getElementById('add-video').addEventListener('submit', async (e) => {
        e.preventDefault();
        const link = document.getElementById('video-link').value.trim();
        if (!link) { showToast('warning', 'Link video wajib diisi'); return; }
        try {
            const res = await fetch('/api/youtube_videos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ link }),
            });
            if (!res.ok) throw new Error('Gagal menambahkan video');
            showToast('success', 'Video berhasil ditambahkan!');
            fetchVideos(1, perPage, searchQuery);
            document.getElementById('video-link').value = '';
        } catch (err) {
            showToast('error', err.message);
        }
    });
    document.getElementById('cancel-edit-video-btn').addEventListener('click', hideEditModal);
    document.getElementById('confirm-edit-video-btn').addEventListener('click', () => {
        const link = document.getElementById('edit-video-link').value.trim();
        if (link) {
            updateVideo(currentEditId, link);
            hideEditModal();
        }
    });
    document.getElementById('cancel-delete-video-btn').addEventListener('click', hideDeleteModal);
    document.getElementById('confirm-delete-video-btn').addEventListener('click', () => {
        deleteVideo(currentDeleteId);
        hideDeleteModal();
    });
    // Initial fetch
    fetchVideos();
});
