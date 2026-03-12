/* Member subscription page */

let selectedPlan = null;
let profileData  = null;

async function loadAll() {
  await Promise.all([loadProfile(), loadPlans(), loadHistory()]);
}

async function loadProfile() {
  try {
    profileData = await api('/api/member/profile');
    renderCurrentSub(profileData.active_subscription);
    renderPending(profileData.pending_subscription);
  } catch(e) {
    toast('Failed to load subscription data', 'error');
  }
}

function renderCurrentSub(sub) {
  const body = document.getElementById('current-sub-body');
  if (!sub) {
    body.innerHTML = `<div style="color:var(--steel);padding:0.5rem 0;">No active subscription. Choose a plan below.</div>`;
    return;
  }
  const left = daysLeft(sub.end_date);
  const warn = left !== null && left <= 7;
  body.innerHTML = `
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1rem;">
      <div><div class="stat-card-label" style="font-family:'Barlow Condensed',sans-serif;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--steel);margin-bottom:4px;">Plan</div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:var(--white);">${sub.plan_name}</div></div>
      <div><div class="stat-card-label" style="font-family:'Barlow Condensed',sans-serif;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--steel);margin-bottom:4px;">Start</div><div style="font-size:0.9rem;color:var(--off);">${fmtDate(sub.start_date)}</div></div>
      <div><div class="stat-card-label" style="font-family:'Barlow Condensed',sans-serif;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--steel);margin-bottom:4px;">Expires</div><div style="font-size:0.9rem;color:${warn ? 'var(--warn)' : 'var(--off)'};">${fmtDate(sub.end_date)}</div></div>
      <div><div class="stat-card-label" style="font-family:'Barlow Condensed',sans-serif;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--steel);margin-bottom:4px;">Days Left</div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:${warn ? 'var(--warn)' : 'var(--white)'};">${left !== null ? left : '—'}</div></div>
    </div>
    ${warn ? `<div style="margin-top:1rem;padding:0.65rem 1rem;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:3px;font-size:0.85rem;color:var(--warn);">⚠️ Your subscription expires soon! Renew below to continue without interruption.</div>` : ''}`;
}

function renderPending(pending) {
  const card = document.getElementById('pending-card');
  const planCard = document.getElementById('plan-select-card');
  if (!pending) {
    card.style.display = 'none';
    planCard.style.display = 'block';
    return;
  }
  card.style.display = 'flex';
  document.getElementById('pending-detail').textContent =
    `${pending.plan_name} · ${fmtMoney(pending.amount)} · ${pending.payment_mode} — Submitted ${fmtDateTime(pending.created_at)}`;
  planCard.style.display = 'none';
}

async function loadPlans() {
  try {
    const plans = await api('/api/member/plans');
    const grid  = document.getElementById('plan-grid');
    if (!plans.length) {
      grid.innerHTML = '<div style="color:var(--steel);">No plans available. Contact admin.</div>';
      return;
    }
    grid.innerHTML = plans.map(p => `
      <div class="plan-card" data-id="${p.id}" data-name="${p.name}" data-price="${p.price}" data-days="${p.duration_days}">
        <div class="plan-name">${p.name}</div>
        <div class="plan-price">${fmtMoney(p.price)} <span>/ ${p.duration_days} days</span></div>
        ${p.description ? `<div class="plan-desc">${p.description}</div>` : ''}
      </div>`).join('');

    grid.querySelectorAll('.plan-card').forEach(card => {
      card.addEventListener('click', () => {
        grid.querySelectorAll('.plan-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedPlan = {
          id:    parseInt(card.dataset.id),
          name:  card.dataset.name,
          price: parseFloat(card.dataset.price),
          days:  parseInt(card.dataset.days),
        };
        document.getElementById('payment-mode-section').style.display = 'block';
        updatePaymentSummary();
      });
    });
  } catch(e) {
    toast('Failed to load plans', 'error');
  }
}

