(function () {
  'use strict';

  const NEWS_ID = window.newsId;
  if (!NEWS_ID) return;

  const API = '/api/news/' + NEWS_ID + '/comments';
  const listEl = document.getElementById('comments-list');
  const formEl = document.getElementById('comment-form');
  const contentEl = document.getElementById('comment-content');
  const charsEl = document.getElementById('comment-chars');
  const replyIndicator = document.getElementById('reply-indicator');
  const replyToName = document.getElementById('reply-to-name');
  const cancelReply = document.getElementById('cancel-reply');
  let parentId = null;

  function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function getRelativeTime(dateStr) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'baru saja';
    if (mins < 60) return mins + 'm lalu';
    const hours = Math.floor(mins / 60);
    if (hours < 24) return hours + 'j lalu';
    const days = Math.floor(hours / 24);
    if (days < 7) return days + 'h lalu';
    return new Date(dateStr).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('id-ID', {
      day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }

  function renderComment(c, isReply) {
    const d = document.createElement('div');
    d.className = isReply ? 'ml-8 mt-3 p-3 rounded' : 'p-4 rounded';
    d.style.cssText = 'border:1px solid hsl(var(--border));background-color:var(--m3-container)';

    const avatarLetter = (c.author_name || 'A')[0].toUpperCase();
    const avatarColor = ['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#06b6d4','#f97316','#6366f1'][
      c.author_name ? c.author_name.length % 8 : 0
    ];

    d.innerHTML =
      '<div class="flex items-start gap-3">' +
        '<div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white" style="background:' + avatarColor + '">' + escapeHtml(avatarLetter) + '</div>' +
        '<div class="flex-1 min-w-0">' +
          '<div class="flex items-center gap-2 mb-1">' +
            '<span class="text-xs font-bold" style="color:hsl(var(--foreground))">' + escapeHtml(c.author_name || 'Anonim') + '</span>' +
            '<span class="text-[10px]" style="color:hsl(var(--muted-foreground))">' + getRelativeTime(c.created_at) + '</span>' +
          '</div>' +
          '<div class="text-sm leading-relaxed" style="color:hsl(var(--foreground))">' + escapeHtml(c.content) + '</div>' +
          (!isReply && !c.parent_id ?
            '<button type="button" class="comment-reply-btn text-[10px] font-semibold mt-2 hover:underline" data-id="' + c.id + '" data-name="' + escapeHtml(c.author_name || 'Anonim') + '" style="color:hsl(var(--primary))">Balas</button>'
          : '') +
        (c.replies && c.replies.length ?
          '<div class="mt-2 space-y-2">' + c.replies.map(function(r) { return renderComment(r, true).outerHTML; }).join('') + '</div>'
        : '') +
        '</div>' +
      '</div>';

    return d;
  }

  function loadComments() {
    fetch(API)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (!data.comments || !data.comments.length) {
          listEl.innerHTML = '<div class="text-center py-8 text-sm" style="color:hsl(var(--muted-foreground))">Belum ada komentar. Jadilah yang pertama!</div>';
          return;
        }
        listEl.innerHTML = '';
        data.comments.forEach(function(c) {
          listEl.appendChild(renderComment(c, false));
        });
        attachReplyHandlers();
      })
      .catch(function() {
        listEl.innerHTML = '<div class="text-center py-8 text-sm" style="color:hsl(var(--muted-foreground))">Gagal memuat komentar.</div>';
      });
  }

  function attachReplyHandlers() {
    document.querySelectorAll('.comment-reply-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        parentId = parseInt(this.dataset.id);
        replyToName.textContent = this.dataset.name;
        replyIndicator.classList.remove('hidden');
        contentEl.focus();
      });
    });
  }

  function submitComment(e) {
    e.preventDefault();
    var content = contentEl.value.trim();
    if (!content) return;

    var payload = { content: content };
    if (parentId) payload.parent_id = parentId;

    if (!window.currentUser) {
      payload.author_name = document.getElementById('comment-name').value.trim();
      payload.author_email = document.getElementById('comment-email').value.trim();
      if (!payload.author_name || !payload.author_email) {
        alert('Nama dan email wajib diisi.');
        return;
      }
    }

    var submitBtn = formEl.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Mengirim...';

    fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      body: JSON.stringify(payload)
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.success) {
        contentEl.value = '';
        parentId = null;
        replyIndicator.classList.add('hidden');
        loadComments();
      } else {
        alert(data.error || 'Gagal mengirim komentar.');
      }
    })
    .catch(function() {
      alert('Gagal mengirim komentar.');
    })
    .finally(function() {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Kirim';
    });
  }

  // Char counter
  contentEl.addEventListener('input', function() {
    charsEl.textContent = this.value.length;
  });

  // Cancel reply
  cancelReply.addEventListener('click', function() {
    parentId = null;
    replyIndicator.classList.add('hidden');
  });

  // Init
  formEl.addEventListener('submit', submitComment);
  loadComments();
})();
