/* Admin dashboard */

let pendingSubId = null;
let rejectSubId  = null;

async function loadStats() {
  try {
    const d = await api('/api/admin/stats');
    document.getElementById('stat-members').textContent    = d.total_members;
    document.getElementById('stat-active-subs').textContent= d.active_subscriptions;
    document.getElementById('stat-pending').textContent    = d.pending_approvals;
    document.getElementById('stat-month-rev').textContent  = fmtMoney(d.month_revenue);
    document.getElementById('stat-total-rev').textContent  = fmtMoney(d.total_revenue);

    // Nav badge
    const badge = document.getElementById('pending-badge');
    if (badge && d.pending_approvals > 0) {
      badge.textContent = d.pending_approvals;
      badge.classList.add('visible');
    }
  } catch {}
}

async function loadPending() {
  try {
    const rows = await api('/api/payment/pending');
    const tbody = document.getElementById('pending-tbody');
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

async function loadExpiring() {
  try {
    // Fetch members and filter by expiring subscription
    const today  = new Date();
    const plus7  = new Date(today); plus7.setDate(plus7.getDate() + 7);
    const data   = await api('/api/admin/members?per_page=100');
    const tbody  = document.getElementById('expiring-tbody');
    const expiring = data.members.filter(m => {
      if (!m.active_subscription) return false;
      const end = new Date(m.active_subscription.end_date);
      return end >= today && end <= plus7;
    });
    if (!expiring.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-empty">No subscriptions expiring soon</td></tr>';
      return;
    }
    tbody.innerHTML = expiring.map(m => {
      const sub  = m.active_subscription;
      const left = daysLeft(sub.end_date);
      return `<tr>
        <td><strong style="color:var(--white);">${m.name}</strong><br><span style="font-size:0.78rem;color:var(--steel);">@${m.username}</span></td>
        <td>${sub.plan_name}</td>
        <td>${fmtDate(sub.end_date)}</td>
        <td style="color:var(--warn);font-weight:700;">${left} days</td>
      </tr>`;
    }).join('');
  } catch {}
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
    <p style="font-size:0.85rem;color:var(--steel);">Approving will activate the subscription and mark the payment as completed.</p>`;
  openModal('approve-modal');
}

document.getElementById('approve-modal-cancel')?.addEventListener('click', () => closeModal('approve-modal'));

document.getElementById('approve-modal-confirm')?.addEventListener('click', async () => {
  if (!pendingSubId) return;
  const btn = document.getElementById('approve-modal-confirm');
  btn.classList.add('btn-loading');
  try {
    const res = await api(`/api/payment/approve/${pendingSubId}`, { method: 'POST', body: JSON.stringify({}) });
    closeModal('approve-modal');
    toast(res.message || 'Payment approved!');
    await Promise.all([loadStats(), loadPending(), loadExpiring()]);
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.classList.remove('btn-loading'); }
});

/* ── Reject ─────────────────────────────────────────────────────────────────── */
function openReject(id) {
  rejectSubId = id;
  document.getElementById('reject-notes').value = '';
  openModal('reject-modal');
}

document.getElementById('reject-modal-cancel')?.addEventListener('click', () => closeModal('reject-modal'));

document.getElementById('reject-modal-confirm')?.addEventListener('click', async () => {
  if (!rejectSubId) return;
  const btn   = document.getElementById('reject-modal-confirm');
  const notes = document.getElementById('reject-notes').value;
  btn.classList.add('btn-loading');
  try {
    await api(`/api/payment/reject/${rejectSubId}`, { method: 'POST', body: JSON.stringify({ notes }) });
    closeModal('reject-modal');
    toast('Payment rejected', 'warn');
    await Promise.all([loadStats(), loadPending()]);
  } catch(e) { toast(e.message, 'error'); }
  finally { btn.classList.remove('btn-loading'); }
});

document.getElementById('refresh-pending')?.addEventListener('click', () => {
  loadStats(); loadPending();
});

// Expose for inline onclick
window.openApprove = openApprove;
window.openReject  = openReject;

loadStats();
loadPending();
loadExpiring();