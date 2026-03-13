/* Admin members page */

let currentPage = 1;
let searchTimer = null;

async function loadMembers(page = 1, q = '') {
  try {
    const data = await api(`/api/admin/members?page=${page}&per_page=20&q=${encodeURIComponent(q)}`);
    const tbody = document.getElementById('members-tbody');

    if (!data.members.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No members found</td></tr>`;
    } else {
      tbody.innerHTML = data.members.map(m => {
        const sub  = m.active_subscription;
        let subCell = '<span style="color:var(--steel);">None</span>';
        if (m.has_pending) {
          subCell = `<span class="badge badge-pending">Pending Approval</span>`;
        } else if (sub) {
          const left = daysLeft(sub.end_date);
          const warn = left !== null && left <= 7;
          subCell = `${sub.plan_name} <span style="color:${warn ? 'var(--warn)' : 'var(--steel)'};font-size:0.78rem;">(${left}d left)</span>`;
        }
        return `<tr>
          <td><strong style="color:var(--white);">${m.name}</strong></td>
          <td style="color:var(--steel);">@${m.username}</td>
          <td>${m.phone}</td>
          <td style="font-size:0.82rem;color:var(--steel);">${fmtDate(m.join_date)}</td>
          <td style="color:var(--fire);font-weight:700;">${m.streak}🔥</td>
          <td>${subCell}</td>
          <td>
            <button class="btn btn-ghost btn-sm" onclick="openMemberDrawer(${m.user_id})">View</button>
          </td>
        </tr>`;
      }).join('');
    }

    renderPagination(data.page, data.pages, page);
    currentPage = page;
  } catch(e) { toast('Failed to load members', 'error'); }
}

function renderPagination(current, total, _) {
  const el = document.getElementById('members-pagination');
  if (!el || total <= 1) { if(el) el.innerHTML = ''; return; }
  let html = `<button class="page-btn" ${current===1?'disabled':''} onclick="loadMembers(${current-1},getSearch())">‹</button>`;
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || Math.abs(i-current) <= 1) {
      html += `<button class="page-btn ${i===current?'active':''}" onclick="loadMembers(${i},getSearch())">${i}</button>`;
    } else if (Math.abs(i-current) === 2) {
      html += `<span style="color:var(--steel);padding:0 4px;">…</span>`;
    }
  }
  html += `<button class="page-btn" ${current===total?'disabled':''} onclick="loadMembers(${current+1},getSearch())">›</button>`;
  el.innerHTML = html;
}

function getSearch() { return document.getElementById('member-search').value.trim(); }

document.getElementById('member-search')?.addEventListener('input', function() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadMembers(1, this.value.trim()), 350);
});

/* ── Member drawer ──────────────────────────────────────────────────────────── */
let currentDrawerMemberId = null;
let currentDrawerMemberName = '';

async function openMemberDrawer(memberId) {
  currentDrawerMemberId = memberId;
  document.getElementById('drawer-title').textContent = 'Loading…';
  document.getElementById('drawer-body').innerHTML = '<div class="skeleton-block"></div>';
  document.getElementById('member-drawer').classList.add('open');
  document.getElementById('member-drawer-backdrop').classList.add('open');

  try {
    const m = await api(`/api/admin/members/${memberId}`);
    document.getElementById('drawer-title').textContent = m.name;
    currentDrawerMemberName = m.name;

    const activeSub = m.subscriptions.find(s => s.status === 'active' && s.end_date >= new Date().toISOString().split('T')[0]);

    document.getElementById('drawer-body').innerHTML = `
      <div class="drawer-section">
        <div class="drawer-section-title">Account</div>
        <div class="drawer-info-row"><span class="drawer-info-key">Username</span><span class="drawer-info-val">@${m.username}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Phone</span><span class="drawer-info-val">${m.phone || '—'}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Email</span><span class="drawer-info-val">${m.email || '—'}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Joined</span><span class="drawer-info-val">${fmtDate(m.join_date)}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Streak</span><span class="drawer-info-val">${m.streak}🔥</span></div>
      </div>

      <div class="drawer-section">
        <div class="drawer-section-title">Profile</div>
        <div class="drawer-info-row"><span class="drawer-info-key">Profession</span><span class="drawer-info-val">${m.profession || '—'}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Height</span><span class="drawer-info-val">${m.height_cm ? m.height_cm + ' cm' : '—'}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">Weight</span><span class="drawer-info-val">${m.weight_kg ? m.weight_kg + ' kg' : '—'}</span></div>
        <div class="drawer-info-row"><span class="drawer-info-key">DOB</span><span class="drawer-info-val">${fmtDate(m.dob)}</span></div>
      </div>

      <div class="drawer-section">
        <div class="drawer-section-title">Current Subscription</div>
        ${activeSub ? `
          <div class="drawer-info-row"><span class="drawer-info-key">Plan</span><span class="drawer-info-val">${activeSub.plan_name}</span></div>
          <div class="drawer-info-row"><span class="drawer-info-key">Start</span><span class="drawer-info-val">${fmtDate(activeSub.start_date)}</span></div>
          <div class="drawer-info-row"><span class="drawer-info-key">Expires</span><span class="drawer-info-val">${fmtDate(activeSub.end_date)}</span></div>
          <div class="drawer-info-row"><span class="drawer-info-key">Days Left</span><span class="drawer-info-val">${daysLeft(activeSub.end_date)}d</span></div>
        ` : '<div style="color:var(--steel);font-size:0.88rem;padding:0.5rem 0;">No active subscription</div>'}
      </div>

      <div class="drawer-section">
        <div class="drawer-section-title">Subscription History</div>
        ${m.subscriptions.length ? `
          <div class="table-wrap" style="margin:-0.25rem;">
            <table class="data-table" style="font-size:0.82rem;">
              <thead><tr><th>Plan</th><th>Amount</th><th>Status</th><th>End</th></tr></thead>
              <tbody>
                ${m.subscriptions.map(s => `<tr>
                  <td>${s.plan_name}</td>
                  <td style="color:var(--fire);">${fmtMoney(s.amount)}</td>
                  <td>${statusBadge(s.status)}</td>
                  <td>${fmtDate(s.end_date)}</td>
                </tr>`).join('')}
              </tbody>
            </table>
          </div>` : '<div style="color:var(--steel);font-size:0.88rem;">No history</div>'}
      </div>

      <div class="drawer-section">
        <div class="drawer-section-title" style="color:var(--danger);">Admin Actions</div>
        <button class="btn btn-danger btn-sm" id="drawer-reset-pw-btn" style="width:100%;margin-top:0.25rem;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;display:inline;vertical-align:middle;margin-right:6px;"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          Reset Password
        </button>
      </div>`;

    document.getElementById('drawer-reset-pw-btn')?.addEventListener('click', () => {
      openResetPwModal(currentDrawerMemberId, currentDrawerMemberName);
    });

  } catch(e) {
    document.getElementById('drawer-body').innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
}

function closeMemberDrawer() {
  document.getElementById('member-drawer').classList.remove('open');
  document.getElementById('member-drawer-backdrop').classList.remove('open');
}

document.getElementById('drawer-close')?.addEventListener('click', closeMemberDrawer);
document.getElementById('member-drawer-backdrop')?.addEventListener('click', closeMemberDrawer);

/* ── Add member modal ───────────────────────────────────────────────────────── */
document.getElementById('btn-add-member')?.addEventListener('click', () => openModal('add-member-modal'));
document.getElementById('add-member-cancel')?.addEventListener('click', () => closeModal('add-member-modal'));

document.getElementById('add-member-confirm')?.addEventListener('click', async () => {
  const btn     = document.getElementById('add-member-confirm');
  const errEl   = document.getElementById('add-member-error');
  const username= document.getElementById('new-username').value.trim();
  const phone   = document.getElementById('new-phone').value.trim();

  errEl.textContent = '';
  if (!username || !phone) { errEl.textContent = 'Username and phone are required.'; return; }

  btn.classList.add('btn-loading');
  try {
    await api('/api/admin/members', {
      method: 'POST',
      body: JSON.stringify({
        username, phone,
        name:      document.getElementById('new-name').value.trim() || username,
        email:     document.getElementById('new-email').value.trim() || null,
        password:  document.getElementById('new-password').value || 'ms@123',
        profession:document.getElementById('new-profession').value.trim() || null,
      }),
    });
    closeModal('add-member-modal');
    toast('Member created!');
    loadMembers(1, getSearch());
  } catch(e) { errEl.textContent = e.message; }
  finally { btn.classList.remove('btn-loading'); }
});

window.openMemberDrawer = openMemberDrawer;
window.loadMembers = loadMembers;
window.getSearch = getSearch;

/* ── Reset password modal (admin only) ──────────────────────────────────────── */
function openResetPwModal(memberId, memberName) {
  document.getElementById('reset-pw-new').value     = '';
  document.getElementById('reset-pw-confirm').value = '';
  document.getElementById('reset-pw-new').type      = 'password';
  document.getElementById('reset-pw-confirm').type  = 'password';
  ['err-reset-pw-new','err-reset-pw-confirm','err-reset-pw-global'].forEach(id =>
    document.getElementById(id).textContent = '');
  document.getElementById('reset-pw-strength-fill').className    = 'pw-fill';
  document.getElementById('reset-pw-strength-label').textContent = 'Enter a new password';
  document.getElementById('reset-pw-member-name').textContent    = memberName;
  document.getElementById('reset-pw-save').dataset.memberId      = memberId;
  openModal('reset-pw-modal');
}

document.getElementById('reset-pw-close')?.addEventListener('click',  () => closeModal('reset-pw-modal'));
document.getElementById('reset-pw-cancel')?.addEventListener('click', () => closeModal('reset-pw-modal'));

document.getElementById('reset-pw-new')?.addEventListener('input', function () {
  updateStrengthMeter(this.value, 'reset-pw-strength-fill', 'reset-pw-strength-label');
  if (document.getElementById('reset-pw-confirm').value)
    liveConfirmCheck('reset-pw-new', 'reset-pw-confirm', 'err-reset-pw-confirm');
});
document.getElementById('reset-pw-confirm')?.addEventListener('input', () =>
  liveConfirmCheck('reset-pw-new', 'reset-pw-confirm', 'err-reset-pw-confirm'));

document.getElementById('reset-pw-save')?.addEventListener('click', async () => {
  const btn     = document.getElementById('reset-pw-save');
  const memberId= btn.dataset.memberId;
  const newPw   = document.getElementById('reset-pw-new').value;
  const confirm = document.getElementById('reset-pw-confirm').value;

  ['err-reset-pw-new','err-reset-pw-confirm','err-reset-pw-global'].forEach(id =>
    document.getElementById(id).textContent = '');

  let valid = true;
  if (!newPw || newPw.length < 8) {
    document.getElementById('err-reset-pw-new').textContent = 'Minimum 8 characters.';
    valid = false;
  }
  if (!confirm) {
    document.getElementById('err-reset-pw-confirm').textContent = 'Please confirm the password.';
    valid = false;
  } else if (newPw !== confirm) {
    document.getElementById('err-reset-pw-confirm').textContent = 'Passwords do not match.';
    valid = false;
  }
  if (!valid) return;

  btn.classList.add('btn-loading');
  try {
    await api(`/api/admin/members/${memberId}/reset_password`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPw, confirm_password: confirm }),
    });
    closeModal('reset-pw-modal');
    toast('Password reset successfully!');
  } catch(e) {
    document.getElementById('err-reset-pw-global').textContent = e.message;
  } finally {
    btn.classList.remove('btn-loading');
  }
});

/* ── Shared password helpers ─────────────────────────────────────────────────── */
function updateStrengthMeter(pw, fillId, labelId) {
  const fill = document.getElementById(fillId);
  const lbl  = document.getElementById(labelId);
  if (!pw) { fill.className = 'pw-fill'; lbl.textContent = 'Enter a new password'; return; }
  let score = 0;
  if (pw.length >= 8)          score++;
  if (pw.length >= 12)         score++;
  if (/[A-Z]/.test(pw))        score++;
  if (/[0-9]/.test(pw))        score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  if      (score <= 1) { fill.className = 'pw-fill weak';   lbl.textContent = 'Weak — add numbers or symbols'; }
  else if (score <= 3) { fill.className = 'pw-fill fair';   lbl.textContent = 'Fair — getting better'; }
  else                 { fill.className = 'pw-fill strong'; lbl.textContent = 'Strong'; }
}

function liveConfirmCheck(newId, confirmId, errId) {
  const match = document.getElementById(newId).value === document.getElementById(confirmId).value;
  document.getElementById(errId).textContent = match ? '' : 'Passwords do not match.';
}


loadMembers(1);