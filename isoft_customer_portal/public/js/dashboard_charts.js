/**
 * Modern Dashboard Charts & Analytics
 * Interactive data visualization for customer portal
 */

class DashboardCharts {
    constructor() {
        this.charts = {};
        this.chartData = {
            revenue: [],
            status: {},
            items: [],
            period: 365
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadChartData();
    }

    setupEventListeners() {
        // Period selector buttons
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changePeriod(e.target.dataset.period);
            });
        });
    }

    changePeriod(period) {
        // Update active button
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${period}"]`).classList.add('active');
        
        this.chartData.period = parseInt(period);
        this.loadChartData();
    }

    loadChartData() {
        // Load data for the current period
        frappe.call({
            method: 'isoft_customer_portal.api.get_dashboard_chart_data',
            args: {
                period: this.chartData.period
            },
            callback: (response) => {
                if (response.message) {
                    this.chartData = { ...this.chartData, ...response.message };
                    this.renderCharts();
                }
            },
            error: (response) => {
                this.showError('Failed to load chart data');
            }
        });
    }

    showChartLoading() {
        const revenueChart = document.getElementById('revenueChart');
        const statusChart = document.getElementById('statusChart');
        
        if (revenueChart) {
            const ctx = revenueChart.getContext('2d');
            ctx.clearRect(0, 0, revenueChart.width, revenueChart.height);
            ctx.fillStyle = '#94A3B8';
            ctx.font = '14px Inter';
            ctx.textAlign = 'center';
            ctx.fillText('Loading...', revenueChart.width / 2, revenueChart.height / 2);
        }
        
        if (statusChart) {
            const ctx = statusChart.getContext('2d');
            ctx.clearRect(0, 0, statusChart.width, statusChart.height);
            ctx.fillStyle = '#94A3B8';
            ctx.font = '14px Inter';
            ctx.textAlign = 'center';
            ctx.fillText('Loading...', statusChart.width / 2, statusChart.height / 2);
        }
    }

    showChartError() {
        const revenueChart = document.getElementById('revenueChart');
        const statusChart = document.getElementById('statusChart');
        
        if (revenueChart) {
            const ctx = revenueChart.getContext('2d');
            ctx.clearRect(0, 0, revenueChart.width, revenueChart.height);
            ctx.fillStyle = '#EF4444';
            ctx.font = '14px Inter';
            ctx.textAlign = 'center';
            ctx.fillText('Error loading chart', revenueChart.width / 2, revenueChart.height / 2);
        }
    }

    renderCharts() {
        this.renderRevenueChart();
        this.renderStatusChart();
        this.renderItemsChart();
    }

    renderRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.revenueChart) {
            this.revenueChart.destroy();
        }

        const data = this.chartData.revenue || [];
        const labels = data.map(item => item.month);
        const values = data.map(item => item.amount);

        this.revenueChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: values,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
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
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    renderStatusChart() {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.statusChart) {
            this.statusChart.destroy();
        }

        const data = this.chartData.status || [];
        const labels = data.map(item => item.status);
        const values = data.map(item => item.count);
        const colors = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

        this.statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
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

    updateActivityTimeline() {
        const timeline = document.getElementById('activity-timeline');
        if (!timeline || !this.chartData.activities) return;

        timeline.innerHTML = '';

        this.chartData.activities.slice(0, 5).forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            
            const timeAgo = this.formatTimeAgo(activity.date);
            const statusBadge = this.getStatusBadge(activity.status);
            
            item.innerHTML = `
                <div class="activity-header">
                    <h4 class="activity-title">${activity.title}</h4>
                    <span class="activity-time">${timeAgo}</span>
                </div>
                <p class="activity-description">${activity.description}</p>
                <div class="activity-meta">
                    ${statusBadge}
                    ${activity.amount ? `<span class="activity-amount">${isoft_customer_portal.utils.formatCurrency(activity.amount)}</span>` : ''}
                </div>
            `;
            
            timeline.appendChild(item);
        });

        // Add "View All" link if there are more activities
        if (this.chartData.activities.length > 5) {
            const viewAll = document.createElement('div');
            viewAll.className = 'activity-item';
            viewAll.innerHTML = `
                <div style="text-align: center; padding: 1rem 0;">
                    <a href="/customer-ledger" class="btn btn-sm btn-ghost">
                        <i class="fas fa-eye"></i>
                        View All Activities
                    </a>
                </div>
            `;
            timeline.appendChild(viewAll);
        }
    }

    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }

    getStatusBadge(status) {
        const badgeClasses = {
            'Completed': 'activity-badge',
            'Submitted': 'activity-badge',
            'Paid': 'activity-badge',
            'To Bill': 'activity-badge',
            'To Deliver': 'activity-badge'
        };
        
        const className = badgeClasses[status] || 'activity-badge';
        return `<span class="${className}">${status}</span>`;
    }

    // Public method to refresh all charts
    refresh() {
        this.destroyAllCharts();
        this.loadChartData();
    }

    destroyAllCharts() {
        // Destroy revenue chart
        if (this.revenueChart) {
            this.revenueChart.destroy();
            this.revenueChart = null;
        }
        
        // Destroy status chart
        if (this.statusChart) {
            this.statusChart.destroy();
            this.statusChart = null;
        }

        // Destroy items chart
        if (this.itemsChart) {
            this.itemsChart.destroy();
            this.itemsChart = null;
        }

        // Check for any registered charts on our canvases
        const revenueCanvas = document.getElementById('revenueChart');
        const statusCanvas = document.getElementById('statusChart');
        const itemsCanvas = document.getElementById('itemsChart');
        
        if (revenueCanvas && Chart.getChart(revenueCanvas)) {
            Chart.getChart(revenueCanvas).destroy();
        }
        
        if (statusCanvas && Chart.getChart(statusCanvas)) {
            Chart.getChart(statusCanvas).destroy();
        }

        if (itemsCanvas && Chart.getChart(itemsCanvas)) {
            Chart.getChart(itemsCanvas).destroy();
        }
    }

    renderItemsChart() {
        const ctx = document.getElementById('itemsChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.itemsChart) {
            this.itemsChart.destroy();
        }

        const data = this.chartData.items || [];
        const labels = data.map(item => item.item_name);
        const values = data.map(item => item.quantity);

        this.itemsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Quantity Sold',
                    data: values,
                    backgroundColor: '#8B5CF6',
                    borderColor: '#7C3AED',
                    borderWidth: 1
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
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize dashboard charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('revenueChart') || document.getElementById('statusChart')) {
        window.dashboardCharts = new DashboardCharts();
    }
});

// Export for global access
window.DashboardCharts = DashboardCharts;