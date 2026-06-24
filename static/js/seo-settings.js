/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

/**
 * SEO Settings Management JavaScript
 * Handles loading, saving, and testing SEO settings
 */

class SEOSettingsManager {
    constructor() {
        this.settings = {};
        this.isLoading = false;
        this.initializeEventListeners();
        this.loadSettings();
    }

    initializeEventListeners() {
        // Global settings form
        const globalForm = document.getElementById('global-seo-settings-form');
        if (globalForm) {
            globalForm.addEventListener('submit', (e) => this.handleGlobalSettingsSubmit(e));
        }

        // Root SEO settings form
        const rootForm = document.getElementById('root-seo-settings-form');
        if (rootForm) {
            rootForm.addEventListener('submit', (e) => this.handleRootSettingsSubmit(e));
        }

        // Root SEO settings modal
        const rootSettingsBtn = document.getElementById('root-seo-settings-btn');
        if (rootSettingsBtn) {
            rootSettingsBtn.addEventListener('click', () => this.openRootSettingsModal());
        }

        const closeRootSettings = document.getElementById('close-root-seo-settings');
        if (closeRootSettings) {
            closeRootSettings.addEventListener('click', () => this.closeRootSettingsModal());
        }

        const cancelRootSettings = document.getElementById('cancel-root-seo-settings');
        if (cancelRootSettings) {
            cancelRootSettings.addEventListener('click', () => this.closeRootSettingsModal());
        }

        // Injection settings
        const testInjectionBtn = document.getElementById('test-injection-settings');
        if (testInjectionBtn) {
            testInjectionBtn.addEventListener('click', () => this.testInjectionSettings());
        }

        const saveInjectionBtn = document.getElementById('save-injection-settings');
        if (saveInjectionBtn) {
            saveInjectionBtn.addEventListener('click', () => this.saveInjectionSettings());
        }

        // Reset buttons
        const resetGlobalBtn = document.getElementById('reset-global-settings');
        if (resetGlobalBtn) {
            resetGlobalBtn.addEventListener('click', () => this.resetGlobalSettings());
        }
    }

