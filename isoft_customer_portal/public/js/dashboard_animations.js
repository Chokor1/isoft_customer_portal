/**
 * Dashboard Animations & Modern Interactions
 * Handles all the cool visual effects and animations for the dashboard
 */

class DashboardAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupParallaxEffects();
        this.setupHoverEffects();
        this.setupCounterAnimations();
        this.setupPageTransitions();
    }

    setupIntersectionObserver() {
        // Create intersection observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animationType = element.getAttribute('data-animate');
                    const delay = element.getAttribute('data-delay') || '0s';
                    
                    if (animationType) {
                        element.style.setProperty('--delay', delay);
                        element.classList.add('animate-in');
                        
                        // Trigger counter animation if it's a summary card
                        if (element.classList.contains('summary-card')) {
                            this.animateCounter(element);
                        }
                    }
                    
                    observer.unobserve(element);
                }
            });
        }, observerOptions);

        // Observe all elements with data-animate attribute
        document.querySelectorAll('[data-animate]').forEach(el => {
            observer.observe(el);
        });
    }

    setupParallaxEffects() {
        // Add subtle parallax effect to cards on scroll
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.modern-card');
            
            parallaxElements.forEach((el, index) => {
                const speed = 0.05 + (index * 0.01);
                const yPos = -(scrolled * speed);
                el.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    setupHoverEffects() {
        // Enhanced hover effects for interactive elements
        document.querySelectorAll('.modern-card').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e);
                this.addGlowEffect(card);
            });

            card.addEventListener('mouseleave', (e) => {
                this.removeGlowEffect(card);
            });
        });

        // Add click ripple effect to buttons
        document.querySelectorAll('.period-btn, .quick-action-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.createClickRipple(e);
            });
        });
    }

    createRippleEffect(event) {
        const card = event.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 1;
        `;

        card.style.position = 'relative';
        card.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    createClickRipple(event) {
        const btn = event.currentTarget;
        const rect = btn.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.cssText = `
            position: absolute;
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: clickRipple 0.4s ease-out;
            pointer-events: none;
            z-index: 2;
        `;

        btn.style.position = 'relative';
        btn.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 400);
    }

    addGlowEffect(element) {
        element.style.boxShadow = '0 0 30px rgba(59, 130, 246, 0.3), 0 20px 25px -5px rgba(0, 0, 0, 0.1)';
    }

    removeGlowEffect(element) {
        element.style.boxShadow = '';
    }

    animateCounter(card) {
        const valueElement = card.querySelector('.summary-value');
        if (!valueElement) return;

        const finalValue = valueElement.textContent.replace(/[^\d.-]/g, '');
        if (!finalValue || isNaN(finalValue)) return;

        const startValue = 0;
        const endValue = parseFloat(finalValue);
        const duration = 2000;
        const startTime = performance.now();

        const animateValue = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (endValue - startValue) * easeOutQuart;
            
            // Format the value based on the original format
            const originalText = valueElement.textContent;
            if (originalText.includes('$')) {
                valueElement.textContent = '$' + Math.floor(currentValue).toLocaleString();
            } else if (originalText.includes('%')) {
                valueElement.textContent = Math.floor(currentValue) + '%';
            } else {
                valueElement.textContent = Math.floor(currentValue).toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(animateValue);
            } else {
                // Restore original formatting
                valueElement.textContent = originalText;
            }
        };

        requestAnimationFrame(animateValue);
    }

    setupCounterAnimations() {
        // Set initial state for counters, but only if they haven't been made visible yet
        document.querySelectorAll('.summary-value').forEach(el => {
            // Only hide elements that haven't been explicitly made visible by updateSummary
            if (!el.hasAttribute('data-summary-updated')) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
            }
        });
    }

    setupPageTransitions() {
        // Smooth page transitions
        document.addEventListener('DOMContentLoaded', () => {
            document.body.style.opacity = '0';
            document.body.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                document.body.style.transition = 'all 0.6s ease-out';
                document.body.style.opacity = '1';
                document.body.style.transform = 'translateY(0)';
            }, 100);
        });

        // Add loading states for dynamic content
        this.setupLoadingStates();
    }

    setupLoadingStates() {
        // Enhanced loading animations for charts and data
        const loadingElements = document.querySelectorAll('.chart-container canvas');
        
        loadingElements.forEach(canvas => {
            const container = canvas.closest('.chart-container');
            if (container) {
                this.showChartSkeleton(container);
            }
        });
    }

    showChartSkeleton(container) {
        const skeleton = document.createElement('div');
        skeleton.className = 'chart-skeleton';
        skeleton.innerHTML = `
            <div class="skeleton-header">
                <div class="skeleton-line" style="width: 60%; height: 16px;"></div>
                <div class="skeleton-line" style="width: 40%; height: 12px; margin-top: 8px;"></div>
            </div>
            <div class="skeleton-chart">
                <div class="skeleton-bars">
                    <div class="skeleton-bar" style="height: 60%;"></div>
                    <div class="skeleton-bar" style="height: 80%;"></div>
                    <div class="skeleton-bar" style="height: 45%;"></div>
                    <div class="skeleton-bar" style="height: 90%;"></div>
                    <div class="skeleton-bar" style="height: 70%;"></div>
                </div>
            </div>
        `;

        skeleton.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            flex-direction: column;
            padding: 20px;
            z-index: 5;
        `;

        container.appendChild(skeleton);

        // Remove skeleton when chart is loaded
        setTimeout(() => {
            skeleton.style.opacity = '0';
            setTimeout(() => {
                skeleton.remove();
            }, 300);
        }, 2000);
    }

    // Utility method to trigger manual animations
    triggerAnimation(element, animationType, delay = 0) {
        setTimeout(() => {
            element.setAttribute('data-animate', animationType);
            element.classList.add('animate-in');
        }, delay);
    }

    // Method to create floating particles effect
    createFloatingParticles() {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'floating-particles';
        particlesContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            overflow: hidden;
        `;

        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(59, 130, 246, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${Math.random() * 20 + 10}s infinite linear;
            `;
            
            particlesContainer.appendChild(particle);
        }

        document.body.appendChild(particlesContainer);
    }
}

