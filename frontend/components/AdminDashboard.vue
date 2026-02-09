<!-- Admin Dashboard Component -->
<template>
  <div class="admin-dashboard">
    <div class="dashboard-container">
      <!-- Welcome Header -->
      <div class="dashboard-header">
        <div>
          <h1 class="dashboard-title">Admin Dashboard</h1>
          <p class="dashboard-subtitle">{{ user.name }} | Business Command Center</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <span class="stat-icon">👥</span>
            <div>
              <div class="stat-value">{{ stats.total_members }}</div>
              <div class="stat-label">Members</div>
            </div>
          </div>
          <div class="stat-card">
            <span class="stat-icon">✅</span>
            <div>
              <div class="stat-value">{{ stats.active_memberships }}</div>
              <div class="stat-label">Active</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab-btn', activeTab === tab.id ? 'active' : '']"
        >
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Priority Call List -->
        <div v-if="activeTab === 'priority'" class="content-section">
          <div class="section-header">
            <h2>⚠️ Priority Call List</h2>
            <p>Members expiring within 7 days - Take action now!</p>
          </div>

          <div v-if="priorityList.length === 0" class="empty-state">
            <div class="empty-icon">✨</div>
            <p>No members expiring soon. Great retention!</p>
          </div>

          <div v-else class="members-grid">
            <div v-for="member in priorityList" :key="member.id" class="member-card expiring">
              <div class="member-header">
                <div class="member-info">
                  <h3 class="member-name">{{ member.user_name }}</h3>
                  <p class="member-meta">Plan: {{ member.plan }}</p>
                </div>
                <div class="urgency-badge">
                  {{ member.days_remaining }} days
                </div>
              </div>
              
              <div class="member-details">
                <div class="detail-row">
                  <span>📅 Expires:</span>
                  <strong>{{ formatDate(member.end_date) }}</strong>
                </div>
              </div>

              <a 
                :href="getWhatsAppLink(member.phone, member.user_name, member.days_remaining)"
                target="_blank"
                class="action-btn whatsapp-btn"
              >
                <span>💬 WhatsApp Reminder</span>
              </a>
            </div>
          </div>
        </div>

        <!-- Digital Gatekeeper (Expired Members) -->
        <div v-if="activeTab === 'gatekeeper'" class="content-section">
          <div class="section-header">
            <h2>🚫 Digital Gatekeeper</h2>
            <p>Expired members waiting for approval</p>
          </div>

          <div v-if="expiredMembers.length === 0" class="empty-state">
            <div class="empty-icon">🎉</div>
            <p>No expired members. Everyone's current!</p>
          </div>

          <div v-else class="members-grid">
            <div v-for="member in expiredMembers" :key="member.user_id" class="member-card expired">
              <div class="member-header">
                <div class="member-info">
                  <h3 class="member-name">{{ member.user_name }}</h3>
                  <p class="member-meta">Last Plan: {{ member.last_plan }}</p>
                </div>
                <div class="expired-badge">
                  {{ member.days_expired }} days ago
                </div>
              </div>

              <div class="member-details">
                <div class="detail-row">
                  <span>📅 Expired On:</span>
                  <strong>{{ formatDate(member.expired_on) }}</strong>
                </div>
              </div>

              <div class="action-buttons">
                <select v-model="renewalPlans[member.user_id]" class="plan-select">
                  <option value="">Select Plan</option>
                  <option v-for="plan in plans" :key="plan.id" :value="plan.id">
                    {{ plan.name }} - ₹{{ plan.price }}
                  </option>
                </select>
                <button 
                  @click="approveRenewal(member.user_id)"
                  :disabled="!renewalPlans[member.user_id]"
                  class="action-btn approve-btn"
                >
                  ✓ Approve Access
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Approval Queue -->
        <div v-if="activeTab === 'approvals'" class="content-section">
          <div class="section-header">
            <h2>⏳ Approval Queue</h2>
            <p>Pending payment verifications</p>
          </div>

          <div v-if="pendingPayments.length === 0" class="empty-state">
            <div class="empty-icon">📭</div>
            <p>No pending approvals</p>
          </div>

          <div v-else class="payments-grid">
            <div v-for="payment in pendingPayments" :key="payment.id" class="payment-card">
              <div class="payment-header">
                <div>
                  <h3 class="payment-user">{{ payment.user_name }}</h3>
                  <p class="payment-plan">{{ payment.plan }}</p>
                </div>
                <div class="payment-amount">₹{{ payment.amount }}</div>
              </div>

              <div class="payment-details">
                <div class="detail-row">
                  <span>💳 Method:</span>
                  <strong>{{ payment.payment_method }}</strong>
                </div>
                <div v-if="payment.txn_ref" class="detail-row">
                  <span>🔢 UTR:</span>
                  <strong class="utr-code">{{ payment.txn_ref }}</strong>
                </div>
                <div class="detail-row">
                  <span>📅 Date:</span>
                  <strong>{{ formatDateTime(payment.date) }}</strong>
                </div>
                <div v-if="payment.notes" class="detail-row notes">
                  <span>📝 Notes:</span>
                  <p>{{ payment.notes }}</p>
                </div>
              </div>

              <div class="action-buttons">
                <button @click="approvePayment(payment.id)" class="action-btn approve-btn">
                  ✓ Approve
                </button>
                <button @click="rejectPayment(payment.id)" class="action-btn reject-btn">
                  ✗ Reject
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Transactions -->
        <div v-if="activeTab === 'transactions'" class="content-section">
          <div class="section-header">
            <h2>💰 Financial Transactions</h2>
            <div class="filter-controls">
              <button 
                v-for="filter in transactionFilters" 
                :key="filter.id"
                @click="selectTransactionFilter(filter.id)"
                :class="['filter-btn', selectedFilter === filter.id ? 'active' : '']"
              >
                {{ filter.label }}
              </button>

              <div v-if="selectedFilter === 'custom'" class="date-inputs">
                <input v-model="customStartDate" type="date" class="date-input" />
                <input v-model="customEndDate" type="date" class="date-input" />
                <button @click="loadTransactions" class="action-btn">Apply</button>
              </div>
            </div>
          </div>

          <div class="revenue-summary">
            <div class="summary-card">
              <div class="summary-icon">💵</div>
              <div>
                <div class="summary-value">₹{{ transactions.total_revenue?.toFixed(2) || 0 }}</div>
                <div class="summary-label">Total Revenue</div>
              </div>
            </div>
            <div class="summary-card">
              <div class="summary-icon">📊</div>
              <div>
                <div class="summary-value">{{ transactions.count || 0 }}</div>
                <div class="summary-label">Transactions</div>
              </div>
            </div>
          </div>
          <div class="view-all-link">
            <button @click="$emit('navigate', 'transactions')" class="view-all-btn">
              📊 View All Transactions →
            </button>
          </div>
          <div class="transactions-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Member</th>
                  <th>Plan</th>
                  <th>Method</th>
                  <th>UTR</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="txn in transactions.transactions" :key="txn.id">
                  <td>{{ formatDate(txn.date) }}</td>
                  <td>{{ txn.user_name }}</td>
                  <td>{{ txn.plan }}</td>
                  <td>
                    <span :class="['method-badge', txn.payment_method.toLowerCase()]">
                      {{ txn.payment_method }}
                    </span>
                  </td>
                  <td>{{ txn.txn_ref || '-' }}</td>
                  <td class="amount">₹{{ txn.amount }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Plan Management -->
        <div v-if="activeTab === 'plans'" class="content-section">
          <div class="section-header">
            <h2>📋 Plan Management</h2>
            <button @click="showPlanForm = true" class="action-btn create-btn">
              ➕ Create Plan
            </button>
          </div>

          <!-- Create Plan Form -->
          <div v-if="showPlanForm" class="plan-form-modal">
            <div class="modal-content">
              <div class="modal-header">
                <h3>{{ editingPlan ? 'Edit Plan' : 'Create New Plan' }}</h3>
                <button @click="closePlanForm" class="close-btn">✕</button>
              </div>

              <form @submit.prevent="savePlan">
                <div class="form-group">
                  <label>Plan Name</label>
                  <input v-model="planForm.name" type="text" required class="form-input" placeholder="e.g., Monthly" />
                </div>

                <div class="form-group">
                  <label>Price (₹)</label>
                  <input v-model="planForm.price" type="number" step="0.01" required class="form-input" placeholder="1500" />
                </div>

                <div class="form-group">
                  <label>Duration (Days)</label>
                  <input v-model="planForm.duration_days" type="number" required class="form-input" placeholder="30" />
                </div>

                <div class="form-actions">
                  <button type="submit" class="action-btn approve-btn">
                    {{ editingPlan ? 'Update' : 'Create' }}
                  </button>
                  <button type="button" @click="closePlanForm" class="action-btn reject-btn">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div class="plans-grid">
            <div v-for="plan in allPlans" :key="plan.id" :class="['plan-card', !plan.is_active ? 'inactive' : '']">
              <div class="plan-header">
                <h3 class="plan-name">{{ plan.name }}</h3>
                <div v-if="!plan.is_active" class="inactive-badge">Inactive</div>
              </div>

              <div class="plan-details">
                <div class="plan-price">₹{{ plan.price }}</div>
                <div class="plan-duration">{{ plan.duration_days }} days</div>
              </div>

              <div class="plan-actions">
                <button @click="editPlan(plan)" class="action-btn-small edit-btn">
                  ✏️ Edit
                </button>
                <button 
                  v-if="plan.is_active" 
                  @click="deactivatePlan(plan.id)" 
                  class="action-btn-small delete-btn"
                >
                  🗑️ Deactivate
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Business Projections -->
        <div v-if="activeTab === 'projections'" class="content-section">
          <div class="section-header">
            <h2>📈 Business Projections</h2>
            <p>Data-driven revenue forecasting</p>
          </div>

          <div class="projections-grid">
            <div class="projection-card highlight">
              <h3>Next Month Forecast</h3>
              <div class="projection-value">₹{{ projections.next_month_expected?.toFixed(2) || 0 }}</div>
              <p class="projection-detail">{{ projections.expiring_count || 0 }} members expiring</p>
            </div>

            <div class="projection-card">
              <h3>Last Month Actual</h3>
              <div class="projection-value">₹{{ projections.last_month_actual?.toFixed(2) || 0 }}</div>
              <p class="projection-detail">Historical performance</p>
            </div>
          </div>

          <div class="scenarios-section">
            <h3>Growth Scenarios</h3>
            <div class="scenarios-grid">
              <div class="scenario-card pessimistic">
                <div class="scenario-header">
                  <span class="scenario-icon">📉</span>
                  <h4>Pessimistic (-5%)</h4>
                </div>
                <div class="scenario-metrics">
                  <div class="metric">
                    <span>Quarterly</span>
                    <strong>₹{{ projections.scenarios?.pessimistic?.quarterly?.toFixed(2) || 0 }}</strong>
                  </div>
                  <div class="metric">
                    <span>Annual</span>
                    <strong>₹{{ projections.scenarios?.pessimistic?.annual?.toFixed(2) || 0 }}</strong>
                  </div>
                </div>
              </div>

              <div class="scenario-card neutral">
                <div class="scenario-header">
                  <span class="scenario-icon">📊</span>
                  <h4>Status Quo (0%)</h4>
                </div>
                <div class="scenario-metrics">
                  <div class="metric">
                    <span>Quarterly</span>
                    <strong>₹{{ projections.scenarios?.status_quo?.quarterly?.toFixed(2) || 0 }}</strong>
                  </div>
                  <div class="metric">
                    <span>Annual</span>
                    <strong>₹{{ projections.scenarios?.status_quo?.annual?.toFixed(2) || 0 }}</strong>
                  </div>
                </div>
              </div>

              <div class="scenario-card optimistic">
                <div class="scenario-header">
                  <span class="scenario-icon">📈</span>
                  <h4>Optimistic (+10%)</h4>
                </div>
                <div class="scenario-metrics">
                  <div class="metric">
                    <span>Quarterly</span>
                    <strong>₹{{ projections.scenarios?.optimistic?.quarterly?.toFixed(2) || 0 }}</strong>
                  </div>
                  <div class="metric">
                    <span>Annual</span>
                    <strong>₹{{ projections.scenarios?.optimistic?.annual?.toFixed(2) || 0 }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue';

export default {
  name: 'AdminDashboard',
  props: {
    user: Object,
    token: String
  },
  emits: ['navigate'],

  setup(props, { emit }) {
    const activeTab = ref('priority');
    const stats = ref({ total_members: 0, active_memberships: 0 });
    const priorityList = ref([]);
    const expiredMembers = ref([]);
    const pendingPayments = ref([]);
    const transactions = ref({ transactions: [], total_revenue: 0, count: 0 });
    const plans = ref([]);
    const allPlans = ref([]);
    const projections = ref({});
    const renewalPlans = reactive({});
    const selectedFilter = ref('last_30_days');
    const customStartDate = ref('');
    const customEndDate = ref('');
    const showPlanForm = ref(false);
    const editingPlan = ref(null);
    const planForm = ref({ name: '', price: '', duration_days: '' });

    const tabs = [
      { id: 'priority', label: 'Priority List', icon: '⚠️' },
      { id: 'gatekeeper', label: 'Gatekeeper', icon: '🚫' },
      { id: 'approvals', label: 'Approvals', icon: '⏳' },
      { id: 'transactions', label: 'Transactions', icon: '💰' },
      { id: 'plans', label: 'Plans', icon: '📋' },
      { id: 'projections', label: 'Projections', icon: '📈' }
    ];

    const transactionFilters = [
      { id: 'last_7_days', label: 'Last 7 Days' },  // CHANGED from last_30_days
      { id: 'this_month', label: 'This Month' },
      { id: 'last_month', label: 'Last Month' },
      { id: 'custom', label: 'Custom Range' }
    ];

    const apiCall = async (endpoint, options = {}) => {
      const response = await fetch(endpoint, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authentication-Token': props.token,
          ...options.headers
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'API request failed');
      }

      return response.json();
    };

    const loadStats = async () => {
      stats.value = await apiCall('/api/stats');
    };

    const loadPriorityList = async () => {
      priorityList.value = await apiCall('/api/admin/priority-list');
    };

    const loadExpiredMembers = async () => {
      expiredMembers.value = await apiCall('/api/admin/expired-members');
    };

    const loadPendingPayments = async () => {
      pendingPayments.value = await apiCall('/api/admin/payments/pending');
    };

    const loadTransactions = async () => {
      let url = `/api/admin/transactions?filter=${selectedFilter.value}`;
      if (selectedFilter.value === 'custom' && customStartDate.value && customEndDate.value) {
        url += `&start_date=${customStartDate.value}&end_date=${customEndDate.value}`;
      }
      transactions.value = await apiCall(url);
    };

    const loadPlans = async () => {
      plans.value = await apiCall('/api/plans');
      allPlans.value = await apiCall('/api/admin/plans');
    };

    const loadProjections = async () => {
      projections.value = await apiCall('/api/admin/projections');
    };

    const selectTransactionFilter = (filterId) => {
      selectedFilter.value = filterId;
      if (filterId !== 'custom') {
        loadTransactions();
      }
    };

    const approvePayment = async (paymentId) => {
      try {
        await apiCall(`/api/admin/payments/${paymentId}/approve`, { method: 'POST' });
        alert('Payment approved and membership activated!');
        loadPendingPayments();
        loadStats();
      } catch (error) {
        alert(error.message);
      }
    };

    const rejectPayment = async (paymentId) => {
      if (!confirm('Are you sure you want to reject this payment?')) return;
      
      try {
        await apiCall(`/api/admin/payments/${paymentId}/reject`, { method: 'POST' });
        alert('Payment rejected');
        loadPendingPayments();
      } catch (error) {
        alert(error.message);
      }
    };

    const approveRenewal = async (userId) => {
      const planId = renewalPlans[userId];
      if (!planId) {
        alert('Please select a plan');
        return;
      }

      try {
        await apiCall(`/api/admin/memberships/${userId}/renew`, {
          method: 'POST',
          body: JSON.stringify({ plan_id: planId })
        });
        alert('Membership renewed successfully!');
        loadExpiredMembers();
        loadStats();
      } catch (error) {
        alert(error.message);
      }
    };

    const savePlan = async () => {
      try {
        if (editingPlan.value) {
          await apiCall(`/api/admin/plans/${editingPlan.value.id}`, {
            method: 'PUT',
            body: JSON.stringify(planForm.value)
          });
          alert('Plan updated successfully!');
        } else {
          await apiCall('/api/admin/plans', {
            method: 'POST',
            body: JSON.stringify(planForm.value)
          });
          alert('Plan created successfully!');
        }
        closePlanForm();
        loadPlans();
      } catch (error) {
        alert(error.message);
      }
    };

    const editPlan = (plan) => {
      editingPlan.value = plan;
      planForm.value = { ...plan };
      showPlanForm.value = true;
    };

    const deactivatePlan = async (planId) => {
      if (!confirm('Are you sure you want to deactivate this plan?')) return;

      try {
        await apiCall(`/api/admin/plans/${planId}`, { method: 'DELETE' });
        alert('Plan deactivated');
        loadPlans();
      } catch (error) {
        alert(error.message);
      }
    };

    const closePlanForm = () => {
      showPlanForm.value = false;
      editingPlan.value = null;
      planForm.value = { name: '', price: '', duration_days: '' };
    };

    const getWhatsAppLink = (phone, name, daysRemaining) => {
      const firstName = name.split(' ')[0];
      const message = `Hi ${firstName}! 👋\n\nYour MS Power Fitness membership expires in ${daysRemaining} days. Don't miss your fitness momentum!\n\nRenew now to continue your journey. 💪`;
      return `https://wa.me/91${phone}?text=${encodeURIComponent(message)}`;
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
      loadStats();
      loadPriorityList();
      loadExpiredMembers();
      loadPendingPayments();
      loadTransactions();
      loadPlans();
      loadProjections();
    });

    return {
      activeTab,
      tabs,
      stats,
      priorityList,
      expiredMembers,
      pendingPayments,
      transactions,
      plans,
      allPlans,
      projections,
      renewalPlans,
      transactionFilters,
      selectedFilter,
      customStartDate,
      customEndDate,
      showPlanForm,
      editingPlan,
      planForm,
      selectTransactionFilter,
      loadTransactions,
      approvePayment,
      rejectPayment,
      approveRenewal,
      savePlan,
      editPlan,
      deactivatePlan,
      closePlanForm,
      getWhatsAppLink,
      formatDate,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.dashboard-header {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
}

.dashboard-title {
  font-family: 'Archivo Black', sans-serif;
  font-size: 2rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
}

.dashboard-subtitle {
  color: var(--gray);
  font-size: 0.95rem;
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-card {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

.tab-navigation {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  margin-bottom: 2rem;
  padding: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.tab-btn {
  background: transparent;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  color: var(--dark);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(255, 107, 53, 0.1);
  color: var(--primary);
}

.tab-btn.active {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}
.view-all-link {
  margin-bottom: 1.5rem;
}

.view-all-btn {
  background: linear-gradient(135deg, var(--secondary) 0%, #003A6C 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.view-all-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 78, 137, 0.4);
}
.content-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h2 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.5rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
}

.section-header p {
  color: var(--gray);
  font-size: 0.9rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.member-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.member-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.member-card.expiring {
  border-color: var(--warning);
  background: linear-gradient(135deg, #FFF9E6 0%, #FFFDF4 100%);
}

.member-card.expired {
  border-color: var(--danger);
  background: linear-gradient(135deg, #FFE6EB 0%, #FFF5F7 100%);
}

.member-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.member-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--dark);
  margin-bottom: 0.25rem;
}

.member-meta {
  font-size: 0.85rem;
  color: var(--gray);
}

.urgency-badge,
.expired-badge {
  padding: 0.5rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}

.urgency-badge {
  background: var(--warning);
  color: #8B6914;
}

.expired-badge {
  background: var(--danger);
  color: white;
}

.member-details {
  margin: 1rem 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row.notes {
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn,
.action-btn-small {
  width: 100%;
  padding: 0.875rem;
  border: none;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.whatsapp-btn {
  background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
  color: white;
}

.whatsapp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4);
}

.approve-btn {
  background: linear-gradient(135deg, var(--success) 0%, #05B48B 100%);
  color: white;
}

.approve-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 214, 160, 0.4);
}

.reject-btn {
  background: linear-gradient(135deg, var(--danger) 0%, #D63D5E 100%);
  color: white;
}

.reject-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 71, 111, 0.4);
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-top: 1rem;
}

.plan-select {
  grid-column: 1 / -1;
  padding: 0.75rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-size: 0.9rem;
}

.payments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.payment-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border: 2px solid var(--secondary);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.payment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 78, 137, 0.15);
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.payment-user {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--dark);
}

.payment-plan {
  font-size: 0.85rem;
  color: var(--gray);
  margin-top: 0.25rem;
}

.payment-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
}

.utr-code {
  font-family: 'Courier New', monospace;
  background: rgba(0, 78, 137, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.filter-controls {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.filter-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.date-inputs {
  display: flex;
  gap: 0.5rem;
}

.date-input {
  padding: 0.5rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
}

.revenue-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: linear-gradient(135deg, var(--secondary) 0%, #003A6C 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 78, 137, 0.3);
}

.summary-icon {
  font-size: 2.5rem;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.summary-label {
  font-size: 0.85rem;
  opacity: 0.9;
}

.transactions-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: linear-gradient(135deg, var(--dark) 0%, #2E2E42 100%);
  color: white;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

th {
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

tbody tr:hover {
  background: rgba(255, 107, 53, 0.05);
}

.amount {
  font-weight: 700;
  color: var(--success);
}

.method-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.method-badge.upi {
  background: #E6F4FF;
  color: var(--secondary);
}

.method-badge.cash {
  background: #E6FFE6;
  color: var(--success);
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.plan-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border: 2px solid var(--primary);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.2);
}

.plan-card.inactive {
  opacity: 0.6;
  border-color: var(--gray);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.plan-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--dark);
}

.inactive-badge {
  background: var(--gray);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.plan-details {
  text-align: center;
  margin: 1.5rem 0;
}

.plan-price {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.plan-duration {
  color: var(--gray);
  font-size: 0.9rem;
}

.plan-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn-small {
  flex: 1;
  padding: 0.6rem;
  font-size: 0.85rem;
  margin-top: 0;
}

.edit-btn {
  background: var(--secondary);
  color: white;
}

.delete-btn {
  background: var(--danger);
  color: white;
}

.plan-form-modal {
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
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.5rem;
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

.modal-content form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--dark);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  width: 100%;
  padding: 0.875rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.form-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2rem;
}

.projections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.projection-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.projection-card.highlight {
  border-color: var(--primary);
  background: linear-gradient(135deg, #FFF4F0 0%, #FFFAF8 100%);
}

.projection-card h3 {
  font-size: 0.9rem;
  color: var(--gray);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.projection-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.projection-detail {
  font-size: 0.85rem;
  color: var(--gray);
}

.scenarios-section {
  margin-top: 2rem;
}

.scenarios-section h3 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  color: var(--dark);
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.scenario-card {
  border-radius: 12px;
  padding: 1.5rem;
  color: white;
}

.scenario-card.pessimistic {
  background: linear-gradient(135deg, var(--danger) 0%, #D63D5E 100%);
}

.scenario-card.neutral {
  background: linear-gradient(135deg, var(--gray) 0%, #5A5F68 100%);
}

.scenario-card.optimistic {
  background: linear-gradient(135deg, var(--success) 0%, #05B48B 100%);
}

.scenario-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.scenario-icon {
  font-size: 2rem;
}

.scenario-header h4 {
  font-size: 1.1rem;
  font-weight: 700;
}

.scenario-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric {
  background: rgba(255, 255, 255, 0.2);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric span {
  font-size: 0.85rem;
  opacity: 0.9;
}

.metric strong {
  font-size: 1.25rem;
}

.create-btn {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  margin-top: 0;
  width: auto;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 0 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-stats {
    width: 100%;
    flex-direction: column;
  }

  .stat-card {
    width: 100%;
  }

  .members-grid,
  .payments-grid,
  .plans-grid {
    grid-template-columns: 1fr;
  }

  .tab-navigation {
    overflow-x: auto;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-controls {
    width: 100%;
  }

  .filter-btn {
    flex: 1;
    min-width: 120px;
  }

  table {
    font-size: 0.85rem;
  }

  th,
  td {
    padding: 0.75rem 0.5rem;
  }
}
</style>
