/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Users Management JavaScript
class UsersManagement {
    constructor() {
        this.currentUser = null;
        this.users = [];
        this.currentPage = 1;
        this.totalPages = 1;
        this.currentUserId = null;
        this.init();
    }

    init() {
    // Set current user data from template
    if (typeof window.currentUserData !== 'undefined') {
            this.currentUser = window.currentUserData;
        }
        
        this.bindEvents();
        this.initTabs();
        this.loadUsers();
        this.loadRoleStats(); // Load role statistics
    }

    bindEvents() {
        // Search and filter handlers
        const searchInput = document.getElementById('search');
        const roleFilter = document.getElementById('role-filter');
        const statusFilter = document.getElementById('status-filter');
        const verificationFilter = document.getElementById('verification-filter');
        
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.loadUsers(1), 500));
        }
        
        if (roleFilter) {
            roleFilter.addEventListener('change', () => this.loadUsers(1));
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.loadUsers(1));
        }
        
        if (verificationFilter) {
            verificationFilter.addEventListener('change', () => this.loadUsers(1));
        }
        
        // Performance period handler
        const performancePeriod = document.getElementById('performance-period');
        if (performancePeriod) {
            performancePeriod.addEventListener('change', () => this.loadPerformanceData());
        }
        
        // Export buttons
        const exportUsersBtn = document.getElementById('export-users-btn');
        if (exportUsersBtn) {
            exportUsersBtn.addEventListener('click', () => this.exportUsers());
        }
        
        const exportPerformanceBtn = document.getElementById('export-performance-btn');
        if (exportPerformanceBtn) {
            exportPerformanceBtn.addEventListener('click', () => this.exportPerformance());
        }
        
        const exportRolesBtn = document.getElementById('export-roles-btn');
        if (exportRolesBtn) {
            exportRolesBtn.addEventListener('click', () => this.exportRoles());
        }
        
        // Active/Suspended checkbox interactions
        const activeCheckbox = document.getElementById('edit-is-active');
        const suspendedCheckbox = document.getElementById('edit-is-suspended');
        
        if (activeCheckbox && suspendedCheckbox) {
            activeCheckbox.addEventListener('change', () => {
                if (activeCheckbox.checked) {
                    suspendedCheckbox.checked = false;
                    this.toggleSuspensionDetails(false);
                }
            });
            
            suspendedCheckbox.addEventListener('change', () => {
                if (suspendedCheckbox.checked) {
                    activeCheckbox.checked = false;
                    this.toggleSuspensionDetails(true);
                } else {
                    this.toggleSuspensionDetails(false);
                }
            });
        }

    // Bulk actions
    const bulkActionsBtn = document.getElementById('bulk-actions-btn');
    if (bulkActionsBtn) {
        bulkActionsBtn.addEventListener('click', () => this.toggleBulkActions());
    }

    // Bulk permission actions
    const bulkActivateBtn = document.getElementById('bulk-activate');
    const bulkDeactivateBtn = document.getElementById('bulk-deactivate');
    const bulkVerifyBtn = document.getElementById('bulk-verify');
    const bulkSuspendBtn = document.getElementById('bulk-suspend');
    
    if (bulkActivateBtn) {
        bulkActivateBtn.addEventListener('click', () => this.bulkUpdateUserStatus(true));
    }
    if (bulkDeactivateBtn) {
        bulkDeactivateBtn.addEventListener('click', () => this.bulkUpdateUserStatus(false));
    }
    if (bulkVerifyBtn) {
        bulkVerifyBtn.addEventListener('click', () => this.bulkVerifyUsers(true));
    }
    if (bulkSuspendBtn) {
        bulkSuspendBtn.addEventListener('click', () => this.bulkSuspendUsers(true));
    }

        // Form handlers
        this.initFormHandlers();
        
        // Deletion requests handlers
        const deletionSearch = document.getElementById('deletion-search');
        const deletionDateFilter = document.getElementById('deletion-date-filter');
        const bulkApproveDeletionBtn = document.getElementById('bulk-approve-deletion-btn');
        const bulkRejectDeletionBtn = document.getElementById('bulk-reject-deletion-btn');
        
        if (deletionSearch) {
            deletionSearch.addEventListener('input', this.debounce(() => this.loadDeletionRequests(), 500));
        }
        
        if (deletionDateFilter) {
            deletionDateFilter.addEventListener('change', () => this.loadDeletionRequests());
        }
        
        if (bulkApproveDeletionBtn) {
            bulkApproveDeletionBtn.addEventListener('click', () => this.bulkApproveDeletions());
        }
        
        if (bulkRejectDeletionBtn) {
            bulkRejectDeletionBtn.addEventListener('click', () => this.bulkRejectDeletions());
        }
        
        // Write access request handlers
        const writeAccessSearch = document.getElementById('write-access-search');
        const writeAccessStatusFilter = document.getElementById('write-access-status-filter');
        const writeAccessDateFilter = document.getElementById('write-access-date-filter');
        
        if (writeAccessSearch) {
            writeAccessSearch.addEventListener('input', this.debounce(() => this.loadWriteAccessRequests(), 500));
        }
        
        if (writeAccessStatusFilter) {
            writeAccessStatusFilter.addEventListener('change', () => this.loadWriteAccessRequests());
        }
        
        if (writeAccessDateFilter) {
            writeAccessDateFilter.addEventListener('change', () => this.loadWriteAccessRequests());
        }
    }

    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => {
                    btn.classList.remove('active', 'bg-white', 'text-sa-warning');
                    btn.classList.add('bg-sa-warning-bg', 'text-sa-warning');
                });
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                button.classList.add('active', 'bg-white', 'text-sa-warning');
                button.classList.remove('bg-sa-warning-bg', 'text-sa-warning');
                document.getElementById(targetTab + '-tab').classList.add('active');
                
                // Load specific data for the tab if needed
                this.loadTabData(targetTab);
            });
        });
    }

    loadTabData(tabName) {
        switch(tabName) {
            case 'users':
                this.loadUsers();
                this.loadUserStats();
                break;
            case 'roles':
                this.loadRoles();
                this.loadRoleStats();
                break;
            case 'pending':
                this.loadPendingUsers();
                this.loadPendingStats();
                break;
            case 'deletion-requests':
                this.loadDeletionRequests();
                break;
            case 'performance':
                this.loadPerformanceData();
                break;
            case 'write-access':
                this.loadWriteAccessRequests();
                break;
        }
    }

    async loadUsers(page = 1) {
        try {
            const search = document.getElementById('search')?.value || '';
        const role = document.getElementById('role-filter')?.value || '';
        const status = document.getElementById('status-filter')?.value || '';
            const verification = document.getElementById('verification-filter')?.value || '';
        
        const params = new URLSearchParams({
            page: page,
            search: search,
            role: role,
                status: status,
                verification: verification
        });
        
            const response = await fetchWithCSRF(`/api/users?${params}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error:', response.status, errorText);
                throw new Error(`Failed to fetch users: ${response.status} ${errorText}`);
            }
        
        const data = await response.json();
            
            // Handle new API response format with pagination
            if (data.users && Array.isArray(data.users)) {
                this.users = data.users;
                this.pagination = data.pagination || {};
                this.currentPage = page;
            } else {
                // Fallback for old format
                this.users = Array.isArray(data) ? data : [];
                this.pagination = {};
                this.currentPage = page;
            }
            
            this.renderUsers();
            this.renderPagination();
            this.loadUserStats(); // Load statistics after users
    } catch (error) {
            console.error('Error loading users:', error);
            this.showToast('error', 'Gagal memuat daftar pengguna');
            this.showErrorInContainers(error.message);
        }
    }

    async loadUserStats() {
        try {
            const response = await fetchWithCSRF('/api/users/stats');
            if (!response.ok) {
                throw new Error('Failed to fetch user statistics');
            }
            
            const stats = await response.json();
            
            // Update statistics display
            const totalUsersElement = document.getElementById('total-users-count');
            const activeUsersElement = document.getElementById('active-users-count');
            const premiumUsersElement = document.getElementById('premium-users-count');
            const pendingUsersElement = document.getElementById('pending-users-count');
            
            if (totalUsersElement) totalUsersElement.textContent = stats.total_users || 0;
            if (activeUsersElement) activeUsersElement.textContent = stats.active_users || 0;
            if (premiumUsersElement) premiumUsersElement.textContent = stats.premium_users || 0;
            if (pendingUsersElement) pendingUsersElement.textContent = stats.pending_users || 0;
            
        } catch (error) {
            console.error('Error loading user statistics:', error);
        }
    }

    async loadRoleStats() {
        try {
            const response = await fetchWithCSRF('/api/roles');
            if (!response.ok) {
                throw new Error('Failed to fetch roles');
            }
            
            const roles = await response.json();
            
            // Update role statistics
            const totalRolesElement = document.getElementById('total-roles-count');
            const activeRolesElement = document.getElementById('active-roles-count');
            const totalPermissionsElement = document.getElementById('total-permissions-count');
            
            if (totalRolesElement) totalRolesElement.textContent = roles.length || 0;
            if (activeRolesElement) {
                const activeRoles = roles.filter(role => role.is_active).length;
                activeRolesElement.textContent = activeRoles;
            }
            
            // Load permissions count
            const permissionsResponse = await fetchWithCSRF('/api/permissions');
            if (permissionsResponse.ok) {
                const permissions = await permissionsResponse.json();
                if (totalPermissionsElement) totalPermissionsElement.textContent = permissions.length || 0;
            }
            
        } catch (error) {
            console.error('Error loading role statistics:', error);
        }
    }

    async loadPendingStats() {
        try {
            const response = await fetchWithCSRF('/api/pending/stats');
            if (!response.ok) {
                throw new Error('Failed to fetch pending statistics');
            }
            
            const stats = await response.json();
            
            // Update pending statistics
            const totalPendingElement = document.getElementById('total-pending-count');
            const approvedTodayElement = document.getElementById('approved-today-count');
            const rejectedTodayElement = document.getElementById('rejected-today-count');
            const avgApprovalTimeElement = document.getElementById('avg-approval-time');
            
            if (totalPendingElement) totalPendingElement.textContent = stats.total_pending || 0;
            if (approvedTodayElement) approvedTodayElement.textContent = stats.approved_today || 0;
            if (rejectedTodayElement) rejectedTodayElement.textContent = stats.rejected_today || 0;
            if (avgApprovalTimeElement) avgApprovalTimeElement.textContent = `${stats.avg_approval_time || 0} jam`;
            
        } catch (error) {
            console.error('Error loading pending statistics:', error);
        }
    }

    renderUsers() {
        const adminContainer = document.getElementById('admin-users');
        const generalContainer = document.getElementById('general-users');
        
        if (!adminContainer || !generalContainer) {
            console.error('User containers not found');
            return;
        }
        
        // Clear containers
        adminContainer.innerHTML = '';
        generalContainer.innerHTML = '';
        
        // Separate users by role
        const adminUsers = this.users.filter(user => user.role === 'SUPERUSER' || user.role === 'ADMIN');
        const generalUsers = this.users.filter(user => user.role === 'GENERAL');
        
        // Render admin users
        if (adminUsers.length === 0) {
            adminContainer.innerHTML = '<div class="col-span-full text-sa-warning">Tidak ada pengguna admin</div>';
        } else {
            adminUsers.forEach(user => {
                const userCard = this.createUserCard(user);
                adminContainer.appendChild(userCard);
            });
        }
        
        // Render general users
        if (generalUsers.length === 0) {
            generalContainer.innerHTML = '<div class="col-span-full text-sa-warning">Tidak ada pengguna umum</div>';
        } else {
            generalUsers.forEach(user => {
                const userCard = this.createUserCard(user);
                generalContainer.appendChild(userCard);
            });
        }
    }

    shouldShowPasswordResetButtons() {
        return window.currentUserData && window.currentUserData.role === 'SUPERUSER';
    }

    createUserCard(user) {
    const card = document.createElement('div');
        card.className = 'bg-white border border-sa-border rounded-lg p-4 hover:shadow-md transition-shadow';
    card.setAttribute('role', 'listitem');
    card.setAttribute('aria-label', `User: ${user.username}`);
    
    
        // Status and role badges
    const statusClass = user.is_suspended ? 'text-sa-critical bg-sa-critical-bg' : 'text-sa-success bg-sa-success-bg';
    const statusText = user.is_suspended ? 'Tersuspend' : 'Aktif';
        
        // Enhanced role display
        let roleBadge = '';
        if (user.role === 'SUPERUSER') {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-sa-critical-bg text-sa-critical">Superuser</span>';
        } else if (user.role === 'ADMIN') {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-sa-accent/10 text-sa-accent">Admin</span>';
        } else {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-sa-bg text-sa-muted">Umum</span>';
        }
        
        // Custom role badge if exists
        let customRoleBadge = '';
        if (user.custom_role && user.custom_role.name) {
            customRoleBadge = `<span class="px-2 py-1 text-xs rounded-full bg-sa-accent/10 text-sa-accent">${user.custom_role.name}</span>`;
        }
        
        // Additional info
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
        const displayName = fullName || user.username;
    
    card.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <input type="checkbox" name="user-select" value="${user.id}" class="rounded border-sa-border text-sa-accent focus:ring-sa-accent/30" onchange="usersManagement.updateSelectedCount()" title="Pilih untuk aksi massal">
                <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden" style="background: #f8f9fa;">
                    <svg width="40" height="40" data-jdenticon-value="${user.username || user.id}"></svg>
                </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-sa-warning">${displayName}</h3>
                        <p class="text-sm text-sa-warning">${user.email || 'Tidak ada email'}</p>
                        ${user.bio ? `<p class="text-xs text-sa-muted mt-1">${user.bio.substring(0, 50)}${user.bio.length > 50 ? '...' : ''}</p>` : ''}
                        <div class="flex items-center space-x-2 mt-2 flex-wrap gap-1">
                        <span class="px-2 py-1 text-xs rounded-full ${statusClass}">${statusText}</span>
                            ${roleBadge}
                            ${customRoleBadge}
                            ${user.verified ? '<span class="px-2 py-1 text-xs rounded-full bg-sa-success-bg text-sa-success">✓ Terverifikasi</span>' : ''}
                            ${user.is_premium ? '<span class="px-2 py-1 text-xs rounded-full bg-sa-warning-bg text-sa-warning">⭐ Premium</span>' : ''}
                        </div>
                </div>
            </div>
            <div class="flex space-x-2">
                    <button onclick="usersManagement.openEditUserModal(${user.id})" class="p-2 bg-sa-warning-bg hover:bg-sa-warning-bg/50 text-sa-warning rounded-full focus:outline-none focus:ring-2 focus:ring-sa-warning/30 transition-colors" title="Edit User">
                    <i class="fas fa-edit"></i>
                </button>
                    ${user.email ? `
                    <button onclick="usersManagement.openSendEmailModal(${user.id})" class="p-2 bg-sa-accent/10 hover:bg-sa-accent/10 text-sa-accent rounded-full focus:outline-none focus:ring-2 focus:ring-sa-accent/30 transition-colors" title="Kirim Email">
                        <i class="fas fa-envelope"></i>
                    </button>
                    ` : `
                    <button class="p-2 bg-sa-bg text-gray-400 rounded-full cursor-not-allowed" title="Tidak ada email" disabled>
                        <i class="fas fa-envelope"></i>
                    </button>
                    `}
                    ${this.shouldShowPasswordResetButtons() ? `
                    <button onclick="usersManagement.openPasswordResetModal(${user.id})" class="p-2 bg-sa-accent/10 hover:bg-blue-200 text-sa-accent rounded-full focus:outline-none focus:ring-2 focus:ring-sa-accent/30 transition-colors" title="Reset Password">
                    <i class="fas fa-key"></i>
                </button>
                    <button onclick="usersManagement.showDefaultPasswordModal(${user.id})" class="p-2 bg-sa-warning-bg hover:bg-sa-warning-bg/70 text-sa-warning rounded-full focus:outline-none focus:ring-2 focus:ring-orange-300 transition-colors" title="Change to Default Password">
                    <i class="fas fa-unlock-alt"></i>
                </button>
                    ` : ''}
                    <button onclick="usersManagement.showDeleteUserModal(${user.id})" class="p-2 bg-sa-critical-bg hover:bg-sa-critical-bg/70 text-sa-critical rounded-full focus:outline-none focus:ring-2 focus:ring-red-300 transition-colors" title="Delete User">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

renderPagination() {
    const paginationContainer = document.getElementById('users-pagination');
    if (!paginationContainer || !this.pagination) {
        return;
    }
    
    const { page, pages, has_next, has_prev } = this.pagination;
    
    if (pages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<nav class="flex items-center space-x-2" aria-label="Navigasi halaman pengguna">';
    
    // Previous button
    if (has_prev) {
        paginationHTML += `
            <button onclick="usersManagement.loadUsers(${page - 1})" 
                    class="px-3 py-2 bg-sa-warning-bg hover:bg-sa-warning-bg text-sa-warning rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 transition-colors">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;
    } else {
        paginationHTML += `
            <span class="px-3 py-2 bg-sa-bg text-gray-400 rounded-lg cursor-not-allowed">
                <i class="fas fa-chevron-left"></i>
            </span>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(pages, page + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <button onclick="usersManagement.loadUsers(1)" 
                    class="px-3 py-2 bg-sa-warning-bg hover:bg-sa-warning-bg text-sa-warning rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 transition-colors">
                1
            </button>
        `;
        if (startPage > 2) {
            paginationHTML += '<span class="px-2 text-sa-warning">...</span>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === page) {
            paginationHTML += `
                <span class="px-3 py-2 bg-amber-500 text-white rounded-lg font-semibold">
                    ${i}
                </span>
            `;
        } else {
            paginationHTML += `
                <button onclick="usersManagement.loadUsers(${i})" 
                        class="px-3 py-2 bg-sa-warning-bg hover:bg-sa-warning-bg text-sa-warning rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 transition-colors">
                    ${i}
                </button>
            `;
        }
    }
    
    if (endPage < pages) {
        if (endPage < pages - 1) {
            paginationHTML += '<span class="px-2 text-sa-warning">...</span>';
        }
        paginationHTML += `
            <button onclick="usersManagement.loadUsers(${pages})" 
                    class="px-3 py-2 bg-sa-warning-bg hover:bg-sa-warning-bg text-sa-warning rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 transition-colors">
                ${pages}
            </button>
        `;
    }
    
    // Next button
    if (has_next) {
        paginationHTML += `
            <button onclick="usersManagement.loadUsers(${page + 1})" 
                    class="px-3 py-2 bg-sa-warning-bg hover:bg-sa-warning-bg text-sa-warning rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 transition-colors">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
    } else {
        paginationHTML += `
            <span class="px-3 py-2 bg-sa-bg text-gray-400 rounded-lg cursor-not-allowed">
                <i class="fas fa-chevron-right"></i>
            </span>
        `;
    }
    
    paginationHTML += '</nav>';
    paginationContainer.innerHTML = paginationHTML;
}

    showErrorInContainers(errorMessage) {
        const adminContainer = document.getElementById('admin-users');
        const generalContainer = document.getElementById('general-users');
        
        if (adminContainer) {
            adminContainer.innerHTML = `<div class="col-span-full text-sa-critical">Error: ${errorMessage}</div>`;
        }
        if (generalContainer) {
            generalContainer.innerHTML = `<div class="col-span-full text-sa-critical">Error: ${errorMessage}</div>`;
        }
    }

    initFormHandlers() {
    // Edit user form
    const editForm = document.getElementById('edit-user-form');
    if (editForm) {
            editForm.addEventListener('submit', (e) => this.handleEditUser(e));
    }
    
    // Create user form
    const createUserForm = document.getElementById('create-user-form');
    if (createUserForm) {
        createUserForm.addEventListener('submit', (e) => this.handleCreateUser(e));
    }
    
    // Password reset form
    const passwordResetForm = document.getElementById('password-reset-form');
    if (passwordResetForm) {
        passwordResetForm.addEventListener('submit', (e) => this.handlePasswordReset(e));
    }
    
    // Send custom email form
    const sendEmailForm = document.getElementById('send-email-form');
    if (sendEmailForm) {
        sendEmailForm.addEventListener('submit', (e) => this.handleSendEmail(e));
    }
    
    // Create role form
    const createRoleForm = document.getElementById('create-role-form');
    if (createRoleForm) {
            createRoleForm.addEventListener('submit', (e) => this.handleCreateRole(e));
        }
        
        // Edit role form
        const editRoleForm = document.getElementById('edit-role-form');
        if (editRoleForm) {
            editRoleForm.addEventListener('submit', (e) => this.handleEditRole(e));
        }
    }

    async handleEditUser(e) {
    e.preventDefault();
        
        const isActive = document.getElementById('edit-is-active').checked;
        const isSuspended = document.getElementById('edit-is-suspended').checked;
        
        // If active is checked, force suspended to be false
        const finalSuspendedStatus = isActive ? false : isSuspended;
    
    const formData = {
        username: document.getElementById('edit-username').value.trim(),
        email: document.getElementById('edit-email').value.trim(),
            first_name: document.getElementById('edit-first-name').value.trim(),
            last_name: document.getElementById('edit-last-name').value.trim(),
            bio: document.getElementById('edit-bio').value.trim(),
        role: document.getElementById('edit-role').value,
        is_verified: document.getElementById('edit-verified').checked,
            is_suspended: finalSuspendedStatus,
        is_premium: document.getElementById('edit-is-premium').checked,
        suspension_reason: document.getElementById('edit-suspension-reason').value.trim(),
            suspension_until: document.getElementById('edit-suspension-until').value,
            custom_role_id: document.getElementById('edit-custom-role').value || null
    };
    
    try {
            const response = await fetchWithCSRF(`/api/users/${this.currentUserId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update user');
        }
        
            this.showToast('success', 'Pengguna berhasil diperbarui!');
            this.closeEditUserModal();
            this.loadUsers(this.currentPage);
    } catch (error) {
            this.showToast('error', `Gagal memperbarui pengguna: ${error.message}`);
    }
}

async handleCreateUser(e) {
    e.preventDefault();
    
    // Validate password confirmation
    const password = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('new-confirm-password').value;
    
    if (password !== confirmPassword) {
        this.showToast('error', 'Password tidak cocok!');
        return;
    }
    
    const formData = {
        username: document.getElementById('new-username').value.trim(),
        email: document.getElementById('new-email').value.trim(),
        password: password,
        first_name: document.getElementById('new-first-name').value.trim(),
        last_name: document.getElementById('new-last-name').value.trim(),
        bio: document.getElementById('new-bio').value.trim(),
        role: document.getElementById('new-role').value,
        custom_role_id: document.getElementById('new-custom-role').value || null,
        is_active: document.getElementById('new-is-active').checked,
        verified: document.getElementById('new-verified').checked,
        is_premium: document.getElementById('new-is-premium').checked,
        premium_duration: document.getElementById('new-premium-duration')?.value,
        send_welcome_email: document.getElementById('new-send-welcome-email').checked,
        premium_features: {
            ads_free: document.getElementById('new-premium-ads-free')?.checked || false,
            priority_support: document.getElementById('new-premium-priority')?.checked || false,
            advanced_features: document.getElementById('new-premium-advanced')?.checked || false
        }
    };
    
    try {
        const response = await fetchWithCSRF('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create user');
        }
        
        const result = await response.json();
        this.showToast('success', 'Pengguna berhasil dibuat!');
        this.closeCreateUserModal();
        this.loadUsers(1); // Reload users to show the new user
        this.loadUserStats(); // Reload statistics
    } catch (error) {
        this.showToast('error', `Gagal membuat pengguna: ${error.message}`);
    }
}