    async loadSettings() {
        try {
            this.showLoading(true);
            const response = await fetchWithCSRF('/api/seo/settings/load');
            
            if (response.ok) {
                const data = await response.json();
                this.settings = data.settings;
                this.populateForms();
                this.updateCurrentSettingsDisplay();
            } else {
                const error = await response.json();
                this.showToast('Error loading settings: ' + error.message, 'error');
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showToast('Error loading settings: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    populateForms() {
        // Populate global settings form
        this.populateForm('global-seo-settings-form', [
            'default_language', 'default_meta_robots', 'default_og_type', 
            'default_twitter_card', 'default_og_image', 'default_twitter_image'
        ]);

        // Populate root SEO settings form
        this.populateForm('root-seo-settings-form', [
            'website_url', 'home_meta_title', 'home_meta_description', 'home_meta_keywords',
            'about_meta_title', 'about_meta_description', 'about_meta_keywords',
            'news_meta_title', 'news_meta_description', 'news_meta_keywords',
            'albums_meta_title', 'albums_meta_description', 'albums_meta_keywords',
            'article_meta_title', 'article_meta_description', 'article_meta_keywords', 'article_og_title',
            'album_meta_title', 'album_meta_description', 'album_meta_keywords', 'album_og_title',
            'chapter_meta_title', 'chapter_meta_description', 'chapter_meta_keywords', 'chapter_og_title'
        ]);

        // Populate brand name (read-only)
        const brandNameInput = document.getElementById('brand-name');
        if (brandNameInput) {
            brandNameInput.value = this.settings.website_name || 'Hystory';
        }
    }

    populateForm(formId, fields) {
        const form = document.getElementById(formId);
        if (!form) return;

        fields.forEach(field => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input && this.settings[field] !== undefined) {
                if (input.type === 'checkbox') {
                    input.checked = this.settings[field];
                } else {
                    input.value = this.settings[field] || '';
                }
            }
        });
    }

    updateCurrentSettingsDisplay() {
        // Update current settings display
        const currentBrandName = document.getElementById('current-brand-name');
        if (currentBrandName) {
            currentBrandName.textContent = this.settings.website_name || 'Content Management System';
        }

        const currentWebsiteUrl = document.getElementById('current-website-url');
        if (currentWebsiteUrl) {
            currentWebsiteUrl.textContent = this.settings.website_url || 'https://example.com';
        }

        const currentHomeTemplate = document.getElementById('current-home-template');
        if (currentHomeTemplate) {
            currentHomeTemplate.textContent = this.settings.home_meta_title || 'Default Template';
        }

        const currentAboutTemplate = document.getElementById('current-about-template');
        if (currentAboutTemplate) {
            currentAboutTemplate.textContent = this.settings.about_meta_title || 'Default Template';
        }

        const currentOgType = document.getElementById('current-og-type');
        if (currentOgType) {
            currentOgType.textContent = this.settings.default_og_type || 'website';
        }

        const currentTwitterCard = document.getElementById('current-twitter-card');
        if (currentTwitterCard) {
            currentTwitterCard.textContent = this.settings.default_twitter_card || 'summary_large_image';
        }
    }

    async handleGlobalSettingsSubmit(e) {
        e.preventDefault();
        
        try {
            this.showLoading(true);
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetchWithCSRF('/api/seo/settings/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Global settings saved successfully!', 'success');
                await this.loadSettings(); // Reload settings
            } else {
                const error = await response.json();
                this.showToast('Error saving global settings: ' + error.message, 'error');
            }
        } catch (error) {
            console.error('Error saving global settings:', error);
            this.showToast('Error saving global settings: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleRootSettingsSubmit(e) {
        e.preventDefault();
        
        try {
            this.showLoading(true);
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetchWithCSRF('/api/seo/settings/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Root SEO settings saved successfully!', 'success');
                this.closeRootSettingsModal();
                await this.loadSettings(); // Reload settings
            } else {
                const error = await response.json();
                this.showToast('Error saving root SEO settings: ' + error.message, 'error');
            }
        } catch (error) {
            console.error('Error saving root SEO settings:', error);
            this.showToast('Error saving root SEO settings: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    openRootSettingsModal() {
        const modal = document.getElementById('root-seo-settings-modal');
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    }

    closeRootSettingsModal() {
        const modal = document.getElementById('root-seo-settings-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    }

    async testInjectionSettings() {
        try {
            this.showLoading(true);
            const response = await fetchWithCSRF('/api/seo/settings/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Test injection completed successfully!', 'success');
                console.log('Test result:', result.test_result);
            } else {
                const error = await response.json();
                this.showToast('Error testing injection: ' + error.message, 'error');
            }
        } catch (error) {
            console.error('Error testing injection:', error);
            this.showToast('Error testing injection: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async saveInjectionSettings() {
        try {
            this.showLoading(true);
            
            // Collect injection settings from checkboxes and inputs
            const injectionSettings = {
                auto_inject_articles: document.getElementById('auto-inject-articles')?.checked || false,
                auto_inject_albums: document.getElementById('auto-inject-albums')?.checked || false,
                auto_inject_chapters: document.getElementById('auto-inject-chapters')?.checked || false,
                enable_seo_lock: document.getElementById('enable-seo-lock')?.checked || false,
                lock_after_injection: document.getElementById('lock-after-injection')?.checked || false,
                batch_size: parseInt(document.getElementById('batch-size')?.value) || 20,
                delay_between_batches: parseInt(document.getElementById('delay-between-batches')?.value) || 100
            };
            
            const response = await fetchWithCSRF('/api/seo/settings/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(injectionSettings)
            });

            if (response.ok) {
                this.showToast('Injection settings saved successfully!', 'success');
                await this.loadSettings(); // Reload settings
            } else {
                const error = await response.json();
                this.showToast('Error saving injection settings: ' + error.message, 'error');
            }
        } catch (error) {
            console.error('Error saving injection settings:', error);
            this.showToast('Error saving injection settings: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    resetGlobalSettings() {
        if (confirm('Are you sure you want to reset global settings to defaults?')) {
            // Reset form to default values
            const form = document.getElementById('global-seo-settings-form');
            if (form) {
                form.reset();
                // Set default values
                document.getElementById('global-meta-language').value = 'en';
                document.getElementById('global-meta-robots').value = 'index, follow';
                document.getElementById('global-og-type').value = 'website';
                document.getElementById('global-twitter-card').value = 'summary_large_image';
            }
            this.showToast('Global settings reset to defaults', 'info');
        }
    }

    showLoading(show) {
        this.isLoading = show;
        const buttons = document.querySelectorAll('button[type="submit"], button[id*="save"], button[id*="test"]');
        buttons.forEach(button => {
            button.disabled = show;
            if (show) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
            }
        });
    }

    showToast(message, type = 'info') {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`Toast [${type}]: ${message}`);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SEOSettingsManager();
});
