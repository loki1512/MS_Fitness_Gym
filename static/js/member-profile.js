/* ── Member profile page ─────────────────────────────────────────────────── */

let profileData = null;

// ── Load & render ─────────────────────────────────────────────────────────

async function loadProfile() {
  try {
    profileData = await api('/api/member/profile');
    renderHero(profileData);
    renderPersonalInfo(profileData);
    renderPhysicalStats(profileData);
    renderSubscription(profileData.active_subscription);
  } catch (e) {
    toast('Failed to load profile: ' + e.message, 'error');
  }
}

function renderHero(d) {
  const initials = (d.name || d.username || '?').trim()
    .split(' ').slice(0, 2).map(w => w[0].toUpperCase()).join('');
  document.getElementById('profile-avatar').textContent   = initials;
  document.getElementById('profile-name').textContent     = d.name || d.username;
  document.getElementById('profile-username').textContent = '@' + d.username;
  document.getElementById('profile-joined').textContent   = 'Joined ' + fmtDate(d.join_date);
  document.getElementById('profile-streak').textContent   = (d.streak || 0) + '🔥';
}

function infoRow(key, val, emptyText = '—') {
  const empty = val === null || val === undefined || val === '';
  return `<div class="info-row">
    <span class="info-key">${key}</span>
    <span class="info-val${empty ? ' info-val-empty' : ''}">${empty ? emptyText : val}</span>
  </div>`;
}

function renderPersonalInfo(d) {
  document.getElementById('personal-info-body').innerHTML =
    infoRow('Full Name',     d.name) +
    infoRow('Username',      '@' + d.username) +
    infoRow('Phone',         d.phone) +
    infoRow('Email',         d.email,      'Not set') +
    infoRow('Profession',    d.profession, 'Not set') +
    infoRow('Date of Birth', d.dob ? fmtDate(d.dob) : '', 'Not set') +
    infoRow('Member Since',  fmtDate(d.join_date));
}

function renderPhysicalStats(d) {
  const h = d.height_cm, w = d.weight_kg;
  let bmiHtml = '';
  if (h && w) {
    const bmi  = w / ((h / 100) ** 2);
    const bmiR = bmi.toFixed(1);
    let cat = 'Normal', cls = 'bmi-normal';
    if      (bmi < 18.5) { cat = 'Underweight'; cls = 'bmi-underweight'; }
    else if (bmi < 25)   { cat = 'Normal';       cls = 'bmi-normal'; }
    else if (bmi < 30)   { cat = 'Overweight';   cls = 'bmi-overweight'; }
    else                 { cat = 'Obese';         cls = 'bmi-obese'; }
    bmiHtml = `<div class="bmi-wrap">
      <span class="bmi-label">BMI</span>
      <span class="bmi-val">${bmiR}</span>
      <span class="bmi-cat ${cls}">${cat}</span>
    </div>`;
  }
  document.getElementById('physical-stats-body').innerHTML = `
    <div class="phys-grid">
      <div class="phys-tile">
        <div class="phys-tile-val">${h || '—'}<span class="phys-tile-unit">${h ? 'cm' : ''}</span></div>
        <div class="phys-tile-label">Height</div>
      </div>
      <div class="phys-tile">
        <div class="phys-tile-val">${w || '—'}<span class="phys-tile-unit">${w ? 'kg' : ''}</span></div>
        <div class="phys-tile-label">Weight</div>
      </div>
    </div>
    ${bmiHtml || '<div class="phys-empty">Add height &amp; weight to see BMI</div>'}`;
}