async handlePasswordReset(e) {
    e.preventDefault();
    
    const newPassword = document.getElementById('new-password-reset').value;
    const confirmPassword = document.getElementById('confirm-password-reset').value;
    
    // Validate password confirmation
    if (newPassword !== confirmPassword) {
        this.showToast('error', 'Password dan konfirmasi password tidak cocok');
        return;
    }
    
    if (newPassword.length < 6) {
        this.showToast('error', 'Password harus minimal 6 karakter');
        return;
    }
    
    const formData = {
        new_password: newPassword,
        send_email: document.getElementById('send-email-reset').checked
    };
    
    try {
        const response = await fetchWithCSRF(`/api/users/${this.currentUserId}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            let errorMessage = 'Failed to reset password';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (parseError) {
                // If response is not JSON, get text
                const errorText = await response.text();
                errorMessage = errorText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        this.showToast('success', 'Password berhasil direset!');
        this.closePasswordResetModal();
    } catch (error) {
        this.showToast('error', `Gagal reset password: ${error.message}`);
    }
}

async handleSendEmail(e) {
    e.preventDefault();
    
    const subject = document.getElementById('email-subject').value.trim();
    const message = document.getElementById('email-message').value.trim();
    
    if (!subject || !message) {
        this.showToast('error', 'Subjek dan pesan harus diisi');
        return;
    }
    
    const formData = {
        subject: subject,
        message: message
    };
    
    // Disable submit button during processing
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Kirim Email';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Mengirim...';
    }
    
    try {
        const response = await fetchWithCSRF(`/api/users/${this.currentUserId}/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            let errorMessage = 'Failed to send email';
            try {
                const error = await response.json();
                errorMessage = error.error || errorMessage;
            } catch (parseError) {
                const errorText = await response.text();
                errorMessage = errorText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        this.showToast('success', 'Email berhasil dikirim!');
        this.closeSendEmailModal();
    } catch (error) {
        this.showToast('error', `Gagal mengirim email: ${error.message}`);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    }
}

    async handleCreateRole(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('role-name').value.trim(),
        description: document.getElementById('role-description').value.trim(),
            is_active: true,
            permission_ids: this.getSelectedPermissions()
    };
    
    try {
        const response = await fetchWithCSRF('/api/roles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create role');
        }
        
            this.showToast('success', 'Peran berhasil dibuat!');
            this.closeCreateRoleModal();
            this.loadRoles();
    } catch (error) {
            this.showToast('error', `Gagal membuat peran: ${error.message}`);
    }
}

    getSelectedPermissions() {
    const checkboxes = document.querySelectorAll('#permissions-list input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

    openEditUserModal(userId) {
        this.currentUserId = userId;
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            this.showToast('error', 'User tidak ditemukan');
            return;
        }

        // Populate form fields with enhanced data handling
        document.getElementById('edit-username').value = user.username || '';
        document.getElementById('edit-email').value = user.email || '';
        document.getElementById('edit-first-name').value = user.first_name || '';
        document.getElementById('edit-last-name').value = user.last_name || '';
        document.getElementById('edit-bio').value = user.bio || '';
        document.getElementById('edit-role').value = user.role || 'user';
        document.getElementById('edit-verified').checked = user.verified || false;
        document.getElementById('edit-is-active').checked = !user.is_suspended; // Active is opposite of suspended
        document.getElementById('edit-is-suspended').checked = user.is_suspended || false;
        document.getElementById('edit-is-premium').checked = user.is_premium || false;
    document.getElementById('edit-suspension-reason').value = user.suspension_reason || '';
        
        // Format datetime for datetime-local input (YYYY-MM-DDTHH:MM)
        let suspensionUntil = '';
        if (user.suspension_until) {
            const date = new Date(user.suspension_until);
            if (!isNaN(date.getTime())) {
                // Format as YYYY-MM-DDTHH:MM for datetime-local input
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                suspensionUntil = `${year}-${month}-${day}T${hours}:${minutes}`;
            }
        }
        document.getElementById('edit-suspension-until').value = suspensionUntil;

        // Populate custom role dropdown with proper handling
        const customRoleId = user.custom_role_id || user.custom_role?.id || null;
        this.populateCustomRoleDropdown(customRoleId);
    
    // Show/hide suspension details
        this.toggleSuspensionDetails(user.is_suspended);
    
        // Show modal
    document.getElementById('edit-user-modal').classList.remove('hidden');
        

    }

    async populateCustomRoleDropdown(selectedRoleId = null) {
        try {
            const response = await fetchWithCSRF('/api/roles');
            if (response.ok) {
                const roles = await response.json();
                const editDropdown = document.getElementById('edit-custom-role');
                const createDropdown = document.getElementById('new-custom-role');
                
                // Clear and populate edit dropdown
                if (editDropdown) {
                    editDropdown.innerHTML = '<option value="">Tidak ada peran kustom</option>';
                    roles.forEach(role => {
                        const option = document.createElement('option');
                        option.value = role.id;
                        option.textContent = role.name;
                        if (selectedRoleId && role.id === parseInt(selectedRoleId)) {
                            option.selected = true;
                        }
                        editDropdown.appendChild(option);
                    });
                }
                
                // Clear and populate create dropdown
                if (createDropdown) {
                    createDropdown.innerHTML = '<option value="">Tidak ada peran kustom</option>';
                    roles.forEach(role => {
                        const option = document.createElement('option');
                        option.value = role.id;
                        option.textContent = role.name;
                        createDropdown.appendChild(option);
                    });
                }

            } else {
                console.error('Failed to load custom roles:', response.status);
            }
        } catch (error) {
            console.error('Error loading custom roles for dropdown:', error);
        }
    }

    closeEditUserModal() {
    document.getElementById('edit-user-modal').classList.add('hidden');
        this.currentUserId = null;
}

    showDeleteUserModal(userId) {
        this.currentUserId = userId;
    document.getElementById('delete-user-modal').classList.remove('hidden');
}

    closeDeleteUserModal() {
    document.getElementById('delete-user-modal').classList.add('hidden');
        this.currentUserId = null;
    }

    async confirmDeleteUser() {
        try {
            const response = await fetchWithCSRF(`/api/users/${this.currentUserId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete user');
            }
            
            this.showToast('success', 'Pengguna berhasil dihapus!');
            this.closeDeleteUserModal();
            this.loadUsers(this.currentPage);
        } catch (error) {
            this.showToast('error', `Gagal menghapus pengguna: ${error.message}`);
        }
    }

    closeCreateRoleModal() {
    document.getElementById('create-role-modal').classList.add('hidden');
}

    openCreateRoleModal() {
        // Clear form fields
        document.getElementById('role-name').value = '';
        document.getElementById('role-description').value = '';
        
        // Clear all permission checkboxes
        const checkboxes = document.querySelectorAll('#permissions-list input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
        
        // Show modal
        document.getElementById('create-role-modal').classList.remove('hidden');
    }

    toggleSuspensionDetails(isSuspended) {
    const details = document.getElementById('suspension-details');
        if (isSuspended) {
            details.classList.remove('hidden');
        } else {
            details.classList.add('hidden');
        }
    }

    async loadRoles() {
        try {
            
            // Load custom roles
            const customRolesResponse = await fetchWithCSRF('/api/roles');
            if (customRolesResponse.ok) {
                const customRoles = await customRolesResponse.json();
                this.renderCustomRoles(customRoles);
            }
            
            // Load permissions
            const permissionsResponse = await fetchWithCSRF('/api/permissions');
            if (permissionsResponse.ok) {
                const permissions = await permissionsResponse.json();
                this.renderPermissions(permissions);
                this.populatePermissionsList(permissions);
            }
        } catch (error) {
            console.error('Error loading roles:', error);
            this.showToast('error', 'Gagal memuat peran dan izin');
        }
    }

    populatePermissionsList(permissions) {
        // Populate create permissions list
        const container = document.getElementById('permissions-list');
        if (container) {
            container.innerHTML = permissions.map(permission => `
                <div class="flex items-center space-x-2">
                    <input type="checkbox" id="perm-${permission.id}" value="${permission.id}" class="rounded border-amber-300 text-sa-warning focus:ring-amber-300">
                    <label for="perm-${permission.id}" class="text-sm text-sa-warning">
                        ${permission.name} (${permission.resource}:${permission.action})
                    </label>
                </div>
            `).join('');
        }
        
        // Populate edit permissions list
        const editContainer = document.getElementById('edit-permissions-list');
        if (editContainer) {
            editContainer.innerHTML = permissions.map(permission => `
                <div class="flex items-center space-x-2">
                    <input type="checkbox" id="edit-perm-${permission.id}" value="${permission.id}" class="rounded border-amber-300 text-sa-warning focus:ring-amber-300">
                    <label for="edit-perm-${permission.id}" class="text-sm text-sa-warning">
                        ${permission.name} (${permission.resource}:${permission.action})
                    </label>
                </div>
            `).join('');
        }
    }

    renderCustomRoles(roles) {
        const container = document.getElementById('custom-roles');
        if (!container) return;
        
        if (roles.length === 0) {
            container.innerHTML = '<div class="text-sa-warning">Tidak ada peran kustom</div>';
            return;
        }
        
        container.innerHTML = roles.map(role => `
            <div class="bg-white border border-sa-border rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-sa-warning">${role.name}</h4>
                        <p class="text-sm text-sa-warning">${role.description || 'Tidak ada deskripsi'}</p>
                        <div class="flex items-center space-x-2 mt-2">
                            <span class="px-2 py-1 text-xs rounded-full ${role.is_active ? 'bg-sa-success-bg text-sa-success' : 'bg-sa-critical-bg text-sa-critical'}">
                                ${role.is_active ? 'Aktif' : 'Tidak Aktif'}
                            </span>
                            <span class="text-xs text-sa-warning">${role.permissions?.length || 0} izin</span>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="usersManagement.editRole(${role.id})" class="p-2 bg-sa-warning-bg hover:bg-sa-warning-bg/50 text-sa-warning rounded-full">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="usersManagement.deleteRole(${role.id})" class="p-2 bg-sa-critical-bg hover:bg-sa-critical-bg/70 text-sa-critical rounded-full">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderPermissions(permissions) {
        const container = document.getElementById('permissions');
        if (!container) return;
        
        if (permissions.length === 0) {
            container.innerHTML = '<div class="text-sa-warning">Tidak ada izin</div>';
            return;
        }
        
        container.innerHTML = permissions.map(permission => `
            <div class="bg-white border border-sa-border rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-sa-warning">${permission.name}</h4>
                        <p class="text-sm text-sa-warning">${permission.description || 'Tidak ada deskripsi'}</p>
                        <div class="flex items-center space-x-2 mt-2">
                            <span class="px-2 py-1 text-xs rounded-full bg-sa-accent/10 text-sa-accent">${permission.resource}</span>
                            <span class="px-2 py-1 text-xs rounded-full bg-sa-accent/10 text-sa-accent">${permission.action}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadPendingUsers() {
        try {
            
            const response = await fetchWithCSRF('/api/registrations/pending');
            if (!response.ok) {
                throw new Error('Failed to fetch pending users');
            }
            
            const pendingUsers = await response.json();
            this.renderPendingUsers(pendingUsers);
        } catch (error) {
            console.error('Error loading pending users:', error);
            this.showToast('error', 'Gagal memuat pengguna yang menunggu persetujuan');
        }
    }

    async loadDeletionRequests() {
        try {
            const response = await fetchWithCSRF('/api/users/deletion-requests');
            if (!response.ok) {
                throw new Error('Failed to fetch deletion requests');
            }
            
            const data = await response.json();
            this.renderDeletionRequests(data.deletion_requests || []);
            this.updateDeletionStats(data);
        } catch (error) {
            console.error('Error loading deletion requests:', error);
            this.showToast('error', 'Gagal memuat permintaan penghapusan');
        }
    }

    renderDeletionRequests(requests) {
        const container = document.getElementById('deletion-requests-list');
        if (!container) return;
        
        if (requests.length === 0) {
            container.innerHTML = '<div class="text-sa-muted">Tidak ada permintaan penghapusan akun yang menunggu</div>';
            return;
        }
        
        container.innerHTML = requests.map(request => `
            <div class="bg-white border border-sa-critical/30 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden" style="background: #f8f9fa;">
                            <svg width="40" height="40" data-jdenticon-value="${request.username || request.user_id}"></svg>
                        </div>
                        <div>
                            <h4 class="font-semibold text-sa-critical">${request.username}</h4>
                            <p class="text-sm text-sa-critical">${request.email || 'Tidak ada email'}</p>
                            <p class="text-xs text-sa-critical">Daftar: ${new Date(request.created_at).toLocaleDateString('id-ID')}</p>
                            <p class="text-xs text-sa-critical">Permintaan: ${new Date(request.deletion_requested_at).toLocaleDateString('id-ID')}</p>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="usersManagement.approveDeletion(${request.id})" class="px-3 py-1 bg-sa-critical-bg hover:bg-sa-critical-bg text-white rounded text-sm">
                            <i class="fas fa-check mr-1"></i>Setujui
                        </button>
                        <button onclick="usersManagement.rejectDeletion(${request.id})" class="px-3 py-1 bg-sa-success-bg hover:bg-sa-success-bg text-white rounded text-sm">
                            <i class="fas fa-times mr-1"></i>Tolak
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateDeletionStats(data) {
        const totalRequests = document.getElementById('total-deletion-requests');
        const approvedToday = document.getElementById('approved-deletions-today');
        const rejectedToday = document.getElementById('rejected-deletions-today');
        const avgTime = document.getElementById('avg-deletion-time');
        
        if (totalRequests) totalRequests.textContent = data.total || 0;
        if (approvedToday) approvedToday.textContent = '0'; // TODO: Add API for today's stats
        if (rejectedToday) rejectedToday.textContent = '0'; // TODO: Add API for today's stats
        if (avgTime) avgTime.textContent = '-'; // TODO: Add API for average time
    }

    async approveDeletion(userId) {
        try {
            const response = await fetchWithCSRF(`/api/users/${userId}/approve-deletion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to approve deletion');
            }
            
            const result = await response.json();
            this.showToast('success', result.message || 'Permintaan penghapusan disetujui');
            this.loadDeletionRequests();
        } catch (error) {
            console.error('Error approving deletion:', error);
            this.showToast('error', error.message || 'Gagal menyetujui permintaan penghapusan');
        }
    }

    async rejectDeletion(userId) {
        try {
            const response = await fetchWithCSRF(`/api/users/${userId}/reject-deletion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to reject deletion');
            }
            
            const result = await response.json();
            this.showToast('success', result.message || 'Permintaan penghapusan ditolak');
            this.loadDeletionRequests();
        } catch (error) {
            console.error('Error rejecting deletion:', error);
            this.showToast('error', error.message || 'Gagal menolak permintaan penghapusan');
        }
    }

    async bulkApproveDeletions() {
        if (!confirm('Apakah Anda yakin ingin menyetujui semua permintaan penghapusan? Tindakan ini tidak dapat dibatalkan.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/users/deletion-requests');
            if (!response.ok) {
                throw new Error('Failed to fetch deletion requests');
            }
            
            const data = await response.json();
            const requests = data.deletion_requests || [];
            
            if (requests.length === 0) {
                this.showToast('info', 'Tidak ada permintaan penghapusan untuk disetujui');
                return;
            }
            
            let approvedCount = 0;
            for (const request of requests) {
                try {
                    await this.approveDeletion(request.id);
                    approvedCount++;
                } catch (error) {
                    console.error(`Error approving deletion for user ${request.id}:`, error);
                }
            }
            
            this.showToast('success', `${approvedCount} permintaan penghapusan berhasil disetujui`);
            this.loadDeletionRequests();
        } catch (error) {
            console.error('Error bulk approving deletions:', error);
            this.showToast('error', 'Gagal menyetujui permintaan penghapusan secara massal');
        }
    }

    async bulkRejectDeletions() {
        if (!confirm('Apakah Anda yakin ingin menolak semua permintaan penghapusan?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/users/deletion-requests');
            if (!response.ok) {
                throw new Error('Failed to fetch deletion requests');
            }
            
            const data = await response.json();
            const requests = data.deletion_requests || [];
            
            if (requests.length === 0) {
                this.showToast('info', 'Tidak ada permintaan penghapusan untuk ditolak');
                return;
            }
            
            let rejectedCount = 0;
            for (const request of requests) {
                try {
                    await this.rejectDeletion(request.id);
                    rejectedCount++;
                } catch (error) {
                    console.error(`Error rejecting deletion for user ${request.id}:`, error);
                }
            }
            
            this.showToast('success', `${rejectedCount} permintaan penghapusan berhasil ditolak`);
            this.loadDeletionRequests();
        } catch (error) {
            console.error('Error bulk rejecting deletions:', error);
            this.showToast('error', 'Gagal menolak permintaan penghapusan secara massal');
        }
    }

    renderPendingUsers(users) {
        const container = document.getElementById('pending-users');
        if (!container) return;
        
        if (users.length === 0) {
            container.innerHTML = '<div class="text-sa-warning">Tidak ada pengguna yang menunggu persetujuan</div>';
            return;
        }
        
        container.innerHTML = users.map(user => `
            <div class="bg-white border border-sa-border rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden" style="background: #f8f9fa;">
                            <svg width="40" height="40" data-jdenticon-value="${user.username || user.id}"></svg>
                        </div>
                        <div>
                            <h4 class="font-semibold text-sa-warning">${user.username}</h4>
                            <p class="text-sm text-sa-warning">${user.email || 'Tidak ada email'}</p>
                            <p class="text-xs text-sa-warning">Daftar: ${new Date(user.created_at).toLocaleDateString('id-ID')}</p>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="usersManagement.approveUser(${user.id})" class="px-3 py-1 bg-sa-success-bg hover:bg-sa-success-bg text-white rounded text-sm">
                            <i class="fas fa-check mr-1"></i>Setujui
                        </button>
                        <button onclick="usersManagement.rejectUser(${user.id})" class="px-3 py-1 bg-sa-critical-bg hover:bg-sa-critical-bg text-white rounded text-sm">
                            <i class="fas fa-times mr-1"></i>Tolak
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadPerformanceData() {
        try {
            
            const period = document.getElementById('performance-period')?.value || '30';
            
            // Load performance summary
            const summaryResponse = await fetch(`/api/users/performance/report?days=${period}`);
            if (summaryResponse.ok) {
                const summary = await summaryResponse.json();
                this.renderPerformanceSummary(summary);
            }
            
            // Load leaderboard
            const leaderboardResponse = await fetch(`/api/users/performance/leaderboard`);
            if (leaderboardResponse.ok) {
                const leaderboard = await leaderboardResponse.json();
                this.renderPerformanceLeaderboard(leaderboard);
            }
        } catch (error) {
            console.error('Error loading performance data:', error);
            this.showToast('error', 'Gagal memuat data performa');
        }
    }

    renderPerformanceSummary(summary) {
        // Update summary cards
        const activeUsersCount = document.getElementById('active-users-count');
        const totalActivities = document.getElementById('total-activities');
        const totalContent = document.getElementById('total-content');
        const avgEngagement = document.getElementById('avg-engagement');
        
        // The API returns data in a nested structure
        const summaryData = summary.summary || summary;
        
        if (activeUsersCount) activeUsersCount.textContent = summaryData.active_users || '-';
        if (totalActivities) totalActivities.textContent = summaryData.total_activities || '-';
        if (totalContent) totalContent.textContent = (summaryData.total_news + summaryData.total_images + summaryData.total_videos) || '-';
        
        // Calculate average engagement score from users data
        if (avgEngagement && summary.users && summary.users.length > 0) {
            const totalScore = summary.users.reduce((sum, user) => sum + user.engagement_score, 0);
            const avgScore = Math.round(totalScore / summary.users.length);
            avgEngagement.textContent = avgScore;
        } else if (avgEngagement) {
            avgEngagement.textContent = '-';
        }
    }

    renderPerformanceLeaderboard(leaderboard) {
        const container = document.getElementById('performance-leaderboard');
        if (!container) return;
        
        if (!leaderboard.leaderboard || leaderboard.leaderboard.length === 0) {
            container.innerHTML = '<div class="text-sa-warning">Tidak ada data performa</div>';
            return;
        }
        
        container.innerHTML = leaderboard.leaderboard.map((entry, index) => {
            const user = entry.user;
            const metrics = entry.metrics;
            
            return `
                <div class="bg-white border border-sa-border rounded-lg p-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full flex items-center justify-center">
                                <span class="text-white font-semibold text-xs">${index + 1}</span>
                            </div>
                            <div>
                                <h4 class="font-semibold text-sa-warning">${user.username}</h4>
                                <p class="text-sm text-sa-warning">${user.role}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-lg font-bold text-sa-warning">${metrics.engagement_score}</div>
                            <div class="text-xs text-sa-warning">Skor</div>
                        </div>
                    </div>
                    <div class="mt-3 grid grid-cols-3 gap-2 text-xs">
                        <div class="text-center">
                            <div class="font-semibold text-sa-accent">${metrics.news_count}</div>
                            <div class="text-sa-muted">Berita</div>
                        </div>
                        <div class="text-center">
                            <div class="font-semibold text-sa-success">${metrics.images_count}</div>
                            <div class="text-sa-muted">Gambar</div>
                        </div>
                        <div class="text-center">
                            <div class="font-semibold text-sa-accent">${metrics.videos_count}</div>
                            <div class="text-sa-muted">Video</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Additional methods for role management
    async editRole(roleId) {
        try {
            // Get role details
            const roleResponse = await fetch(`/api/roles/${roleId}`);
            if (!roleResponse.ok) {
                throw new Error('Failed to fetch role details');
            }
            
            const role = await roleResponse.json();
            
            // Get role permissions
            const permissionsResponse = await fetch(`/api/roles/${roleId}/permissions`);
            const rolePermissions = permissionsResponse.ok ? await permissionsResponse.json() : [];
            
            // Populate edit form
            document.getElementById('edit-role-name').value = role.name;
            document.getElementById('edit-role-description').value = role.description || '';
            document.getElementById('edit-role-active').checked = role.is_active;
            
            // Clear and set permissions
            const permissionCheckboxes = document.querySelectorAll('#edit-permissions-list input[type="checkbox"]');
            permissionCheckboxes.forEach(cb => {
                cb.checked = rolePermissions.some(p => p.id === parseInt(cb.value));
            });
            
            // Store role ID for update
            this.currentRoleId = roleId;
            
            // Show edit modal
            document.getElementById('edit-role-modal').classList.remove('hidden');
        } catch (error) {
            console.error('Error loading role for edit:', error);
            this.showToast('error', 'Gagal memuat detail peran');
        }
    }

    async deleteRole(roleId) {
        // Store role ID for confirmation
        this.currentRoleId = roleId;
        
        // Show confirmation modal
        document.getElementById('delete-role-modal').classList.remove('hidden');
    }

    async confirmDeleteRole() {
        try {
            const response = await fetchWithCSRF(`/api/roles/${this.currentRoleId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete role');
            }
            
            this.showToast('success', 'Peran berhasil dihapus!');
            this.closeDeleteRoleModal();
            this.loadRoles();
        } catch (error) {
            this.showToast('error', `Gagal menghapus peran: ${error.message}`);
        }
    }

    closeDeleteRoleModal() {
        document.getElementById('delete-role-modal').classList.add('hidden');
        this.currentRoleId = null;
    }

    async handleEditRole(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('edit-role-name').value.trim(),
            description: document.getElementById('edit-role-description').value.trim(),
            is_active: document.getElementById('edit-role-active').checked,
            permission_ids: this.getSelectedEditPermissions()
        };
        
        try {
            const response = await fetchWithCSRF(`/api/roles/${this.currentRoleId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update role');
            }
            
            this.showToast('success', 'Peran berhasil diperbarui!');
            this.closeEditRoleModal();
            this.loadRoles();
        } catch (error) {
            this.showToast('error', `Gagal memperbarui peran: ${error.message}`);
        }
    }

    getSelectedEditPermissions() {
        const checkboxes = document.querySelectorAll('#edit-permissions-list input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => parseInt(cb.value));
    }

    closeEditRoleModal() {
        document.getElementById('edit-role-modal').classList.add('hidden');
        this.currentRoleId = null;
    }

    // Additional methods for user approval
    async approveUser(userId) {
        try {
            const response = await fetchWithCSRF(`/api/registrations/${userId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to approve user');
            }
            
            this.showToast('success', 'Pengguna berhasil disetujui!');
            this.loadPendingUsers();
        } catch (error) {
            this.showToast('error', `Gagal menyetujui pengguna: ${error.message}`);
        }
    }

    async rejectUser(userId) {
        try {
            const response = await fetchWithCSRF(`/api/registrations/${userId}/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason: 'Ditolak oleh administrator' })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to reject user');
            }
            
            this.showToast('success', 'Pengguna berhasil ditolak!');
            this.loadPendingUsers();
        } catch (error) {
            this.showToast('error', `Gagal menolak pengguna: ${error.message}`);
        }
    }

    toggleBulkActions() {
        const panel = document.getElementById('bulk-actions-panel');
        if (panel) {
            panel.classList.toggle('hidden');
        }
    }

    async bulkUpdateUserStatus(isActive) {
        const selectedUsers = this.getSelectedUsers();
        if (selectedUsers.length === 0) {
            this.showToast('warning', 'Pilih pengguna terlebih dahulu');
            return;
        }

        const action = isActive ? 'mengaktifkan' : 'menonaktifkan';
        if (!confirm(`Apakah Anda yakin ingin ${action} ${selectedUsers.length} pengguna?`)) {
            return;
        }

        try {
            const response = await fetchWithCSRF('/api/users/bulk/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_ids: selectedUsers,
                    is_active: isActive
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update user status');
            }

            const result = await response.json();
            this.showToast('success', result.message || `Berhasil ${action} ${result.updated_count || selectedUsers.length} pengguna`);
            this.loadUsers(this.currentPage);
            this.clearUserSelection();
        } catch (error) {
            this.showToast('error', `Gagal ${action} pengguna: ${error.message}`);
        }
    }

    async bulkVerifyUsers(verified) {
        const selectedUsers = this.getSelectedUsers();
        if (selectedUsers.length === 0) {
            this.showToast('warning', 'Pilih pengguna terlebih dahulu');
            return;
        }

        const action = verified ? 'memverifikasi' : 'membatalkan verifikasi';
        if (!confirm(`Apakah Anda yakin ingin ${action} ${selectedUsers.length} pengguna?`)) {
            return;
        }

        try {
            const response = await fetchWithCSRF('/api/users/bulk/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_ids: selectedUsers,
                    verified: verified
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update user verification');
            }

            const result = await response.json();
            this.showToast('success', result.message || `Berhasil ${action} ${result.updated_count || selectedUsers.length} pengguna`);
            this.loadUsers(this.currentPage);
            this.clearUserSelection();
        } catch (error) {
            this.showToast('error', `Gagal ${action} pengguna: ${error.message}`);
        }
    }

    async bulkSuspendUsers(suspend) {
        const selectedUsers = this.getSelectedUsers();
        if (selectedUsers.length === 0) {
            this.showToast('warning', 'Pilih pengguna terlebih dahulu');
            return;
        }

        const action = suspend ? 'mensuspend' : 'menghentikan suspend';
        if (!confirm(`Apakah Anda yakin ingin ${action} ${selectedUsers.length} pengguna?`)) {
            return;
        }

        try {
            const response = await fetchWithCSRF('/api/users/bulk/suspend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_ids: selectedUsers,
                    suspend: suspend,
                    reason: 'Bulk suspension by admin'
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to update user suspension');
            }

            const result = await response.json();
            this.showToast('success', result.message || `Berhasil ${action} ${result.updated_count || selectedUsers.length} pengguna`);
            this.loadUsers(this.currentPage);
            this.clearUserSelection();
        } catch (error) {
            this.showToast('error', `Gagal ${action} pengguna: ${error.message}`);
        }
    }

    getSelectedUsers() {
        // Get selected user IDs from checkboxes
        const checkboxes = document.querySelectorAll('input[type="checkbox"][name="user-select"]:checked');
        return Array.from(checkboxes).map(cb => parseInt(cb.value));
    }

    clearUserSelection() {
        // Clear all user selection checkboxes
        const checkboxes = document.querySelectorAll('input[type="checkbox"][name="user-select"]');
        checkboxes.forEach(cb => cb.checked = false);
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const selectedCount = document.getElementById('selected-count');
        if (selectedCount) {
            const count = this.getSelectedUsers().length;
            selectedCount.textContent = count;
            
            // Show/hide bulk actions button based on selection
            const bulkActionsBtn = document.getElementById('bulk-actions-btn');
            if (bulkActionsBtn) {
                if (count > 0) {
                    bulkActionsBtn.classList.remove('hidden');
                } else {
                    bulkActionsBtn.classList.add('hidden');
                }
            }
        }
    }

    async exportUsers() {
        try {
            const response = await fetchWithCSRF('/api/users/bulk/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ format: 'csv' })
            });
            
            if (!response.ok) {
                throw new Error('Failed to export users');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'users-export.csv';
            a.click();
            window.URL.revokeObjectURL(url);
            
            this.showToast('success', 'Ekspor berhasil!');
        } catch (error) {
            this.showToast('error', 'Gagal mengekspor pengguna');
        }
    }

    async exportPerformance() {
        try {
            const period = document.getElementById('performance-period')?.value || '30';
            const response = await fetchWithCSRF(`/api/users/performance/report/export?days=${period}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ format: 'csv' })
            });

            if (!response.ok) {
                throw new Error('Failed to export performance report');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'performance-report.csv';
            a.click();
            window.URL.revokeObjectURL(url);

            this.showToast('success', 'Ekspor laporan performa berhasil!');
        } catch (error) {
            this.showToast('error', 'Gagal mengekspor laporan performa');
        }
    }

    async exportRoles() {
        try {
            const response = await fetchWithCSRF('/api/roles/bulk/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ format: 'csv' })
            });

            if (!response.ok) {
                throw new Error('Failed to export roles');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'roles-export.csv';
            a.click();
            window.URL.revokeObjectURL(url);

            this.showToast('success', 'Ekspor peran berhasil!');
        } catch (error) {
            this.showToast('error', 'Gagal mengekspor peran');
        }
    }

    debounce(func, wait) {
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

    showToast(message, type = 'info') {
        if (typeof showToast === 'function') {
            showToast(type, message);
        }
    }

    // Modal functions for new features
    openCreateUserModal() {
        const modal = document.getElementById('create-user-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            // Load custom roles when modal opens
            this.populateCustomRoleDropdown();
        }
    }

    closeCreateUserModal() {
        const modal = document.getElementById('create-user-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            // Reset form
            const form = document.getElementById('create-user-form');
            if (form) form.reset();
            // Hide premium settings
            const premiumSettings = document.getElementById('premium-settings');
            if (premiumSettings) {
                premiumSettings.classList.add('hidden');
            }
            // Clear username status
            const usernameStatus = document.getElementById('username-status');
            if (usernameStatus) {
                usernameStatus.classList.add('hidden');
            }
            // Reset username field styling
            const usernameField = document.getElementById('new-username');
            if (usernameField) {
                usernameField.classList.remove('border-sa-critical');
                usernameField.classList.add('border-sa-border');
            }
            // Clear email status
            const emailStatus = document.getElementById('email-status');
            if (emailStatus) {
                emailStatus.classList.add('hidden');
            }
            // Reset email field styling
            const emailField = document.getElementById('new-email');
            if (emailField) {
                emailField.classList.remove('border-sa-critical');
                emailField.classList.add('border-sa-border');
            }
        }
    }

    openUserDetailsModal(userId) {
        this.currentUserId = userId;
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            this.showToast('error', 'User tidak ditemukan');
            return;
        }

        // Generate user details HTML
        const detailsHTML = this.generateUserDetailsHTML(user);
        const detailsContainer = document.getElementById('user-details-content');
        if (detailsContainer) {
            detailsContainer.innerHTML = detailsHTML;
        }

        const modal = document.getElementById('user-details-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    closeUserDetailsModal() {
        const modal = document.getElementById('user-details-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    openPasswordResetModal(userId) {
        this.currentUserId = userId;
        const modal = document.getElementById('password-reset-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            // Reset form
            const form = document.getElementById('password-reset-form');
            if (form) form.reset();
            // Set the user ID in the hidden field
            const userIdField = document.getElementById('reset-user-id');
            if (userIdField) userIdField.value = userId;
        }
    }

    closePasswordResetModal() {
        const modal = document.getElementById('password-reset-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    openSendEmailModal(userId) {
        this.currentUserId = userId;
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            this.showToast('error', 'Pengguna tidak ditemukan');
            return;
        }
        
        const modal = document.getElementById('send-email-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            
            // Reset form
            const form = document.getElementById('send-email-form');
            if (form) form.reset();
            
            // Set fields
            const userIdField = document.getElementById('email-user-id');
            if (userIdField) userIdField.value = userId;
            
            const recipientField = document.getElementById('email-recipient');
            if (recipientField) {
                const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
                recipientField.value = `${fullName || user.username} (${user.email})`;
            }
        }
    }

    closeSendEmailModal() {
        const modal = document.getElementById('send-email-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    showDefaultPasswordModal(userId) {
        this.currentUserId = userId;
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            this.showToast('error', 'User tidak ditemukan');
            return;
        }

        // Store the username for confirmation
        this.currentUsername = user.username;
        
        // Reset the confirmation input
        const confirmInput = document.getElementById('confirm-username');
        if (confirmInput) {
            confirmInput.value = '';
        }

        const modal = document.getElementById('default-password-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    closeDefaultPasswordModal() {
        const modal = document.getElementById('default-password-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
        this.currentUserId = null;
        this.currentUsername = null;
    }

    async confirmDefaultPasswordReset() {
        const confirmInput = document.getElementById('confirm-username');
        const enteredUsername = confirmInput.value.trim();
        
        if (enteredUsername !== this.currentUsername) {
            this.showToast('error', 'Username tidak cocok. Silakan ketik username yang benar.');
            return;
        }

        try {
            const response = await fetchWithCSRF(`/api/users/${this.currentUserId}/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    new_password: 'password123',
                    send_email: false
                })
            });

            if (!response.ok) {
                let errorMessage = 'Failed to reset password';
                try {
                    const error = await response.json();
                    errorMessage = error.error || errorMessage;
                } catch (parseError) {
                    // If response is not JSON, get text
                    const errorText = await response.text();
                    errorMessage = errorText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            this.showToast('success', 'Password berhasil direset ke default!');
            this.closeDefaultPasswordModal();
        } catch (error) {
            console.error('Error resetting password to default:', error);
            this.showToast('error', `Gagal reset password: ${error.message}`);
        }
    }

    generateUserDetailsHTML(user) {
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
        const displayName = fullName || user.username;
        
        return `
            <div class="space-y-4">
                <div class="flex items-center space-x-4">
                    <div class="w-16 h-16 rounded-full flex items-center justify-center overflow-hidden" style="background: #f8f9fa;">
                        <svg width="64" height="64" data-jdenticon-value="${user.username || user.id}"></svg>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold text-sa-warning">${displayName}</h3>
                        <p class="text-sa-warning">@${user.username}</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-semibold text-sa-warning mb-2">Informasi Dasar</h4>
                        <div class="space-y-2 text-sm">
                            <p><span class="font-medium">Email:</span> ${user.email || 'Tidak ada email'}</p>
                            <p><span class="font-medium">Bio:</span> ${user.bio || 'Tidak ada bio'}</p>
                            <p><span class="font-medium">Role:</span> ${user.role || 'Tidak ada role'}</p>
                            <p><span class="font-medium">Custom Role:</span> ${user.custom_role?.name || 'Tidak ada'}</p>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="font-semibold text-sa-warning mb-2">Status</h4>
                        <div class="space-y-2 text-sm">
                            <p><span class="font-medium">Aktif:</span> ${user.is_active ? 'Ya' : 'Tidak'}</p>
                            <p><span class="font-medium">Terverifikasi:</span> ${user.verified ? 'Ya' : 'Tidak'}</p>
                            <p><span class="font-medium">Premium:</span> ${user.is_premium ? 'Ya' : 'Tidak'}</p>
                            <p><span class="font-medium">Tersuspend:</span> ${user.is_suspended ? 'Ya' : 'Tidak'}</p>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h4 class="font-semibold text-sa-warning mb-2">Aktivitas</h4>
                    <div class="space-y-2 text-sm">
                        <p><span class="font-medium">Login Terakhir:</span> ${user.last_login ? new Date(user.last_login).toLocaleString() : 'Tidak ada'}</p>
                        <p><span class="font-medium">Jumlah Login:</span> ${user.login_count || 0}</p>
                        <p><span class="font-medium">Dibuat:</span> ${user.created_at ? new Date(user.created_at).toLocaleString() : 'Tidak ada'}</p>
                        <p><span class="font-medium">Diperbarui:</span> ${user.updated_at ? new Date(user.updated_at).toLocaleString() : 'Tidak ada'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    async loadWriteAccessRequests() {
        try {
            // Get current filter values
            const search = document.getElementById('write-access-search')?.value || '';
            const statusFilter = document.getElementById('write-access-status-filter')?.value || '';
            const dateFilter = document.getElementById('write-access-date-filter')?.value || '';
            
            const params = new URLSearchParams({
                search: search,
                status: statusFilter,
                date_filter: dateFilter,
                page: 1
            });
            
            const response = await fetchWithCSRF(`/api/write-access-requests?${params}`);
            if (!response.ok) {
                throw new Error('Failed to fetch write access requests');
            }

            const data = await response.json();
            this.renderWriteAccessRequests(data.requests || []);
            this.updateWriteAccessStats(data);
        } catch (error) {
            console.error('Error loading write access requests:', error);
            this.showToast('error', 'Gagal memuat permintaan akses tulis');
        }
    }

    renderWriteAccessRequests(requests) {
        const container = document.getElementById('write-access-requests');
        if (!container) return;

        if (!requests || requests.length === 0) {
            container.innerHTML = '<div class="text-sa-muted">Tidak ada permintaan akses tulis yang menunggu.</div>';
            return;
        }

        const html = requests.map(request => {
            const isPending = request.status === 'pending';
            const statusColor = request.status === 'approved' ? 'green' : 
                               request.status === 'rejected' ? 'red' : 'yellow';
            const statusText = request.status === 'approved' ? 'Disetujui' : 
                              request.status === 'rejected' ? 'Ditolak' : 'Menunggu';
            
            return `
            <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <h4 class="font-semibold text-gray-800">${request.user.username}</h4>
                        <p class="text-sa-muted text-sm">${request.user.email || 'Tidak ada email'}</p>
                        <p class="text-sa-muted text-xs">Diminta pada: ${new Date(request.requested_at).toLocaleDateString('id-ID')}</p>
                        <span class="px-2 py-1 text-xs rounded-full bg-${statusColor}-100 text-${statusColor}-600 mt-1">
                            ${statusText}
                        </span>
                    </div>
                    <div class="flex space-x-2">
                        ${isPending ? `
                        <button onclick="approveWriteAccessRequest(${request.id})" class="bg-sa-success-bg hover:bg-sa-success-bg text-white px-3 py-1 rounded text-sm">
                            <i class="fas fa-check mr-1"></i>Setujui
                        </button>
                        <button onclick="rejectWriteAccessRequest(${request.id})" class="bg-sa-critical-bg hover:bg-sa-critical-bg text-white px-3 py-1 rounded text-sm">
                            <i class="fas fa-times mr-1"></i>Tolak
                        </button>
                        ` : ''}
                        <button onclick="viewWriteAccessRequest(${request.id})" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm">
                            <i class="fas fa-eye mr-1"></i>Lihat
                        </button>
                    </div>
                </div>
                <div class="text-sm text-sa-muted">
                    <p><strong>Alasan:</strong> ${request.request_reason || 'Tidak ada alasan'}</p>
                    <p><strong>Pengalaman:</strong> ${request.experience_description || 'Tidak ada pengalaman'}</p>
                    <p><strong>Portfolio:</strong> ${request.portfolio_links || 'Tidak ada portfolio'}</p>
                    ${request.admin_notes ? `<p><strong>Catatan Admin:</strong> ${request.admin_notes}</p>` : ''}
                    ${request.reviewed_at ? `<p><strong>Ditinjau:</strong> ${new Date(request.reviewed_at).toLocaleDateString('id-ID')}</p>` : ''}
                </div>
            </div>
        `;
        }).join('');

        container.innerHTML = html;
    }

    updateWriteAccessStats(data) {
        const totalPending = document.getElementById('total-write-access-pending');
        const approvedToday = document.getElementById('approved-write-access-today');
        const rejectedToday = document.getElementById('rejected-write-access-today');
        const avgTime = document.getElementById('avg-write-access-time');

        if (totalPending) totalPending.textContent = data.total_pending || 0;
        if (approvedToday) approvedToday.textContent = data.approved_today || 0;
        if (rejectedToday) rejectedToday.textContent = data.rejected_today || 0;
        if (avgTime) avgTime.textContent = data.avg_time || '-';
    }

    async approveWriteAccess(requestId) {
        console.log('approveWriteAccess called with requestId:', requestId);
        try {
            console.log('Making API call to approve write access request');
            const response = await fetchWithCSRF(`/api/write-access-requests/${requestId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            console.log('API response received, status:', response.status);

            if (!response.ok) {
                const error = await response.json();
                
                // Handle specific error cases
                if (error.error && (error.error.includes('already been') || error.error.includes('already been reviewed'))) {
                    this.showToast('warning', 'Permintaan ini sudah diproses sebelumnya');
                    this.loadWriteAccessRequests(); // Refresh to update UI
                    return;
                }
                
                throw new Error(error.error || 'Failed to approve write access request');
            }

            const result = await response.json();
            this.showToast('success', result.message || 'Permintaan akses tulis berhasil disetujui');
            this.loadWriteAccessRequests(); // Refresh the list
        } catch (error) {
            console.error('Error approving write access request:', error);
            this.showToast('error', error.message || 'Gagal menyetujui permintaan akses tulis');
        }
    }

    async rejectWriteAccess(requestId) {
        console.log('rejectWriteAccess called with requestId:', requestId);
        try {
            console.log('Making API call to reject write access request');
            const response = await fetchWithCSRF(`/api/write-access-requests/${requestId}/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            console.log('API response received, status:', response.status);

            if (!response.ok) {
                const error = await response.json();
                
                // Handle specific error cases
                if (error.error && (error.error.includes('already been') || error.error.includes('already been reviewed'))) {
                    this.showToast('warning', 'Permintaan ini sudah diproses sebelumnya');
                    this.loadWriteAccessRequests(); // Refresh to update UI
                    return;
                }
                
                throw new Error(error.error || 'Failed to reject write access request');
            }

            const result = await response.json();
            this.showToast('success', result.message || 'Permintaan akses tulis berhasil ditolak');
            this.loadWriteAccessRequests(); // Refresh the list
        } catch (error) {
            console.error('Error rejecting write access request:', error);
            this.showToast('error', error.message || 'Gagal menolak permintaan akses tulis');
        }
    }

    async viewWriteAccessRequest(requestId) {
        try {
            const response = await fetchWithCSRF(`/api/write-access-requests/${requestId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch write access request details');
            }

            const data = await response.json();
            if (data.success && data.request) {
                this.showWriteAccessDetails(data.request);
            }
        } catch (error) {
            console.error('Error loading write access request details:', error);
            this.showToast('error', 'Gagal memuat detail permintaan akses tulis');
        }
    }

    showWriteAccessDetails(request) {
        // This could open a modal or show details in place
        alert(`Detail Permintaan Akses Tulis:\n\nPengguna: ${request.user.username}\nAlasan: ${request.request_reason}\nPengalaman: ${request.experience_description}`);
    }

    async bulkApproveWriteAccess() {
        try {
            const response = await fetchWithCSRF('/api/write-access-requests/bulk/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const error = await response.json();
                
                // Handle specific error cases
                if (error.error && error.error.includes('No pending requests')) {
                    this.showToast('info', 'Tidak ada permintaan yang menunggu untuk disetujui');
                    this.loadWriteAccessRequests(); // Refresh to update UI
                    return;
                }
                
                throw new Error(error.error || 'Failed to bulk approve write access requests');
            }

            const result = await response.json();
            this.showToast('success', result.message || 'Semua permintaan akses tulis yang menunggu berhasil disetujui');
            this.loadWriteAccessRequests(); // Refresh the list
        } catch (error) {
            console.error('Error bulk approving write access requests:', error);
            this.showToast('error', error.message || 'Gagal menyetujui permintaan akses tulis secara massal');
        }
    }

    async bulkRejectWriteAccess() {
        try {
            const response = await fetchWithCSRF('/api/write-access-requests/bulk/reject', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const error = await response.json();
                
                // Handle specific error cases
                if (error.error && error.error.includes('No pending requests')) {
                    this.showToast('info', 'Tidak ada permintaan yang menunggu untuk ditolak');
                    this.loadWriteAccessRequests(); // Refresh to update UI
                    return;
                }
                
                throw new Error(error.error || 'Failed to bulk reject write access requests');
            }

            const result = await response.json();
            this.showToast('success', result.message || 'Semua permintaan akses tulis yang menunggu berhasil ditolak');
            this.loadWriteAccessRequests(); // Refresh the list
        } catch (error) {
            console.error('Error bulk rejecting write access requests:', error);
            this.showToast('error', error.message || 'Gagal menolak permintaan akses tulis secara massal');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.usersManagement = new UsersManagement();
});

// Global functions for onclick handlers
function openEditUserModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.openEditUserModal(userId);
    }
}

function closeEditUserModal() {
    if (window.usersManagement) {
        window.usersManagement.closeEditUserModal();
    }
}

function showDeleteUserModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.showDeleteUserModal(userId);
    }
}

function closeDeleteUserModal() {
    if (window.usersManagement) {
        window.usersManagement.closeDeleteUserModal();
    }
}

function confirmDeleteUser() {
    if (window.usersManagement) {
        window.usersManagement.confirmDeleteUser();
    }
}

function closeCreateRoleModal() {
    if (window.usersManagement) {
        window.usersManagement.closeCreateRoleModal();
    }
}

function openCreateRoleModal() {
    if (window.usersManagement) {
        window.usersManagement.openCreateRoleModal();
    }
}

// Additional global functions for new features
function editRole(roleId) {
    if (window.usersManagement) {
        window.usersManagement.editRole(roleId);
    }
}

function deleteRole(roleId) {
    if (window.usersManagement) {
        window.usersManagement.deleteRole(roleId);
    }
}

function closeEditRoleModal() {
    if (window.usersManagement) {
        window.usersManagement.closeEditRoleModal();
    }
}

function confirmDeleteRole() {
    if (window.usersManagement) {
        window.usersManagement.confirmDeleteRole();
    }
}

function closeDeleteRoleModal() {
    if (window.usersManagement) {
        window.usersManagement.closeDeleteRoleModal();
    }
}

function approveUser(userId) {
    if (window.usersManagement) {
        window.usersManagement.approveUser(userId);
    }
}

// New modal functions
function openCreateUserModal() {
    if (window.usersManagement) {
        window.usersManagement.openCreateUserModal();
    }
}

function closeCreateUserModal() {
    if (window.usersManagement) {
        window.usersManagement.closeCreateUserModal();
    }
}

function openUserDetailsModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.openUserDetailsModal(userId);
    }
}

function closeUserDetailsModal() {
    if (window.usersManagement) {
        window.usersManagement.closeUserDetailsModal();
    }
}

function openPasswordResetModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.openPasswordResetModal(userId);
    }
}

