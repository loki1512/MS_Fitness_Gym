<!-- Transactions View Component -->
<template>
  <div class="transactions-view">
    <div class="transactions-container">
      <!-- Header -->
      <div class="transactions-header">
        <div>
          <h1 class="transactions-title">💰 Transaction History</h1>
          <p class="transactions-subtitle">Complete payment records and financial insights</p>
        </div>
        
        <div class="header-stats">
          <div class="stat-card">
            <span class="stat-icon">📊</span>
            <div>
              <div class="stat-value">₹{{ totalRevenue.toFixed(2) }}</div>
              <div class="stat-label">Total Revenue</div>
            </div>
          </div>
          <div class="stat-card">
            <span class="stat-icon">📝</span>
            <div>
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">Transactions</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters Section -->
      <div class="filters-section">
        <div class="search-bar">
          <span class="search-icon">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by member name, email, phone, or UTR..."
            class="search-input"
            @input="performSearch"
          />
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">✕</button>
        </div>

        <div class="filter-tabs">
          <button 
            v-for="filter in quickFilters" 
            :key="filter.id"
            @click="selectQuickFilter(filter.id)"
            :class="['filter-tab', selectedQuickFilter === filter.id ? 'active' : '']"
          >
            {{ filter.label }}
          </button>
        </div>

        <div class="advanced-filters">
          <div class="filter-row">
            <div class="filter-group">
              <label>Payment Method</label>
              <select v-model="filters.paymentMethod" @change="applyFilters" class="filter-select">
                <option value="">All Methods</option>
                <option value="UPI">UPI</option>
                <option value="Cash">Cash</option>
              </select>
            </div>

            <div class="filter-group">
              <label>Status</label>
              <select v-model="filters.status" @change="applyFilters" class="filter-select">
                <option value="">All Statuses</option>
                <option value="Approved">Approved</option>
                <option value="Pending">Pending</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            <div class="filter-group">
              <label>Plan</label>
              <select v-model="filters.plan" @change="applyFilters" class="filter-select">
                <option value="">All Plans</option>
                <option v-for="plan in availablePlans" :key="plan" :value="plan">
                  {{ plan }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>Amount Range</label>
              <div class="amount-range">
                <input 
                  v-model="filters.minAmount" 
                  type="number" 
                  placeholder="Min"
                  @change="applyFilters"
                  class="amount-input"
                />
                <span class="range-separator">to</span>
                <input 
                  v-model="filters.maxAmount" 
                  type="number" 
                  placeholder="Max"
                  @change="applyFilters"
                  class="amount-input"
                />
              </div>
            </div>
          </div>

          <div class="filter-row">
            <div class="filter-group date-range">
              <label>Custom Date Range</label>
              <div class="date-inputs">
                <input 
                  v-model="filters.startDate" 
                  type="date" 
                  @change="selectCustomDate"
                  class="date-input"
                />
                <span class="range-separator">to</span>
                <input 
                  v-model="filters.endDate" 
                  type="date" 
                  @change="selectCustomDate"
                  class="date-input"
                />
              </div>
            </div>

            <button @click="resetFilters" class="reset-btn">
              🔄 Reset All Filters
            </button>

            <button @click="exportTransactions" class="export-btn">
              📥 Export CSV
            </button>
          </div>
        </div>
      </div>

      <!-- Transactions Table -->
      <div class="table-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading transactions...</p>
        </div>

        <div v-else-if="filteredTransactions.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>No transactions found matching your criteria</p>
        </div>

        <div v-else>
          <!-- Summary Cards -->
          <div class="summary-cards">
            <div class="summary-card approved">
              <div class="summary-icon">✅</div>
              <div class="summary-info">
                <div class="summary-amount">₹{{ approvedTotal.toFixed(2) }}</div>
                <div class="summary-label">Approved ({{ approvedCount }})</div>
              </div>
            </div>

            <div class="summary-card pending">
              <div class="summary-icon">⏳</div>
              <div class="summary-info">
                <div class="summary-amount">₹{{ pendingTotal.toFixed(2) }}</div>
                <div class="summary-label">Pending ({{ pendingCount }})</div>
              </div>
            </div>

            <div class="summary-card rejected">
              <div class="summary-icon">❌</div>
              <div class="summary-info">
                <div class="summary-amount">₹{{ rejectedTotal.toFixed(2) }}</div>
                <div class="summary-label">Rejected ({{ rejectedCount }})</div>
              </div>
            </div>
          </div>

          <!-- Transactions Table -->
          <div class="table-wrapper">
            <table class="transactions-table">
              <thead>
                <tr>
                  <th @click="sortBy('date')" class="sortable">
                    Date 
                    <span class="sort-icon">{{ getSortIcon('date') }}</span>
                  </th>
                  <th>Member Details</th>
                  <th>Plan</th>
                  <th @click="sortBy('amount')" class="sortable">
                    Amount
                    <span class="sort-icon">{{ getSortIcon('amount') }}</span>
                  </th>
                  <th>Payment Method</th>
                  <th>UTR / Reference</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="txn in paginatedTransactions" :key="txn.id" class="transaction-row">
                  <td class="date-cell">
                    <div class="date-primary">{{ formatDate(txn.date) }}</div>
                    <div class="date-time">{{ formatTime(txn.date) }}</div>
                  </td>
                  <td class="member-cell">
                    <div class="member-name">{{ txn.user_name }}</div>
                    <div class="member-contact">{{ txn.user_email }}</div>
                    <div class="member-contact">📱 {{ txn.user_phone }}</div>
                  </td>
                  <td>
                    <span class="plan-badge">{{ txn.plan }}</span>
                  </td>
                  <td class="amount-cell">
                    <div class="amount-value">₹{{ txn.amount.toFixed(2) }}</div>
                  </td>
                  <td>
                    <span :class="['method-badge', txn.payment_method.toLowerCase()]">
                      {{ txn.payment_method }}
                    </span>
                  </td>
                  <td>
                    <span v-if="txn.txn_ref" class="utr-code">{{ txn.txn_ref }}</span>
                    <span v-else class="no-utr">-</span>
                  </td>
                  <td>
                    <span :class="['status-badge', txn.status.toLowerCase()]">
                      {{ txn.status }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button @click="viewDetails(txn)" class="action-btn view-btn" title="View Details">
                      👁️
                    </button>
                    <a 
                      :href="getWhatsAppLink(txn.user_phone, txn.user_name)"
                      target="_blank"
                      class="action-btn whatsapp-btn"
                      title="Contact Member"
                    >
                      💬
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="pagination">
            <button 
              @click="previousPage" 
              :disabled="currentPage === 1"
              class="page-btn"
            >
              ← Previous
            </button>

            <div class="page-info">
              Page {{ currentPage }} of {{ totalPages }}
              <span class="record-count">({{ filteredTransactions.length }} records)</span>
            </div>

            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="page-btn"
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      <!-- Transaction Detail Modal -->
      <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>💳 Transaction Details</h2>
            <button @click="closeDetailModal" class="close-btn">✕</button>
          </div>

          <div class="modal-body" v-if="selectedTransaction">
            <div class="detail-section">
              <h3>Transaction Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Transaction ID</label>
                  <div class="detail-value">#{{ selectedTransaction.id }}</div>
                </div>
                <div class="detail-item">
                  <label>Date & Time</label>
                  <div class="detail-value">{{ formatDateTime(selectedTransaction.date) }}</div>
                </div>
                <div class="detail-item">
                  <label>Amount</label>
                  <div class="detail-value amount-highlight">₹{{ selectedTransaction.amount.toFixed(2) }}</div>
                </div>
                <div class="detail-item">
                  <label>Status</label>
                  <span :class="['status-badge', selectedTransaction.status.toLowerCase()]">
                    {{ selectedTransaction.status }}
                  </span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Member Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Name</label>
                  <div class="detail-value">{{ selectedTransaction.user_name }}</div>
                </div>
                <div class="detail-item">
                  <label>Email</label>
                  <div class="detail-value">{{ selectedTransaction.user_email }}</div>
                </div>
                <div class="detail-item">
                  <label>Phone</label>
                  <div class="detail-value">{{ selectedTransaction.user_phone }}</div>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h3>Payment Details</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Plan</label>
                  <div class="detail-value">{{ selectedTransaction.plan }}</div>
                </div>
                <div class="detail-item">
                  <label>Payment Method</label>
                  <span :class="['method-badge', selectedTransaction.payment_method.toLowerCase()]">
                    {{ selectedTransaction.payment_method }}
                  </span>
                </div>
                <div class="detail-item" v-if="selectedTransaction.txn_ref">
                  <label>UTR / Reference</label>
                  <div class="detail-value utr-highlight">{{ selectedTransaction.txn_ref }}</div>
                </div>
                <div class="detail-item" v-if="selectedTransaction.notes">
                  <label>Notes</label>
                  <div class="detail-value">{{ selectedTransaction.notes }}</div>
                </div>
              </div>
            </div>

            <div v-if="selectedTransaction.approved_at" class="detail-section">
              <h3>Approval Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Approved At</label>
                  <div class="detail-value">{{ formatDateTime(selectedTransaction.approved_at) }}</div>
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
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'TransactionsView',
  props: {
    user: Object,
    token: String
  },
  setup(props) {
    const transactions = ref([]);
    const loading = ref(false);
    const searchQuery = ref('');
    const selectedQuickFilter = ref('all');
    const sortField = ref('date');
    const sortDirection = ref('desc');
    const currentPage = ref(1);
    const itemsPerPage = ref(20);
    const showDetailModal = ref(false);
    const selectedTransaction = ref(null);

    const filters = ref({
      paymentMethod: '',
      status: '',
      plan: '',
      minAmount: '',
      maxAmount: '',
      startDate: '',
      endDate: ''
    });

    const availablePlans = ref([]);

    const quickFilters = [
      { id: 'all', label: 'All Time' },
      { id: 'today', label: 'Today' },
      { id: 'week', label: 'This Week' },
      { id: 'month', label: 'This Month' },
      { id: 'last_month', label: 'Last Month' },
      { id: 'quarter', label: 'This Quarter' }
    ];

    const filteredTransactions = computed(() => {
      let result = [...transactions.value];

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(txn => 
          txn.user_name.toLowerCase().includes(query) ||
          txn.user_email.toLowerCase().includes(query) ||
          txn.user_phone.includes(query) ||
          (txn.txn_ref && txn.txn_ref.includes(query))
        );
      }

      // Payment method filter
      if (filters.value.paymentMethod) {
        result = result.filter(txn => txn.payment_method === filters.value.paymentMethod);
      }

      // Status filter
      if (filters.value.status) {
        result = result.filter(txn => txn.status === filters.value.status);
      }

      // Plan filter
      if (filters.value.plan) {
        result = result.filter(txn => txn.plan === filters.value.plan);
      }

      // Amount range filter
      if (filters.value.minAmount) {
        result = result.filter(txn => txn.amount >= parseFloat(filters.value.minAmount));
      }
      if (filters.value.maxAmount) {
        result = result.filter(txn => txn.amount <= parseFloat(filters.value.maxAmount));
      }

      // Sort
      result.sort((a, b) => {
        let aVal = a[sortField.value];
        let bVal = b[sortField.value];

        if (sortField.value === 'date') {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }

        if (sortDirection.value === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });

      return result;
    });

    const paginatedTransactions = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value;
      const end = start + itemsPerPage.value;
      return filteredTransactions.value.slice(start, end);
    });

    const totalPages = computed(() => {
      return Math.ceil(filteredTransactions.value.length / itemsPerPage.value);
    });

    const totalRevenue = computed(() => {
      return filteredTransactions.value.reduce((sum, txn) => sum + txn.amount, 0);
    });

    const totalCount = computed(() => {
      return filteredTransactions.value.length;
    });

    const approvedTotal = computed(() => {
      return filteredTransactions.value
        .filter(txn => txn.status === 'Approved')
        .reduce((sum, txn) => sum + txn.amount, 0);
    });

    const approvedCount = computed(() => {
      return filteredTransactions.value.filter(txn => txn.status === 'Approved').length;
    });

    const pendingTotal = computed(() => {
      return filteredTransactions.value
        .filter(txn => txn.status === 'Pending')
        .reduce((sum, txn) => sum + txn.amount, 0);
    });

    const pendingCount = computed(() => {
      return filteredTransactions.value.filter(txn => txn.status === 'Pending').length;
    });

    const rejectedTotal = computed(() => {
      return filteredTransactions.value
        .filter(txn => txn.status === 'Rejected')
        .reduce((sum, txn) => sum + txn.amount, 0);
    });

    const rejectedCount = computed(() => {
      return filteredTransactions.value.filter(txn => txn.status === 'Rejected').length;
    });

    const loadAllTransactions = async () => {
      loading.value = true;
      try {
        let url = '/api/admin/transactions/all';
        
        const params = new URLSearchParams();
        if (filters.value.startDate) params.append('start_date', filters.value.startDate);
        if (filters.value.endDate) params.append('end_date', filters.value.endDate);

        if (params.toString()) {
          url += `?${params.toString()}`;
        }

        const response = await fetch(url, {
          headers: {
            'Authentication-Token': props.token
          }
        });

        if (response.ok) {
          const data = await response.json();
          transactions.value = data.transactions;

          // Extract unique plans
          const plans = new Set();
          data.transactions.forEach(txn => {
            if (txn.plan && txn.plan !== 'N/A') {
              plans.add(txn.plan);
            }
          });
          availablePlans.value = Array.from(plans).sort();
        }
      } catch (err) {
        console.error('Failed to load transactions:', err);
      } finally {
        loading.value = false;
      }
    };

    const selectQuickFilter = (filterId) => {
      selectedQuickFilter.value = filterId;
      const today = new Date();
      
      filters.value.startDate = '';
      filters.value.endDate = '';

      switch(filterId) {
        case 'today':
          filters.value.startDate = today.toISOString().split('T')[0];
          filters.value.endDate = today.toISOString().split('T')[0];
          break;
        case 'week':
          const weekStart = new Date(today);
          weekStart.setDate(today.getDate() - today.getDay());
          filters.value.startDate = weekStart.toISOString().split('T')[0];
          filters.value.endDate = today.toISOString().split('T')[0];
          break;
        case 'month':
          const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
          filters.value.startDate = monthStart.toISOString().split('T')[0];
          filters.value.endDate = today.toISOString().split('T')[0];
          break;
        case 'last_month':
          const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
          const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
          filters.value.startDate = lastMonthStart.toISOString().split('T')[0];
          filters.value.endDate = lastMonthEnd.toISOString().split('T')[0];
          break;
        case 'quarter':
          const quarterStart = new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3, 1);
          filters.value.startDate = quarterStart.toISOString().split('T')[0];
          filters.value.endDate = today.toISOString().split('T')[0];
          break;
      }

      loadAllTransactions();
    };

    const selectCustomDate = () => {
      selectedQuickFilter.value = '';
      loadAllTransactions();
    };

    const applyFilters = () => {
      currentPage.value = 1;
    };

    const performSearch = () => {
      currentPage.value = 1;
    };

    const clearSearch = () => {
      searchQuery.value = '';
      currentPage.value = 1;
    };

    const resetFilters = () => {
      filters.value = {
        paymentMethod: '',
        status: '',
        plan: '',
        minAmount: '',
        maxAmount: '',
        startDate: '',
        endDate: ''
      };
      searchQuery.value = '';
      selectedQuickFilter.value = 'all';
      currentPage.value = 1;
      loadAllTransactions();
    };

    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortField.value = field;
        sortDirection.value = 'desc';
      }
    };

    const getSortIcon = (field) => {
      if (sortField.value !== field) return '↕️';
      return sortDirection.value === 'asc' ? '↑' : '↓';
    };

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    const viewDetails = (transaction) => {
      selectedTransaction.value = transaction;
      showDetailModal.value = true;
    };

    const closeDetailModal = () => {
      showDetailModal.value = false;
      selectedTransaction.value = null;
    };

    const exportTransactions = () => {
      const csvContent = [
        ['Date', 'Member', 'Email', 'Phone', 'Plan', 'Amount', 'Method', 'UTR', 'Status'],
        ...filteredTransactions.value.map(txn => [
          formatDateTime(txn.date),
          txn.user_name,
          txn.user_email,
          txn.user_phone,
          txn.plan,
          txn.amount,
          txn.payment_method,
          txn.txn_ref || '-',
          txn.status
        ])
      ].map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    };

    const getWhatsAppLink = (phone, name) => {
      const firstName = name.split(' ')[0];
      const message = `Hi ${firstName}! 👋\n\nThank you for your payment. If you have any questions, feel free to reach out!`;
      return `https://wa.me/91${phone}?text=${encodeURIComponent(message)}`;
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    };

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit'
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
      loadAllTransactions();
    });

    return {
      transactions,
      filteredTransactions,
      paginatedTransactions,
      loading,
      searchQuery,
      selectedQuickFilter,
      quickFilters,
      filters,
      availablePlans,
      currentPage,
      totalPages,
      totalRevenue,
      totalCount,
      approvedTotal,
      approvedCount,
      pendingTotal,
      pendingCount,
      rejectedTotal,
      rejectedCount,
      showDetailModal,
      selectedTransaction,
      selectQuickFilter,
      selectCustomDate,
      applyFilters,
      performSearch,
      clearSearch,
      resetFilters,
      sortBy,
      getSortIcon,
      previousPage,
      nextPage,
      viewDetails,
      closeDetailModal,
      exportTransactions,
      getWhatsAppLink,
      formatDate,
      formatTime,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.transactions-view {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.transactions-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem;
}

.transactions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.transactions-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 2.5rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.transactions-subtitle {
  color: var(--gray);
  font-size: 1rem;
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-card {
  background: linear-gradient(135deg, var(--secondary) 0%, #003A6C 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 78, 137, 0.3);
  min-width: 200px;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  opacity: 0.9;
}

.filters-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
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

.filter-tabs {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: 2px solid var(--border);
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.filter-tab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.advanced-filters {
  border-top: 2px solid var(--border);
  padding-top: 1.5rem;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: end;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group.date-range {
  grid-column: span 2;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--dark);
}

.filter-select,
.date-input,
.amount-input {
  padding: 0.75rem;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-select:focus,
.date-input:focus,
.amount-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.amount-range,
.date-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-separator {
  color: var(--gray);
  font-weight: 600;
}

.amount-input {
  flex: 1;
}

.reset-btn,
.export-btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--gray);
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  color: var(--gray);
}

.reset-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(255, 107, 53, 0.05);
}

.export-btn {
  border-color: var(--success);
  color: var(--success);
}

.export-btn:hover {
  background: var(--success);
  color: white;
  box-shadow: 0 4px 12px rgba(6, 214, 160, 0.3);
}

.table-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-card.approved {
  background: linear-gradient(135deg, #E6FFE6 0%, #F0FFF0 100%);
  border: 2px solid var(--success);
}

.summary-card.pending {
  background: linear-gradient(135deg, #FFF4E6 0%, #FFFDF4 100%);
  border: 2px solid var(--warning);
}

.summary-card.rejected {
  background: linear-gradient(135deg, #FFE6EB 0%, #FFF5F7 100%);
  border: 2px solid var(--danger);
}

.summary-icon {
  font-size: 2.5rem;
}

.summary-amount {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.summary-label {
  font-size: 0.85rem;
  color: var(--gray);
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 2rem;
}

.transactions-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.transactions-table thead {
  background: linear-gradient(135deg, var(--dark) 0%, #2E2E42 100%);
  color: white;
}

.transactions-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.transactions-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.transactions-table th.sortable:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sort-icon {
  margin-left: 0.5rem;
}

.transactions-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}

.transaction-row:hover {
  background: rgba(255, 107, 53, 0.05);
}

.date-cell {
  font-size: 0.9rem;
}

.date-primary {
  font-weight: 600;
  color: var(--dark);
}

.date-time {
  font-size: 0.8rem;
  color: var(--gray);
  margin-top: 0.25rem;
}

.member-cell {
  font-size: 0.85rem;
}

.member-name {
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 0.25rem;
}

.member-contact {
  color: var(--gray);
  margin-top: 0.25rem;
}

.plan-badge {
  display: inline-block;
  padding: 0.4rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  background: #E6F4FF;
  color: var(--secondary);
}

.amount-cell {
  font-size: 1.1rem;
}

.amount-value {
  font-weight: 700;
  color: var(--success);
}

.method-badge {
  display: inline-block;
  padding: 0.4rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
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

.utr-code {
  font-family: 'Courier New', monospace;
  background: rgba(0, 78, 137, 0.1);
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.no-utr {
  color: var(--gray);
}

.status-badge {
  display: inline-block;
  padding: 0.4rem 0.875rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-badge.approved {
  background: #E6FFE6;
  color: var(--success);
}

.status-badge.pending {
  background: #FFF4E6;
  color: var(--warning);
}

.status-badge.rejected {
  background: #FFE6EB;
  color: var(--danger);
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

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 2px solid var(--border);
}

.page-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-weight: 600;
  color: var(--dark);
}

.record-count {
  color: var(--gray);
  font-weight: 400;
  margin-left: 0.5rem;
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
  max-width: 800px;
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

.detail-section:last-child {
  margin-bottom: 0;
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

.detail-value {
  font-size: 1rem;
  color: var(--dark);
  font-weight: 600;
}

.amount-highlight {
  font-size: 1.5rem;
  color: var(--success);
}

.utr-highlight {
  font-family: 'Courier New', monospace;
  background: rgba(0, 78, 137, 0.1);
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .transactions-container {
    padding: 0 1rem;
  }

  .transactions-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-stats {
    flex-direction: column;
    width: 100%;
  }

  .stat-card {
    width: 100%;
  }

  .filter-tabs {
    overflow-x: auto;
  }

  .filter-row {
    grid-template-columns: 1fr;
  }

  .filter-group.date-range {
    grid-column: span 1;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
