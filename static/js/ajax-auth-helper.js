/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// AJAX Authentication Helper for Web UI
// This helper ensures all AJAX calls include proper authentication

(function() {
    'use strict';
    
    // Store original fetch and XMLHttpRequest
    const originalFetch = window.fetch;
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;
    
    // Helper to get CSRF token from meta tag
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
    }
    
    // Helper to get session cookie for API calls
    function getSessionCookie() {
        return document.cookie.split(';').find(cookie => 
            cookie.trim().startsWith('lily_session=')
        );
    }
    
    // Enhanced fetch with authentication
    window.fetch = function(url, options = {}) {
        // Only add authentication for API calls (safely convert URL objects/Requests to string)
        const urlString = (url && typeof url === 'object' && 'url' in url) ? url.url : String(url || '');
        if (urlString.includes('/api/')) {
            options.headers = options.headers || {};
            
            // Add CSRF token if available
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                options.headers['X-CSRFToken'] = csrfToken;
            }
            
            // Add session cookie
            const sessionCookie = getSessionCookie();
            if (sessionCookie) {
                options.headers['Cookie'] = sessionCookie;
            }
            
            // Ensure credentials are included for session authentication
            options.credentials = 'same-origin';
        }
        
        return originalFetch.call(this, url, options);
    };
    
    // Enhanced XMLHttpRequest with authentication
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        this._url = url;
        return originalXHROpen.call(this, method, url, async, user, password);
    };
    
    XMLHttpRequest.prototype.send = function(data) {
        // Only add authentication for API calls
        const urlString = this._url ? String(this._url) : '';
        if (urlString.includes('/api/')) {
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                this.setRequestHeader('X-CSRFToken', csrfToken);
            }
            
            const sessionCookie = getSessionCookie();
            if (sessionCookie) {
                this.setRequestHeader('Cookie', sessionCookie);
            }
        }
        
        return originalXHRSend.call(this, data);
    };
    
    console.log('🔐 AJAX Authentication Helper loaded');
})();
