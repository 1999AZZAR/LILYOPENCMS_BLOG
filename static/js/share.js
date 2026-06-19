// Share logic (share count, clipboard, tracking)
// showToast is now available globally

// Make function globally available
function initializeSharing(newsData, logger) {
    // Make functions globally available
    window.initializeSharing = initializeSharing;
    

    
    if (!newsData || newsData.id === null) {
        if (logger) logger.error("Cannot initialize sharing: Invalid or missing news ID.");
        const shareSection = document.querySelector('.share-section');
        if (shareSection) {
            shareSection.style.display = 'none';
            if (logger) logger.log("Hiding share section due to missing News ID.");
        }
        return;
    }
    const shareButtons = document.querySelectorAll('.share-button');
    if (logger) logger.log(`Found ${shareButtons.length} share buttons.`);
    if (shareButtons.length === 0) {
        if (logger) logger.warn("No share buttons found with class '.share-button'.");
        return;
    }
    fetchShareData(newsData, logger);
    shareButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const platform = button.dataset.platform;
            if (logger) logger.log(`Share button clicked for platform: ${platform}`);
            if (platform) {
                handleShareClick(platform, newsData, logger);
            } else {
                if (logger) logger.warn("Share button clicked without a 'data-platform' attribute.");
            }
        });
    });
}

function fetchShareData(newsData, logger) {
    if (!newsData || newsData.id === null) return;
    const apiUrl = `/api/news/${newsData.id}/share-data`;
    fetch(apiUrl)
    .then(response => response.ok ? response.json() : {})
    .then(data => {
        if (logger) logger.log("Share data received:", data);
        let totalShares = 0;
        const countSpans = document.querySelectorAll('.share-count');
        countSpans.forEach(span => {
            const platform = span.dataset.platform;
            const count = Number(data[`${platform}_count`]) || 0;
            span.textContent = count;
            totalShares += count;
        });
        const totalSpan = document.querySelector('#total-share-count span');
        if (totalSpan) totalSpan.textContent = totalShares;
    });
}

function trackShare(platform, newsData, logger) {
    if (!newsData || newsData.id === null) return Promise.reject("Invalid newsData for tracking");
    const trackUrl = `/api/news/${newsData.id}/track-share`;
    return fetch(trackUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ platform })
    })
    .then(response => response.ok ? response.json() : {})
    .then(data => {
        if (logger) logger.log("Share track successful:", data.message || 'Success (No message)');
        fetchShareData(newsData, logger);
    });
}

function handleShareClick(platform, newsData, logger) {
    if (!newsData || !newsData.url) {
        if (logger) logger.error("Cannot handle share click: Missing newsData or URL.");
        return;
    }
    trackShare(platform, newsData, logger).catch(() => {});
    const title = newsData.title;
    const url = newsData.url;
    const encodedUrl = encodeURIComponent(url);
    const encodedTitle = encodeURIComponent(title);
    let shareUrl = '';
    switch (platform) {
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(`${title} ${url}`)}`;
            break;
        case 'instagram':
            showToast('info', 'Untuk berbagi ke Instagram:\n1. Salin tautan berita ini.\n2. Buka Instagram dan buat Story.\n3. Tempel tautan menggunakan fitur Stiker Tautan di Story, atau di bio profil Anda.');
            copyToClipboard(newsData, logger);
            return;
        case 'bluesky':
            shareUrl = `https://bsky.app/intent/compose?text=${encodeURIComponent(title + '\n\n' + url)}`;
            break;
        case 'clipboard':
            copyToClipboard(newsData, logger);
            return;
        default:
            if (logger) logger.warn(`Unknown share platform clicked: ${platform}`);
            return;
    }
    if (shareUrl) {
        const windowFeatures = 'noopener,noreferrer,width=600,height=450,resizable=yes,scrollbars=yes';
        window.open(shareUrl, '_blank', windowFeatures);
        if (logger) logger.log(`Opened share window for ${platform}: ${shareUrl}`);
    }
}

function copyToClipboard(newsData, logger) {
    if (!newsData || !newsData.url) {
        if (logger) logger.error("Cannot copy: No URL available in newsData.");
        showToast('error', 'Gagal menyalin: Tautan tidak tersedia.');
        return;
    }
    const urlToCopy = newsData.url;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(urlToCopy).then(() => {
            showToast('success', 'Tautan berhasil disalin ke clipboard!');
            if (logger) logger.log('Link copied using modern Clipboard API.');
        }).catch(() => {
            showToast('error', 'Gagal menyalin tautan secara otomatis. Coba salin manual.');
        });
    } else {
        const textArea = document.createElement("textarea");
        textArea.value = urlToCopy;
        textArea.style.position = "fixed";
        textArea.style.top = "-9999px";
        textArea.style.left = "-9999px";
        textArea.style.opacity = "0";
        textArea.setAttribute("readonly", "");
        document.body.appendChild(textArea);
        try {
            textArea.select();
            textArea.setSelectionRange(0, textArea.value.length);
            document.execCommand('copy');
            showToast('success', 'Tautan berhasil disalin ke clipboard!');
            if (logger) logger.log('Link copied using fallback execCommand.');
        } catch (err) {
            showToast('error', 'Gagal menyalin tautan secara otomatis. Coba salin manual.');
        } finally {
            if (document.body.contains(textArea)) {
                document.body.removeChild(textArea);
            }
        }
    }
}
