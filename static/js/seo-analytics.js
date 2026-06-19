/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * SEO Analytics JavaScript
 * Handles the SEO analytics page functionality
 */

let seoScoreChart = null;
let contentPerformanceChart = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the page
    initializeAnalytics();
    
    // Load analytics data
    loadAnalyticsData();
    
    // Setup event listeners
    setupEventListeners();
});

function initializeAnalytics() {
    console.log('Initializing SEO Analytics...');
}

function loadAnalyticsData() {
    // Load overview stats
    loadOverviewStats();
    
    // Load charts
    loadCharts();
    
    // Load status breakdown
    loadStatusBreakdown();
    
    // Load recent activity
    loadRecentActivity();
    
    // Load recommendations
    loadRecommendations();
}

function loadOverviewStats() {
    // Load total content stats
    fetch('/api/seo/stats/overview')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateOverviewStats(data.stats);
            }
        })
        .catch(error => {
            console.error('Error loading overview stats:', error);
            // Use mock data for now
            updateOverviewStats(getMockOverviewStats());
        });
}

function updateOverviewStats(stats) {
    // Total content
    document.getElementById('total-content').textContent = stats.total_content || 0;
    document.getElementById('total-articles').textContent = stats.total_articles || 0;
    document.getElementById('total-albums').textContent = stats.total_albums || 0;
    document.getElementById('total-chapters').textContent = stats.total_chapters || 0;
    
    // Average SEO score
    const avgScore = stats.avg_seo_score || 0;
    document.getElementById('avg-seo-score').textContent = avgScore.toFixed(1);
    document.getElementById('seo-score-progress').style.width = `${Math.min(avgScore, 100)}%`;
    
    // Completion rate
    const completionRate = stats.seo_completion_rate || 0;
    document.getElementById('seo-completion-rate').textContent = `${completionRate.toFixed(1)}%`;
    document.getElementById('completion-progress').style.width = `${completionRate}%`;
    
    // Recent activity
    document.getElementById('recent-activity-count').textContent = stats.recent_activity_count || 0;
}

function loadCharts() {
    // Load SEO score distribution chart
    loadSEOScoreChart();
    
    // Load content performance chart
    loadContentPerformanceChart();
}

function loadSEOScoreChart() {
    fetch('/api/seo/stats/score-distribution')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                createSEOScoreChart(data.distribution);
            }
        })
        .catch(error => {
            console.error('Error loading score distribution:', error);
            // Use mock data
            createSEOScoreChart(getMockScoreDistribution());
        });
}

function createSEOScoreChart(distribution) {
    // Check if canvas element exists and has proper context
    const canvasElement = document.getElementById('seo-score-chart');
    if (!canvasElement) {
        console.error('SEO Score chart canvas element not found');
        return;
    }

    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.error('Failed to get 2D context for SEO Score chart');
        return;
    }

    // Destroy existing chart if it exists
    if (seoScoreChart) {
        try {
            seoScoreChart.destroy();
        } catch (error) {
            console.warn('Error destroying existing SEO Score chart:', error);
        }
    }
    
    seoScoreChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
            datasets: [{
                label: 'Jumlah Konten',
                data: [
                    distribution.score_0_20 || 0,
                    distribution.score_21_40 || 0,
                    distribution.score_41_60 || 0,
                    distribution.score_61_80 || 0,
                    distribution.score_81_100 || 0
                ],
                backgroundColor: [
                    '#ef4444', // red
                    '#f97316', // orange
                    '#eab308', // yellow
                    '#22c55e', // green
                    '#3b82f6'  // blue
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function loadContentPerformanceChart() {
    fetch('/api/seo/stats/content-performance')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                createContentPerformanceChart(data.performance);
            }
        })
        .catch(error => {
            console.error('Error loading content performance:', error);
            // Use mock data
            createContentPerformanceChart(getMockContentPerformance());
        });
}