// Add required CSS for animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes ripple {
        to {
            transform: scale(50);
            opacity: 0;
        }
    }

    @keyframes clickRipple {
        to {
            transform: scale(20);
            opacity: 0;
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
        }
        25% {
            transform: translateY(-20px) rotate(90deg);
        }
        50% {
            transform: translateY(-40px) rotate(180deg);
        }
        75% {
            transform: translateY(-20px) rotate(270deg);
        }
    }

    .skeleton-line {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200px 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px;
        margin-bottom: 8px;
    }

    .skeleton-bars {
        display: flex;
        align-items: end;
        gap: 8px;
        height: 200px;
        margin-top: 20px;
    }

    .skeleton-bar {
        flex: 1;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200px 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px 4px 0 0;
        animation-delay: calc(var(--i) * 0.1s);
    }

    .skeleton-bar:nth-child(1) { --i: 0; }
    .skeleton-bar:nth-child(2) { --i: 1; }
    .skeleton-bar:nth-child(3) { --i: 2; }
    .skeleton-bar:nth-child(4) { --i: 3; }
    .skeleton-bar:nth-child(5) { --i: 4; }

    .animate-in .summary-value {
        opacity: 1 !important;
        transform: translateY(0) !important;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        transition-delay: 0.2s;
    }

    .floating-particles {
        opacity: 0.6;
    }
`;

document.head.appendChild(animationStyles);

// Initialize dashboard animations when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for other scripts to load
    setTimeout(() => {
        window.dashboardAnimations = new DashboardAnimations();
    }, 500);
});

// Export for global access
window.DashboardAnimations = DashboardAnimations;