function closePasswordResetModal() {
    if (window.usersManagement) {
        window.usersManagement.closePasswordResetModal();
    }
}

function openSendEmailModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.openSendEmailModal(userId);
    }
}

function closeSendEmailModal() {
    if (window.usersManagement) {
        window.usersManagement.closeSendEmailModal();
    }
}

function rejectUser(userId) {
    if (window.usersManagement) {
        window.usersManagement.rejectUser(userId);
    }
}

// Deletion request functions
function approveDeletion(userId) {
    if (window.usersManagement) {
        window.usersManagement.approveDeletion(userId);
    }
}

function rejectDeletion(userId) {
    if (window.usersManagement) {
        window.usersManagement.rejectDeletion(userId);
    }
}

// Default password reset functions
function showDefaultPasswordModal(userId) {
    if (window.usersManagement) {
        window.usersManagement.showDefaultPasswordModal(userId);
    }
}

function closeDefaultPasswordModal() {
    if (window.usersManagement) {
        window.usersManagement.closeDefaultPasswordModal();
    }
}

function confirmDefaultPasswordReset() {
    if (window.usersManagement) {
        window.usersManagement.confirmDefaultPasswordReset();
    }
}

// Write access request functions
function loadWriteAccessRequests() {
    if (window.usersManagement) {
        window.usersManagement.loadWriteAccessRequests();
    }
}

function approveWriteAccessRequest(requestId) {
    console.log('approveWriteAccessRequest called with requestId:', requestId);
    console.log('window.usersManagement exists:', !!window.usersManagement);
    if (window.usersManagement) {
        window.usersManagement.approveWriteAccess(requestId);
    } else {
        console.error('window.usersManagement is not initialized');
    }
}

function rejectWriteAccessRequest(requestId) {
    console.log('rejectWriteAccessRequest called with requestId:', requestId);
    console.log('window.usersManagement exists:', !!window.usersManagement);
    if (window.usersManagement) {
        window.usersManagement.rejectWriteAccess(requestId);
    } else {
        console.error('window.usersManagement is not initialized');
    }
}

function viewWriteAccessRequest(requestId) {
    if (window.usersManagement) {
        window.usersManagement.viewWriteAccessRequest(requestId);
    }
}

function bulkApproveWriteAccess() {
    if (window.usersManagement) {
        window.usersManagement.bulkApproveWriteAccess();
    }
}

function bulkRejectWriteAccess() {
    if (window.usersManagement) {
        window.usersManagement.bulkRejectWriteAccess();
    }
}
