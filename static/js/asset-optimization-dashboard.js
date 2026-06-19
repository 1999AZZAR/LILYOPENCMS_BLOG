// Asset Optimization Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Asset optimization dashboard loaded');
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log('Found tab buttons:', tabButtons.length);
    console.log('Found tab contents:', tabContents.length);

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            console.log('Clicked tab:', targetTab);
            
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
        });
    });

    // Refresh functionality
    document.getElementById('refresh-assets').addEventListener('click', function() {
        location.reload();
    });

    // Custom confirmation dialog
    function showConfirmDialog(message, onConfirm) {
        const dialog = document.createElement('div');
        dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        dialog.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                <div class="flex items-center mb-4">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-2xl"></i>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-lg font-medium text-gray-900">Konfirmasi</h3>
                    </div>
                </div>
                <div class="mb-6">
                    <p class="text-sm text-gray-600">${message}</p>
                </div>
                <div class="flex justify-end space-x-3">
                    <button type="button" class="cancel-btn px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-amber-400">
                        Batal
                    </button>
                    <button type="button" class="confirm-btn px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 focus:outline-none focus:ring-2 focus:ring-amber-400">
                        Ya, Lanjutkan
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        const confirmBtn = dialog.querySelector('.confirm-btn');
        const cancelBtn = dialog.querySelector('.cancel-btn');
        
        const closeDialog = () => {
            document.body.removeChild(dialog);
        };
        
        confirmBtn.addEventListener('click', () => {
            closeDialog();
            onConfirm();
        });
        
        cancelBtn.addEventListener('click', closeDialog);
        
        // Close on backdrop click
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                closeDialog();
            }
        });
    }

    document.getElementById('precompile-assets').addEventListener('click', function() {
        showConfirmDialog('Apakah Anda yakin ingin melakukan compress assets?', () => {
            showToast('info', 'Compressing assets...');
            
            fetch('/api/asset-optimization/compress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('success', data.message);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showToast('error', data.message);
                }
            })
            .catch(error => {
                showToast('error', 'Error: ' + error.message);
            });
        });
    });

    // Add functionality for other buttons
    document.getElementById('run-optimization').addEventListener('click', function() {
        showConfirmDialog('Apakah Anda yakin ingin menjalankan optimasi assets?', () => {
            showToast('info', 'Running asset optimization...');
            
            fetch('/api/asset-optimization/regenerate-hashes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('success', data.message);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showToast('error', data.message);
                }
            })
            .catch(error => {
                showToast('error', 'Error: ' + error.message);
            });
        });
    });

    // Add clear cache functionality
    document.querySelectorAll('.bg-yellow-500').forEach(button => {
        if (button.textContent.includes('Clear Asset Cache')) {
            button.addEventListener('click', function() {
                showConfirmDialog('Apakah Anda yakin ingin membersihkan cache assets?', () => {
                    showToast('info', 'Clearing asset cache...');
                    
                    fetch('/api/asset-optimization/clear-cache', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('success', data.message);
                            setTimeout(() => location.reload(), 2000);
                        } else {
                            showToast('error', data.message);
                        }
                    })
                    .catch(error => {
                        showToast('error', 'Error: ' + error.message);
                    });
                });
            });
        }
    });
});