function updatePaymentSummary() {
  if (!selectedPlan) return;
  const mode = document.querySelector('input[name="payment_mode"]:checked')?.value || 'cash';
  const activeSub = profileData?.active_subscription;
  let renewNote = '';
  if (activeSub && activeSub.end_date && daysLeft(activeSub.end_date) > 0) {
    renewNote = `<br><span style="color:var(--warn);">⚡ Will activate after current plan ends (${fmtDate(activeSub.end_date)})</span>`;
  }
  document.getElementById('payment-summary').innerHTML = `
    <strong>Plan:</strong> ${selectedPlan.name}<br>
    <strong>Duration:</strong> ${selectedPlan.days} days<br>
    <strong>Amount:</strong> ${fmtMoney(selectedPlan.price)}<br>
    <strong>Payment Mode:</strong> ${mode}
    ${renewNote}`;
}

document.querySelectorAll('input[name="payment_mode"]').forEach(r => {
  r.addEventListener('change', updatePaymentSummary);
});

/* ── Initialize payment ─────────────────────────────────────────────────────── */
document.getElementById('btn-initialize-payment')?.addEventListener('click', () => {
  if (!selectedPlan) return toast('Select a plan first', 'warn');
  const mode = document.querySelector('input[name="payment_mode"]:checked')?.value || 'cash';
  const activeSub = profileData?.active_subscription;
  let renewMsg = '';
  if (activeSub && activeSub.end_date && daysLeft(activeSub.end_date) > 0) {
    renewMsg = `<p style="margin-top:0.75rem;color:var(--warn);font-size:0.85rem;">⚡ This will activate after your current plan expires on <strong>${fmtDate(activeSub.end_date)}</strong>.</p>`;
  }

  document.getElementById('confirm-modal-body').innerHTML = `
    <div style="display:flex;flex-direction:column;gap:0.5rem;">
      <div class="drawer-info-row"><span class="drawer-info-key">Plan</span><span class="drawer-info-val">${selectedPlan.name}</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Duration</span><span class="drawer-info-val">${selectedPlan.days} days</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Amount</span><span class="drawer-info-val" style="color:var(--fire);font-weight:700;">${fmtMoney(selectedPlan.price)}</span></div>
      <div class="drawer-info-row"><span class="drawer-info-key">Payment</span><span class="drawer-info-val">${mode}</span></div>
    </div>
    ${renewMsg}
    <p style="margin-top:1rem;font-size:0.85rem;color:var(--steel);">Your request will be sent to the admin for approval. Subscription activates after approval.</p>`;

  openModal('confirm-modal');
});

document.getElementById('modal-cancel')?.addEventListener('click', () => closeModal('confirm-modal'));

document.getElementById('modal-confirm')?.addEventListener('click', async () => {
  const btn = document.getElementById('modal-confirm');
  btn.classList.add('btn-loading');
  const mode = document.querySelector('input[name="payment_mode"]:checked')?.value || 'cash';
  try {
    const res = await api('/api/member/subscription/request', {
      method: 'POST',
      body: JSON.stringify({ plan_id: selectedPlan.id, payment_mode: mode }),
    });
    closeModal('confirm-modal');
    toast(res.message || 'Payment request sent!');
    selectedPlan = null;
    await loadAll();
  } catch(e) {
    toast(e.message, 'error');
  } finally { btn.classList.remove('btn-loading'); }
});

/* ── Cancel pending ─────────────────────────────────────────────────────────── */
document.getElementById('btn-cancel-pending')?.addEventListener('click', async () => {
  if (!confirm('Cancel your pending payment request?')) return;
  try {
    await api('/api/member/subscription/cancel-pending', { method: 'POST' });
    toast('Request cancelled');
    await loadAll();
  } catch(e) { toast(e.message, 'error'); }
});

/* ── History ────────────────────────────────────────────────────────────────── */
async function loadHistory() {
  try {
    const subs = await api('/api/member/subscriptions');
    const tbody = document.getElementById('sub-history-tbody');
    if (!subs.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="table-empty">No subscription history</td></tr>';
      return;
    }
    tbody.innerHTML = subs.map(s => `<tr>
      <td>${s.plan_name}</td>
      <td style="color:var(--fire);font-weight:600;">${fmtMoney(s.amount)}</td>
      <td>${s.payment_mode}</td>
      <td>${statusBadge(s.status)}</td>
      <td>${fmtDate(s.start_date)}</td>
      <td>${fmtDate(s.end_date)}</td>
      <td style="color:var(--steel);font-size:0.82rem;">${fmtDate(s.created_at)}</td>
    </tr>`).join('');
  } catch {}
}

loadAll();