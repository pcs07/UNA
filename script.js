// ===========================
//  UNA — UPSC News Analysis
//  Frontend Logic
// ===========================

const PAGE_SIZE = 24;

let allArticles = [];
let filteredArticles = [];
let currentPage = 1;
let activeCategory = 'All';
let activeSource = 'All';
let searchQuery = '';

// ---- INIT ----

async function loadNews() {
  showLoading();
  try {
    const res = await fetch(`data/news.json?t=${Date.now()}`);
    if (!res.ok) throw new Error('Not found');
    const data = await res.json();
    allArticles = data.articles || [];
    setLastUpdated(data.last_updated);
    document.getElementById('statTotal').textContent = allArticles.length;
    applyFilters();
  } catch (e) {
    showEmpty('Could not load news data. Run <code>python scripts/fetch_news.py</code> or push to GitHub to trigger the workflow.');
  }
}

window.addEventListener('DOMContentLoaded', () => {
  setupFilters();
  setupSearch();
  loadNews();
});

// ---- FILTERS ----

function setupFilters() {
  document.getElementById('categoryTabs').addEventListener('click', e => {
    const btn = e.target.closest('.tab');
    if (!btn) return;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    activeCategory = btn.dataset.cat;
    currentPage = 1;
    applyFilters();
  });

  document.getElementById('sourcePills').addEventListener('click', e => {
    const btn = e.target.closest('.pill');
    if (!btn) return;
    document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    activeSource = btn.dataset.src;
    currentPage = 1;
    applyFilters();
  });
}

function setupSearch() {
  const input = document.getElementById('searchInput');
  const clear = document.getElementById('searchClear');

  input.addEventListener('input', () => {
    searchQuery = input.value.trim().toLowerCase();
    clear.classList.toggle('visible', searchQuery.length > 0);
    currentPage = 1;
    applyFilters();
  });
}

function clearSearch() {
  document.getElementById('searchInput').value = '';
  document.getElementById('searchClear').classList.remove('visible');
  searchQuery = '';
  currentPage = 1;
  applyFilters();
}

function applyFilters() {
  const sort = document.getElementById('sortSelect').value;

  filteredArticles = allArticles.filter(a => {
    const catOk  = activeCategory === 'All' || a.category === activeCategory;
    const srcOk  = activeSource === 'All'   || a.source === activeSource;
    const searchOk = !searchQuery ||
      (a.title || '').toLowerCase().includes(searchQuery) ||
      (a.description || '').toLowerCase().includes(searchQuery) ||
      (a.source || '').toLowerCase().includes(searchQuery);
    return catOk && srcOk && searchOk;
  });

  // Sort
  filteredArticles.sort((a, b) => {
    if (sort === 'newest') return (b.published || '') > (a.published || '') ? 1 : -1;
    if (sort === 'oldest') return (a.published || '') > (b.published || '') ? 1 : -1;
    if (sort === 'source') return (a.source || '').localeCompare(b.source || '');
    return 0;
  });

  document.getElementById('statFiltered').textContent = filteredArticles.length;

  renderPage(currentPage);
  renderPagination();
}

// ---- RENDER ----

function renderPage(page) {
  currentPage = page;
  const grid = document.getElementById('newsGrid');

  if (filteredArticles.length === 0) {
    showEmpty('No articles match your filters. Try changing the category or source.');
    return;
  }

  const start = (page - 1) * PAGE_SIZE;
  const slice = filteredArticles.slice(start, start + PAGE_SIZE);

  grid.innerHTML = slice.map(article => buildCard(article)).join('');
}

function buildCard(a) {
  const srcClass = slugify(a.source);
  const catClass = slugify(a.category);
  const time     = formatTime(a.published);
  const desc     = strip(a.description);

  return `
    <article class="news-card">
      <div class="card-meta">
        <span class="source-badge src--${srcClass}">${escHtml(a.source)}</span>
        <span class="category-badge cat--${catClass}">${escHtml(a.category)}</span>
        <time class="published-time">${time}</time>
      </div>
      <h2 class="card-title">
        <a href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer">${escHtml(a.title)}</a>
      </h2>
      ${desc ? `<p class="card-description">${escHtml(desc)}</p>` : ''}
      <div class="card-footer">
        <a class="read-more" href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer">Read full article →</a>
      </div>
    </article>`;
}

// ---- PAGINATION ----

function renderPagination() {
  const totalPages = Math.ceil(filteredArticles.length / PAGE_SIZE);
  const container  = document.getElementById('pagination');
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  let html = '';

  html += `<button class="page-btn" onclick="goPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>← Prev</button>`;

  const range = pageRange(currentPage, totalPages);
  let prev = null;
  for (const p of range) {
    if (prev !== null && p - prev > 1) html += `<span style="color:var(--text-muted);padding:0 4px;">…</span>`;
    html += `<button class="page-btn ${p === currentPage ? 'active' : ''}" onclick="goPage(${p})">${p}</button>`;
    prev = p;
  }

  html += `<button class="page-btn" onclick="goPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next →</button>`;
  container.innerHTML = html;
}

function goPage(p) {
  const total = Math.ceil(filteredArticles.length / PAGE_SIZE);
  if (p < 1 || p > total) return;
  currentPage = p;
  renderPage(p);
  renderPagination();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function pageRange(current, total) {
  const delta = 2;
  const range = new Set([1, total]);
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) range.add(i);
  return [...range].sort((a, b) => a - b);
}

// ---- MODAL ----

function openModal(a) {
  document.getElementById('modalBody').innerHTML = `
    <div class="card-meta" style="margin-bottom:16px">
      <span class="source-badge src--${slugify(a.source)}">${escHtml(a.source)}</span>
      <span class="category-badge cat--${slugify(a.category)}">${escHtml(a.category)}</span>
    </div>
    <h2 style="font-size:18px;margin-bottom:12px;line-height:1.4">${escHtml(a.title)}</h2>
    <p style="color:var(--text-muted);font-size:12px;margin-bottom:16px">${formatTime(a.published)}</p>
    <p style="font-size:14px;color:var(--text-secondary);line-height:1.7;margin-bottom:20px">${escHtml(strip(a.description))}</p>
    <a href="${escHtml(a.url)}" target="_blank" class="read-more" style="font-size:14px">Read full article on ${escHtml(a.source)} →</a>`;
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ---- STATES ----

function showLoading() {
  document.getElementById('newsGrid').innerHTML =
    `<div class="loading-state"><div class="spinner"></div> Fetching latest articles…</div>`;
  document.getElementById('pagination').innerHTML = '';
}

function showEmpty(msg) {
  document.getElementById('newsGrid').innerHTML =
    `<div class="empty-state"><div class="empty-icon">📰</div><h2>No articles found</h2><p>${msg}</p></div>`;
  document.getElementById('pagination').innerHTML = '';
}

// ---- UTILS ----

function slugify(str) {
  return (str || '').toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function escHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function strip(html) {
  if (!html) return '';
  return html
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim()
    .slice(0, 280);
}

function formatTime(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    const mins  = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days  = Math.floor(diff / 86400000);

    if (mins < 2)   return 'just now';
    if (mins < 60)  return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days === 1) return 'yesterday';
    if (days < 7)   return `${days}d ago`;

    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: days > 365 ? 'numeric' : undefined });
  } catch { return ''; }
}

function setLastUpdated(iso) {
  const el = document.getElementById('lastUpdated');
  if (!iso) { el.textContent = 'Never updated'; return; }
  try {
    const d = new Date(iso);
    el.textContent = `Updated ${d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })} at ${d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;
  } catch { el.textContent = 'Unknown'; }
}
