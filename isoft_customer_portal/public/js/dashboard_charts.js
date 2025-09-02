/**
 * Modern Dashboard Charts & Analytics
 * Interactive data visualization for customer portal
 * Enhanced with animations, better error handling, and modern design
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
        // Update active button with smooth transition
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${period}"]`).classList.add('active');
        
        this.chartData.period = parseInt(period);
        this.showChartLoading();
        this.loadChartData();
    }

    loadChartData() {
        // Check if frappe is available
        if (typeof frappe === 'undefined' || !frappe.call) {
            console.warn('Frappe not available, retrying in 1 second...');
            setTimeout(() => this.loadChartData(), 1000);
            return;
        }

        this.showChartLoading();

        // Load data for the current period
        frappe.call({
            method: 'isoft_customer_portal.api.get_dashboard_chart_data',
            args: {
                period: this.chartData.period
            },
            callback: (response) => {
                console.log('Chart data response:', response);
                if (response.message) {
                    this.chartData = { ...this.chartData, ...response.message };
                    console.log('Updated chart data:', this.chartData);
                    this.renderCharts();
                } else {
                    console.warn('No data received from server');
                    this.renderChartsWithEmptyData();
                }
            },
            error: (response) => {
                console.error('Failed to load chart data:', response);
                if (response && response.exc_type === 'PermissionError') {
                    this.showChartError('Permission denied. Please check your access.');
                } else {
                    this.renderChartsWithEmptyData();
                }
            }
        });
    }

    renderChartsWithEmptyData() {
        console.log('Rendering charts with empty data');
        // Set empty data and render charts
        this.chartData = {
            ...this.chartData,
            revenue: [],
            status: {},
            items: [],
            activities: []
        };
        this.renderCharts();
    }

    showChartLoading() {
        const charts = ['revenueChart', 'statusChart', 'itemsChart'];
        
        charts.forEach(chartId => {
            const canvas = document.getElementById(chartId);
            const loadingDiv = document.getElementById(chartId.replace('Chart', '-loading'));
            
            if (canvas) {
                // Hide canvas while loading
                canvas.style.display = 'none';
            }
            
            if (loadingDiv) {
                // Show loading div
                loadingDiv.style.display = 'flex';
            }
        });
    }

    hideChartLoading() {
        const charts = ['revenueChart', 'statusChart', 'itemsChart'];
        
        charts.forEach(chartId => {
            const canvas = document.getElementById(chartId);
            const loadingDiv = document.getElementById(chartId.replace('Chart', '-loading'));
            
            if (canvas) {
                // Show canvas after loading
                canvas.style.display = 'block';
            }
            
            if (loadingDiv) {
                // Hide loading div
                loadingDiv.style.display = 'none';
            }
        });
    }

    drawLoadingSpinner(ctx, x, y) {
        ctx.save();
        ctx.translate(x, y);
        
        // Draw spinning circle
        const radius = 20;
        const lineWidth = 4;
        
        ctx.lineWidth = lineWidth;
        ctx.lineCap = 'round';
        
        // Background circle
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(156, 163, 175, 0.3)';
        ctx.stroke();
        
        // Animated arc
        const progress = (Date.now() / 10) % 360;
        ctx.beginPath();
        ctx.arc(0, 0, radius, -Math.PI / 2, -Math.PI / 2 + (progress * Math.PI / 180));
        ctx.strokeStyle = '#3B82F6';
        ctx.stroke();
        
        // Loading text
        ctx.fillStyle = '#6B7280';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Loading...', 0, radius + 35);
        
        ctx.restore();
        
        // Continue animation
        setTimeout(() => {
            if (document.getElementById('revenueChart')) {
                this.drawLoadingSpinner(ctx, x, y);
            }
        }, 50);
    }

    showChartError(message = 'Error loading chart') {
        const charts = ['revenueChart', 'statusChart', 'itemsChart'];
        
        charts.forEach(chartId => {
            const canvas = document.getElementById(chartId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Error icon and message
                ctx.fillStyle = '#EF4444';
                ctx.font = '16px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('⚠️', canvas.width / 2, canvas.height / 2 - 10);
                
                ctx.fillStyle = '#6B7280';
                ctx.font = '14px Inter, sans-serif';
                ctx.fillText(message, canvas.width / 2, canvas.height / 2 + 20);
            }
        });
    }

    renderCharts() {
        this.hideChartLoading();
        this.renderRevenueChart();
        this.renderStatusChart();
        this.renderItemsChart();
        this.updateActivityTimeline();
    }

    renderRevenueChart() {
        const canvas = document.getElementById('revenueChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.revenueChart) {
            this.revenueChart.destroy();
            this.revenueChart = null;
        }

        // Also check for any existing Chart.js instance on this canvas
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        const ctx = canvas.getContext('2d');

        const data = this.chartData.revenue || [];
        
        // Handle different data formats - could be monthly aggregated or daily data
        let labels, values;
        if (data.length > 0 && data[0].month) {
            // Monthly data format
            labels = data.map(item => item.month);
            values = data.map(item => item.amount || 0);
        } else if (data.length > 0 && data[0].date) {
            // Daily data format - group by month
            const monthlyData = this.groupDataByMonth(data);
            labels = monthlyData.map(item => item.month);
            values = monthlyData.map(item => item.amount);
        } else {
            // No data - show empty chart with sample structure
            labels = this.getEmptyLabels();
            values = new Array(labels.length).fill(0);
        }

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)');

        this.revenueChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: values,
                    borderColor: '#3B82F6',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3B82F6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: '#1D4ED8',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#F9FAFB',
                        bodyColor: '#F9FAFB',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Revenue: ' + context.parsed.y.toLocaleString() + ' AKZ';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)',
                            borderDash: [2, 2]
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12,
                                family: 'Inter'
                            },
                            callback: function(value) {
                                return value.toLocaleString() + ' AKZ';
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                },
                elements: {
                    line: {
                        capBezierPoints: false
                    }
                }
            }
        });
    }

    renderStatusChart() {
        const canvas = document.getElementById('statusChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.statusChart) {
            this.statusChart.destroy();
            this.statusChart = null;
        }

        // Also check for any existing Chart.js instance on this canvas
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        const ctx = canvas.getContext('2d');

        const data = this.chartData.status || {};
        
        // Handle different data formats - array or object
        let labels, values;
        if (Array.isArray(data) && data.length > 0) {
            // If data is an array of objects
            labels = data.map(item => item.status || item.label || 'Unknown');
            values = data.map(item => item.count || item.value || 0);
        } else if (typeof data === 'object' && Object.keys(data).length > 0) {
            // If data is an object
            labels = Object.keys(data);
            values = Object.values(data);
        } else {
            // Default data if no status data available
            labels = ['No Data'];
            values = [1];
        }

        const colors = {
            'Draft': '#94A3B8',
            'Submitted': '#3B82F6', 
            'Paid': '#10B981',
            'Overdue': '#EF4444',
            'Cancelled': '#6B7280',
            'Open': '#F59E0B',
            'No Data': '#E5E7EB'
        };
        
        const backgroundColors = labels.map(label => colors[label] || '#8B5CF6');
        const hoverColors = labels.map(label => {
            const baseColor = colors[label] || '#8B5CF6';
            return this.darkenColor(baseColor, 0.1);
        });

        this.statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    hoverBackgroundColor: hoverColors,
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                size: 12,
                                family: 'Inter',
                                weight: '500'
                            },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#F9FAFB',
                        bodyColor: '#F9FAFB',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    renderItemsChart() {
        const canvas = document.getElementById('itemsChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.itemsChart) {
            this.itemsChart.destroy();
            this.itemsChart = null;
        }

        // Also check for any existing Chart.js instance on this canvas
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        const ctx = canvas.getContext('2d');

        const data = this.chartData.items || [];
        
        let labels, values;
        if (data.length > 0) {
            // Take top 10 items to avoid overcrowding, filter out items with 0 values
            const validItems = data.filter(item => (item.total_quantity || item.quantity || item.amount || item.total_revenue || 0) > 0);
            const topItems = validItems.slice(0, 10);
            
            if (topItems.length > 0) {
                labels = topItems.map(item => {
                    // Truncate long item names
                    const name = item.item_name || item.name || 'Unknown Item';
                    return name.length > 15 ? name.substring(0, 15) + '...' : name;
                });
                // Use total_quantity first, then quantity, then total_revenue as fallback
                values = topItems.map(item => item.total_quantity || item.quantity || item.total_revenue || item.amount || 0);
            } else {
                labels = ['No sales data'];
                values = [1]; // Show 1 to display something in the chart
            }
        } else {
            labels = ['No data available'];
            values = [1]; // Show 1 to display something in the chart
        }

        // Create gradient for bars
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, '#8B5CF6');
        gradient.addColorStop(1, '#A855F7');

        this.itemsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Quantity Sold',
                    data: values,
                    backgroundColor: gradient,
                    borderColor: '#7C3AED',
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: '#7C3AED',
                    hoverBorderColor: '#6D28D9',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#F9FAFB',
                        bodyColor: '#F9FAFB',
                        borderColor: '#374151',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                // Show full item name in tooltip
                                const validItems = data.filter(item => (item.total_quantity || item.quantity || item.amount || item.total_revenue || 0) > 0);
                                const topItems = validItems.slice(0, 10);
                                const fullData = topItems[context[0].dataIndex];
                                return fullData ? (fullData.item_name || fullData.name || 'Unknown Item') : context[0].label;
                            },
                            label: function(context) {
                                const validItems = data.filter(item => (item.total_quantity || item.quantity || item.amount || item.total_revenue || 0) > 0);
                                const topItems = validItems.slice(0, 10);
                                const itemData = topItems[context.dataIndex];
                                
                                if (itemData) {
                                    if (itemData.total_quantity || itemData.quantity) {
                                        return 'Quantity: ' + (itemData.total_quantity || itemData.quantity).toLocaleString();
                                    } else if (itemData.total_revenue) {
                                        return 'Revenue: ' + itemData.total_revenue.toLocaleString() + ' AKZ';
                                    }
                                }
                                return 'Value: ' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 11,
                                family: 'Inter'
                            },
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)',
                            borderDash: [2, 2]
                        },
                        ticks: {
                            color: '#6B7280',
                            font: {
                                size: 12,
                                family: 'Inter'
                            },
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                animation: {
                    duration: 1800,
                    easing: 'easeInOutQuart',
                    delay: function(context) {
                        return context.dataIndex * 100;
                    }
                }
            }
        });
    }

    updateActivityTimeline() {
        const timeline = document.getElementById('activity-timeline');
        if (!timeline || !this.chartData.activities) return;

        timeline.innerHTML = '';

        this.chartData.activities.slice(0, 5).forEach((activity, index) => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.style.animationDelay = `${index * 0.1}s`;
            
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
                    ${activity.amount ? `<span class="activity-amount">${this.formatCurrency(activity.amount)}</span>` : ''}
                </div>
            `;
            
            timeline.appendChild(item);
        });

        // Add "View All" link if there are more activities
        if (this.chartData.activities.length > 5) {
            const viewAll = document.createElement('div');
            viewAll.className = 'activity-item view-all-item';
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
            'Completed': 'activity-badge success',
            'Submitted': 'activity-badge info',
            'Paid': 'activity-badge success',
            'To Bill': 'activity-badge warning',
            'To Deliver': 'activity-badge warning',
            'Draft': 'activity-badge secondary',
            'Overdue': 'activity-badge danger'
        };
        
        const className = badgeClasses[status] || 'activity-badge';
        return `<span class="${className}">${status}</span>`;
    }

    formatCurrency(amount) {
        if (typeof amount === 'number') {
            return amount.toLocaleString('pt-AO') + ' AKZ';
        }
        return amount;
    }

    // Helper method to group daily data by month
    groupDataByMonth(dailyData) {
        const monthlyData = {};
        
        dailyData.forEach(item => {
            const date = new Date(item.date);
            const monthKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
            
            if (!monthlyData[monthKey]) {
                monthlyData[monthKey] = {
                    month: monthKey,
                    amount: 0
                };
            }
            
            monthlyData[monthKey].amount += parseFloat(item.amount || 0);
        });
        
        return Object.values(monthlyData).sort((a, b) => new Date(a.month) - new Date(b.month));
    }

    // Helper method to darken a color
    darkenColor(color, factor) {
        // Convert hex to rgb
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        
        // Darken each component
        const newR = Math.round(r * (1 - factor));
        const newG = Math.round(g * (1 - factor));
        const newB = Math.round(b * (1 - factor));
        
        // Convert back to hex
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }

    // Helper method to get empty labels based on period
    getEmptyLabels() {
        const now = new Date();
        const labels = [];
        
        if (this.chartData.period <= 90) {
            // For short periods, show last few months
            for (let i = 5; i >= 0; i--) {
                const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
                labels.push(date.toLocaleDateString('en-US', { month: 'short' }));
            }
        } else {
            // For longer periods, show last 12 months
            for (let i = 11; i >= 0; i--) {
                const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
                labels.push(date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' }));
            }
        }
        
        return labels;
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
        const canvases = ['revenueChart', 'statusChart', 'itemsChart'];
        canvases.forEach(canvasId => {
            const canvas = document.getElementById(canvasId);
            if (canvas && Chart.getChart(canvas)) {
                Chart.getChart(canvas).destroy();
            }
        });
    }
}

// Initialize dashboard charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        if ((document.getElementById('revenueChart') || document.getElementById('statusChart')) && !window.dashboardCharts) {
            window.dashboardCharts = new DashboardCharts();
        }
    }, 1000);
});

// Export for global access
window.DashboardCharts = DashboardCharts;