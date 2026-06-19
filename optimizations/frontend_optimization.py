"""
Frontend Optimization Module
Handles asset minification, bundling, lazy loading, and progressive image loading
"""

import os
import re
from flask import current_app, url_for, request
from datetime import datetime
import hashlib

class FrontendOptimizer:
    """Frontend optimization utilities"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize frontend optimizer with app"""
        self.app = app
        
        # Register template filters
        app.jinja_env.filters['asset_version'] = self.asset_version
        app.jinja_env.filters['lazy_image'] = self.lazy_image
        app.jinja_env.filters['progressive_image'] = self.progressive_image
        
        # Register template globals
        app.jinja_env.globals['get_asset_url'] = self.get_asset_url
        app.jinja_env.globals['is_production'] = self.is_production
    
    def asset_version(self, filename):
        """Add version hash to asset URLs for cache busting"""
        if not filename:
            return filename
        
        # Get file path
        static_folder = self.app.static_folder
        file_path = os.path.join(static_folder, filename.lstrip('/'))
        
        if os.path.exists(file_path):
            # Get file modification time for versioning
            mtime = os.path.getmtime(file_path)
            version = str(int(mtime))
            return f"{filename}?v={version}"
        
        return filename
    
    def lazy_image(self, src, alt="", classes="", placeholder="/static/pic/placeholder.png"):
        """Generate lazy loading image HTML"""
        return f'''
        <img src="{placeholder}" 
             data-src="{src}" 
             alt="{alt}" 
             class="lazy {classes}" 
             loading="lazy"
             onload="this.classList.remove('lazy')">
        '''
    
    def progressive_image(self, src, alt="", classes="", sizes="100vw"):
        """Generate progressive loading image HTML with multiple sizes"""
        # Generate different sizes for responsive images
        base_name = os.path.splitext(src)[0]
        ext = os.path.splitext(src)[1]
        
        # Create srcset for different sizes
        srcset_parts = []
        sizes = [300, 600, 900, 1200, 1500]
        
        for size in sizes:
            # In a real implementation, you'd have different sized images
            # For now, we'll use the same image with size parameter
            srcset_parts.append(f"{src}?w={size} {size}w")
        
        srcset = ", ".join(srcset_parts)
        
        return f'''
        <img src="{src}" 
             srcset="{srcset}"
             sizes="{sizes}"
             alt="{alt}" 
             class="progressive {classes}" 
             loading="lazy">
        '''
    
    def get_asset_url(self, filename):
        """Get optimized asset URL with versioning"""
        return url_for('static', filename=filename)
    
    def is_production(self):
        """Check if running in production mode"""
        return not self.app.debug
    
    def minify_css(self, css_content):
        """Minify CSS content"""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        
        return css_content.strip()
    
    def minify_js(self, js_content):
        """Minify JavaScript content"""
        # Remove single-line comments
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        return js_content.strip()
    
    def generate_critical_css(self, template_name):
        """Generate critical CSS for above-the-fold content"""
        # This would integrate with a CSS extraction tool
        # For now, return basic critical CSS
        return """
        /* Critical CSS for above-the-fold content */
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        .header { background: #fff; padding: 1rem; }
        .main-content { padding: 1rem; }
        .news-item { margin-bottom: 1rem; padding: 1rem; border: 1px solid #ddd; }
        """

def create_frontend_optimizer(app):
    """Create and configure frontend optimizer"""
    optimizer = FrontendOptimizer(app)
    return optimizer

# Utility functions for template usage
def get_optimized_image_url(image_path, size=None):
    """Get optimized image URL with size parameter"""
    if size:
        return f"{image_path}?w={size}"
    return image_path

def generate_image_srcset(image_path, sizes=[300, 600, 900, 1200]):
    """Generate srcset for responsive images"""
    srcset_parts = []
    for size in sizes:
        srcset_parts.append(f"{image_path}?w={size} {size}w")
    return ", ".join(srcset_parts)

def get_lazy_loading_script():
    """Get lazy loading JavaScript"""
    return """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));
        
        if ("IntersectionObserver" in window) {
            let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        let lazyImage = entry.target;
                        lazyImage.src = lazyImage.dataset.src;
                        lazyImage.classList.remove("lazy");
                        lazyImageObserver.unobserve(lazyImage);
                    }
                });
            });
            
            lazyImages.forEach(function(lazyImage) {
                lazyImageObserver.observe(lazyImage);
            });
        } else {
            // Fallback for older browsers
            let active = false;
            
            const lazyLoad = function() {
                if (active === false) {
                    active = true;
                    
                    setTimeout(function() {
                        lazyImages.forEach(function(lazyImage) {
                            if ((lazyImage.getBoundingClientRect().top <= window.innerHeight && lazyImage.getBoundingClientRect().bottom >= 0) && getComputedStyle(lazyImage).display !== "none") {
                                lazyImage.src = lazyImage.dataset.src;
                                lazyImage.classList.remove("lazy");
                                
                                lazyImages = lazyImages.filter(function(image) {
                                    return image !== lazyImage;
                                });
                                
                                if (lazyImages.length === 0) {
                                    document.removeEventListener("scroll", lazyLoad);
                                    window.removeEventListener("resize", lazyLoad);
                                    window.removeEventListener("orientationchange", lazyLoad);
                                }
                            }
                        });
                        
                        active = false;
                    }, 200);
                }
            };
            
            document.addEventListener("scroll", lazyLoad);
            window.addEventListener("resize", lazyLoad);
            window.addEventListener("orientationchange", lazyLoad);
        }
    });
    </script>
    """

def get_performance_monitoring_script():
    """Get performance monitoring JavaScript"""
    return """
    <script>
    // Performance monitoring
    window.addEventListener('load', function() {
        setTimeout(function() {
            var perfData = performance.getEntriesByType('navigation')[0];
            var loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            var domContentLoaded = perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart;
            
            console.log('Page Load Time:', loadTime + 'ms');
            console.log('DOM Content Loaded:', domContentLoaded + 'ms');
            
            // Send to analytics if available
            if (typeof gtag !== 'undefined') {
                gtag('event', 'timing_complete', {
                    'name': 'load',
                    'value': loadTime
                });
            }
        }, 0);
    });
    </script>
    """ 