/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * CSRF Utilities for AJAX Requests
 * Provides CSRF token handling for all AJAX requests
 */

// Get CSRF token from meta tag
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
}

// Add CSRF token to form data
function addCSRFTokenToFormData(formData) {
    const token = getCSRFToken();
    if (token) {
        formData.append('csrf_token', token);
    }
    return formData;
}

// Add CSRF token to object data
function addCSRFTokenToData(data) {
    const token = getCSRFToken();
    if (token) {
        data.csrf_token = token;
    }
    return data;
}

// Enhanced fetch with CSRF token
function fetchWithCSRF(url, options = {}) {
    const token = getCSRFToken();

    console.log('fetchWithCSRF called for:', url);
    console.log('CSRF token retrieved:', !!token, token ? token.substring(0, 20) + '...' : 'null');

    // Set default headers (but don't set Content-Type for FormData)
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers
    };

    // Only set Content-Type if not sending FormData
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    // Add CSRF token to headers
    if (token) {
        headers['X-CSRFToken'] = token;
        console.log('Added CSRF token to headers');
    }

    // Add CSRF token to body
    if (options.body) {
        if (options.body instanceof FormData) {
            // Add CSRF token to FormData
            options.body.append('csrf_token', token);
            console.log('Added CSRF token to FormData');
        } else if (typeof options.body === 'string') {
            try {
                const data = JSON.parse(options.body);
                data.csrf_token = token;
                options.body = JSON.stringify(data);
                console.log('Added CSRF token to JSON body');
            } catch (e) {
                // If not JSON, leave as string
                console.log('Body is string but not JSON, leaving as-is');
            }
        }
    } else {
        console.log('No body to add CSRF token to');
    }

    return fetch(url, {
        ...options,
        headers
    });
}

// Enhanced jQuery AJAX with CSRF token
if (typeof $ !== 'undefined') {
    // Set up CSRF token for all AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            const token = getCSRFToken();
            if (token && !settings.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', token);
            }
        }
    });
    
    // Add CSRF token to form data
    $.fn.serializeWithCSRF = function() {
        const formData = $(this).serializeArray();
        const token = getCSRFToken();
        if (token) {
            formData.push({name: 'csrf_token', value: token});
        }
        return $.param(formData);
    };
}

/**
 * Unified fetch function that supports both JWT (mobile/Firebase) and CSRF (web) authentication
 * Automatically detects which authentication method to use
 */
async function fetchWithAuth(url, options = {}) {
    // Check if JWT token is available (mobile/Firebase)
    let jwtToken = null;
    if (typeof window !== 'undefined' && window.tokenManager) {
        jwtToken = window.tokenManager.accessToken;
        // Check if token is expired and refresh if needed
        if (jwtToken && window.tokenManager.isTokenExpired()) {
            try {
                await window.tokenManager.refreshTokens();
                jwtToken = window.tokenManager.accessToken;
            } catch (e) {
                console.warn('Token refresh failed, falling back to CSRF:', e);
                jwtToken = null;
            }
        }
    } else {
        // Fallback: check localStorage directly
        try {
            jwtToken = localStorage.getItem('access_token');
            if (jwtToken) {
                // Basic expiry check
                try {
                    const payload = jwtToken.split('.')[1];
                    const decoded = JSON.parse(atob(payload));
                    const now = Math.floor(Date.now() / 1000);
                    if (decoded.exp && decoded.exp < now) {
                        jwtToken = null; // Token expired
                    }
                } catch (e) {
                    jwtToken = null; // Invalid token
                }
            }
        } catch (e) {
            // localStorage not available or token invalid
            jwtToken = null;
        }
    }

    // Set default headers
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers
    };

    // Use JWT Bearer token if available (mobile/Firebase)
    if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
        // Don't set Content-Type for FormData
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
        }
    } else {
        // Fallback to CSRF token (web)
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        // Only set Content-Type if not sending FormData
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
        }

        // Add CSRF token to body if needed
        if (options.body && csrfToken) {
            if (options.body instanceof FormData) {
                options.body.append('csrf_token', csrfToken);
            } else if (typeof options.body === 'string') {
                try {
                    const data = JSON.parse(options.body);
                    data.csrf_token = csrfToken;
                    options.body = JSON.stringify(data);
                } catch (e) {
                    // If not JSON, leave as string
                }
            }
        }
    }

    // Make the request
    let response = await fetch(url, {
        ...options,
        headers
    });

    // If 401 and we have JWT token, try refreshing once
    if (response.status === 401 && jwtToken && window.tokenManager && window.tokenManager.refreshToken) {
        try {
            await window.tokenManager.refreshTokens();
            // Retry with new token
            headers['Authorization'] = `Bearer ${window.tokenManager.accessToken}`;
            response = await fetch(url, {
                ...options,
                headers
            });
        } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
        }
    }

    return response;
}

// Expose to global scope for scripts loaded outside the bundle
window.getCSRFToken = getCSRFToken;
window.addCSRFTokenToFormData = addCSRFTokenToFormData;
window.addCSRFTokenToData = addCSRFTokenToData;
window.fetchWithCSRF = fetchWithCSRF;
window.fetchWithAuth = fetchWithAuth;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCSRFToken,
        addCSRFTokenToFormData,
        addCSRFTokenToData,
        fetchWithCSRF,
        fetchWithAuth
    };
}

// Automatically inject CSRF token into all POST forms
document.addEventListener('DOMContentLoaded', function() {
    const token = getCSRFToken();
    if (token) {
        document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(form => {
            if (!form.querySelector('input[name="csrf_token"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = token;
                form.appendChild(input);
            }
        });
    }
});
