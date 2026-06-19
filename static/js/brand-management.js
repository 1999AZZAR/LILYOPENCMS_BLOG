// Brand Management JavaScript
let COLOR_VARIABLES = [];

// Professional Color Palettes for M3 Pastel Glass
const FIXED_PRESETS = {
  "Studio Mix": {
    "--background": "210 20% 96% / 1",
    "--foreground": "215 28% 17% / 1",
    "--card": "210 20% 96% / 1",
    "--card-foreground": "215 28% 17% / 1",
    "--popover": "210 20% 96% / 1",
    "--popover-foreground": "215 28% 17% / 1",
    "--primary": "206 63% 86% / 1",
    "--primary-foreground": "206 100% 17% / 1",
    "--secondary": "264 57% 87% / 1",
    "--secondary-foreground": "264 100% 17% / 1",
    "--muted": "60 30% 96% / 1",
    "--muted-foreground": "60 10% 40% / 1",
    "--accent": "44 82% 89% / 1",
    "--accent-foreground": "44 100% 17% / 1",
    "--destructive": "356 82% 88% / 1",
    "--destructive-foreground": "356 100% 17% / 1",
    "--border": "210 20% 92% / 1",
    "--input": "210 20% 98% / 1",
    "--ring": "206 63% 86% / 1"
  },
  "Warm Blush": {
    "--background": "12 50% 95% / 1",
    "--foreground": "12 40% 15% / 1",
    "--card": "12 50% 95% / 1",
    "--card-foreground": "12 40% 15% / 1",
    "--popover": "12 50% 95% / 1",
    "--popover-foreground": "12 40% 15% / 1",
    "--primary": "9 68% 75% / 1",
    "--primary-foreground": "9 100% 15% / 1",
    "--secondary": "11 88% 90% / 1",
    "--secondary-foreground": "11 100% 15% / 1",
    "--muted": "12 30% 92% / 1",
    "--muted-foreground": "12 20% 45% / 1",
    "--accent": "28 97% 80% / 1",
    "--accent-foreground": "28 100% 15% / 1",
    "--destructive": "0 84% 60% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "12 40% 90% / 1",
    "--input": "12 50% 98% / 1",
    "--ring": "9 68% 75% / 1"
  },
  "Soft Studio": {
    "--background": "51 20% 93% / 1",
    "--foreground": "225 30% 15% / 1",
    "--card": "51 20% 93% / 1",
    "--card-foreground": "225 30% 15% / 1",
    "--popover": "51 20% 93% / 1",
    "--popover-foreground": "225 30% 15% / 1",
    "--primary": "224 83% 93% / 1",
    "--primary-foreground": "224 100% 15% / 1",
    "--secondary": "162 30% 91% / 1",
    "--secondary-foreground": "162 100% 15% / 1",
    "--muted": "51 10% 88% / 1",
    "--muted-foreground": "51 10% 45% / 1",
    "--accent": "224 83% 90% / 1",
    "--accent-foreground": "224 100% 15% / 1",
    "--destructive": "356 82% 90% / 1",
    "--destructive-foreground": "356 100% 15% / 1",
    "--border": "51 20% 88% / 1",
    "--input": "51 30% 98% / 1",
    "--ring": "224 83% 93% / 1"
  },
  "Soft Cream": {
    "--background": "12 50% 95% / 1",
    "--foreground": "12 30% 15% / 1",
    "--card": "12 50% 95% / 1",
    "--card-foreground": "12 30% 15% / 1",
    "--popover": "12 50% 95% / 1",
    "--popover-foreground": "12 30% 15% / 1",
    "--primary": "9 97% 86% / 1",
    "--primary-foreground": "9 100% 15% / 1",
    "--secondary": "32 28% 89% / 1",
    "--secondary-foreground": "32 100% 15% / 1",
    "--muted": "12 20% 90% / 1",
    "--muted-foreground": "12 20% 45% / 1",
    "--accent": "28 97% 80% / 1",
    "--accent-foreground": "28 100% 15% / 1",
    "--destructive": "0 84% 60% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "12 30% 90% / 1",
    "--input": "12 50% 98% / 1",
    "--ring": "9 97% 86% / 1"
  },
  "Midnight Glass": {
    "--background": "225 30% 8% / 1",
    "--foreground": "210 20% 98% / 1",
    "--card": "225 30% 8% / 1",
    "--card-foreground": "210 20% 98% / 1",
    "--popover": "225 30% 8% / 1",
    "--popover-foreground": "210 20% 98% / 1",
    "--primary": "206 63% 56% / 1",
    "--primary-foreground": "0 0% 100% / 1",
    "--secondary": "264 57% 57% / 1",
    "--secondary-foreground": "0 0% 100% / 1",
    "--muted": "225 20% 15% / 1",
    "--muted-foreground": "225 20% 70% / 1",
    "--accent": "206 63% 56% / 1",
    "--accent-foreground": "0 0% 100% / 1",
    "--destructive": "356 82% 56% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "225 30% 15% / 1",
    "--input": "225 30% 12% / 1",
    "--ring": "206 63% 56% / 1"
  }
};

