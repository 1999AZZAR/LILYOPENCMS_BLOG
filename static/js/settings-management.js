// Settings Management JavaScript

// Fetch and display quick stats
async function fetchQuickStats() {
    try {
        const response = await fetch('/api/settings/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const stats = await response.json();
        document.getElementById('total-users').textContent = stats.total_users;
        document.getElementById('total-news').textContent = stats.total_news;
        document.getElementById('total-images').textContent = stats.total_images;
        document.getElementById('total-videos').textContent = stats.total_videos;
    } catch (error) {
        console.error(error);
        document.getElementById('total-users').textContent = 'Error';
        document.getElementById('total-news').textContent = 'Error';
        document.getElementById('total-images').textContent = 'Error';
        document.getElementById('total-videos').textContent = 'Error';
    }
}

// Fetch user role and show/hide cards
async function checkUserRole() {
    try {
        const response = await fetch('/api/user/role');
        if (!response.ok) throw new Error('Failed to fetch user role');
        const data = await response.json();
        const userRole = data.role;
        if (userRole === 'su' || userRole === 'admin') {
            document.getElementById('user-management-card').classList.remove('hidden');
            document.getElementById('privacy-policy-card').classList.remove('hidden');
            document.getElementById('media-guidelines-card').classList.remove('hidden');
            document.getElementById('pedoman-hak-card').classList.remove('hidden');
            document.getElementById('penyangkalan-card').classList.remove('hidden');
            document.getElementById('visi-misi-card').classList.remove('hidden');
            document.getElementById('social-media-card').classList.remove('hidden');
            document.getElementById('contact-details-card').classList.remove('hidden');
            document.getElementById('team-members-card').classList.remove('hidden');
            document.getElementById('brand-identity-card').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error fetching user role:', error);
    }
}

// Brand Identity Management JS
function refreshBrandImages() {
    document.getElementById('brand-logo-header').src = '/static/pic/logo.png?' + Date.now();
    document.getElementById('brand-logo-footer').src = '/static/pic/logo_footer.png?' + Date.now();
    document.getElementById('brand-favicon').src = '/static/pic/favicon.png?' + Date.now();
    document.getElementById('brand-placeholder').src = '/static/pic/placeholder.png?' + Date.now();
}

function handleBrandForm(formId, fieldName) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData();
        const fileInput = form.querySelector('input[type="file"]');
        if (!fileInput.files.length) return alert('Pilih file terlebih dahulu!');
        formData.append(fieldName, fileInput.files[0]);
        try {
            const resp = await fetch('/api/brand-identity', {
                method: 'POST',
                body: formData
            });
            if (!resp.ok) throw new Error('Gagal upload');
            refreshBrandImages();
            fileInput.value = '';
        } catch (err) {
            alert('Upload gagal: ' + err.message);
        }
    });
}

// Settings Management Tab Functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings management script loaded');
    
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    function switchTab(tabName) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        tabButtons.forEach(button => {
            button.classList.remove('active', 'border-amber-500');
            button.classList.add('border-transparent');
        });

        // Show selected tab content
        const selectedTab = document.getElementById(tabName + '-tab');
        if (selectedTab) {
            selectedTab.classList.add('active');
        }

        // Add active class to clicked button
        const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeButton) {
            activeButton.classList.add('active', 'border-amber-500');
            activeButton.classList.remove('border-transparent');
        }
    }

    // Add click event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Only load stats if we're on the settings dashboard page
    if (document.querySelector('.tab-btn')) {
        console.log('Tab buttons found, loading stats...');
        showLoadingState();
        // Delay stats loading to avoid conflicts with admin base template
        setTimeout(() => {
            loadStats();
        }, 1000);
    }
});

// Load dashboard statistics
async function loadStats() {
    try {
        console.log('Loading stats from /api/settings/stats...');
        const response = await fetch('/api/settings/stats');
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Stats data:', data);
            
            // Update stats display
            const usersElement = document.getElementById('total-users');
            const newsElement = document.getElementById('total-news');
            const imagesElement = document.getElementById('total-images');
            const videosElement = document.getElementById('total-videos');
            
            if (usersElement) usersElement.textContent = data.total_users || '0';
            if (newsElement) newsElement.textContent = data.total_news || '0';
            if (imagesElement) imagesElement.textContent = data.total_images || '0';
            if (videosElement) videosElement.textContent = data.total_videos || '0';
            
            console.log('Stats updated successfully');
        } else {
            console.error('Failed to fetch stats:', response.status);
            setDefaultStats();
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        setDefaultStats();
    }
}

// Set default stats values
function setDefaultStats() {
    console.log('Setting default stats values');
    const elements = {
        'total-users': '0',
        'total-news': '0', 
        'total-images': '0',
        'total-videos': '0'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            console.log(`Set ${id} to ${value}`);
        } else {
            console.warn(`Element with id '${id}' not found`);
        }
    });
}

// Add loading state management
function showLoadingState() {
    const statsElements = ['total-users', 'total-news', 'total-images', 'total-videos'];
    statsElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = 'Loading...';
        }
    });
}

function hideLoadingState() {
    // Loading state is cleared when stats are loaded or defaults are set
}