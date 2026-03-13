/* Member profile page */

let profileData = null;

// ── Load & render ─────────────────────────────────────────────────────────────

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
  const initials = (d.name || d.username || '?').trim().split(' ')
    .slice(0, 2).map(w => w[0].toUpperCase()).join('');
  document.getElementById('profile-avatar').textContent   = initials;
  document.getElementById('profile-name').textContent     = d.name || d.username;
  document.getElementById('profile-username').textContent = '@' + d.username;
  document.getElementById('profile-joined').textContent   = 'Joined ' + fmtDate(d.join_date);
  document.getElementById('profile-streak').textContent   = (d.streak || 0) + '🔥';
}

function infoRow(key, val, emptyText = '—') {
  const empty = !val && val !== 0;
  return `<div class="info-row">
    <span class="info-key">${key}</span>
    <span class="info-val ${empty ? 'info-val-empty' : ''}">${empty ? emptyText : val}</span>
  </div>`;
}

function renderPersonalInfo(d) {
  const body = document.getElementById('personal-info-body');
  body.innerHTML = '<div class="info-rows-wrap">' +
    infoRow('Full Name',   d.name) +
    infoRow('Username',    '@' + d.username) +
    infoRow('Phone',       d.phone) +
    infoRow('Email',       d.email, 'Not set') +
    infoRow('Profession',  d.profession, 'Not set') +
    infoRow('Date of Birth', d.dob ? fmtDate(d.dob) : '', 'Not set') +
    infoRow('Member Since', fmtDate(d.join_date));
}

