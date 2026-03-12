/**
 * MS Fitness – Registration JS
 * Two-stage form: Stage 1 (account) → Stage 2 (profile) → POST /api/register → Success
 */

// ── State ────────────────────────────────────────────────────────────────────
const formData = {};        // accumulated data across both stages

// ── Element refs ─────────────────────────────────────────────────────────────
const stage1El      = document.getElementById('stage-1');
const stage2El      = document.getElementById('stage-2');
const successEl     = document.getElementById('stage-success');
const form1         = document.getElementById('form-stage-1');
const form2         = document.getElementById('form-stage-2');
const btnBack       = document.getElementById('btn-back');
const btnSubmit     = document.getElementById('btn-submit');
const apiErrorEl    = document.getElementById('api-error');
const bgNumber      = document.getElementById('bg-number');
const dot1          = document.getElementById('dot-1');
const dot2          = document.getElementById('dot-2');
const stepConnector = document.querySelector('.step-connector');

// ── Helpers ───────────────────────────────────────────────────────────────────
function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.textContent = msg;
}
function clearError(id) {
  const el = document.getElementById(id);
  if (el) el.textContent = '';
}
function markInput(input, valid) {
  input.classList.toggle('error', !valid);
  input.classList.toggle('valid', valid);
}
function setApiError(msg) {
  if (!msg) {
    apiErrorEl.textContent = '';
    apiErrorEl.classList.remove('visible');
    return;
  }
  apiErrorEl.textContent = msg;
  apiErrorEl.classList.add('visible');
  // Re-trigger shake animation
  apiErrorEl.style.animation = 'none';
  void apiErrorEl.offsetWidth;
  apiErrorEl.style.animation = '';
}

function transitionTo(fromEl, toEl, dir = 'forward') {
  fromEl.style.animation = `stage-out 0.25s ease forwards`;
  setTimeout(() => {
    fromEl.classList.remove('active');
    fromEl.style.animation = '';
    toEl.style.display = 'block';
    toEl.style.animation = `stage-in 0.35s ease forwards`;
    toEl.classList.add('active');
  }, 250);
}

function updateSidePanel(step) {
  bgNumber.textContent = step === 1 ? '01' : step === 2 ? '02' : '✓';

  if (step === 1) {
    dot1.className = 'step-dot active';
    dot2.className = 'step-dot';
    stepConnector.classList.remove('active');
  } else if (step === 2) {
    dot1.className = 'step-dot done';
    dot1.textContent = '✓';
    dot2.className = 'step-dot active';
    stepConnector.classList.add('active');
  } else {
    dot1.className = 'step-dot done';
    dot2.className = 'step-dot done';
    dot2.textContent = '✓';
    stepConnector.classList.add('active');
  }
}

// ── Password strength ─────────────────────────────────────────────────────────
const pwFill  = document.getElementById('pw-fill');
const pwLabel = document.getElementById('pw-label');

function measureStrength(pw) {
  if (!pw) return { score: 0, label: 'Enter a password' };
  let score = 0;
  if (pw.length >= 8)  score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  if (score <= 1) return { score: 1, label: 'Weak', cls: 'weak' };
  if (score <= 3) return { score: 2, label: 'Fair', cls: 'fair' };
  return { score: 3, label: 'Strong', cls: 'strong' };
}

document.getElementById('password').addEventListener('input', function () {
  const { label, cls } = measureStrength(this.value);
  pwFill.className = `pw-fill${cls ? ' ' + cls : ''}`;
  pwLabel.textContent = label;
});

// ── Password visibility toggles ───────────────────────────────────────────────
document.querySelectorAll('.toggle-pw').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.dataset.target;
    const input    = document.getElementById(targetId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    btn.setAttribute('aria-pressed', input.type === 'text');
    btn.style.color = input.type === 'text' ? 'var(--fire)' : '';
  });
});

// ── Stage 1 validation ────────────────────────────────────────────────────────
function validateStage1() {
  let valid = true;

  const username = document.getElementById('username').value.trim();
  const email    = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm  = document.getElementById('confirm-password').value;
  const phone    = document.getElementById('phone').value.trim();

  // Username
  clearError('err-username');
  if (!username) {
    showError('err-username', 'Username is required.');
    markInput(document.getElementById('username'), false);
    valid = false;
  } else if (username.length < 3) {
    showError('err-username', 'Must be at least 3 characters.');
    markInput(document.getElementById('username'), false);
    valid = false;
  } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    showError('err-username', 'Only letters, numbers and underscores.');
    markInput(document.getElementById('username'), false);
    valid = false;
  } else {
    markInput(document.getElementById('username'), true);
  }

  // Email (optional but validate format if provided)
  clearError('err-email');
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showError('err-email', 'Enter a valid email address.');
    markInput(document.getElementById('email'), false);
    valid = false;
  } else if (email) {
    markInput(document.getElementById('email'), true);
  }

  // Password
  clearError('err-password');
  if (!password) {
    showError('err-password', 'Password is required.');
    markInput(document.getElementById('password'), false);
    valid = false;
  } else if (password.length < 8) {
    showError('err-password', 'Must be at least 8 characters.');
    markInput(document.getElementById('password'), false);
    valid = false;
  } else {
    markInput(document.getElementById('password'), true);
  }

  // Confirm password
  clearError('err-confirm-password');
  if (!confirm) {
    showError('err-confirm-password', 'Please confirm your password.');
    markInput(document.getElementById('confirm-password'), false);
    valid = false;
  } else if (confirm !== password) {
    showError('err-confirm-password', 'Passwords do not match.');
    markInput(document.getElementById('confirm-password'), false);
    valid = false;
  } else {
    markInput(document.getElementById('confirm-password'), true);
  }

  // Phone
  clearError('err-phone');
  if (!phone) {
    showError('err-phone', 'Phone number is required.');
    markInput(document.getElementById('phone'), false);
    valid = false;
  } else if (!/^[\d\s\+\-\(\)]{7,15}$/.test(phone)) {
    showError('err-phone', 'Enter a valid phone number.');
    markInput(document.getElementById('phone'), false);
    valid = false;
  } else {
    markInput(document.getElementById('phone'), true);
  }

  return valid;
}

