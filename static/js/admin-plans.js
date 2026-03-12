/* Admin plans page */

let editPlanId = null;
let showInactivePlans = false;

/* ── Inject toggle button (no HTML change required) ────────────────────────── */
(function injectToggle() {
  const topbar = document.querySelector('.topbar-actions') || document.querySelector('.topbar-right');
  if (!topbar) return;

  const btn = document.createElement('button');
  btn.id = "btn-toggle-inactive";
  btn.className = "btn btn-ghost btn-sm";
  btn.textContent = "Show Inactive Plans";

  btn.addEventListener("click", () => {
    showInactivePlans = !showInactivePlans;
    btn.textContent = showInactivePlans ? "Hide Inactive Plans" : "Show Inactive Plans";
    loadPlans();
  });

  topbar.prepend(btn);
})();

async function loadPlans() {
  try {
    const plans = await api('/api/admin/plans');
    const grid  = document.getElementById('plan-admin-grid');

    if (!plans.length) {
      grid.innerHTML = '<div style="color:var(--steel);">No plans yet. Create one above.</div>';
      return;
    }

    const filteredPlans = showInactivePlans
      ? plans
      : plans.filter(p => p.is_active);

    if (!filteredPlans.length) {
      grid.innerHTML = '<div style="color:var(--steel);">No active plans.</div>';
      return;
    }

    grid.innerHTML = filteredPlans.map(p => `
      <div class="plan-admin-card ${p.is_active ? '' : 'pac-inactive'}">
        <div class="pac-name">${p.name}</div>
        <div class="pac-price">${fmtMoney(p.price)}</div>
        <div class="pac-meta">
          ${p.duration_days} days<br>
          ${p.description || ''}<br>
          <span style="color:${p.is_active ? 'var(--success)' : 'var(--steel)'};">
            ${p.is_active ? '● Active' : '○ Inactive'}
          </span>
        </div>
        <div class="pac-actions">
          <button class="btn btn-ghost btn-sm"
            onclick="openEditPlan(${p.id},'${escHtml(p.name)}',${p.price},${p.duration_days},'${escHtml(p.description||'')}',${p.is_active})">
            Edit
          </button>

          <button class="btn btn-${p.is_active ? 'danger' : 'success'} btn-sm"
            onclick="togglePlan(${p.id},${!p.is_active})">
            ${p.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      </div>
    `).join('');

  } catch(e) { toast('Failed to load plans', 'error'); }
}

function escHtml(s) { return s.replace(/'/g, "\\'"); }

/* ── New plan ─────────────────────────────────────────────────────────────── */
document.getElementById('btn-new-plan')?.addEventListener('click', () => {
  editPlanId = null;

  document.getElementById('plan-modal-title').textContent = 'New Plan';
  document.getElementById('plan-name').value     = '';
  document.getElementById('plan-price').value    = '';
  document.getElementById('plan-duration').value = '';
  document.getElementById('plan-desc').value     = '';
  document.getElementById('plan-status').value   = 'true';
  document.getElementById('plan-modal-error').textContent = '';

  openModal('plan-modal');
});

function openEditPlan(id, name, price, duration, desc, isActive) {
  editPlanId = id;

  document.getElementById('plan-modal-title').textContent = 'Edit Plan';
  document.getElementById('plan-name').value     = name;
  document.getElementById('plan-price').value    = price;
  document.getElementById('plan-duration').value = duration;
  document.getElementById('plan-desc').value     = desc;
  document.getElementById('plan-status').value   = String(isActive);
  document.getElementById('plan-modal-error').textContent = '';

  openModal('plan-modal');
}

document.getElementById('plan-modal-cancel')?.addEventListener('click', () =>
  closeModal('plan-modal')
);

document.getElementById('plan-modal-save')?.addEventListener('click', async () => {

  const btn     = document.getElementById('plan-modal-save');
  const errEl   = document.getElementById('plan-modal-error');

  const name     = document.getElementById('plan-name').value.trim();
  const price    = document.getElementById('plan-price').value;
  const duration = document.getElementById('plan-duration').value;

  errEl.textContent = '';

  if (!name || !price || !duration) {
    errEl.textContent = 'Name, price, and duration are required.';
    return;
  }

  const payload = {
    name,
    price: parseFloat(price),
    duration_days: parseInt(duration),
    description: document.getElementById('plan-desc').value.trim() || null,
    is_active: document.getElementById('plan-status').value === 'true'
  };

  btn.classList.add('btn-loading');

  try {

    if (editPlanId) {
      await api(`/api/admin/plans/${editPlanId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });
      toast('Plan updated!');
    }
    else {
      await api('/api/admin/plans', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      toast('Plan created!');
    }

    closeModal('plan-modal');
    loadPlans();

  } catch(e) {
    errEl.textContent = e.message;
  }
  finally {
    btn.classList.remove('btn-loading');
  }
});

async function togglePlan(id, activate) {
  try {
    await api(`/api/admin/plans/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: activate })
    });

    toast(
      activate ? 'Plan activated' : 'Plan deactivated',
      activate ? 'success' : 'warn'
    );

    loadPlans();

  } catch(e) {
    toast(e.message, 'error');
  }
}

window.openEditPlan = openEditPlan;
window.togglePlan   = togglePlan;

loadPlans();