function createContentPerformanceChart(performance) {
    // Check if canvas element exists and has proper context
    const canvasElement = document.getElementById('content-performance-chart');
    if (!canvasElement) {
        console.error('Content performance chart canvas element not found');
        return;
    }

    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.error('Failed to get 2D context for content performance chart');
        return;
    }

    // Destroy existing chart if it exists
    if (contentPerformanceChart) {
        try {
            contentPerformanceChart.destroy();
        } catch (error) {
            console.warn('Error destroying existing content performance chart:', error);
        }
    }
    
    contentPerformanceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Artikel', 'Album', 'Bab'],
            datasets: [{
                data: [
                    performance.articles_avg_score || 0,
                    performance.albums_avg_score || 0,
                    performance.chapters_avg_score || 0
                ],
                backgroundColor: [
                    '#3b82f6', // blue
                    '#10b981', // green
                    '#f59e0b'  // amber
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function loadStatusBreakdown() {
    fetch('/api/seo/stats/status-breakdown')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatusBreakdown(data.breakdown);
            }
        })
        .catch(error => {
            console.error('Error loading status breakdown:', error);
            // Use mock data
            updateStatusBreakdown(getMockStatusBreakdown());
        });
}

function updateStatusBreakdown(breakdown) {
    // Complete SEO
    document.getElementById('complete-articles').textContent = breakdown.complete?.articles || 0;
    document.getElementById('complete-albums').textContent = breakdown.complete?.albums || 0;
    document.getElementById('complete-chapters').textContent = breakdown.complete?.chapters || 0;
    document.getElementById('complete-total').textContent = (breakdown.complete?.articles || 0) + (breakdown.complete?.albums || 0) + (breakdown.complete?.chapters || 0);
    
    // Incomplete SEO
    document.getElementById('incomplete-articles').textContent = breakdown.incomplete?.articles || 0;
    document.getElementById('incomplete-albums').textContent = breakdown.incomplete?.albums || 0;
    document.getElementById('incomplete-chapters').textContent = breakdown.incomplete?.chapters || 0;
    document.getElementById('incomplete-total').textContent = (breakdown.incomplete?.articles || 0) + (breakdown.incomplete?.albums || 0) + (breakdown.incomplete?.chapters || 0);
    
    // Missing SEO
    document.getElementById('missing-articles').textContent = breakdown.missing?.articles || 0;
    document.getElementById('missing-albums').textContent = breakdown.missing?.albums || 0;
    document.getElementById('missing-chapters').textContent = breakdown.missing?.chapters || 0;
    document.getElementById('missing-total').textContent = (breakdown.missing?.articles || 0) + (breakdown.missing?.albums || 0) + (breakdown.missing?.chapters || 0);
}

function loadRecentActivity() {
    fetch('/api/seo/activity/recent')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateActivityTable(data.activities);
            }
        })
        .catch(error => {
            console.error('Error loading recent activity:', error);
            // Use mock data
            updateActivityTable(getMockRecentActivity());
        });
}