// ── Set max date for DOB (today) ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const dobInput = document.getElementById('dob');
  if (dobInput) {
    dobInput.max = new Date().toISOString().split('T')[0];
  }
});

// ── Stage 2 validation ────────────────────────────────────────────────────────
function validateStage2() {
  let valid = true;

  const height = document.getElementById('height').value;
  const weight = document.getElementById('weight').value;
  const dob    = document.getElementById('dob').value;

  clearError('err-height');
  if (height && (parseFloat(height) < 100 || parseFloat(height) > 250)) {
    showError('err-height', 'Enter a height between 100–250 cm.');
    markInput(document.getElementById('height'), false);
    valid = false;
  } else if (height) {
    markInput(document.getElementById('height'), true);
  }

  clearError('err-weight');
  if (weight && (parseFloat(weight) < 30 || parseFloat(weight) > 300)) {
    showError('err-weight', 'Enter a weight between 30–300 kg.');
    markInput(document.getElementById('weight'), false);
    valid = false;
  } else if (weight) {
    markInput(document.getElementById('weight'), true);
  }

  clearError('err-dob');
  if (dob) {
    const today   = new Date();
    const dobDate = new Date(dob);
    const age     = today.getFullYear() - dobDate.getFullYear();
    if (dobDate > today) {
      showError('err-dob', 'Date of birth cannot be in the future.');
      markInput(document.getElementById('dob'), false);
      valid = false;
    } else if (age > 120) {
      showError('err-dob', 'Please enter a valid date of birth.');
      markInput(document.getElementById('dob'), false);
      valid = false;
    } else {
      markInput(document.getElementById('dob'), true);
    }
  }

  return valid;
}

// ── Stage 1 submit → go to stage 2 ───────────────────────────────────────────
form1.addEventListener('submit', function (e) {
  e.preventDefault();
  if (!validateStage1()) return;

  // Stash stage-1 data
  formData.username   = document.getElementById('username').value.trim();
  formData.email      = document.getElementById('email').value.trim() || null;
  formData.password   = document.getElementById('password').value;
  formData.phone      = document.getElementById('phone').value.trim();
  formData.profession = document.getElementById('profession').value.trim() || null;

  transitionTo(stage1El, stage2El, 'forward');
  updateSidePanel(2);
});

// ── Back button ───────────────────────────────────────────────────────────────
btnBack.addEventListener('click', () => {
  setApiError('');
  transitionTo(stage2El, stage1El, 'back');
  updateSidePanel(1);
});

// ── Stage 2 submit → POST to API ──────────────────────────────────────────────
form2.addEventListener('submit', async function (e) {
  e.preventDefault();
  if (!validateStage2()) return;

  setApiError('');

  // Collect stage-2 data
  const height = document.getElementById('height').value;
  const weight = document.getElementById('weight').value;
  const dob    = document.getElementById('dob').value;

  const payload = {
    username:   formData.username,
    email:      formData.email,
    password:   formData.password,
    phone:      formData.phone,
    profession: formData.profession,
    height_cm:  height ? parseFloat(height) : null,
    weight_kg:  weight ? parseFloat(weight) : null,
    dob:        dob || null,
  };

  // Loading state
  btnSubmit.classList.add('btn-loading');
  btnSubmit.disabled = true;
  btnBack.disabled   = true;

  try {
    const res = await fetch('/api/member/register', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      setApiError(data.error || `Registration failed (${res.status}). Please try again.`);
      btnSubmit.classList.remove('btn-loading');
      btnSubmit.disabled = false;
      btnBack.disabled   = false;
      return;
    }

    // Success
    document.getElementById('success-name').textContent = formData.username;
    updateSidePanel(3);
    transitionTo(stage2El, successEl, 'forward');

  } catch (err) {
    setApiError('Network error — please check your connection and try again.');
    btnSubmit.classList.remove('btn-loading');
    btnSubmit.disabled = false;
    btnBack.disabled   = false;
  }
});

// ── Live validation on blur (better UX) ──────────────────────────────────────
document.getElementById('username').addEventListener('blur', function () {
  if (!this.value.trim()) return;
  const ok = this.value.trim().length >= 3 && /^[a-zA-Z0-9_]+$/.test(this.value.trim());
  markInput(this, ok);
  if (!ok) showError('err-username', 'Only letters, numbers and underscores (min 3).');
  else clearError('err-username');
});

document.getElementById('email').addEventListener('blur', function () {
  if (!this.value.trim()) return;
  const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value.trim());
  markInput(this, ok);
  if (!ok) showError('err-email', 'Enter a valid email address.');
  else clearError('err-email');
});

document.getElementById('confirm-password').addEventListener('input', function () {
  const pw = document.getElementById('password').value;
  if (!this.value) return;
  const match = this.value === pw;
  markInput(this, match);
  if (!match) showError('err-confirm-password', 'Passwords do not match.');
  else clearError('err-confirm-password');
});