/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * Lazy Loading Implementation
 * Handles progressive image loading and performance optimization
 */

class LazyLoader {
    constructor() {
        this.images = [];
        this.observer = null;
        this.init();
    }

    init() {
        // Get all lazy images
        this.images = document.querySelectorAll('img[data-src]');
        
        if (this.images.length === 0) return;

        // Check if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            this.setupIntersectionObserver();
        } else {
            this.setupFallback();
        }
    }

    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px 0px', // Start loading 50px before image enters viewport
            threshold: 0.01
        });

        this.images.forEach(img => {
            this.observer.observe(img);
        });
    }

    setupFallback() {
        // Fallback for older browsers
        let active = false;

        const lazyLoad = () => {
            if (active) return;
            active = true;

            setTimeout(() => {
                this.images.forEach(img => {
                    if (this.isInViewport(img)) {
                        this.loadImage(img);
                    }
                });

                // Remove loaded images from array
                this.images = Array.from(this.images).filter(img => !img.dataset.src);
                
                if (this.images.length === 0) {
                    document.removeEventListener('scroll', lazyLoad);
                    window.removeEventListener('resize', lazyLoad);
                    window.removeEventListener('orientationchange', lazyLoad);
                }

                active = false;
            }, 200);
        };

        document.addEventListener('scroll', lazyLoad);
        window.addEventListener('resize', lazyLoad);
        window.addEventListener('orientationchange', lazyLoad);
        
        // Initial load
        lazyLoad();
    }

    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (!src) return;

        // Create a new image to preload
        const tempImage = new Image();
        
        tempImage.onload = () => {
            img.src = src;
            img.classList.remove('lazy');
            img.classList.add('loaded');
            
            // Trigger custom event
            img.dispatchEvent(new CustomEvent('lazyLoaded', { detail: { src } }));
        };

        tempImage.onerror = () => {
            img.classList.add('lazy-error');
            console.warn(`Failed to load image: ${src}`);
        };

        tempImage.src = src;
        img.removeAttribute('data-src');
    }
}

/**
 * Progressive Image Loading
 * Loads low-quality placeholder first, then high-quality image
 */
class ProgressiveLoader {
    constructor() {
        this.images = [];
        this.init();
    }

    init() {
        this.images = document.querySelectorAll('img[data-srcset]');
        
        if (this.images.length === 0) return;

        this.images.forEach(img => {
            this.loadProgressiveImage(img);
        });
    }

    loadProgressiveImage(img) {
        const srcset = img.dataset.srcset;
        const sizes = img.dataset.sizes || '100vw';
        
        // Set srcset and sizes
        img.srcset = srcset;
        img.sizes = sizes;
        
        // Remove data attributes
        img.removeAttribute('data-srcset');
        img.removeAttribute('data-sizes');
        
        // Add loaded class
        img.classList.add('progressive-loaded');
    }
}

/**
 * Performance Monitoring
 * Tracks image loading performance
 */
class PerformanceTracker {
    constructor() {
        this.metrics = {
            totalImages: 0,
            loadedImages: 0,
            failedImages: 0,
            totalLoadTime: 0
        };
        this.init();
    }

    init() {
        document.addEventListener('lazyLoaded', (e) => {
            this.metrics.loadedImages++;
            this.updateMetrics();
        });

        // Track failed loads
        document.addEventListener('error', (e) => {
            if (e.target.tagName === 'IMG') {
                this.metrics.failedImages++;
                this.updateMetrics();
            }
        }, true);
    }

    updateMetrics() {
        const total = this.metrics.loadedImages + this.metrics.failedImages;
        const successRate = total > 0 ? (this.metrics.loadedImages / total * 100).toFixed(1) : 0;
        
        console.log(`Image loading: ${this.metrics.loadedImages} loaded, ${this.metrics.failedImages} failed (${successRate}% success rate)`);
    }
}

/**
 * Image Optimization Utilities
 */
class ImageOptimizer {
    static generateSrcSet(src, sizes = [300, 600, 900, 1200, 1500]) {
        return sizes.map(size => `${src}?w=${size} ${size}w`).join(', ');
    }

    static generateSizes(breakpoints = {
        'default': '100vw',
        '768px': '50vw',
        '1024px': '33.33vw'
    }) {
        return Object.entries(breakpoints)
            .map(([breakpoint, size]) => 
                breakpoint === 'default' ? size : `(min-width: ${breakpoint}) ${size}`
            )
            .join(', ');
    }

    static createLazyImage(src, alt = '', classes = '', placeholder = '/static/pic/placeholder.png') {
        return `
            <img src="${placeholder}" 
                 data-src="${src}" 
                 alt="${alt}" 
                 class="lazy ${classes}" 
                 loading="lazy">
        `;
    }

    static createProgressiveImage(src, alt = '', classes = '', sizes = '100vw') {
        const srcset = this.generateSrcSet(src);
        return `
            <img src="${src}" 
                 srcset="${srcset}"
                 sizes="${sizes}"
                 alt="${alt}" 
                 class="progressive ${classes}" 
                 loading="lazy">
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new LazyLoader();
    new ProgressiveLoader();
    new PerformanceTracker();
});

// Export for use in other modules
window.LazyLoader = LazyLoader;
window.ProgressiveLoader = ProgressiveLoader;
window.PerformanceTracker = PerformanceTracker;
window.ImageOptimizer = ImageOptimizer;
