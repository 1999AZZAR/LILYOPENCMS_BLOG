/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * Firebase Authentication Integration for LilyOpenCMS
 *
 * This module handles Firebase Authentication for social login
 * while maintaining integration with the existing session management system.
 *
 * Uses Firebase v9+ Modular SDK
 */

// Import Firebase functions
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.6.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.6.0/firebase-analytics.js";
import {
    getAuth,
    connectAuthEmulator,
    GoogleAuthProvider,
    FacebookAuthProvider,
    TwitterAuthProvider,
    GithubAuthProvider,
    signInWithPopup,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.6.0/firebase-auth.js";

class FirebaseAuthManager {
    constructor() {
        this.app = null;
        this.auth = null;
        this.analytics = null;
        this.initialized = false;
        this.config = null;
    }

    /**
     * Initialize Firebase Auth
     */
    async initialize() {
        try {
            // Get Firebase configuration from server
            const configResponse = await fetch('/auth/firebase/config');
            if (!configResponse.ok) {
                console.warn('Failed to fetch Firebase configuration from server');
                return false;
            }

            const firebaseConfig = await configResponse.json();

            // Check if Firebase config is available
            if (!firebaseConfig.api_key || !firebaseConfig.project_id) {
                console.warn('Firebase configuration not available. Social login disabled.');
                return false;
            }

            // Initialize Firebase app
            this.app = initializeApp({
                apiKey: firebaseConfig.api_key,
                authDomain: firebaseConfig.auth_domain,
                projectId: firebaseConfig.project_id,
                storageBucket: firebaseConfig.storage_bucket,
                messagingSenderId: firebaseConfig.messaging_sender_id,
                appId: firebaseConfig.app_id
            });

            // Initialize Firebase Auth
            this.auth = getAuth(this.app);

            // Connect to emulator if configured
            if (firebaseConfig.use_emulator === 'true' || firebaseConfig.use_emulator === true) {
                const emulatorHost = firebaseConfig.emulator_host || 'localhost:9099';
                try {
                    connectAuthEmulator(this.auth, `http://${emulatorHost}`);
                    console.log('Connected to Firebase Auth emulator at', emulatorHost);
                } catch (emulatorError) {
                    console.warn('Failed to connect to Firebase emulator:', emulatorError);
                }
            }

            // Initialize Analytics (optional) - skip if using emulator
            if (!firebaseConfig.use_emulator) {
                try {
                    this.analytics = getAnalytics(this.app);
                } catch (analyticsError) {
                    console.warn('Firebase Analytics initialization failed:', analyticsError);
                }
            }

            this.initialized = true;

            // Set up auth state listener
            onAuthStateChanged(this.auth, (user) => {
                if (user) {
                    console.log('Firebase user authenticated:', user.uid);
                } else {
                    console.log('Firebase user signed out');
                }
            });

            console.log('Firebase Auth initialized successfully');
            return true;

        } catch (error) {
            console.error('Failed to initialize Firebase Auth:', error);
            return false;
        }
    }

    /**
     * Sign in with Google
     */
    async signInWithGoogle() {
        if (!this.initialized) {
            throw new Error('Firebase Auth not initialized');
        }

        try {
            const provider = new GoogleAuthProvider();
            provider.addScope('email');
            provider.addScope('profile');

            const result = await signInWithPopup(this.auth, provider);
            return await this.handleAuthResult(result);

        } catch (error) {
            console.error('Google sign-in error:', error);
            throw error;
        }
    }

    /**
     * Sign in with Facebook
     */
    async signInWithFacebook() {
        if (!this.initialized) {
            throw new Error('Firebase Auth not initialized');
        }

        try {
            const provider = new FacebookAuthProvider();
            provider.addScope('email');

            const result = await signInWithPopup(this.auth, provider);
            return await this.handleAuthResult(result);

        } catch (error) {
            console.error('Facebook sign-in error:', error);
            throw error;
        }
    }

    /**
     * Sign in with Twitter
     */
    async signInWithTwitter() {
        if (!this.initialized) {
            throw new Error('Firebase Auth not initialized');
        }

        try {
            const provider = new TwitterAuthProvider();

            const result = await signInWithPopup(this.auth, provider);
            return await this.handleAuthResult(result);

        } catch (error) {
            console.error('Twitter sign-in error:', error);
            throw error;
        }
    }

    /**
     * Sign in with GitHub
     */
    async signInWithGitHub() {
        if (!this.initialized) {
            throw new Error('Firebase Auth not initialized');
        }

        try {
            const provider = new GithubAuthProvider();
            provider.addScope('user:email');

            const result = await signInWithPopup(this.auth, provider);
            return await this.handleAuthResult(result);

        } catch (error) {
            console.error('GitHub sign-in error:', error);
            throw error;
        }
    }

    /**
     * Handle authentication result
     */
    async handleAuthResult(result) {
        try {
            const user = result.user;
            const idToken = await user.getIdToken();

            // Send token to server for verification and session creation
            const response = await fetchWithCSRF('/auth/firebase/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    idToken: idToken
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Redirect to dashboard or intended page
                window.location.href = data.redirect_url || '/dashboard';
                return data;
            } else {
                throw new Error(data.message || 'Authentication failed');
            }

        } catch (error) {
            console.error('Auth result handling error:', error);
            throw error;
        }
    }

    /**
     * Sign out
     */
    async signOut() {
        if (!this.initialized) {
            throw new Error('Firebase Auth not initialized');
        }

        try {
            // Sign out from Firebase
            await signOut(this.auth);

            // Notify server
            const response = await fetchWithCSRF('/auth/firebase/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Redirect to home page
                window.location.href = data.redirect_url || '/';
                return data;
            } else {
                throw new Error(data.message || 'Logout failed');
            }

        } catch (error) {
            console.error('Sign out error:', error);
            throw error;
        }
    }

    /**
     * Get current user
     */
    getCurrentUser() {
        if (!this.initialized) {
            return null;
        }
        return this.auth.currentUser;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return this.getCurrentUser() !== null;
    }
}

// Create global instance for backward compatibility
const firebaseAuthManager = new FirebaseAuthManager();
window.firebaseAuthManager = firebaseAuthManager;

// Add initialization status tracking
window.firebaseAuthManager.initialized = false;
window.firebaseAuthManager.initializing = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🔄 Initializing Firebase Auth Manager...');
        window.firebaseAuthManager.initializing = true;
        const initialized = await firebaseAuthManager.initialize();
        window.firebaseAuthManager.initialized = initialized;
        window.firebaseAuthManager.initializing = false;

        if (initialized) {
            console.log('✅ Firebase Auth Manager initialized successfully');
            // Dispatch custom event to notify other scripts
            window.dispatchEvent(new CustomEvent('firebaseAuthReady', {
                detail: { initialized: true }
            }));
        } else {
            console.warn('⚠️ Firebase Auth Manager not initialized - social login disabled');
            // Dispatch custom event to notify other scripts
            window.dispatchEvent(new CustomEvent('firebaseAuthReady', {
                detail: { initialized: false }
            }));
        }
    } catch (error) {
        console.error('❌ Failed to initialize Firebase Auth:', error);
        window.firebaseAuthManager.initialized = false;
        window.firebaseAuthManager.initializing = false;

        // Dispatch custom event to notify other scripts
        window.dispatchEvent(new CustomEvent('firebaseAuthReady', {
            detail: { initialized: false, error: error.message }
        }));
    }
});

// Export for module usage
export default FirebaseAuthManager;
export { firebaseAuthManager };
