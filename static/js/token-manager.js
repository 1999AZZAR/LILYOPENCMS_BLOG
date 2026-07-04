/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * Token Manager - Handles JWT token storage, refresh, and automatic renewal
 * Provides seamless authentication experience for users
 */

class TokenManager {
    constructor() {
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenData = null;
        this.refreshPromise = null;
        this.isRefreshing = false;
        this.init();
    }

    init() {
        // Load tokens from localStorage if available
        this.loadTokensFromStorage();

        // Set up automatic refresh check
        this.scheduleTokenRefreshCheck();
    }

    loadTokensFromStorage() {
        try {
            this.accessToken = localStorage.getItem('access_token');
            this.refreshToken = localStorage.getItem('refresh_token');
            this.tokenData = this.accessToken ? this.parseToken(this.accessToken) : null;
        } catch (e) {
            console.warn('Could not load tokens from localStorage:', e);
        }
    }

    saveTokensToStorage(accessToken, refreshToken, userData = null) {
        try {
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            if (userData) {
                localStorage.setItem('user_data', JSON.stringify(userData));
            }
            this.accessToken = accessToken;
            this.refreshToken = refreshToken;
            this.tokenData = this.parseToken(accessToken);
        } catch (e) {
            console.error('Could not save tokens to localStorage:', e);
        }
    }

    clearTokens() {
        try {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_data');
            this.accessToken = null;
            this.refreshToken = null;
            this.tokenData = null;
        } catch (e) {
            console.error('Could not clear tokens from localStorage:', e);
        }
    }

    parseToken(token) {
        try {
            const payload = token.split('.')[1];
            const decoded = JSON.parse(atob(payload));
            return {
                user_id: decoded.user_id,
                username: decoded.username,
                role: decoded.role,
                is_premium: decoded.is_premium,
                exp: decoded.exp,
                iat: decoded.iat
            };
        } catch (e) {
            console.error('Could not parse token:', e);
            return null;
        }
    }

    isTokenExpired(token = null, thresholdMinutes = 5) {
        const tokenToCheck = token || this.accessToken;
        if (!tokenToCheck) return true;

        const tokenData = this.parseToken(tokenToCheck);
        if (!tokenData || !tokenData.exp) return true;

        const now = Math.floor(Date.now() / 1000);
        const thresholdTime = tokenData.exp - (thresholdMinutes * 60);

        return now >= thresholdTime;
    }

    getTimeUntilExpiry(token = null) {
        const tokenToCheck = token || this.accessToken;
        if (!tokenToCheck) return 0;

        const tokenData = this.parseToken(tokenToCheck);
        if (!tokenData || !tokenData.exp) return 0;

        const now = Math.floor(Date.now() / 1000);
        return Math.max(0, tokenData.exp - now);
    }

    async refreshTokens() {
        if (!this.refreshToken) {
            throw new Error('No refresh token available');
        }

        if (this.isRefreshing) {
            return this.refreshPromise;
        }

        this.isRefreshing = true;

        this.refreshPromise = this.performTokenRefresh();

        try {
            const result = await this.refreshPromise;
            return result;
        } finally {
            this.isRefreshing = false;
            this.refreshPromise = null;
        }
    }

    async performTokenRefresh() {
        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Save new tokens
            this.saveTokensToStorage(data.access_token, data.refresh_token, data.user);

            // Dispatch custom event for successful refresh
            window.dispatchEvent(new CustomEvent('tokensRefreshed', {
                detail: { user: data.user }
            }));

            return data;
        } catch (error) {
            console.error('Token refresh failed:', error);

            // Clear tokens on refresh failure
            this.clearTokens();

            // Dispatch custom event for refresh failure
            window.dispatchEvent(new CustomEvent('tokenRefreshFailed', {
                detail: { error: error.message }
            }));

            throw error;
        }
    }

    scheduleTokenRefreshCheck() {
        // Check token status every minute
        setInterval(() => {
            if (this.accessToken && this.isTokenExpired()) {
                console.log('Token expired, attempting refresh...');
                this.refreshTokens().catch(error => {
                    console.error('Auto token refresh failed:', error);
                });
            }
        }, 60000); // 1 minute
    }

    async makeAuthenticatedRequest(url, options = {}) {
        const makeRequest = async (token) => {
            const headers = {
                'Authorization': `Bearer ${token}`,
                ...options.headers
            };

            return fetch(url, {
                ...options,
                headers
            });
        };

        // Try with current token first
        let response = await makeRequest(this.accessToken);

        // If unauthorized and we have a refresh token, try refreshing
        if (response.status === 401 && this.refreshToken) {
            try {
                await this.refreshTokens();
                response = await makeRequest(this.accessToken);
            } catch (refreshError) {
                // Refresh failed, let original response through
                console.error('Token refresh failed:', refreshError);
            }
        }

        return response;
    }

    getUserData() {
        try {
            const stored = localStorage.getItem('user_data');
            return stored ? JSON.parse(stored) : null;
        } catch (e) {
            console.error('Could not get user data:', e);
            return null;
        }
    }

    isAuthenticated() {
        return this.accessToken && !this.isTokenExpired();
    }
}

// Create global instance
const tokenManager = new TokenManager();

// Export for use in other modules
window.TokenManager = TokenManager;
window.tokenManager = tokenManager;
