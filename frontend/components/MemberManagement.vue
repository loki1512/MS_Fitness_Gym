<!-- Member Management Component -->
<template>
  <div class="member-management">
    <div class="management-container">
      <!-- Header -->
      <div class="management-header">
        <div>
          <h1 class="management-title">👥 Member Management</h1>
          <p class="management-subtitle">View and manage all gym members</p>
        </div>
        
        <div class="header-stats">
          <div class="stat-badge">
            <span class="stat-number">{{ filteredMembers.length }}</span>
            <span class="stat-label">{{ filteredMembers.length === 1 ? 'Member' : 'Members' }}</span>
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="search-filter-section">
        <div class="search-bar">
          <span class="search-icon">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by name, email, or phone..."
            class="search-input"
            @input="performSearch"
          />
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">✕</button>
        </div>

        <div class="filters-row">
          <div class="filter-group">
            <label>Gender</label>
            <select v-model="filters.gender" @change="performSearch" class="filter-select">
              <option value="">All Genders</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Plan</label>
            <select v-model="filters.plan" @change="performSearch" class="filter-select">
              <option value="">All Plans</option>
              <option v-for="plan in availablePlans" :key="plan" :value="plan">
                {{ plan }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>DOB From</label>
            <input 
              v-model="filters.dobFrom" 
              type="date" 
              @change="performSearch"
              class="filter-input"
            />
          </div>

          <div class="filter-group">
            <label>DOB To</label>
            <input 
              v-model="filters.dobTo" 
              type="date" 
              @change="performSearch"
              class="filter-input"
            />
          </div>

          <button @click="clearFilters" class="clear-filters-btn">
            🔄 Reset Filters
          </button>
        </div>
      </div>

      <!-- Members Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading members...</p>
        </div>

        <div v-else-if="filteredMembers.length === 0" class="empty-state">
          <div class="empty-icon">😕</div>
          <p>No members found matching your criteria</p>
        </div>

        <table v-else class="members-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Contact</th>
              <th>Gender</th>
              <th>DOB(Age)</th>
              <th>Current Plan</th>
              <th>Status</th>
              <th>Days Left</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in filteredMembers" :key="member.id" class="member-row">
              <td class="member-name">{{ member.name }}</td>
              <td class="member-contact">
                <div>📧 {{ member.email }}</div>
                <div>📱 {{ member.phone }}</div>
              </td>
              <td>{{ member.gender || '-' }}</td>
              <td>{{ member.date_of_birth ? formatDate(member.date_of_birth) : '-' }}</td>
              <td>
                <span :class="['plan-badge', getPlanClass(member.current_plan)]">
                  {{ member.current_plan }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', getStatusClass(member.membership_status)]">
                  {{ member.membership_status }}
                </span>
              </td>
              <td>
                <span v-if="member.days_remaining !== null" :class="getDaysClass(member.days_remaining)">
                  {{ member.days_remaining }} days
                </span>
                <span v-else>-</span>
              </td>
              <td class="actions-cell">
                <button @click="viewMember(member.id)" class="action-btn view-btn" title="View Details">
                  👁️
                </button>
                <a 
                  :href="getWhatsAppLink(member.phone, member.name)"
                  target="_blank"
                  class="action-btn whatsapp-btn"
                  title="WhatsApp Reminder"
                >
                  💬
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Member Detail Modal -->
      <div v-if="showMemberModal" class="modal-overlay" @click="closeMemberModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>{{ editingMember ? '✏️ Edit Member' : '👤 Member Details' }}</h2>
            <button @click="closeMemberModal" class="close-btn">✕</button>
          </div>

          <div class="modal-body">
            <div v-if="memberLoading" class="loading-state">
              <div class="spinner"></div>
              <p>Loading member details...</p>
            </div>

            <div v-else-if="selectedMember">
              <!-- View Mode -->
              <div v-if="!editingMember">
                <div class="detail-section">
                  <h3>Personal Information</h3>
                  <div class="detail-grid">
                    <div class="detail-item">
                      <label>Full Name</label>
                      <div>{{ selectedMember.name }}</div>
                    </div>
                    <div class="detail-item">
                      <label>Email</label>
                      <div>{{ selectedMember.email }}</div>
                    </div>
                    <div class="detail-item">
                      <label>Phone</label>
                      <div>{{ selectedMember.phone }}</div>
                    </div>
                    <div class="detail-item">
                      <label>Date of Birth</label>
                      <div>{{ selectedMember.date_of_birth ? formatDate(selectedMember.date_of_birth) : 'Not provided' }}</div>
                    </div>
                    <div class="detail-item">
                      <label>Gender</label>
                      <div>{{ selectedMember.gender || 'Not specified' }}</div>
                    </div>
                    <div class="detail-item">
                      <label>Member Since</label>
                      <div>{{ formatDate(selectedMember.created_at) }}</div>
                    </div>
                  </div>
                </div>

                <div v-if="selectedMember.current_membership" class="detail-section">
                  <h3>Current Membership</h3>
                  <div class="membership-card" :class="selectedMember.current_membership.active ? 'active' : 'inactive'">
                    <div class="membership-status-badge">
                      <span class="status-icon">{{ selectedMember.current_membership.active ? '✅' : '🚫' }}</span>
                      <span class="status-text">{{ selectedMember.current_membership.status }}</span>
                    </div>
                    <div v-if="selectedMember.current_membership.active" class="membership-details">
                      <div><strong>Plan:</strong> {{ selectedMember.current_membership.plan }}</div>
                      <div><strong>Start Date:</strong> {{ formatDate(selectedMember.current_membership.start_date) }}</div>
                      <div><strong>End Date:</strong> {{ formatDate(selectedMember.current_membership.end_date) }}</div>
                      <div><strong>Days Remaining:</strong> 
                        <span :class="getDaysClass(selectedMember.current_membership.days_remaining)">
                          {{ selectedMember.current_membership.days_remaining }} days
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="selectedMember.memberships_history && selectedMember.memberships_history.length > 0" class="detail-section">
                  <h3>Membership History</h3>
                  <div class="history-list">
                    <div v-for="membership in selectedMember.memberships_history" :key="membership.id" class="history-item">
                      <div class="history-info">
                        <strong>{{ membership.plan }}</strong>
                        <span class="history-date">{{ formatDate(membership.start_date) }} - {{ formatDate(membership.end_date) }}</span>
                      </div>
                      <span :class="['status-badge', getStatusClass(membership.status)]">
                        {{ membership.status }}
                      </span>
                    </div>
                  </div>
                </div>

                <div v-if="selectedMember.payments_history && selectedMember.payments_history.length > 0" class="detail-section">
                  <h3>Payment History</h3>
                  <div class="history-list">
                    <div v-for="payment in selectedMember.payments_history" :key="payment.id" class="history-item">
                      <div class="history-info">
                        <strong>₹{{ payment.amount }} - {{ payment.plan }}</strong>
                        <span class="history-date">{{ formatDateTime(payment.date) }} • {{ payment.payment_method }}</span>
                        <span v-if="payment.txn_ref" class="utr-code">UTR: {{ payment.txn_ref }}</span>
                      </div>
                      <span :class="['status-badge', payment.status.toLowerCase()]">
                        {{ payment.status }}
                      </span>
                    </div>
                  </div>
                </div>

                <button 
                  v-if="user.role === 'admin'" 
                  @click="startEditing" 
                  class="modal-action-btn edit-mode-btn"
                >
                  ✏️ Edit Member Details
                </button>
              </div>

              <!-- Edit Mode -->
              <div v-else>
                <div v-if="error" class="alert alert-danger">{{ error }}</div>
                <div v-if="success" class="alert alert-success">{{ success }}</div>

                <form @submit.prevent="saveMemberDetails">
                  <div class="detail-section">
                    <h3>Edit Personal Information</h3>
                    <div class="form-grid">
                      <div class="form-group">
                        <label>Full Name *</label>
                        <input v-model="editForm.name" type="text" required class="form-input" />
                      </div>

                      <div class="form-group">
                        <label>Email *</label>
                        <input v-model="editForm.email" type="email" required class="form-input" />
                      </div>

                      <div class="form-group">
                        <label>Phone *</label>
                        <input 
                          v-model="editForm.phone" 
                          type="tel" 
                          pattern="[0-9]{10}"
                          maxlength="10"
                          required 
                          class="form-input" 
                        />
                      </div>

                      <div class="form-group">
                        <label>Date of Birth</label>
                        <input v-model="editForm.date_of_birth" type="date" class="form-input" />
                      </div>

                      <div class="form-group">
                        <label>Gender</label>
                        <select v-model="editForm.gender" class="form-input">
                          <option value="">Not specified</option>
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div class="form-group">
                        <label>New Password (leave blank to keep current)</label>
                        <input v-model="editForm.password" type="password" minlength="6" class="form-input" />
                        <small class="form-hint">Minimum 6 characters</small>
                      </div>
                    </div>
                  </div>

                  <div class="modal-actions">
                    <button type="submit" :disabled="saveLoading" class="modal-action-btn save-btn">
                      <span v-if="!saveLoading">💾 Save Changes</span>
                      <span v-else>⏳ Saving...</span>
                    </button>
                    <button type="button" @click="cancelEditing" class="modal-action-btn cancel-btn">
                      ✖️ Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'MemberManagement',
  props: {
    user: Object,
    token: String
  },
  setup(props) {
    const members = ref([]);
    const loading = ref(false);
    const searchQuery = ref('');
    const filters = ref({
      gender: '',
      plan: '',
      dobFrom: '',
      dobTo: ''
    });

    const availablePlans = ref([]);
    const showMemberModal = ref(false);
    const selectedMember = ref(null);
    const memberLoading = ref(false);
    const editingMember = ref(false);
    const saveLoading = ref(false);
    const error = ref('');
    const success = ref('');

    const editForm = ref({
      name: '',
      email: '',
      phone: '',
      date_of_birth: '',
      gender: '',
      password: ''
    });

    const filteredMembers = computed(() => {
      return members.value;
    });

    const loadMembers = async () => {
      loading.value = true;
      try {
        const params = new URLSearchParams();
        if (searchQuery.value) params.append('search', searchQuery.value);
        if (filters.value.gender) params.append('gender', filters.value.gender);
        if (filters.value.plan) params.append('plan', filters.value.plan);
        if (filters.value.dobFrom) params.append('dob_from', filters.value.dobFrom);
        if (filters.value.dobTo) params.append('dob_to', filters.value.dobTo);

        const response = await fetch(`/api/admin/members?${params.toString()}`, {
          headers: {
            'Authentication-Token': props.token
          }
        });

        if (response.ok) {
          const data = await response.json();
          members.value = data.members;
          
          // Extract unique plans
          const plans = new Set();
          data.members.forEach(m => {
            if (m.current_plan && m.current_plan !== 'No Plan') {
              plans.add(m.current_plan);
            }
          });
          availablePlans.value = Array.from(plans).sort();
        }
      } catch (err) {
        console.error('Failed to load members:', err);
      } finally {
        loading.value = false;
      }
    };

    const performSearch = () => {
      loadMembers();
    };

    const clearSearch = () => {
      searchQuery.value = '';
      loadMembers();
    };

    const clearFilters = () => {
      filters.value = {
        gender: '',
        plan: '',
        dobFrom: '',
        dobTo: ''
      };
      searchQuery.value = '';
      loadMembers();
    };

    const viewMember = async (memberId) => {
      showMemberModal.value = true;
      memberLoading.value = true;
      editingMember.value = false;
      error.value = '';
      success.value = '';

      try {
        const response = await fetch(`/api/admin/users/${memberId}`, {
          headers: {
            'Authentication-Token': props.token
          }
        });

        if (response.ok) {
          selectedMember.value = await response.json();
        }
      } catch (err) {
        console.error('Failed to load member details:', err);
      } finally {
        memberLoading.value = false;
      }
    };

    const startEditing = () => {
      editingMember.value = true;
      editForm.value = {
        name: selectedMember.value.name,
        email: selectedMember.value.email,
        phone: selectedMember.value.phone,
        date_of_birth: selectedMember.value.date_of_birth || '',
        gender: selectedMember.value.gender || '',
        password: ''
      };
    };

    const cancelEditing = () => {
      editingMember.value = false;
      editForm.value = {
        name: '',
        email: '',
        phone: '',
        date_of_birth: '',
        gender: '',
        password: ''
      };
      error.value = '';
      success.value = '';
    };

    const saveMemberDetails = async () => {
      saveLoading.value = true;
      error.value = '';
      success.value = '';

      try {
        const updateData = {
          name: editForm.value.name,
          email: editForm.value.email,
          phone: editForm.value.phone,
          date_of_birth: editForm.value.date_of_birth || null,
          gender: editForm.value.gender || null
        };

        if (editForm.value.password) {
          updateData.password = editForm.value.password;
        }

        const response = await fetch(`/api/admin/users/${selectedMember.value.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': props.token
          },
          body: JSON.stringify(updateData)
        });

        const data = await response.json();

        if (response.ok) {
          success.value = 'Member details updated successfully!';
          setTimeout(() => {
            editingMember.value = false;
            viewMember(selectedMember.value.id);
            loadMembers();
          }, 1500);
        } else {
          error.value = data.error || 'Failed to update member details';
        }
      } catch (err) {
        error.value = 'Network error. Please try again.';
      } finally {
        saveLoading.value = false;
      }
    };

    const closeMemberModal = () => {
      showMemberModal.value = false;
      selectedMember.value = null;
      editingMember.value = false;
      error.value = '';
      success.value = '';
    };

    const getWhatsAppLink = (phone, name) => {
      const firstName = name.split(' ')[0];
      const message = `Hi ${firstName}! 👋\n\nThis is a reminder for your gym attendance today. Keep up the great work! 💪`;
      return `https://wa.me/91${phone}?text=${encodeURIComponent(message)}`;
    };

    const getPlanClass = (plan) => {
      if (plan === 'No Plan') return 'no-plan';
      return 'has-plan';
    };

    const getStatusClass = (status) => {
      const statusMap = {
        'Active': 'active',
        'Expiring': 'expiring',
        'Expired': 'expired',
        'No Membership': 'no-membership',
        'Pending': 'pending',
        'Approved': 'approved',
        'Rejected': 'rejected'
      };
      return statusMap[status] || 'default';
    };

    const getDaysClass = (days) => {
      if (days === null || days === undefined) return '';
      if (days <= 3) return 'critical';
      if (days <= 7) return 'warning';
      return 'good';
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    };

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    onMounted(() => {
      loadMembers();
    });

    return {
      members,
      filteredMembers,
      loading,
      searchQuery,
      filters,
      availablePlans,
      showMemberModal,
      selectedMember,
      memberLoading,
      editingMember,
      saveLoading,
      error,
      success,
      editForm,
      performSearch,
      clearSearch,
      clearFilters,
      viewMember,
      startEditing,
      cancelEditing,
      saveMemberDetails,
      closeMemberModal,
      getWhatsAppLink,
      getPlanClass,
      getStatusClass,
      getDaysClass,
      formatDate,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.member-management {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.management-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.management-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 2.5rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.management-subtitle {
  color: var(--gray);
  font-size: 1rem;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-badge {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  display: block;
  font-size: 0.85rem;
  opacity: 0.9;
}

.search-filter-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-bar {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.25rem;
}

.search-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid var(--border);
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--gray);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.3s ease;
}

.clear-btn:hover {
  color: var(--danger);
}

.filters-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--dark);
}

.filter-select,
.filter-input {
  padding: 0.75rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.clear-filters-btn {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: 2px solid var(--gray);
  color: var(--gray);
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-filters-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(255, 107, 53, 0.05);
}

.table-container {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 107, 53, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.members-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.members-table thead {
  background: linear-gradient(135deg, var(--dark) 0%, #2E2E42 100%);
  color: white;
}

.members-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.members-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}

.member-row:hover {
  background: rgba(255, 107, 53, 0.05);
}

.member-name {
  font-weight: 600;
  color: var(--dark);
}

.member-contact {
  font-size: 0.85rem;
}

.member-contact div {
  margin: 0.25rem 0;
}

.plan-badge,
.status-badge {
  display: inline-block;
  padding: 0.4rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
}

.plan-badge.has-plan {
  background: #E6F4FF;
  color: var(--secondary);
}

.plan-badge.no-plan {
  background: #F5F5F5;
  color: var(--gray);
}

.status-badge.active {
  background: #E6FFE6;
  color: var(--success);
}

.status-badge.expiring {
  background: #FFF4E6;
  color: var(--warning);
}

.status-badge.expired,
.status-badge.no-membership {
  background: #FFE6EB;
  color: var(--danger);
}

.status-badge.pending {
  background: #FFF4E6;
  color: var(--warning);
}

.status-badge.approved {
  background: #E6FFE6;
  color: var(--success);
}

.status-badge.rejected {
  background: #FFE6EB;
  color: var(--danger);
}

.critical {
  color: var(--danger);
  font-weight: 700;
}

.warning {
  color: var(--warning);
  font-weight: 700;
}

.good {
  color: var(--success);
  font-weight: 600;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 0.875rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.view-btn {
  background: linear-gradient(135deg, var(--secondary) 0%, #003A6C 100%);
  color: white;
}

.view-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 78, 137, 0.4);
}

.whatsapp-btn {
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  color: white;
}

.whatsapp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 2rem;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 20px 20px 0 0;
}

.modal-header h2 {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 2rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h3 {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.25rem;
  color: var(--dark);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--primary);
  font-weight: 700;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 8px;
  border: 2px solid var(--border);
}

.detail-item label {
  display: block;
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.detail-item div {
  font-size: 1rem;
  color: var(--dark);
  font-weight: 600;
}

.membership-card {
  padding: 1.5rem;
  border-radius: 12px;
  border: 2px solid var(--border);
}

.membership-card.active {
  background: linear-gradient(135deg, #E6FFE6 0%, #F0FFF0 100%);
  border-color: var(--success);
}

.membership-card.inactive {
  background: linear-gradient(135deg, #FFE6EB 0%, #FFF5F7 100%);
  border-color: var(--danger);
}

.membership-status-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-weight: 700;
  font-size: 1.25rem;
}

.status-icon {
  font-size: 1.5rem;
}

.membership-details div {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
}

.membership-details div:last-child {
  border-bottom: none;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 8px;
  border: 2px solid var(--border);
}

.history-info {
  flex: 1;
}

.history-info strong {
  display: block;
  color: var(--dark);
  margin-bottom: 0.25rem;
}

.history-date {
  display: block;
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 0.25rem;
}

.utr-code {
  display: inline-block;
  font-family: 'Courier New', monospace;
  background: rgba(0, 78, 137, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--dark);
  font-size: 0.95rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.form-hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--gray);
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.alert-danger {
  background: #FEE;
  color: var(--danger);
  border: 2px solid var(--danger);
}

.alert-success {
  background: #EFE;
  color: var(--success);
  border: 2px solid var(--success);
}

.modal-action-btn {
  width: 100%;
  padding: 1.25rem;
  border: none;
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.edit-mode-btn {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
}

.edit-mode-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
}

.modal-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2rem;
}

.save-btn {
  background: linear-gradient(135deg, var(--success) 0%, #05B48B 100%);
  color: white;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(6, 214, 160, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: transparent;
  color: var(--gray);
  border: 2px solid var(--gray);
}

.cancel-btn:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 71, 111, 0.05);
}

@media (max-width: 768px) {
  .management-container {
    padding: 0 1rem;
  }

  .management-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters-row {
    grid-template-columns: 1fr;
  }

  .members-table {
    font-size: 0.85rem;
  }

  .members-table th,
  .members-table td {
    padding: 0.75rem 0.5rem;
  }

  .modal-content {
    max-width: 100%;
    margin: 1rem;
  }

  .detail-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    grid-template-columns: 1fr;
  }
}
</style>
