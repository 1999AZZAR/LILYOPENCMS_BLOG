/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Main entry for reader page
// Functions are now loaded globally via script tags

// Logger utility
const IS_DEBUG = false;
const logger = {
    log: (...args) => IS_DEBUG && console.log('[Reader]', ...args),
    error: (...args) => console.error('[Reader]', ...args),
    warn: (...args) => console.warn('[Reader]', ...args),
};

// Data from Flask (assume window.newsData is set in template)
let newsData = null;
try {
    const newsId = window.newsId;
    const newsTitle = window.newsTitle;
    const newsUrl = window.newsUrl || window.location.href;
    if (newsId === null || typeof newsId !== 'number') throw new Error("News ID is missing or invalid from template.");
    newsData = { id: newsId, title: newsTitle || "Artikel Ini", url: newsUrl };
    logger.log("News data initialized:", newsData);
} catch (e) {
    logger.error("Could not parse newsData for JS:", e);
    newsData = { id: null, title: "Artikel Ini", url: window.location.href };
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeLazyLoad(logger);
        initializeSharing(newsData, logger);
        initializeFeaturedImageModal(logger);
        
        // Wait for Slick to be available
        const waitForSlick = () => {
            if (typeof $ !== 'undefined' && typeof $.fn !== 'undefined' && typeof $.fn.slick !== 'undefined') {
                initializeSlick(logger);
            } else {
                setTimeout(waitForSlick, 100);
            }
        };
        
        // Start waiting for Slick
        waitForSlick();
    } catch (error) {
        console.error('[Reader] Error during initialization:', error);
    }
});
