// ads-injection.js (Always Inject)

// Global variables for user preferences
let userHasPremiumAccess = false;
let userShouldShowAds = true;

// Function to check user's premium status and ad preferences
async function checkUserPreferences() {
    try {
        const response = await fetch('/api/subscriptions/check-premium-access');
        if (response.ok) {
            const data = await response.json();
            userHasPremiumAccess = data.has_premium_access;
            userShouldShowAds = data.should_show_ads;
        }
    } catch (error) {
        console.warn('Could not check user preferences:', error);
        // Default to showing ads if we can't check
        userHasPremiumAccess = false;
        userShouldShowAds = true;
    }
}

// Function to create an ad placeholder
function createAdPlaceholder() {
  const placeholder = document.createElement('div');
  placeholder.className = 'ad-placeholder bg-gray-800 rounded-lg overflow-hidden shadow-lg flex relative';
  placeholder.innerHTML = `
    <div class="w-full p-6 flex flex-col justify-between">
      <p class="text-gray-400">Advertisement</p>
    </div>
  `;
  return placeholder;
}

// Function to inject Google Ads (if available)
function injectGoogleAds(container) {
  if (typeof adsbygoogle !== 'undefined') {
    // Create Google Ads slot
    const adScript = document.createElement('script');
    adScript.innerHTML = `
      (adsbygoogle = window.adsbygoogle || []).push({
        google_ad_client: "ca-pub-YOUR_PUBLISHER_ID",
        enable_page_level_ads: true,
        overlays: { bottom: true }
      });
    `;
    container.appendChild(adScript);

    // Create a container for the ad
    const adSlot = document.createElement('div');
    adSlot.className = 'google-ads-slot bg-gray-800 rounded-lg overflow-hidden shadow-lg flex relative';
    container.appendChild(adSlot);
  } else {
    // If Google Ads script fails to load, inject a blank ad
    container.appendChild(createAdPlaceholder());
  }
}

// Function to inject ads into a specific section
function injectAdsIntoSection(section, interval) {
  // Don't inject ads if user has premium access and doesn't want ads
  if (userHasPremiumAccess && !userShouldShowAds) {
    return;
  }

  const newsItems = section.querySelectorAll('.news-card');
  newsItems.forEach((item, index) => {
    if ((index + 1) % interval === 0) {
      const adContainer = document.createElement('div');
      adContainer.className = 'ad-container';
      section.insertBefore(adContainer, item.nextSibling);

      // Inject Google Ads or a blank placeholder
      if (typeof adsbygoogle !== 'undefined') {
        injectGoogleAds(adContainer);
      } else {
        adContainer.appendChild(createAdPlaceholder());
      }
    }
  });
}

// Function to initialize ad injection
async function initializeAds() {
  // Check user preferences first
  await checkUserPreferences();

  // Inject ads into the right side
  const adContainer = document.getElementById('ad-container');
  if (adContainer) {
    // Don't show ads if user has premium access and doesn't want ads
    if (userHasPremiumAccess && !userShouldShowAds) {
      adContainer.style.display = 'none';
      return;
    }

    if (typeof adsbygoogle !== 'undefined') {
      injectGoogleAds(adContainer);
    } else {
      adContainer.appendChild(createAdPlaceholder());
    }
  }

  // Inject ads into Latest News and Popular News sections
  const latestNewsSection = document.querySelector('[data-group="latest-news"]');
  const popularNewsSection = document.querySelector('[data-group="popular-news"]');

  if (latestNewsSection) {
    injectAdsIntoSection(latestNewsSection, 3); // Inject ad after every 3 news items
  }
  if (popularNewsSection) {
    injectAdsIntoSection(popularNewsSection, 3); // Inject ad after every 3 news items
  }
}

// Function to update ad preferences
async function updateAdPreferences(showAds) {
  try {
    const response = await fetch('/api/settings/ads-injection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            show_ads: showAds
        })
    });

    if (response.ok) {
      userShouldShowAds = showAds;
      // Reinitialize ads with new preferences
      await initializeAds();
      return true;
    } else {
      console.error('Failed to update ad preferences');
      return false;
    }
  } catch (error) {
    console.error('Error updating ad preferences:', error);
    return false;
  }
}

// Function to show premium upgrade prompt
function showPremiumUpgradePrompt() {
  const prompt = document.createElement('div');
  prompt.className = 'fixed bottom-4 right-4 bg-primary text-primary-foreground p-4 rounded-lg shadow-lg max-w-sm z-50';
  prompt.innerHTML = `
    <div class="flex items-start gap-3">
      <div class="flex-1">
        <h3 class="font-semibold mb-2">Upgrade ke Premium</h3>
        <p class="text-sm opacity-90 mb-3">Nikmati pengalaman bebas iklan dan akses ke konten eksklusif.</p>
        <div class="flex gap-2">
          <button onclick="window.location.href='/premium'" class="bg-white text-primary px-3 py-1 rounded text-sm font-medium hover:bg-gray-100 transition-colors">
            Lihat Paket
          </button>
          <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-white/70 hover:text-white text-sm">
            Tutup
          </button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(prompt);
  
  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (prompt.parentElement) {
      prompt.remove();
    }
  }, 10000);
}

// Initialize ads when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializeAds);

// Reinitialize ads on window resize (optional)
window.addEventListener('resize', initializeAds);

// Export functions for use in other scripts
window.adsInjection = {
  initializeAds,
  updateAdPreferences,
  showPremiumUpgradePrompt,
  checkUserPreferences
};
