/**
 * Modern Sidebar Navigation Controller
 * Handles sidebar toggle, active states, and breadcrumb navigation
 */

class SidebarNavigation {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.toggleBtn = null;
        this.closeBtn = null;
        this.isOpen = true; // Start with sidebar open
        this.init();
    }

    init() {
        this.bindElements();
        this.setupEventListeners();
        this.setActiveNavItem();
        this.updateBreadcrumb();
        this.loadUserInfo();
    }

    bindElements() {
        this.sidebar = document.getElementById('modernSidebar');
        this.overlay = document.getElementById('sidebarOverlay');
        this.toggleBtn = document.getElementById('sidebarToggle');
        this.closeBtn = document.getElementById('sidebarClose');
    }

    setupEventListeners() {
        // Toggle button
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggleSidebar());
        }

        // Close button
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.closeSidebar());
        }

        // Overlay click (removed since overlay is hidden)

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeSidebar();
            }
        });

        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                // Close sidebar on mobile after navigation
                if (window.innerWidth <= 768) {
                    setTimeout(() => this.closeSidebar(), 150);
                }
            });
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                // On mobile, close sidebar by default
                if (this.isOpen) {
                    this.closeSidebar();
                }
            } else {
                // On desktop, open sidebar by default
                if (!this.isOpen) {
                    this.openSidebar();
                }
            }
        });
    }

    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        if (!this.sidebar || !this.toggleBtn) return;

        this.isOpen = true;
        this.sidebar.classList.remove('closed');
        this.toggleBtn.classList.add('active');
        
        // Update main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.classList.remove('sidebar-closed');
        }
        
        // Animate hamburger
        this.animateHamburger(true);
    }

    closeSidebar() {
        if (!this.sidebar || !this.toggleBtn) return;

        this.isOpen = false;
        this.sidebar.classList.add('closed');
        this.toggleBtn.classList.remove('active');
        
        // Update main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.classList.add('sidebar-closed');
        }
        
        // Animate hamburger
        this.animateHamburger(false);
    }

    animateHamburger(isOpen) {
        const lines = this.toggleBtn && this.toggleBtn.querySelectorAll('.hamburger-line');
        if (!lines) return;

        if (isOpen) {
            lines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            lines[1].style.opacity = '0';
            lines[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        } else {
            lines[0].style.transform = '';
            lines[1].style.opacity = '';
            lines[2].style.transform = '';
        }
    }

    setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
                link.classList.add('active');
            }
        });
    }

    updateBreadcrumb() {
        const breadcrumbList = document.getElementById('breadcrumbList');
        if (!breadcrumbList) return;

        const currentPath = window.location.pathname;
        const pageTitle = document.title.replace(' - Isoft Customer Portal', '');
        
        // Clear existing breadcrumbs
        breadcrumbList.innerHTML = '';
        
        // Home breadcrumb
        const homeItem = document.createElement('li');
        homeItem.className = 'breadcrumb-item';
        homeItem.innerHTML = `
            <a href="/customer-dashboard" class="breadcrumb-link">
                <i class="fas fa-home"></i>
                <span>Dashboard</span>
            </a>
        `;
        breadcrumbList.appendChild(homeItem);
        
        // Current page breadcrumb (if not dashboard)
        if (currentPath !== '/customer-dashboard') {
            const currentItem = document.createElement('li');
            currentItem.className = 'breadcrumb-item';
            
            let icon = 'fas fa-file';
            if (currentPath.includes('invoice')) icon = 'fas fa-file-invoice-dollar';
            else if (currentPath.includes('sales-order')) icon = 'fas fa-shopping-cart';
            else if (currentPath.includes('quotation')) icon = 'fas fa-quote-left';
            else if (currentPath.includes('delivery')) icon = 'fas fa-truck';
            else if (currentPath.includes('payment')) icon = 'fas fa-credit-card';
            else if (currentPath.includes('ledger')) icon = 'fas fa-book';
            
            currentItem.innerHTML = `
                <a href="${currentPath}" class="breadcrumb-link">
                    <i class="${icon}"></i>
                    <span>${pageTitle}</span>
                </a>
            `;
            breadcrumbList.appendChild(currentItem);
        }
    }

    async loadUserInfo() {
        const userNameElement = document.getElementById('sidebarUserName');
        if (!userNameElement) return;

        // Check if we're on login/logout pages - skip loading user info
        const currentPath = window.location.pathname;
        if (currentPath.includes('login') || currentPath.includes('logout')) {
            userNameElement.textContent = 'Guest';
            return;
        }

        try {
            // Check authentication first
            const authResponse = await frappe.call({
                method: 'isoft_customer_portal.api.check_customer_auth',
                freeze: false
            });

            if (!authResponse.message || !authResponse.message.authenticated) {
                userNameElement.textContent = 'Guest';
                return;
            }

            // Get current customer info
            const response = await frappe.call({
                method: 'isoft_customer_portal.api.get_current_customer_info',
                freeze: false
            });

            if (response.message && response.message.customer_name && response.message.customer_name !== 'Guest') {
                userNameElement.textContent = response.message.customer_name;
                
                // Update header user name if exists
                const headerUserName = document.getElementById('customer-name');
                if (headerUserName) {
                    headerUserName.textContent = response.message.customer_name;
                }
            } else {
                userNameElement.textContent = 'Guest';
            }
        } catch (error) {
            console.error('Error loading user info:', error);
            userNameElement.textContent = 'Guest';
        }
    }

    // Public method to update active nav item
    updateActiveNavItem(path) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === path) {
                link.classList.add('active');
            }
        });
    }

    // Public method to update breadcrumb
    updateBreadcrumbManually(items) {
        const breadcrumbList = document.getElementById('breadcrumbList');
        if (!breadcrumbList) return;

        breadcrumbList.innerHTML = '';
        
        items.forEach((item, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'breadcrumb-item';
            
            if (index === items.length - 1) {
                // Last item (current page)
                listItem.innerHTML = `
                    <span class="breadcrumb-link">
                        <i class="${item.icon}"></i>
                        <span>${item.text}</span>
                    </span>
                `;
            } else {
                // Clickable items
                listItem.innerHTML = `
                    <a href="${item.href}" class="breadcrumb-link">
                        <i class="${item.icon}"></i>
                        <span>${item.text}</span>
                    </a>
                `;
            }
            
            breadcrumbList.appendChild(listItem);
        });
    }
}

// Initialize sidebar navigation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on login/logout pages - don't initialize sidebar
    const currentPath = window.location.pathname;
    if (currentPath.includes('login') || currentPath.includes('logout')) {
        return;
    }
    
    // Only initialize sidebar on protected pages
    const protectedPages = ['/customer-dashboard', '/customer-invoices', '/customer-ledger', 
                           '/customer-quotations', '/customer-sales-orders', '/customer-delivery-notes', 
                           '/customer-payment-entries'];
    
    if (protectedPages.some(page => currentPath.includes(page))) {
        window.sidebarNavigation = new SidebarNavigation();
    }
});

// Export for global access
window.SidebarNavigation = SidebarNavigation;