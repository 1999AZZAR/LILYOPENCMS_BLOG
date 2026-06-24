/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Login page functionality

// Tab Toggling
window.showTab = function(tabName) {
    const loginTab = document.getElementById('loginTabButton');
    const registerTab = document.getElementById('registerTabButton');
    const loginForm = document.getElementById('loginFormContainer');
    const registerForm = document.getElementById('registerFormContainer');

    if (tabName === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        loginTab.className = "flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-2xl transition-all duration-300 bg-white shadow-sm text-slate-800";
        registerTab.className = "flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-2xl transition-all duration-300 text-slate-400 hover:text-slate-600";
    } else {
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        registerTab.className = "flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-2xl transition-all duration-300 bg-white shadow-sm text-slate-800";
        loginTab.className = "flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-2xl transition-all duration-300 text-slate-400 hover:text-slate-600";
    }
};

// Modal toggling
window.toggleModal = function(type) {
    const modal = document.getElementById(type + 'Modal');
    if (!modal) return;

    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        loadContent(type);
    } else {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
};

async function loadContent(type) {
    const contentDiv = document.getElementById(type + 'Content');
    if (!contentDiv) return;

    let endpoint = '';
    switch(type) {
        case 'privacy': endpoint = '/api/privacy-policy'; break;
        case 'media': endpoint = '/api/media-guidelines'; break;
        default: return;
    }

    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        if (data && data.length > 0) {
            contentDiv.innerHTML = data.map(item => `
                <div class="mb-8">
                    <h3 class="text-xl font-bold text-slate-800 mb-2">${item.title}</h3>
                    <div class="prose prose-slate text-sm text-slate-500 font-medium">${item.content}</div>
                </div>
            `).join('');
        }
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    // Check hash
    if (window.location.hash === '#register') window.showTab('register');
});