function updateActivityTable(activities) {
    const tbody = document.getElementById('activity-table-body');
    tbody.innerHTML = '';
    
    if (activities.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                    Tidak ada aktivitas terbaru
                </td>
            </tr>
        `;
        return;
    }
    
    activities.forEach(activity => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${formatDate(activity.timestamp)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${getContentTypeLabel(activity.content_type)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${activity.content_title}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${activity.action}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${activity.score_before || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${activity.score_after || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(activity.status)}">
                    ${activity.status}
                </span>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function loadRecommendations() {
    fetch('/api/seo/recommendations')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateRecommendations(data.recommendations);
            }
        })
        .catch(error => {
            console.error('Error loading recommendations:', error);
            // Use mock data
            updateRecommendations(getMockRecommendations());
        });
}

function updateRecommendations(recommendations) {
    // Priority actions
    const priorityActions = document.getElementById('priority-actions');
    priorityActions.innerHTML = '';
    
    if (recommendations.priority_actions && recommendations.priority_actions.length > 0) {
        recommendations.priority_actions.forEach(action => {
            const div = document.createElement('div');
            div.className = 'text-sm text-red-700';
            div.innerHTML = `• ${action}`;
            priorityActions.appendChild(div);
        });
    } else {
        priorityActions.innerHTML = '<div class="text-sm text-red-700">Tidak ada aksi prioritas</div>';
    }
    
    // Improvement suggestions
    const improvementSuggestions = document.getElementById('improvement-suggestions');
    improvementSuggestions.innerHTML = '';
    
    if (recommendations.improvement_suggestions && recommendations.improvement_suggestions.length > 0) {
        recommendations.improvement_suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'text-sm text-blue-700';
            div.innerHTML = `• ${suggestion}`;
            improvementSuggestions.appendChild(div);
        });
    } else {
        improvementSuggestions.innerHTML = '<div class="text-sm text-blue-700">Tidak ada saran peningkatan</div>';
    }
}

function setupEventListeners() {
    // Refresh button
    document.getElementById('refresh-analytics').addEventListener('click', function() {
        showToast('Memperbarui data analitik...', 'info');
        loadAnalyticsData();
    });
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            // Add active class to clicked button
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-gray-200', 'text-gray-700');
            
            // Filter data based on selected type
            const filter = this.dataset.filter;
            filterData(filter);
        });
    });
}

function filterData(filter) {
    // This would filter the displayed data based on the selected filter
    console.log('Filtering data by:', filter);
    // For now, just show a toast
    showToast(`Filtering by: ${filter}`, 'info');
}

// Utility functions
function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getContentTypeLabel(type) {
    const labels = {
        'article': 'Artikel',
        'album': 'Album',
        'chapter': 'Bab',
        'root': 'Halaman Root'
    };
    return labels[type] || type;
}

function getStatusColor(status) {
    const colors = {
        'success': 'bg-green-100 text-green-800',
        'error': 'bg-red-100 text-red-800',
        'warning': 'bg-yellow-100 text-yellow-800',
        'info': 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';
    
    toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);
}

// Mock data functions for development
function getMockOverviewStats() {
    return {
        total_content: 150,
        total_articles: 80,
        total_albums: 45,
        total_chapters: 25,
        avg_seo_score: 75.5,
        seo_completion_rate: 68.3,
        recent_activity_count: 12
    };
}

function getMockScoreDistribution() {
    return {
        score_0_20: 5,
        score_21_40: 12,
        score_41_60: 28,
        score_61_80: 45,
        score_81_100: 60
    };
}

function getMockContentPerformance() {
    return {
        articles_avg_score: 78.5,
        albums_avg_score: 72.3,
        chapters_avg_score: 68.9
    };
}

function getMockStatusBreakdown() {
    return {
        complete: {
            articles: 45,
            albums: 25,
            chapters: 15
        },
        incomplete: {
            articles: 25,
            albums: 15,
            chapters: 8
        },
        missing: {
            articles: 10,
            albums: 5,
            chapters: 2
        }
    };
}

function getMockRecentActivity() {
    return [
        {
            timestamp: new Date().toISOString(),
            content_type: 'article',
            content_title: 'Artikel Terbaru',
            action: 'SEO Injection',
            score_before: 45,
            score_after: 85,
            status: 'success'
        },
        {
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            content_type: 'album',
            content_title: 'Album Populer',
            action: 'SEO Update',
            score_before: 70,
            score_after: 90,
            status: 'success'
        }
    ];
}

function getMockRecommendations() {
    return {
        priority_actions: [
            'Perbaiki 15 artikel dengan skor SEO di bawah 50',
            'Tambahkan meta description untuk 8 album',
            'Update Open Graph tags untuk 5 bab'
        ],
        improvement_suggestions: [
            'Optimalkan gambar untuk meningkatkan loading speed',
            'Tambahkan structured data untuk artikel',
            'Perbaiki internal linking antar halaman'
        ]
    };
}

// Export functions for potential external use
window.SEOAnalytics = {
    loadAnalyticsData,
    refreshData: loadAnalyticsData,
    filterData
};
