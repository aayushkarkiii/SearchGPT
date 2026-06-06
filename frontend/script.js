// Frontend logic for SearchGPT
// Communicates with backend endpoints:
//  - POST /api/chat       (x-www-form-urlencoded: question)
//  - POST /api/pdf/ask    (multipart/form-data: pdf, question)
//  - POST /api/url/ask    (x-www-form-urlencoded: url, question)

let activeUrlContext = null;

async function callChat(question) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ question })
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Chat request failed (${res.status}): ${text}`);
  }

  return res.json();
}

async function callPdfAsk(pdfFile, question) {
  const form = new FormData();
  form.append('pdf', pdfFile);
  form.append('question', question);

  const res = await fetch('/api/pdf/ask', {
    method: 'POST',
    body: form
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`PDF ask request failed (${res.status}): ${text}`);
  }

  return res.json();
}

async function callUrlAsk(url, question) {
  const res = await fetch('/api/url/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ url, question })
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`URL ask request failed (${res.status}): ${text}`);
  }

  return res.json();
}

function setSuggestionLoading(isLoading, text) {
  const el = document.getElementById('aiSuggestion');
  const textEl = document.getElementById('suggestionText');
  if (!el || !textEl) return;

  el.classList.toggle('hidden', !isLoading);
  if (text && textEl) textEl.textContent = text;
}

async function handleSearch() {
  const input = document.getElementById('searchInput');
  if (!input) return;

  const q = input.value.trim();
  if (!q) return;

  input.value = '';

  setSuggestionLoading(true, 'AI-powered results loading...');

  try {
    let data;
    if (activeUrlContext) {
      setSuggestionLoading(true, 'Reading webpage context and searching...');
      data = await callUrlAsk(activeUrlContext, q);
    } else {
      data = await callChat(q);
    }

    setSuggestionLoading(true, data.answer || '');
    const el = document.getElementById('searchOutput');
    if (el) {
      el.textContent = data.answer || '';
    }
  } catch (e) {
    setSuggestionLoading(true, `Error: ${e.message}`);
  }
}

function ensureSearchOutputContainer() {
  if (document.getElementById('searchOutput')) return;

  const parent = document.querySelector('.w-full.max-w-2xl.mx-auto.mb-6');
  if (!parent) return;

  const div = document.createElement('div');
  div.id = 'searchOutput';
  div.className = 'w-full max-w-2xl mx-auto mt-4 text-gray-800 text-sm md:text-base p-4 bg-gray-50 border border-gray-100 rounded-2xl search-shadow';
  parent.appendChild(div);
}

function showUrlFeedback(msg, colorClass) {
  const el = document.getElementById('urlFeedback');
  if (!el) return;
  el.textContent = msg;
  el.className = `text-xs font-medium mt-1 ${colorClass || 'text-gray-500'}`;
  el.classList.toggle('hidden', !msg);
}

document.addEventListener('DOMContentLoaded', () => {
  ensureSearchOutputContainer();

  const input = document.getElementById('searchInput');
  const btn = document.getElementById('searchBtn');
  if (btn) btn.addEventListener('click', handleSearch);
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSearch();
      }
    });
  }

  // Link button/URL panel wires
  const linkBtn = document.getElementById('linkBtn');
  const urlPanel = document.getElementById('urlPanel');
  const closeUrlPanel = document.getElementById('closeUrlPanel');
  const addUrlBtn = document.getElementById('addUrlBtn');
  const urlInput = document.getElementById('urlInput');
  const activeContextPill = document.getElementById('activeContextPill');
  const activeContextUrl = document.getElementById('activeContextUrl');
  const clearContextBtn = document.getElementById('clearContextBtn');

  if (linkBtn && urlPanel) {
    linkBtn.addEventListener('click', () => {
      urlPanel.classList.toggle('hidden');
      if (!urlPanel.classList.contains('hidden') && urlInput) {
        urlInput.focus();
      }
    });
  }

  if (closeUrlPanel && urlPanel) {
    closeUrlPanel.addEventListener('click', () => {
      urlPanel.classList.add('hidden');
    });
  }

  if (addUrlBtn && urlInput) {
    addUrlBtn.addEventListener('click', () => {
      const url = urlInput.value.trim();
      if (!url) {
        showUrlFeedback('Please enter a URL.', 'text-red-500');
        return;
      }
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        showUrlFeedback('URL must start with http:// or https://', 'text-red-500');
        return;
      }

      showUrlFeedback('Activating webpage context...', 'text-yellow-600');
      
      // Instantly set active context
      activeUrlContext = url;
      if (activeContextUrl) activeContextUrl.textContent = url;
      if (activeContextPill) activeContextPill.classList.remove('hidden');
      if (urlPanel) urlPanel.classList.add('hidden');
      urlInput.value = '';
      showUrlFeedback('', '');
    });
  }

  if (clearContextBtn && activeContextPill) {
    clearContextBtn.addEventListener('click', () => {
      activeUrlContext = null;
      activeContextPill.classList.add('hidden');
    });
  }
});
