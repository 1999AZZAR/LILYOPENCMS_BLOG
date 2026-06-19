// Analytics Dashboard JavaScript
class AnalyticsDashboard {
    constructor() {
        this.currentPeriod = 30;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
        this.trackVisitor();
    }

    bindEvents() {
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadAllData();
        });

        // Period selector
        document.getElementById('period-selector').addEventListener('change', (e) => {
            this.currentPeriod = parseInt(e.target.value);
            this.loadAllData();
        });

        // Export buttons
        document.getElementById('export-content').addEventListener('click', () => {
            this.exportReport('content');
        });

        document.getElementById('export-users').addEventListener('click', () => {
            this.exportReport('users');
        });

        document.getElementById('export-activity').addEventListener('click', () => {
            this.exportReport('activity');
        });

        // Tab functionality
        this.initTabs();
    }

    async loadInitialData() {
        this.showLoading();
        await Promise.all([
            this.loadVisitorStats(),
            this.loadContentAnalytics(),
            this.loadActivityLogs(),
            this.loadPerformanceMetrics(),
            this.loadDashboardSummary()
        ]);
        this.hideLoading();
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
            case 'overview':
                this.loadVisitorStats();
                this.loadDashboardSummary();
                break;
            case 'content':
                this.loadContentAnalytics();
                break;
            case 'activity':
                this.loadActivityLogs();
                break;
            case 'performance':
                this.loadPerformanceMetrics();
                break;
        }
    }

    async loadAllData() {
        this.showLoading();
        await Promise.all([
            this.loadVisitorStats(),
            this.loadContentAnalytics(),
            this.loadActivityLogs(),
            this.loadPerformanceMetrics(),
            this.loadDashboardSummary()
        ]);
        this.hideLoading();
        this.showToast('Data berhasil diperbarui!', 'success');
    }

    async loadVisitorStats() {
        try {
            const response = await fetch('/api/analytics/visitors');
            const data = await response.json();
            
            document.getElementById('active-visitors').textContent = data.active_visitors;
            document.getElementById('total-users').textContent = data.total_users;
            
            // Calculate content created for this period
            const contentCreated = data.total_news + data.total_images + data.total_videos;
            document.getElementById('content-created').textContent = contentCreated;
            
            // Calculate engagement score
            const engagementScore = Math.round((data.active_visitors / data.total_users) * 100);
            document.getElementById('engagement-score').textContent = engagementScore + '%';
            
        } catch (error) {
            console.error('Error loading visitor stats:', error);
            this.showToast('Error memuat statistik pengunjung', 'error');
        }
    }

    async loadContentAnalytics() {
        try {
            const response = await fetch(`/api/analytics/content?days=${this.currentPeriod}`);
            const data = await response.json();
            
            // Update news stats
            document.getElementById('news-count').textContent = data.news.total;
            document.getElementById('news-reads').textContent = data.news.total_reads;
            document.getElementById('news-stats').textContent = `Avg: ${data.news.avg_reads.toFixed(1)} reads`;
            
            // Update image stats
            document.getElementById('image-count').textContent = data.images.total;
            document.getElementById('image-downloads').textContent = data.images.avg_downloads.toFixed(1);
            document.getElementById('image-stats').textContent = `Avg: ${data.images.avg_downloads.toFixed(1)} downloads`;
            
            // Update video stats
            document.getElementById('video-count').textContent = data.videos.total;
            document.getElementById('video-views').textContent = data.videos.avg_views.toFixed(1);
            document.getElementById('video-stats').textContent = `Avg: ${data.videos.avg_views.toFixed(1)} views`;
            
            // Update popular content
            this.updatePopularContent(data.news.top_articles);
            
        } catch (error) {
            console.error('Error loading content analytics:', error);
            this.showToast('Error memuat analitik konten', 'error');
        }
    }

    async loadActivityLogs() {
        try {
            const response = await fetch(`/api/analytics/activity?days=7`);
            const data = await response.json();
            
            const activityContainer = document.getElementById('activity-logs');
            activityContainer.innerHTML = '';
            
            if (data.activities.length === 0) {
                activityContainer.innerHTML = '<div class="text-center text-gray-500 py-4">No recent activity</div>';
                return;
            }
            
            data.activities.slice(0, 10).forEach(activity => {
                const activityElement = this.createActivityElement(activity);
                activityContainer.appendChild(activityElement);
            });
            
        } catch (error) {
            console.error('Error loading activity logs:', error);
            this.showToast('Error memuat log aktivitas', 'error');
        }
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch('/api/analytics/performance');
            const data = await response.json();
            
            // Update CPU usage
            const cpuPercent = data.system.cpu_percent;
            document.getElementById('cpu-percent').textContent = cpuPercent + '%';
            document.getElementById('cpu-bar').style.width = cpuPercent + '%';
            
            // Update memory usage
            const memoryPercent = data.system.memory_percent;
            document.getElementById('memory-percent').textContent = memoryPercent.toFixed(1) + '%';
            document.getElementById('memory-bar').style.width = memoryPercent + '%';
            
            // Update database response time
            document.getElementById('db-response').textContent = data.database.query_time_ms + 'ms';
            
        } catch (error) {
            console.error('Error loading performance metrics:', error);
            this.showToast('Error memuat metrik performa', 'error');
        }
    }

    async loadDashboardSummary() {
        try {
            const response = await fetch('/api/analytics/dashboard');
            const data = await response.json();
            
            // Update weekly summary
            document.getElementById('weekly-news').textContent = data.weekly.news_created;
            document.getElementById('weekly-images').textContent = data.weekly.images_uploaded;
            document.getElementById('weekly-videos').textContent = data.weekly.videos_uploaded;
            document.getElementById('weekly-users').textContent = data.weekly.active_users;
            
        } catch (error) {
            console.error('Error loading dashboard summary:', error);
            this.showToast('Error memuat ringkasan dashboard', 'error');
        }
    }

    updatePopularContent(topArticles) {
        const container = document.getElementById('popular-content');
        container.innerHTML = '';
        
        if (topArticles.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 py-8">No popular content found</div>';
            return;
        }
        
        topArticles.slice(0, 6).forEach(article => {
            const articleElement = this.createPopularContentElement(article);
            container.appendChild(articleElement);
        });
    }

    createActivityElement(activity) {
        const div = document.createElement('div');
        div.className = 'flex items-center space-x-3 p-3 bg-gray-50 rounded-lg';
        
        const icon = this.getActivityIcon(activity.activity_type);
        const time = new Date(activity.created_at).toLocaleString();
        
        div.innerHTML = `
            <div class="flex-shrink-0">
                <i class="${icon} text-blue-600"></i>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">${activity.user || 'Unknown'}</p>
                <p class="text-sm text-gray-500">${activity.description || activity.activity_type}</p>
                <p class="text-xs text-gray-400">${time}</p>
            </div>
        `;
        
        return div;
    }

    createPopularContentElement(article) {
        const div = document.createElement('div');
        div.className = 'bg-white rounded-lg shadow-sm p-4 border border-gray-200';
        
        div.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <h4 class="text-sm font-medium text-gray-900 line-clamp-2">${article.title}</h4>
                    <p class="text-xs text-gray-500 mt-1">by ${article.author}</p>
                </div>
                <div class="ml-3 flex-shrink-0">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${article.read_count} reads
                    </span>
                </div>
            </div>
            <div class="mt-2 text-xs text-gray-400">
                ${new Date(article.created_at).toLocaleDateString()}
            </div>
        `;
        
        return div;
    }

    getActivityIcon(activityType) {
        const icons = {
            'login': 'fas fa-sign-in-alt',
            'logout': 'fas fa-sign-out-alt',
            'create_news': 'fas fa-plus-circle',
            'update_news': 'fas fa-edit',
            'delete_news': 'fas fa-trash',
            'upload_image': 'fas fa-image',
            'upload_video': 'fas fa-video',
            'export_data': 'fas fa-download',
            'suspend_user': 'fas fa-user-slash',
            'unsuspend_user': 'fas fa-user-check',
            'export_analytics': 'fas fa-chart-bar'
        };
        
        return icons[activityType] || 'fas fa-info-circle';
    }

    async exportReport(type) {
        try {
            this.showLoading();
            
            const response = await fetch('/api/analytics/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    days: this.currentPeriod
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_report_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                const reportNames = {
                    'content': 'Performa Konten',
                    'users': 'Statistik Pengguna',
                    'activity': 'Log Aktivitas'
                };
                this.showToast(`Laporan ${reportNames[type] || type} berhasil diekspor!`, 'success');
            } else {
                throw new Error('Export failed');
            }
            
        } catch (error) {
            console.error('Error exporting report:', error);
            this.showToast('Error mengekspor laporan', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async trackVisitor() {
        try {
            const visitorId = 'visitor_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            
            await fetch('/api/analytics/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    visitor_id: visitorId
                })
            });
            
            // Store visitor ID for future tracking
            localStorage.setItem('visitor_id', visitorId);
            
        } catch (error) {
            console.error('Error tracking visitor:', error);
        }
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadVisitorStats();
            this.loadPerformanceMetrics();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            // Fallback toast
            const toast = document.createElement('div');
            toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white ${
                type === 'success' ? 'bg-green-600' : 
                type === 'error' ? 'bg-red-600' : 'bg-blue-600'
            }`;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 3000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.analyticsDashboard) {
        window.analyticsDashboard.stopAutoRefresh();
    }
}); 