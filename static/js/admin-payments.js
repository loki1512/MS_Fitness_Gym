/* Admin payments page */

let pendingSubId = null;
let rejectSubId  = null;
let txnPage      = 1;

async function loadStats() {
  try {
    const d = await api('/api/payment/stats');
    document.getElementById('ps-pending').textContent = d.pending_approvals;
    document.getElementById('ps-month').textContent   = fmtMoney(d.month_revenue);
    document.getElementById('ps-total').textContent   = fmtMoney(d.total_revenue);
  } catch {}
}

async function loadPending() {
  try {
    const rows = await api('/api/payment/pending');
    const tbody = document.getElementById('pending-payments-tbody');
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No pending approvals 🎉</td></tr>';
      return;
    }
    tbody.innerHTML = rows.map(r => `<tr>
      <td><strong style="color:var(--white);">${r.member_name}</strong><br><span style="font-size:0.78rem;color:var(--steel);">@${r.member_username}</span></td>
      <td>${r.plan_name}</td>
      <td style="color:var(--fire);font-weight:700;">${fmtMoney(r.amount)}</td>
      <td>${r.payment_mode}</td>
      <td style="font-size:0.82rem;color:var(--steel);">${fmtDateTime(r.created_at)}</td>
      <td>
        <div style="display:flex;gap:0.4rem;">
          <button class="btn btn-success btn-sm" onclick="openApprove(${r.id},'${r.member_name}','${r.plan_name}',${r.amount},'${r.payment_mode}')">Approve</button>
          <button class="btn btn-danger btn-sm" onclick="openReject(${r.id})">Reject</button>
        </div>
      </td>
    </tr>`).join('');
  } catch(e) { toast('Failed to load pending: ' + e.message, 'error'); }
}

async function loadHistory(page = 1) {
  const status = document.getElementById('status-filter').value;
  try {
    const data = await api(`/api/payment/history?page=${page}&per_page=20${status ? '&status=' + status : ''}`);
    const tbody = document.getElementById('txn-tbody');
    if (!data.transactions.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No transactions found</td></tr>';
    } else {
      tbody.innerHTML = data.transactions.map(t => `<tr>
        <td><strong style="color:var(--white);">${t.member_name}</strong><br><span style="font-size:0.78rem;color:var(--steel);">@${t.member_username}</span></td>
        <td style="font-size:0.82rem;color:var(--steel);">${t.description || '—'}</td>
        <td style="color:var(--fire);font-weight:700;">${fmtMoney(t.amount)}</td>
        <td>${t.mode}</td>
        <td>${statusBadge(t.status)}</td>
        <td style="font-size:0.82rem;color:var(--steel);">${fmtDate(t.transaction_date)}</td>
      </tr>`).join('');
    }
    renderPagination(data.page, data.pages, (p) => loadHistory(p), 'txn-pagination');
    txnPage = page;
  } catch(e) { toast('Failed to load history', 'error'); }
}

function renderPagination(current, total, cb, containerId) {
  const el = document.getElementById(containerId);
  if (!el || total <= 1) { if(el) el.innerHTML = ''; return; }
  let html = `<button class="page-btn" ${current===1?'disabled':''} onclick="(${cb})(${current-1})">‹</button>`;
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || Math.abs(i - current) <= 1) {
      html += `<button class="page-btn ${i===current?'active':''}" onclick="(${cb})(${i})">${i}</button>`;
    } else if (Math.abs(i - current) === 2) {
      html += `<span style="color:var(--steel);padding:0 4px;">…</span>`;
    }
  }
  html += `<button class="page-btn" ${current===total?'disabled':''} onclick="(${cb})(${current+1})">›</button>`;
  el.innerHTML = html;
}

/* ── Approve ────────────────────────────────────────────────────────────────── */
function openApprove(id, name, plan, amount, mode) {
  pendingSubId = id;
  document.getElementById('approve-modal-body').innerHTML = `
    <div style="display:flex;flex-direction:column;gap:0.5rem;margin-bottom:0.75rem;">
      <div class="drawer-info-row"><span class="drawer-info-key">Member</span><span class="drawer-info-val">${name}</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Plan</span><span class="drawer-info-val">${plan}</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Amount</span><span class="drawer-info-val" style="color:var(--fire);font-weight:700;">${fmtMoney(amount)}</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Mode</span><span class="drawer-info-val">${mode}</span></div>
    </div>
    <p style="font-size:0.85rem;color:var(--steel);">Confirming will activate the subscription immediately and mark the payment as completed.</p>`;
  openModal('approve-modal');
}

document.getElementById('approve-cancel')?.addEventListener('click', () => closeModal('approve-modal'));
document.getElementById('approve-confirm')?.addEventListener('click', async () => {
  if (!pendingSubId) return;
  const btn = document.getElementById('approve-confirm');
  btn.classList.add('btn-loading');
  try {
    const res = await api(`/api/payment/approve/${pendingSubId}`, { method: 'POST', body: JSON.stringify({}) });
    closeModal('approve-modal');
    toast(res.message || 'Approved!');
    await Promise.all([loadStats(), loadPending(), loadHistory(txnPage)]);
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.classList.remove('btn-loading'); }
});

/* ── Reject ─────────────────────────────────────────────────────────────────── */
function openReject(id) {
  rejectSubId = id;
  document.getElementById('reject-notes').value = '';
  openModal('reject-modal');
}

document.getElementById('reject-cancel')?.addEventListener('click', () => closeModal('reject-modal'));
document.getElementById('reject-confirm')?.addEventListener('click', async () => {
  if (!rejectSubId) return;
  const btn = document.getElementById('reject-confirm');
  btn.classList.add('btn-loading');
  const notes = document.getElementById('reject-notes').value;
  try {
    await api(`/api/payment/reject/${rejectSubId}`, { method: 'POST', body: JSON.stringify({ notes }) });
    closeModal('reject-modal');
    toast('Rejected', 'warn');
    await Promise.all([loadStats(), loadPending(), loadHistory(txnPage)]);
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.classList.remove('btn-loading'); }
});

document.getElementById('refresh-pending-btn')?.addEventListener('click', () => { loadPending(); loadStats(); });
document.getElementById('status-filter')?.addEventListener('change', () => loadHistory(1));

window.openApprove = openApprove;
window.openReject  = openReject;

loadStats();
loadPending();
loadHistory(1);