// Categorize presets
const PRESET_CATEGORIES = {
  classic: ["Studio Mix", "Warm Blush", "Soft Studio", "Soft Cream", "Midnight Glass"],
  capuchin: [],
  themed: []
};

function createPaletteCard(name, palette) {
  const card = document.createElement('div');
  card.className = 'bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-200 overflow-hidden palette-card';
  card.setAttribute('data-palette-name', name);
  
  // Create color preview squares
  const colorSquares = Object.entries(palette).slice(0, 8).map(([key, value]) => {
    const hslMatch = value.match(/^(\d+)\s+(\d+)%\s+(\d+)%\s*\/\s*([\d.]+)$/);
    if (!hslMatch) return '';
    
    const [, h, s, l, a] = hslMatch;
    const hex = hslToHex(parseInt(h), parseInt(s), parseInt(l));
    
    // Determine border color based on lightness
    const lightness = parseInt(l);
    const borderColor = lightness > 70 ? '#d1d5db' : lightness > 40 ? '#9ca3af' : '#374151';
    
    return `<div class="w-8 h-8 rounded-lg color-square shadow-sm" style="background: linear-gradient(135deg, ${hex} 0%, ${hex} 100%); border: 2px solid ${borderColor};" title="${key}"></div>`;
  }).join('');
  
  card.innerHTML = `
    <div class="p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-gray-800 text-sm">${name}</h4>
        <button class="apply-palette-btn bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white px-3 py-1 rounded text-xs font-medium transition-all duration-300 shadow-sm flex items-center gap-1" data-palette="${name}">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 7.5h-.75A2.25 2.25 0 004.5 9.75v7.5a2.25 2.25 0 002.25 2.25h7.5a2.25 2.25 0 002.25-2.25v-7.5a2.25 2.25 0 00-2.25-2.25h-.75m-6 3l-3-3m0 0l-3 3m3-3v11.25m6-5.25h-.75a2.25 2.25 0 00-2.25 2.25v7.5a2.25 2.25 0 002.25 2.25h7.5a2.25 2.25 0 002.25-2.25v-7.5a2.25 2.25 0 00-2.25-2.25h-.75" />
          </svg>
          Apply
        </button>
      </div>
      <div class="grid grid-cols-4 gap-2 mb-3">
        ${colorSquares}
      </div>
      <div class="text-xs text-gray-500">
        ${Object.keys(palette).length} colors
      </div>
    </div>
  `;
  
  return card;
}

function populatePaletteTabs() {
  // Populate Classic tab
  const classicContainer = document.querySelector('#classic-palettes .grid');
  if (classicContainer) {
    classicContainer.innerHTML = '';
    PRESET_CATEGORIES.classic.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        classicContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
  
  // Populate Capuchin tab
  const capuchinContainer = document.querySelector('#capuchin-palettes .grid');
  if (capuchinContainer) {
    capuchinContainer.innerHTML = '';
    PRESET_CATEGORIES.capuchin.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        capuchinContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
  
  // Populate Themed tab
  const themedContainer = document.querySelector('#themed-palettes .grid');
  if (themedContainer) {
    themedContainer.innerHTML = '';
    PRESET_CATEGORIES.themed.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        themedContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
}

function getPresetPalette(name) {
  if (name.startsWith('__custom__')) {
    const custom = getCustomPresets();
    return custom[name.replace('__custom__', '')];
  }
  return FIXED_PRESETS[name] || null;
}

function previewPreset(name) {
  const palette = getPresetPalette(name);
  if (!palette) return;
  
  // Update COLOR_VARIABLES in-place for preview only
  COLOR_VARIABLES.forEach(cv => {
    if (palette[cv.name]) {
      cv.value = palette[cv.name];
    }
  });
  renderColorPaletteTable();
}

// Form handling
function handleBrandForm(formId, fieldName) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
      showToast('warning', 'Pilih file terlebih dahulu!');
      return;
    }
    formData.append(fieldName, fileInput.files[0]);
    try {
      const headers = {};
      const csrfToken = getCSRFToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const resp = await fetch('/api/brand-identity', {
        method: 'POST',
        headers: headers,
        body: formData
      });
      if (!resp.ok) throw new Error('Upload failed');
      showToast('success', 'Gambar berhasil diunggah!');
      refreshBrandImages();
      form.reset();
    } catch (err) {
      console.error('Upload error:', err);
      showToast('error', 'Gagal mengunggah gambar: ' + err.message);
    }
  });
}