function renderSubscription(sub) {
  const body = document.getElementById('profile-sub-body');
  if (!sub) {
    body.innerHTML = `<div class="sub-empty">
      <div class="sub-empty-icon">🏋️</div>
      <div style="color:var(--steel);margin-bottom:1rem;">No active subscription</div>
      <a href="/member/subscription" class="btn btn-fire btn-sm">Browse Plans</a>
    </div>`;
    return;
  }
  const left = daysLeft(sub.end_date);
  const warn = left !== null && left <= 7;
  body.innerHTML = `
    <div class="sub-summary-grid">
      <div class="sub-stat">
        <div class="sub-stat-val" style="font-size:1.1rem;">${sub.plan_name}</div>
        <div class="sub-stat-label">Plan</div>
      </div>
      <div class="sub-stat">
        <div class="sub-stat-val" style="color:var(--fire);">${fmtMoney(sub.amount)}</div>
        <div class="sub-stat-label">Paid</div>
      </div>
      <div class="sub-stat">
        <div class="sub-stat-val" style="color:${warn ? 'var(--warn)' : 'var(--white)'};">${left !== null ? left : '—'}</div>
        <div class="sub-stat-label">Days Left</div>
      </div>
      <div class="sub-stat">
        <div class="sub-stat-val" style="font-size:1rem;">${fmtDate(sub.end_date)}</div>
        <div class="sub-stat-label">Expires</div>
      </div>
    </div>
    ${warn ? `<div class="sub-warn-banner">⚠️ Expiring soon — renew to keep access.</div>` : ''}`;
}


// ── EDIT PROFILE MODAL ────────────────────────────────────────────────────

document.getElementById('btn-edit-profile')?.addEventListener('click', () => {
  if (!profileData) return;
  document.getElementById('edit-name').value       = profileData.name || '';
  document.getElementById('edit-phone').value      = profileData.phone || '';
  document.getElementById('edit-email').value      = profileData.email || '';
  document.getElementById('edit-profession').value = profileData.profession || '';
  document.getElementById('edit-height').value     = profileData.height_cm || '';
  document.getElementById('edit-weight').value     = profileData.weight_kg || '';
  document.getElementById('edit-dob').value        = profileData.dob || '';
  document.getElementById('edit-dob').max          = new Date().toISOString().split('T')[0];
  document.getElementById('edit-profile-error').textContent = '';
  openModal('edit-profile-modal');
});

document.getElementById('edit-profile-close')?.addEventListener('click',  () => closeModal('edit-profile-modal'));
document.getElementById('edit-profile-cancel')?.addEventListener('click', () => closeModal('edit-profile-modal'));

document.getElementById('edit-profile-save')?.addEventListener('click', async () => {
  const btn   = document.getElementById('edit-profile-save');
  const errEl = document.getElementById('edit-profile-error');
  errEl.textContent = '';

  const name  = document.getElementById('edit-name').value.trim();
  const phone = document.getElementById('edit-phone').value.trim();
  if (!name)  { errEl.textContent = 'Name is required.'; return; }
  if (!phone) { errEl.textContent = 'Phone is required.'; return; }

  btn.classList.add('btn-loading');
  try {
    await api('/api/member/profile', {
      method: 'PATCH',
      body: JSON.stringify({
        name, phone,
        email:      document.getElementById('edit-email').value.trim() || null,
        profession: document.getElementById('edit-profession').value.trim() || null,
        dob:        document.getElementById('edit-dob').value || null,
        height_cm:  parseFloatOrNull(document.getElementById('edit-height').value),
        weight_kg:  parseFloatOrNull(document.getElementById('edit-weight').value),
      }),
    });
    closeModal('edit-profile-modal');
    toast('Profile updated!');
    await loadProfile();
  } catch (e) {
    errEl.textContent = e.message;
  } finally {
    btn.classList.remove('btn-loading');
  }
});


// ── CHANGE PASSWORD MODAL (needs current) ─────────────────────────────────

function openChangePwModal() {
  ['pw-current','pw-new','pw-confirm'].forEach(id => {
    document.getElementById(id).value = '';
    document.getElementById(id).type  = 'password';
  });
  ['err-pw-current','err-pw-new','err-pw-confirm','err-pw-global'].forEach(id =>
    document.getElementById(id).textContent = '');
  document.getElementById('pw-strength-fill').className  = 'pw-fill';
  document.getElementById('pw-strength-label').textContent = 'Enter a new password';
  openModal('change-pw-modal');
}

