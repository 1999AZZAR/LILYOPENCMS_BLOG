(function () {
  'use strict';

  const ALL_TAGS = [];
  const selectedTags = new Map();
  const tagInput = document.getElementById('tag-input');
  const tagList = document.getElementById('tag-list');
  const suggestions = document.getElementById('tag-suggestions');
  const addBtn = document.getElementById('tag-add-btn');
  const tagIdsInput = document.getElementById('news-tag-ids');
  const tagarInput = document.getElementById('news-tagar');
  let allTagsLoaded = false;

  function updateHiddenInputs() {
    const ids = [];
    const names = [];
    selectedTags.forEach(function (name, id) {
      ids.push(id);
      names.push(name);
    });
    tagIdsInput.value = ids.join(',');
    tagarInput.value = names.join(', ');
  }

  function renderTags() {
    tagList.innerHTML = '';
    selectedTags.forEach(function (name, id) {
      var chip = document.createElement('span');
      chip.className = 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium';
      chip.style.cssText = 'background:hsl(var(--primary)/0.12);color:hsl(var(--primary))';
      chip.innerHTML = name +
        '<button type="button" data-id="' + id +
        '" class="tag-remove inline-flex items-center justify-center w-4 h-4 rounded-full text-[9px] font-bold border-0 cursor-pointer hover:bg-red-100 hover:text-red-600 transition-all" style="background:transparent;color:inherit">×</button>';
      tagList.appendChild(chip);
    });
    chipRemoveListeners();
    updateHiddenInputs();
  }

  function chipRemoveListeners() {
    document.querySelectorAll('.tag-remove').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectedTags.delete(parseInt(this.dataset.id));
        renderTags();
        tagInput.focus();
      });
    });
  }

  function addTag(id, name) {
    if (selectedTags.has(id)) return;
    selectedTags.set(id, name);
    renderTags();
    tagInput.value = '';
    hideSuggestions();
    tagInput.focus();
  }

  function showSuggestions(list) {
    if (!list.length) { hideSuggestions(); return; }
    suggestions.innerHTML = '';
    suggestions.classList.remove('hidden');
    list.forEach(function (t) {
      if (selectedTags.has(t.id)) return;
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'w-full text-left px-3 py-2 text-sm hover:bg-gray-100 transition-colors cursor-pointer border-0';
      item.textContent = t.name + ' (' + t.count + ')';
      item.addEventListener('click', function () { addTag(t.id, t.name); });
      suggestions.appendChild(item);
    });
  }

  function hideSuggestions() {
    suggestions.classList.add('hidden');
  }

  function loadAllTags() {
    if (allTagsLoaded) return Promise.resolve(ALL_TAGS);
    return fetch('/api/tags')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var tags = data.tags || data || [];
        ALL_TAGS.length = 0;
        tags.forEach(function (t) { ALL_TAGS.push(t); });
        allTagsLoaded = true;
        return ALL_TAGS;
      });
  }

  function suggestTags(query) {
    if (!query) { hideSuggestions(); return; }
    var q = query.toLowerCase();
    var matched = ALL_TAGS.filter(function (t) {
      return t.name.toLowerCase().indexOf(q) !== -1;
    }).sort(function (a, b) { return b.count - a.count; });
    showSuggestions(matched.slice(0, 8));
  }

  function createTagAndSelect(name) {
    fetch('/api/settings/tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      body: JSON.stringify({ name: name.trim() })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.id) {
        addTag(data.id, data.name);
        ALL_TAGS.push({ id: data.id, name: data.name, count: 0 });
      }
    })
    .catch(function () {});
  }

  // Init
  loadAllTags();

  tagInput.addEventListener('input', function () {
    suggestTags(this.value);
  });

  tagInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      var val = this.value.trim();
      if (!val) return;
      var exact = ALL_TAGS.find(function (t) { return t.name.toLowerCase() === val.toLowerCase(); });
      if (exact) {
        addTag(exact.id, exact.name);
      } else {
        createTagAndSelect(val);
      }
    }
    if (e.key === 'Escape') hideSuggestions();
  });

  tagInput.addEventListener('blur', function () {
    setTimeout(hideSuggestions, 200);
  });

  tagInput.addEventListener('focus', function () {
    if (this.value) suggestTags(this.value);
  });

  addBtn.addEventListener('click', function () {
    var val = tagInput.value.trim();
    if (!val) return;
    var exact = ALL_TAGS.find(function (t) { return t.name.toLowerCase() === val.toLowerCase(); });
    if (exact) {
      addTag(exact.id, exact.name);
    } else {
      createTagAndSelect(val);
    }
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('#tag-suggestions') && !e.target.closest('#tag-input')) {
      hideSuggestions();
    }
  });
})();