function renderPhysicalStats(d) {
  const body = document.getElementById('physical-stats-body');
  const h = d.height_cm;
  const w = d.weight_kg;

  let bmiHtml = '';
  if (h && w) {
    const bmi   = w / ((h / 100) ** 2);
    const bmiR  = bmi.toFixed(1);
    let cat = 'Normal'; let cls = 'bmi-normal';
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

  body.innerHTML = `
    <div class="phys-grid">
      <div class="phys-tile">
        <div class="phys-tile-val">${h ? h : '—'}<span class="phys-tile-unit">${h ? 'cm' : ''}</span></div>
        <div class="phys-tile-label">Height</div>
      </div>
      <div class="phys-tile">
        <div class="phys-tile-val">${w ? w : '—'}<span class="phys-tile-unit">${w ? 'kg' : ''}</span></div>
        <div class="phys-tile-label">Weight</div>
      </div>
    </div>
    ${bmiHtml || `<div style="color:var(--steel);font-size:0.85rem;margin-top:1rem;text-align:center;">Add height &amp; weight to see BMI</div>`}`;
}

function renderSubscription(sub) {
  const body = document.getElementById('profile-sub-body');
  if (!sub) {
    body.innerHTML = `<div style="text-align:center;padding:1.5rem 0;">
      <div style="font-size:2rem;margin-bottom:0.5rem;">🏋️</div>
      <div style="color:var(--steel);margin-bottom:1rem;font-size:0.9rem;">No active subscription</div>
      <a href="/member/subscription" class="btn btn-fire btn-sm">Browse Plans</a>
    </div>`;
    return;
  }
  const left = daysLeft(sub.end_date);
  const warn = left !== null && left <= 7;
  body.innerHTML = `<div class="sub-summary-grid">
    <div class="sub-stat">
      <div class="sub-stat-val" style="font-size:1.1rem;letter-spacing:0.01em;">${sub.plan_name}</div>
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
  ${warn ? `<div style="margin-top:1rem;padding:0.65rem 1rem;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:3px;font-size:0.85rem;color:var(--warn);">⚠️ Expiring soon — renew to keep access.</div>` : ''}`;
}

// ── EDIT PROFILE MODAL ────────────────────────────────────────────────────────

function openEditModal() {
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
}

function closeEditModal() { closeModal('edit-profile-modal'); }

document.getElementById('btn-edit-profile')?.addEventListener('click', openEditModal);
document.getElementById('edit-profile-close')?.addEventListener('click', closeEditModal);
document.getElementById('edit-profile-cancel')?.addEventListener('click', closeEditModal);

document.getElementById('edit-profile-save')?.addEventListener('click', async () => {
  const btn   = document.getElementById('edit-profile-save');
  const errEl = document.getElementById('edit-profile-error');
  errEl.textContent = '';

  const name  = document.getElementById('edit-name').value.trim();
  const phone = document.getElementById('edit-phone').value.trim();
  if (!name)  { errEl.textContent = 'Name is required.'; return; }
  if (!phone) { errEl.textContent = 'Phone is required.'; return; }

  const payload = {
    name,
    phone,
    email:      document.getElementById('edit-email').value.trim() || null,
    profession: document.getElementById('edit-profession').value.trim() || null,
    dob:        document.getElementById('edit-dob').value || null,
    height_cm:  parseFloatOrNull(document.getElementById('edit-height').value),
    weight_kg:  parseFloatOrNull(document.getElementById('edit-weight').value),
  };

  btn.classList.add('btn-loading');
  try {
    await api('/api/member/profile', { method: 'PATCH', body: JSON.stringify(payload) });
    closeEditModal();
    toast('Profile updated!');
    await loadProfile();
  } catch (e) {
    errEl.textContent = e.message;
  } finally {
    btn.classList.remove('btn-loading');
  }
});

// ── CHANGE PASSWORD MODAL ─────────────────────────────────────────────────────

function openPwModal() {
  document.getElementById('pw-current').value  = '';
  document.getElementById('pw-new').value      = '';
  document.getElementById('pw-confirm').value  = '';
  document.getElementById('err-pw-current').textContent = '';
  document.getElementById('err-pw-new').textContent     = '';
  document.getElementById('err-pw-confirm').textContent = '';
  document.getElementById('err-pw-global').textContent  = '';
  document.getElementById('pw-strength-fill').className = 'pw-fill';
  document.getElementById('pw-strength-label').textContent = 'Enter a new password';
  openModal('change-pw-modal');
}

function closePwModal() { closeModal('change-pw-modal'); }

document.getElementById('btn-change-pw')?.addEventListener('click', openPwModal);
document.getElementById('change-pw-close')?.addEventListener('click', closePwModal);
document.getElementById('change-pw-cancel')?.addEventListener('click', closePwModal);

// Password strength meter
document.getElementById('pw-new')?.addEventListener('input', function () {
  const { cls, label } = measurePwStrength(this.value);
  const fill  = document.getElementById('pw-strength-fill');
  const lbl   = document.getElementById('pw-strength-label');
  fill.className = 'pw-fill' + (cls ? ' ' + cls : '');
  lbl.textContent = label;
  // Live confirm check
  const confirm = document.getElementById('pw-confirm').value;
  if (confirm) checkConfirmMatch();
});

document.getElementById('pw-confirm')?.addEventListener('input', checkConfirmMatch);

function checkConfirmMatch() {
  const nv = document.getElementById('pw-new').value;
  const cv = document.getElementById('pw-confirm').value;
  const el = document.getElementById('err-pw-confirm');
  if (!cv) { el.textContent = ''; return; }
  el.textContent = nv === cv ? '' : 'Passwords do not match.';
}

function measurePwStrength(pw) {
  if (!pw) return { cls: '', label: 'Enter a new password' };
  let score = 0;
  if (pw.length >= 8)          score++;
  if (pw.length >= 12)         score++;
  if (/[A-Z]/.test(pw))        score++;
  if (/[0-9]/.test(pw))        score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  if (score <= 1) return { cls: 'weak',   label: 'Weak — add numbers or symbols' };
  if (score <= 3) return { cls: 'fair',   label: 'Fair — getting better' };
  return               { cls: 'strong', label: 'Strong password' };
}

document.getElementById('change-pw-save')?.addEventListener('click', async () => {
  const btn     = document.getElementById('change-pw-save');
  const current = document.getElementById('pw-current').value;
  const newPw   = document.getElementById('pw-new').value;
  const confirm = document.getElementById('pw-confirm').value;

  // Reset errors
  ['err-pw-current','err-pw-new','err-pw-confirm','err-pw-global'].forEach(id => {
    document.getElementById(id).textContent = '';
  });

  let valid = true;
  if (!current) {
    document.getElementById('err-pw-current').textContent = 'Current password is required.';
    valid = false;
  }
  if (!newPw || newPw.length < 8) {
    document.getElementById('err-pw-new').textContent = 'New password must be at least 8 characters.';
    valid = false;
  }
  if (!confirm) {
    document.getElementById('err-pw-confirm').textContent = 'Please confirm your new password.';
    valid = false;
  } else if (newPw !== confirm) {
    document.getElementById('err-pw-confirm').textContent = 'Passwords do not match.';
    valid = false;
  }
  if (!valid) return;

  btn.classList.add('btn-loading');
  try {
    await api('/api/member/profile/update_password', {
      method: 'POST',
      body: JSON.stringify({ current_password: current, new_password: newPw }),
    });
    closePwModal();
    toast('Password updated successfully!');
  } catch (e) {
    document.getElementById('err-pw-global').textContent = e.message;
  } finally {
    btn.classList.remove('btn-loading');
  }
});

// ── Password visibility toggles ───────────────────────────────────────────────
document.querySelectorAll('.pw-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const inp = document.getElementById(btn.dataset.target);
    if (!inp) return;
    inp.type = inp.type === 'password' ? 'text' : 'password';
    btn.style.color = inp.type === 'text' ? 'var(--fire)' : '';
  });
});

// ── Utility ───────────────────────────────────────────────────────────────────
function parseFloatOrNull(val) {
  const n = parseFloat(val);
  return isNaN(n) ? null : n;
}

// ── Init ──────────────────────────────────────────────────────────────────────
loadProfile();