document.getElementById('btn-change-pw')?.addEventListener('click', openChangePwModal);
document.getElementById('change-pw-close')?.addEventListener('click',  () => closeModal('change-pw-modal'));
document.getElementById('change-pw-cancel')?.addEventListener('click', () => closeModal('change-pw-modal'));



document.getElementById('pw-new')?.addEventListener('input', function () {
  updateStrengthMeter(this.value, 'pw-strength-fill', 'pw-strength-label');
  if (document.getElementById('pw-confirm').value) liveConfirmCheck('pw-new', 'pw-confirm', 'err-pw-confirm');
});
document.getElementById('pw-confirm')?.addEventListener('input', () =>
  liveConfirmCheck('pw-new', 'pw-confirm', 'err-pw-confirm'));

document.getElementById('change-pw-save')?.addEventListener('click', async () => {
  const btn     = document.getElementById('change-pw-save');
  const current = document.getElementById('pw-current').value;
  const newPw   = document.getElementById('pw-new').value;
  const confirm = document.getElementById('pw-confirm').value;

  clearPwErrors(['err-pw-current','err-pw-new','err-pw-confirm','err-pw-global']);

  let valid = true;
  if (!current) { document.getElementById('err-pw-current').textContent = 'Current password is required.'; valid = false; }
  if (!newPw || newPw.length < 8) { document.getElementById('err-pw-new').textContent = 'Minimum 8 characters.'; valid = false; }
  if (!confirm) { document.getElementById('err-pw-confirm').textContent = 'Please confirm your new password.'; valid = false; }
  else if (newPw !== confirm) { document.getElementById('err-pw-confirm').textContent = 'Passwords do not match.'; valid = false; }
  if (!valid) return;

  btn.classList.add('btn-loading');
  try {
    await api('/api/member/profile/update_password', {
      method: 'POST',
      body: JSON.stringify({ current_password: current, new_password: newPw }),
    });
    closeModal('change-pw-modal');
    toast('Password updated successfully!');
  } catch (e) {
    document.getElementById('err-pw-global').textContent = e.message;
  } finally {
    btn.classList.remove('btn-loading');
  }
});


// ── Password visibility toggles ───────────────────────────────────────────

document.querySelectorAll('.pw-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const inp = document.getElementById(btn.dataset.target);
    if (!inp) return;
    inp.type = inp.type === 'password' ? 'text' : 'password';
    btn.style.color = inp.type === 'text' ? 'var(--fire)' : '';
  });
});


// ── Shared helpers ────────────────────────────────────────────────────────

function updateStrengthMeter(pw, fillId, labelId) {
  const fill  = document.getElementById(fillId);
  const label = document.getElementById(labelId);
  if (!pw) { fill.className = 'pw-fill'; label.textContent = 'Enter a new password'; return; }
  let score = 0;
  if (pw.length >= 8)          score++;
  if (pw.length >= 12)         score++;
  if (/[A-Z]/.test(pw))        score++;
  if (/[0-9]/.test(pw))        score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  if (score <= 1) { fill.className = 'pw-fill weak';   label.textContent = 'Weak — add numbers or symbols'; }
  else if (score <= 3) { fill.className = 'pw-fill fair';   label.textContent = 'Fair — getting better'; }
  else             { fill.className = 'pw-fill strong'; label.textContent = 'Strong'; }
}

function liveConfirmCheck(newId, confirmId, errId) {
  const match = document.getElementById(newId).value === document.getElementById(confirmId).value;
  document.getElementById(errId).textContent = match ? '' : 'Passwords do not match.';
}

function clearPwErrors(ids) {
  ids.forEach(id => document.getElementById(id).textContent = '');
}

function parseFloatOrNull(val) {
  const n = parseFloat(val);
  return isNaN(n) ? null : n;
}

// ── Init ──────────────────────────────────────────────────────────────────
loadProfile();