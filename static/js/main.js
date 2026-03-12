/* ── Sidebar toggle ──────────────────────────────────────────────────────────── */
const sidebar  = document.getElementById('sidebar');
const overlay  = document.getElementById('sidebarOverlay');
const hamburger= document.getElementById('topbarHamburger');
const sidebarClose = document.getElementById('sidebarClose');

function openSidebar()  { sidebar.classList.add('open'); overlay.classList.add('open'); document.body.style.overflow = 'hidden'; }
function closeSidebar() { sidebar.classList.remove('open'); overlay.classList.remove('open'); document.body.style.overflow = ''; }

hamburger?.addEventListener('click', openSidebar);
sidebarClose?.addEventListener('click', closeSidebar);
overlay?.addEventListener('click', closeSidebar);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSidebar(); });

/* ── Toast ───────────────────────────────────────────────────────────────────── */
(function() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  document.body.appendChild(container);
})();

function toast(msg, type = 'success', duration = 3500) {
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    el.style.transition = 'all 0.3s';
    setTimeout(() => el.remove(), 300);
  }, duration);
}

/* ── API helper ──────────────────────────────────────────────────────────────── */
async function api(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  };
  const res = await fetch(url, { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, message: data.error || `Request failed (${res.status})` };
  return data;
}

/* ── Format helpers ──────────────────────────────────────────────────────────── */
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
function fmtDateTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function fmtMoney(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}
function daysLeft(endDate) {
  if (!endDate) return null;
  const diff = Math.ceil((new Date(endDate) - new Date()) / 86400000);
  return diff;
}
function statusBadge(status) {
  const map = { active: 'badge-active', pending: 'badge-pending', expired: 'badge-expired', rejected: 'badge-rejected', completed: 'badge-active', refunded: 'badge-expired' };
  return `<span class="badge ${map[status] || 'badge-expired'}">${status}</span>`;
}

/* ── Modal helpers ───────────────────────────────────────────────────────────── */
function openModal(id)  { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

/* ── Pending nav badge ───────────────────────────────────────────────────────── */
async function updatePendingBadge() {
  const badge = document.getElementById('pending-badge');
  if (!badge) return;
  try {
    const data = await api('/api/payment/stats');
    if (data.pending_approvals > 0) {
      badge.textContent = data.pending_approvals;
      badge.classList.add('visible');
    } else {
      badge.classList.remove('visible');
    }
  } catch {}
}
updatePendingBadge();