/* =========================================================
   ADMIN MEMBERS PAGE
   Handles:
   - Member list loading
   - Search + pagination
   - Member drawer view
   - Edit member modal
   - Add member modal
   - Extend subscription modal
========================================================= */

let currentPage = 1;      // current pagination page
let searchTimer = null;   // debounce timer for search
let editMemberId = null;  // member currently being edited
let extendMemberId = null;// member whose subscription will be extended


/* =========================================================
   LOAD MEMBERS TABLE
========================================================= */

async function loadMembers(page = 1, q = '') {

  try {

    // Request paginated member list
    const data = await api(`/api/admin/members?page=${page}&per_page=20&q=${encodeURIComponent(q)}`);

    const tbody = document.getElementById('members-tbody');

    /* ---------- Empty state ---------- */
    if (!data.members.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No members found</td></tr>`;
    }

    /* ---------- Render table rows ---------- */
    else {

      tbody.innerHTML = data.members.map(m => {

        const sub = m.active_subscription;

        let subCell = '<span style="color:var(--steel);">None</span>';

        // pending approval indicator
        if (m.has_pending) {

          subCell = `<span class="badge badge-pending">Pending Approval</span>`;

        }

        // active subscription display
        else if (sub) {

          const left = daysLeft(sub.end_date);
          const warn = left !== null && left <= 7;

          subCell = `${sub.plan_name}
            <span style="color:${warn ? 'var(--warn)' : 'var(--steel)'};font-size:0.78rem;">
            (${left}d left)</span>`;
        }

        return `
        <tr>
          <td><strong style="color:var(--white);">${m.name}</strong></td>
          <td style="color:var(--steel);">@${m.username}</td>
          <td>${m.phone}</td>
          <td style="font-size:0.82rem;color:var(--steel);">${fmtDate(m.join_date)}</td>
          <td style="color:var(--fire);font-weight:700;">${m.streak}🔥</td>
          <td>${subCell}</td>
          <td>
            <button class="btn btn-ghost btn-sm"
              onclick="openMemberDrawer(${m.user_id})">
              View
            </button>
          </td>
        </tr>`;

      }).join('');
    }

    renderPagination(data.page, data.pages, page);

    currentPage = page;

  }

  catch(e) {

    toast('Failed to load members', 'error');

  }
}


/* =========================================================
   PAGINATION RENDERING
========================================================= */

function renderPagination(current, total) {

  const el = document.getElementById('members-pagination');

  if (!el || total <= 1) {
    if(el) el.innerHTML = '';
    return;
  }

  let html =
  `<button class="page-btn" ${current===1?'disabled':''}
    onclick="loadMembers(${current-1},getSearch())">‹</button>`;

  for (let i = 1; i <= total; i++) {

    if (i === 1 || i === total || Math.abs(i-current) <= 1) {

      html +=
      `<button class="page-btn ${i===current?'active':''}"
        onclick="loadMembers(${i},getSearch())">${i}</button>`;

    }

    else if (Math.abs(i-current) === 2) {

      html += `<span style="color:var(--steel);padding:0 4px;">…</span>`;

    }

  }

  html +=
  `<button class="page-btn" ${current===total?'disabled':''}
    onclick="loadMembers(${current+1},getSearch())">›</button>`;

  el.innerHTML = html;

}


/* =========================================================
   SEARCH INPUT (debounced)
========================================================= */

function getSearch() {
  return document.getElementById('member-search').value.trim();
}

document.getElementById('member-search')?.addEventListener('input', function(){

  clearTimeout(searchTimer);

  searchTimer = setTimeout(() => {

    loadMembers(1, this.value.trim());

  }, 350);

});


/* =========================================================
   MEMBER DRAWER
   Shows full profile information
========================================================= */

async function openMemberDrawer(memberId){

  document.getElementById('drawer-title').textContent = 'Loading…';
  document.getElementById('drawer-body').innerHTML = '<div class="skeleton-block"></div>';

  document.getElementById('member-drawer').classList.add('open');
  document.getElementById('member-drawer-backdrop').classList.add('open');

  try{

    const m = await api(`/api/admin/members/${memberId}`);

    document.getElementById('drawer-title').textContent = m.name;

    /* ---------- Active subscription ---------- */

    const activeSub = m.subscriptions.find(
      s => s.status === 'active' &&
      s.end_date >= new Date().toISOString().split('T')[0]
    );


    /* ---------- Edit button ---------- */

    const editBtn = document.getElementById('drawer-edit-member');

    editBtn.style.display = "inline-flex";

    editBtn.onclick = () => openEditMember(
      memberId,
      m.name,
      m.phone,
      m.email,
      m.profession,
      m.height_cm,
      m.weight_kg
    );


    /* ---------- Extend subscription button ---------- */

    const extendBtn = document.getElementById('drawer-extend-sub');

    extendBtn.style.display = "inline-flex";

    extendBtn.onclick = () => {

      extendMemberId = memberId;

      document.getElementById('extend-days').value = '';

      document.getElementById('extend-sub-error').textContent = '';

      openModal('extend-sub-modal');

    };


    /* ---------- Drawer content ---------- */

    document.getElementById('drawer-body').innerHTML = `
      <div class="drawer-section">

        <div class="drawer-section-title">Account</div>

        <div class="drawer-info-row">
          <span class="drawer-info-key">Username</span>
          <span class="drawer-info-val">@${m.username}</span>
        </div>

        <div class="drawer-info-row">
          <span class="drawer-info-key">Phone</span>
          <span class="drawer-info-val">${m.phone || '—'}</span>
        </div>

        <div class="drawer-info-row">
          <span class="drawer-info-key">Email</span>
          <span class="drawer-info-val">${m.email || '—'}</span>
        </div>

        <div class="drawer-info-row">
          <span class="drawer-info-key">Joined</span>
          <span class="drawer-info-val">${fmtDate(m.join_date)}</span>
        </div>

        <div class="drawer-info-row">
          <span class="drawer-info-key">Streak</span>
          <span class="drawer-info-val">${m.streak}🔥</span>
        </div>

      </div>
    `;

  }

  catch(e){

    document.getElementById('drawer-body').innerHTML =
      `<div class="alert alert-error">${e.message}</div>`;

  }

}


/* =========================================================
   CLOSE DRAWER
========================================================= */

function closeMemberDrawer(){

  document.getElementById('member-drawer').classList.remove('open');

  document.getElementById('member-drawer-backdrop').classList.remove('open');

}

document.getElementById('drawer-close')?.addEventListener('click', closeMemberDrawer);
document.getElementById('member-drawer-backdrop')?.addEventListener('click', closeMemberDrawer);



/* =========================================================
   EDIT MEMBER MODAL
========================================================= */

function openEditMember(id, name, phone, email, profession, height, weight){

  editMemberId = id;

  document.getElementById('edit-name').value = name || '';
  document.getElementById('edit-phone').value = phone || '';
  document.getElementById('edit-email').value = email || '';
  document.getElementById('edit-profession').value = profession || '';
  document.getElementById('edit-height').value = height || '';
  document.getElementById('edit-weight').value = weight || '';

  document.getElementById('edit-member-error').textContent = '';

  openModal('edit-member-modal');

}

document.getElementById('edit-member-cancel')
?.addEventListener('click', () => closeModal('edit-member-modal'));


/* ---------- Confirm edit ---------- */

document.getElementById('edit-member-confirm')
?.addEventListener('click', async () => {

  const btn = document.getElementById('edit-member-confirm');
  const err = document.getElementById('edit-member-error');

  btn.classList.add('btn-loading');

  try{

    await api(`/api/admin/members/${editMemberId}`, {

      method: 'PATCH',

      body: JSON.stringify({

        name: document.getElementById('edit-name').value.trim(),
        phone: document.getElementById('edit-phone').value.trim(),
        email: document.getElementById('edit-email').value.trim() || null,
        profession: document.getElementById('edit-profession').value.trim() || null,
        height_cm: document.getElementById('edit-height').value || null,
        weight_kg: document.getElementById('edit-weight').value || null

      })

    });

    closeModal('edit-member-modal');

    toast("Member updated!");

    loadMembers(currentPage, getSearch());

  }

  catch(e){

    err.textContent = e.message;

  }

  finally{

    btn.classList.remove('btn-loading');

  }

});



/* =========================================================
   ADD MEMBER MODAL
========================================================= */

document.getElementById('btn-add-member')?.addEventListener('click', () => openModal('add-member-modal'));

document.getElementById('add-member-cancel')
?.addEventListener('click', () => closeModal('add-member-modal'));


/* ---------- Confirm add ---------- */

document.getElementById('add-member-confirm')
?.addEventListener('click', async () => {

  const btn = document.getElementById('add-member-confirm');
  const errEl = document.getElementById('add-member-error');

  const username = document.getElementById('new-username').value.trim();
  const phone = document.getElementById('new-phone').value.trim();

  errEl.textContent = '';

  if (!username || !phone) {

    errEl.textContent = 'Username and phone are required.';

    return;

  }

  btn.classList.add('btn-loading');

  try{

    await api('/api/admin/members', {

      method: 'POST',

      body: JSON.stringify({

        username,
        phone,
        name: document.getElementById('new-name').value.trim() || username,
        email: document.getElementById('new-email').value.trim() || null,
        password: document.getElementById('new-password').value || 'ms@123',
        profession: document.getElementById('new-profession').value.trim() || null

      }),

    });

    closeModal('add-member-modal');

    toast('Member created!');

    loadMembers(1, getSearch());

  }

  catch(e){

    errEl.textContent = e.message;

  }

  finally{

    btn.classList.remove('btn-loading');

  }

});


/* =========================================================
   GLOBAL EXPORTS
========================================================= */

window.openMemberDrawer = openMemberDrawer;
window.loadMembers = loadMembers;
window.getSearch = getSearch;


/* =========================================================
   INITIAL PAGE LOAD
========================================================= */

loadMembers(1);