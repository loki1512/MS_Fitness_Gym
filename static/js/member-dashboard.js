/* Member dashboard */

async function loadProfile() {
  try {
    const data = await api('/api/member/profile');

    // Stats
    document.getElementById('stat-streak').textContent = data.streak || 0;

    const sub = data.active_subscription;
    if (sub) {
      document.getElementById('stat-plan').textContent = sub.plan_name;
      const left = daysLeft(sub.end_date);
      document.getElementById('stat-expiry').textContent = left !== null ? `${left}d` : '—';
      document.getElementById('stat-expiry-sub').textContent = fmtDate(sub.end_date);
      document.getElementById('stat-plan-sub').textContent = sub.payment_mode;
    } else {
      document.getElementById('stat-plan').textContent = 'None';
      document.getElementById('stat-plan-sub').textContent = 'No active plan';
      document.getElementById('stat-expiry').textContent = '—';
    }

    document.querySelectorAll('.stat-card.loading').forEach(c => c.classList.remove('loading'));

    // Subscription status card
    renderSubStatus(data.active_subscription, data.pending_subscription);
  } catch(e) {
    toast('Failed to load profile: ' + e.message, 'error');
  }
}

function renderSubStatus(sub, pending) {
  const body = document.getElementById('sub-status-body');
  if (pending) {
    body.innerHTML = `
      <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
        <span style="font-size:1.5rem;">⏳</span>
        <div>
          <div style="font-weight:700;color:var(--white);">Payment Pending — ${pending.plan_name}</div>
          <div style="font-size:0.85rem;color:var(--steel);">Awaiting admin approval. Requested ${fmtDateTime(pending.created_at)}.</div>
        </div>
      </div>`;
    return;
  }
  if (!sub) {
    body.innerHTML = `
      <div style="text-align:center;padding:1.5rem 0;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🏋️</div>
        <div style="color:var(--steel);margin-bottom:1rem;">No active subscription</div>
        <a href="/member/subscription" class="btn btn-fire">Choose a Plan</a>
      </div>`;
    return;
  }
  const left = daysLeft(sub.end_date);
  const urgency = left !== null && left <= 7 ? 'color:var(--warn);font-weight:700;' : 'color:var(--steel);';
  body.innerHTML = `
    <div class="drawer-info-row"><span class="drawer-info-key">Plan</span><span class="drawer-info-val">${sub.plan_name}</span></div>
    <div class="drawer-info-row"><span class="drawer-info-key">Start</span><span class="drawer-info-val">${fmtDate(sub.start_date)}</span></div>
    <div class="drawer-info-row"><span class="drawer-info-key">Expires</span><span class="drawer-info-val">${fmtDate(sub.end_date)}</span></div>
    <div class="drawer-info-row"><span class="drawer-info-key">Days Remaining</span><span class="drawer-info-val" style="${urgency}">${left !== null ? left + ' days' : '—'}</span></div>
    <div class="drawer-info-row"><span class="drawer-info-key">Status</span><span class="drawer-info-val">${statusBadge(sub.status)}</span></div>`;
}

/* ── Attendance ─────────────────────────────────────────────────────────────── */
async function loadAttendance() {
  try {
    const records = await api('/api/member/attendance/history');
    const tbody = document.getElementById('attendance-tbody');
    if (!records.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-empty">No visits yet</td></tr>';
      return;
    }
    tbody.innerHTML = records.map(r => {
      const cin  = r.check_in_time  ? new Date(r.check_in_time)  : null;
      const cout = r.check_out_time ? new Date(r.check_out_time) : null;
      let dur = '—';
      if (cin && cout) {
        const mins = Math.round((cout - cin) / 60000);
        dur = mins < 60 ? `${mins}m` : `${Math.floor(mins/60)}h ${mins%60}m`;
      }
      return `<tr>
        <td>${cin ? cin.toLocaleDateString('en-IN') : '—'}</td>
        <td>${cin ? cin.toLocaleTimeString('en-IN', {hour:'2-digit',minute:'2-digit'}) : '—'}</td>
        <td>${cout ? cout.toLocaleTimeString('en-IN', {hour:'2-digit',minute:'2-digit'}) : '<span style="color:var(--warn)">Active</span>'}</td>
        <td>${dur}</td>
      </tr>`;
    }).join('');
  } catch {}
}

document.getElementById('btn-checkin')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-checkin');
  btn.classList.add('btn-loading');
  try {
    await api('/api/member/attendance/checkin', { method: 'POST' });
    toast('Checked in! 💪');
    document.getElementById('attendance-status').textContent = 'You are checked in.';
    loadAttendance();
  } catch(e) {
    toast(e.message, 'error');
  } finally { btn.classList.remove('btn-loading'); }
});

document.getElementById('btn-checkout')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-checkout');
  btn.classList.add('btn-loading');
  try {
    await api('/api/member/attendance/checkout', { method: 'POST' });
    toast('Checked out! See you next time 🔥');
    document.getElementById('attendance-status').textContent = '';
    loadProfile();
    loadAttendance();
  } catch(e) {
    toast(e.message, 'error');
  } finally { btn.classList.remove('btn-loading'); }
});

loadProfile();
loadAttendance();