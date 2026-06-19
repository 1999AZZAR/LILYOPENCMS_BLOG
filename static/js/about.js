// About page functionality

// Modal toggling (Global)
window.toggleModal = function(type) {
    const modal = document.getElementById(type + 'Modal');
    if (!modal) return;

    if (modal.classList.contains('hidden')) {
        // Open
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        loadContent(type);
    } else {
        // Close
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
};

// Content loading for policies
async function loadContent(type) {
    const contentDiv = document.getElementById(type + 'Content');
    if (!contentDiv) return;

    let endpoint = '';
    switch(type) {
        case 'privacy': endpoint = '/api/privacy-policy'; break;
        case 'media': endpoint = '/api/media-guidelines'; break;
        case 'disclaimer': endpoint = '/api/penyangkalan'; break;
        case 'rights': endpoint = '/api/pedomanhak'; break;
        default: return;
    }

    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        if (!data || data.length === 0) {
            contentDiv.innerHTML = '<p class="text-slate-400">Konten tidak tersedia.</p>';
            return;
        }
        contentDiv.innerHTML = data.map(item => `
            <div class="mb-10">
                <h3 class="text-xl font-bold text-slate-800 mb-4">${item.title}</h3>
                <div class="prose prose-slate max-w-none text-slate-500 font-medium">${item.content}</div>
            </div>
        `).join('');
    } catch (e) {
        contentDiv.innerHTML = '<p class="text-red-400 font-bold">Gagal memuat konten.</p>';
    }
}

// Load vision/mission content
async function loadVisiMisi() {
    try {
        const response = await fetch('/api/visi-misi');
        const data = await response.json();
        const visi = data.find(i => i.title.toLowerCase() === 'visi');
        const misi = data.find(i => i.title.toLowerCase() === 'misi');
        
        if (visi) document.getElementById('visi-content').innerHTML = `<p>${visi.content}</p>`;
        if (misi) document.getElementById('misi-content').innerHTML = `<p>${misi.content}</p>`;
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', loadVisiMisi);
