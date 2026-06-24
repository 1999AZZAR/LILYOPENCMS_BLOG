/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Categories Management JavaScript

// Fetch and populate categories
async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) throw new Error('Failed to fetch categories');
        const categories = await response.json();
        renderManageCategories(categories);
    } catch (error) {
        console.error(error);
        showToast('error', 'Gagal memuat kategori');
    }
}

// Render list and actions
function renderManageCategories(categories) {
    const list = document.getElementById('category-list'); 
    list.innerHTML = '';
    
    categories.forEach(cat => {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between p-3 border-b border-gray-200 last:border-b-0 hover:bg-gray-50';
        row.setAttribute('role', 'listitem');
        row.setAttribute('aria-label', `Kategori: ${cat.name}`);

        const name = document.createElement('span');
        name.textContent = cat.name;
        name.className = 'text-gray-800 font-medium';
        row.appendChild(name);

        const btns = document.createElement('div'); 
        btns.className = 'flex space-x-3';
        btns.setAttribute('role', 'group');
        btns.setAttribute('aria-label', `Actions for category ${cat.name}`);

        // Edit Button (Icon Style)
        const editBtn = document.createElement('button');
        editBtn.innerHTML = '<i class="fas fa-edit" aria-hidden="true"></i>';
        editBtn.className = 'p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-600 rounded-full focus:outline-none focus:ring-2 focus:ring-yellow-300';
        editBtn.setAttribute('aria-label', `Edit category ${cat.name}`);
        editBtn.title = 'Edit';
        editBtn.onclick = () => showEditModal(cat.id, cat.name);
        btns.appendChild(editBtn);

        // Delete Button (Icon Style)
        const delBtn = document.createElement('button');
        delBtn.innerHTML = '<i class="fas fa-trash" aria-hidden="true"></i>';
        delBtn.className = 'p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-full focus:outline-none focus:ring-2 focus:ring-red-300';
        delBtn.setAttribute('aria-label', `Delete category ${cat.name}`);
        delBtn.title = 'Delete';
        delBtn.onclick = () => showDeleteModal(cat.id);
        btns.appendChild(delBtn);

        row.appendChild(btns); 
        list.appendChild(row);
    });
}

// Update category
async function updateCategory(id, name) {
    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
        if (!response.ok) throw new Error('Gagal memperbarui kategori');
        fetchCategories();
        showToast('success', 'Kategori berhasil diperbarui!');
    } catch (error) {
        showToast('error', error.message);
    }
}

// Delete category
async function deleteCategory(id) {
    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error('Gagal menghapus kategori');
        fetchCategories();
        showToast('success', 'Kategori berhasil dihapus!');
    } catch (error) {
        showToast('error', error.message);
    }
}

// Show edit modal
function showEditModal(id, name) {
    document.getElementById('edit-category-id').value = id;
    document.getElementById('edit-category-name').value = name;
    document.getElementById('edit-category-modal').classList.remove('hidden');
}

// Show delete modal
function showDeleteModal(id) {
    document.getElementById('delete-category-id').value = id;
    document.getElementById('delete-category-modal').classList.remove('hidden');
}

// Close modals
function closeEditModal() {
    document.getElementById('edit-category-modal').classList.add('hidden');
}

function closeDeleteModal() {
    document.getElementById('delete-category-modal').classList.add('hidden');
}

// Initialize categories management
document.addEventListener('DOMContentLoaded', () => {
    // Load categories on page load
    fetchCategories();
    
    // Add new category form handler
    document.getElementById('add-category').addEventListener('submit', async (e) => {
        e.preventDefault();
        const categoryName = document.getElementById('category-name').value.trim();
        if (!categoryName) { 
            showToast('warning', 'Nama kategori diperlukan'); 
            return; 
        }
        
        try {
            const response = await fetch('/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: categoryName }),
            });
            if (!response.ok) { 
                const err = await response.json(); 
                throw new Error(err.error || 'Failed to add category'); 
            }
            showToast('success', 'Kategori berhasil ditambahkan!');
            fetchCategories(); 
            document.getElementById('category-name').value = '';
        } catch (error) {
            showToast('error', `Gagal menambahkan kategori: ${error.message}`);
        }
    });

    // Edit category form handler
    document.getElementById('edit-category-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-category-id').value;
        const name = document.getElementById('edit-category-name').value.trim();
        if (!name) {
            showToast('warning', 'Nama kategori diperlukan');
            return;
        }
        await updateCategory(id, name);
        closeEditModal();
    });

    // Cancel edit button
    document.getElementById('cancel-edit-btn').addEventListener('click', () => {
        closeEditModal();
    });

    // Delete category confirmation
    document.getElementById('confirm-delete-category-btn').addEventListener('click', async () => {
        const id = document.getElementById('delete-category-id').value;
        await deleteCategory(id);
        closeDeleteModal();
    });

    // Cancel delete button
    document.getElementById('cancel-delete-btn').addEventListener('click', () => {
        closeDeleteModal();
    });

    // Close modals when clicking outside
    document.getElementById('edit-category-modal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeEditModal();
        }
    });

    document.getElementById('delete-category-modal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeDeleteModal();
        }
    });
});
