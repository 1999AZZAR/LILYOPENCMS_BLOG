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

        // Form handlers
        this.initFormHandlers();
    }

    initTabs() {
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
                
                // Load specific data for the tab if needed
                this.loadTabData(targetTab);
            });
        });
    }

    loadTabData(tabName) {
        switch(tabName) {
            case 'users':
                this.loadUsers();
                break;
            case 'roles':
                this.loadRoles();
                break;
            case 'pending':
                this.loadPendingUsers();
                break;
            case 'performance':
                this.loadPerformanceData();
                break;
        }
    }

    async loadUsers(page = 1) {
        try {
            console.log('Loading users...');
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
        
            console.log('API URL:', `/api/users?${params}`);
        const response = await fetch(`/api/users?${params}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error:', response.status, errorText);
                throw new Error(`Failed to fetch users: ${response.status} ${errorText}`);
            }
        
        const data = await response.json();
            console.log('API Response:', data);
            
            this.users = data;
            this.currentPage = page;
            
            this.renderUsers();
    } catch (error) {
            console.error('Error loading users:', error);
            this.showToast('error', 'Gagal memuat daftar pengguna');
            this.showErrorInContainers(error.message);
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
        const adminUsers = this.users.filter(user => user.role === 'su' || user.role === 'admin');
        const generalUsers = this.users.filter(user => user.role === 'general');
        
        // Render admin users
        if (adminUsers.length === 0) {
            adminContainer.innerHTML = '<div class="col-span-full text-amber-600">Tidak ada pengguna admin</div>';
        } else {
            adminUsers.forEach(user => {
                const userCard = this.createUserCard(user);
                adminContainer.appendChild(userCard);
            });
        }
        
        // Render general users
        if (generalUsers.length === 0) {
            generalContainer.innerHTML = '<div class="col-span-full text-amber-600">Tidak ada pengguna umum</div>';
        } else {
            generalUsers.forEach(user => {
                const userCard = this.createUserCard(user);
                generalContainer.appendChild(userCard);
            });
        }
    }

    createUserCard(user) {
    const card = document.createElement('div');
        card.className = 'bg-white border border-amber-200 rounded-lg p-4 hover:shadow-md transition-shadow';
    card.setAttribute('role', 'listitem');
    card.setAttribute('aria-label', `User: ${user.username}`);
    
        // Status and role badges
    const statusClass = user.is_suspended ? 'text-red-600 bg-red-100' : 'text-green-600 bg-green-100';
    const statusText = user.is_suspended ? 'Tersuspend' : 'Aktif';
        
        // Enhanced role display
        let roleBadge = '';
        if (user.role === 'su') {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-red-100 text-red-600">Superuser</span>';
        } else if (user.role === 'admin') {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-600">Admin</span>';
        } else {
            roleBadge = '<span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">Umum</span>';
        }
        
        // Custom role badge if exists
        let customRoleBadge = '';
        if (user.custom_role && user.custom_role.name) {
            customRoleBadge = `<span class="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-600">${user.custom_role.name}</span>`;
        }
        
        // Additional info
        const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
        const displayName = fullName || user.username;
    
    card.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full flex items-center justify-center">
                    <span class="text-white font-semibold text-sm">${user.username.charAt(0).toUpperCase()}</span>
                </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-amber-800">${displayName}</h3>
                        <p class="text-sm text-amber-600">${user.email || 'Tidak ada email'}</p>
                        ${user.bio ? `<p class="text-xs text-gray-500 mt-1">${user.bio.substring(0, 50)}${user.bio.length > 50 ? '...' : ''}</p>` : ''}
                        <div class="flex items-center space-x-2 mt-2 flex-wrap gap-1">
                        <span class="px-2 py-1 text-xs rounded-full ${statusClass}">${statusText}</span>
                            ${roleBadge}
                            ${customRoleBadge}
                            ${user.verified ? '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-600">✓ Terverifikasi</span>' : ''}
                            ${user.is_premium ? '<span class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-600">⭐ Premium</span>' : ''}
                        </div>
                </div>
            </div>
            <div class="flex space-x-2">
                    <button onclick="usersManagement.openEditUserModal(${user.id})" class="p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-600 rounded-full focus:outline-none focus:ring-2 focus:ring-yellow-300 transition-colors" title="Edit User">
                    <i class="fas fa-edit"></i>
                </button>
                    <button onclick="usersManagement.showDeleteUserModal(${user.id})" class="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-full focus:outline-none focus:ring-2 focus:ring-red-300 transition-colors" title="Delete User">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

    showErrorInContainers(errorMessage) {
        const adminContainer = document.getElementById('admin-users');
        const generalContainer = document.getElementById('general-users');
        
        if (adminContainer) {
            adminContainer.innerHTML = `<div class="col-span-full text-red-600">Error: ${errorMessage}</div>`;
        }
        if (generalContainer) {
            generalContainer.innerHTML = `<div class="col-span-full text-red-600">Error: ${errorMessage}</div>`;
        }
    }

    initFormHandlers() {
    // Edit user form
    const editForm = document.getElementById('edit-user-form');
    if (editForm) {
            editForm.addEventListener('submit', (e) => this.handleEditUser(e));
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
            const response = await fetch(`/api/users/${this.currentUserId}`, {
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

    async handleCreateRole(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('role-name').value.trim(),
        description: document.getElementById('role-description').value.trim(),
            is_active: true,
            permission_ids: this.getSelectedPermissions()
    };
    
    try {
        const response = await fetch('/api/roles', {
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
        
        // Log for debugging
        console.log('Edit modal populated with user data:', {
            id: user.id,
            username: user.username,
            email: user.email,
            first_name: user.first_name,
            last_name: user.last_name,
            bio: user.bio,
            role: user.role,
            custom_role_id: customRoleId,
            verified: user.verified,
            is_suspended: user.is_suspended,
            is_premium: user.is_premium
        });
    }

    async populateCustomRoleDropdown(selectedRoleId = null) {
        try {
            const response = await fetch('/api/roles');
            if (response.ok) {
                const roles = await response.json();
                const dropdown = document.getElementById('edit-custom-role');
                
                // Clear existing options
                dropdown.innerHTML = '<option value="">Tidak ada peran kustom</option>';
                
                // Add role options
                roles.forEach(role => {
                    const option = document.createElement('option');
                    option.value = role.id;
                    option.textContent = role.name;
                    if (selectedRoleId && role.id === parseInt(selectedRoleId)) {
                        option.selected = true;
                    }
                    dropdown.appendChild(option);
                });
                
                console.log('Custom roles dropdown populated:', {
                    rolesCount: roles.length,
                    selectedRoleId: selectedRoleId
                });
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
            const response = await fetch(`/api/users/${this.currentUserId}`, {
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
            console.log('Loading roles...');
            
            // Load custom roles
            const customRolesResponse = await fetch('/api/roles');
            if (customRolesResponse.ok) {
                const customRoles = await customRolesResponse.json();
                this.renderCustomRoles(customRoles);
            }
            
            // Load permissions
            const permissionsResponse = await fetch('/api/permissions');
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
                    <input type="checkbox" id="perm-${permission.id}" value="${permission.id}" class="rounded border-amber-300 text-amber-500 focus:ring-amber-300">
                    <label for="perm-${permission.id}" class="text-sm text-amber-700">
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
                    <input type="checkbox" id="edit-perm-${permission.id}" value="${permission.id}" class="rounded border-amber-300 text-amber-500 focus:ring-amber-300">
                    <label for="edit-perm-${permission.id}" class="text-sm text-amber-700">
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
            container.innerHTML = '<div class="text-amber-600">Tidak ada peran kustom</div>';
            return;
        }
        
        container.innerHTML = roles.map(role => `
            <div class="bg-white border border-amber-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-amber-800">${role.name}</h4>
                        <p class="text-sm text-amber-600">${role.description || 'Tidak ada deskripsi'}</p>
                        <div class="flex items-center space-x-2 mt-2">
                            <span class="px-2 py-1 text-xs rounded-full ${role.is_active ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                                ${role.is_active ? 'Aktif' : 'Tidak Aktif'}
                            </span>
                            <span class="text-xs text-amber-600">${role.permissions?.length || 0} izin</span>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="usersManagement.editRole(${role.id})" class="p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-600 rounded-full">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="usersManagement.deleteRole(${role.id})" class="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-full">
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
            container.innerHTML = '<div class="text-amber-600">Tidak ada izin</div>';
            return;
        }
        
        container.innerHTML = permissions.map(permission => `
            <div class="bg-white border border-amber-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-amber-800">${permission.name}</h4>
                        <p class="text-sm text-amber-600">${permission.description || 'Tidak ada deskripsi'}</p>
                        <div class="flex items-center space-x-2 mt-2">
                            <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-600">${permission.resource}</span>
                            <span class="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-600">${permission.action}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadPendingUsers() {
        try {
            console.log('Loading pending users...');
            
            const response = await fetch('/api/registrations/pending');
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

    renderPendingUsers(users) {
        const container = document.getElementById('pending-users');
        if (!container) return;
        
        if (users.length === 0) {
            container.innerHTML = '<div class="text-amber-600">Tidak ada pengguna yang menunggu persetujuan</div>';
            return;
        }
        
        container.innerHTML = users.map(user => `
            <div class="bg-white border border-amber-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full flex items-center justify-center">
                            <span class="text-white font-semibold text-sm">${user.username.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                            <h4 class="font-semibold text-amber-800">${user.username}</h4>
                            <p class="text-sm text-amber-600">${user.email || 'Tidak ada email'}</p>
                            <p class="text-xs text-amber-500">Daftar: ${new Date(user.created_at).toLocaleDateString('id-ID')}</p>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="usersManagement.approveUser(${user.id})" class="px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded text-sm">
                            <i class="fas fa-check mr-1"></i>Setujui
                        </button>
                        <button onclick="usersManagement.rejectUser(${user.id})" class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-sm">
                            <i class="fas fa-times mr-1"></i>Tolak
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadPerformanceData() {
        try {
            console.log('Loading performance data...');
            
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
            container.innerHTML = '<div class="text-amber-600">Tidak ada data performa</div>';
            return;
        }
        
        container.innerHTML = leaderboard.leaderboard.map((entry, index) => {
            const user = entry.user;
            const metrics = entry.metrics;
            
            return `
                <div class="bg-white border border-amber-200 rounded-lg p-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-gradient-to-r from-amber-400 to-yellow-400 rounded-full flex items-center justify-center">
                                <span class="text-white font-semibold text-xs">${index + 1}</span>
                            </div>
                            <div>
                                <h4 class="font-semibold text-amber-800">${user.username}</h4>
                                <p class="text-sm text-amber-600">${user.role}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-lg font-bold text-amber-800">${metrics.engagement_score}</div>
                            <div class="text-xs text-amber-600">Skor</div>
                        </div>
                    </div>
                    <div class="mt-3 grid grid-cols-3 gap-2 text-xs">
                        <div class="text-center">
                            <div class="font-semibold text-blue-600">${metrics.news_count}</div>
                            <div class="text-gray-500">Berita</div>
                        </div>
                        <div class="text-center">
                            <div class="font-semibold text-green-600">${metrics.images_count}</div>
                            <div class="text-gray-500">Gambar</div>
                        </div>
                        <div class="text-center">
                            <div class="font-semibold text-purple-600">${metrics.videos_count}</div>
                            <div class="text-gray-500">Video</div>
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
            const response = await fetch(`/api/roles/${this.currentRoleId}`, {
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
            const response = await fetch(`/api/roles/${this.currentRoleId}`, {
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
            const response = await fetch(`/api/registrations/${userId}/approve`, {
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
            const response = await fetch(`/api/registrations/${userId}/reject`, {
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

    async exportUsers() {
        try {
            const response = await fetch('/api/users/bulk/export', {
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
            const response = await fetch(`/api/users/performance/report/export?days=${period}`, {
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
            const response = await fetch('/api/roles/bulk/export', {
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
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
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

function rejectUser(userId) {
    if (window.usersManagement) {
        window.usersManagement.rejectUser(userId);
    }
}