function handleBrandTextForm(formId, fieldName) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const input = form.querySelector('input[type="text"]');
    const value = input.value.trim();
    
    if (!value) {
      showToast('warning', 'Field tidak boleh kosong!');
      return;
    }
    
    try {
      const headers = {
        'Content-Type': 'application/json',
      };
      const csrfToken = getCSRFToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const resp = await fetch('/api/brand-identity/text', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          field: fieldName,
          value: value
        })
      });
      
      if (!resp.ok) throw new Error('Update failed');
      
      showToast('success', `${fieldName === 'brand_name' ? 'Brand name' : 'Tagline'} berhasil diperbarui!`);
      
      // Update the input value to reflect the saved state
      input.value = value;
      
    } catch (err) {
      console.error('Update error:', err);
      showToast('error', `Gagal memperbarui ${fieldName === 'brand_name' ? 'brand name' : 'tagline'}: ` + err.message);
    }
  });
}

// Initialize everything
document.addEventListener('DOMContentLoaded', function() {
  // Load color palette
  fetch('/api/brand-colors')
    .then(resp => resp.json())
    .then(data => {
      COLOR_VARIABLES = data;
      populatePaletteTabs();
      renderColorPaletteTable();
    })
    .catch(err => console.error('Failed to load colors:', err));
  
  // Brand form handlers
  handleBrandForm('form-logo-header', 'logo_header');
  handleBrandForm('form-logo-footer', 'logo_footer');
  handleBrandForm('form-favicon', 'favicon');
  handleBrandForm('form-placeholder', 'placeholder_image');
  
  // Brand text form handlers
  handleBrandTextForm('form-brand-name', 'brand_name');
  handleBrandTextForm('form-tagline', 'tagline');
  
  // Tab switching functionality
  const paletteTabs = document.querySelectorAll('.palette-tab');
  paletteTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const targetTab = this.getAttribute('data-tab');
      
      // Update tab states
      paletteTabs.forEach(t => {
        // Remove all possible gradient classes
        t.classList.remove('active', 'bg-gradient-to-r', 'from-amber-500', 'to-yellow-500', 'from-blue-500', 'to-indigo-500', 'from-gray-400', 'to-gray-500');
        // Add gray gradient for inactive
        t.classList.add('bg-gradient-to-r', 'from-gray-400', 'to-gray-500');
        t.setAttribute('aria-selected', 'false');
      });
      
      // Add amber gradient for active tab
      this.classList.add('active', 'bg-gradient-to-r', 'from-amber-500', 'to-yellow-500');
      this.classList.remove('bg-gradient-to-r', 'from-gray-400', 'to-gray-500', 'from-blue-500', 'to-indigo-500');
      this.setAttribute('aria-selected', 'true');
      
      // Show/hide content
      const allContents = document.querySelectorAll('.palette-content');
      allContents.forEach(content => content.classList.add('hidden'));
      
      const targetContent = document.getElementById(`${targetTab}-palettes`);
      if (targetContent) {
        targetContent.classList.remove('hidden');
      }
    });
  });
  
  // Apply palette functionality
  document.addEventListener('click', async function(e) {
    if (e.target.classList.contains('apply-palette-btn')) {
      const paletteName = e.target.getAttribute('data-palette');
      const palette = getPresetPalette(paletteName);
      
      if (!palette) {
        showToast('warning', 'Palette tidak ditemukan!');
        return;
      }
      
      console.log('Applying palette:', paletteName);
      console.log('Palette data:', palette);
      
      // Create array of updates needed
      const updates = [];
      
      COLOR_VARIABLES.forEach(cv => {
        const presetValue = palette[cv.name];
        if (presetValue) {
          // Normalize values for comparison
          const currentNormalized = cv.value.trim().replace(/\s+/g, ' ').replace(/\s*\/\s*/, ' / ');
          const presetNormalized = presetValue.trim().replace(/\s+/g, ' ').replace(/\s*\/\s*/, ' / ');
          
          if (currentNormalized !== presetNormalized) {
            updates.push({
              variable: cv.name,
              value: presetValue
            });
          }
        }
      });
      
      if (updates.length === 0) {
        showToast('info', 'Tidak ada warna yang perlu diperbarui!');
        return;
      }
      
      console.log('Applying palette with', updates.length, 'updates');
      
      try {
        // Apply all updates
        for (const update of updates) {
          const headers = {
            'Content-Type': 'application/json'
          };
          const csrfToken = getCSRFToken();
          if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
          }
          
          const response = await fetch('/api/brand-colors', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(update)
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update ${update.variable}`);
          }
        }
        
        // Reload palette from backend
        const response = await fetch('/api/brand-colors');
        const data = await response.json();
        COLOR_VARIABLES = data;
        renderColorPaletteTable();
        
        // Reload CSS
        const link = document.querySelector('link[href*="base_css.css"]');
        if (link) {
          link.href = link.href.split('?')[0] + '?v=' + Date.now();
        }
        
        showToast('success', `Palette "${paletteName}" berhasil diterapkan!`);
      } catch (err) {
        console.error('Error applying palette:', err);
        showToast('error', 'Gagal menerapkan palette: ' + err.message);
      }
    }
  });
  

  
  // Add keyboard event listener for modal
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      const modal = document.getElementById('color-picker-modal');
      if (modal && !modal.classList.contains('hidden')) {
        closeColorPickerModal();
      }
    }
  });
}); 