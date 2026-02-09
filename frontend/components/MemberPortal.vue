<!-- Member Portal Component -->
<template>
  <div class="member-portal">
    <div class="portal-container">
      <!-- Status Card -->
      <div :class="['status-card', membershipStatus.class]">
        <div class="status-icon">{{ membershipStatus.icon }}</div>
        <div class="status-content">
          <h1 class="status-title">{{ membershipStatus.title }}</h1>
          <p class="status-message">{{ membershipStatus.message }}</p>
          
          <div v-if="user.membership && user.membership.active" class="status-details">
            <div class="detail-item">
              <span class="detail-label">Plan:</span>
              <span class="detail-value">{{ user.membership.plan }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Valid Until:</span>
              <span class="detail-value">{{ formatDate(user.membership.end_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Days Remaining:</span>
              <span :class="['detail-value', getDaysClass(user.membership.days_remaining)]">
                {{ user.membership.days_remaining }} days
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Section -->
      <div v-if="!user.membership || !user.membership.active || user.membership.days_remaining <= 7" class="payment-section">
        <div class="section-header">
          <h2>💳 Renew Membership</h2>
          <p>Choose your plan and complete payment</p>
        </div>

        <div v-if="!showPaymentFlow" class="plans-grid">
          <div 
            v-for="plan in plans" 
            :key="plan.id"
            @click="selectPlan(plan)"
            :class="['plan-card', selectedPlan?.id === plan.id ? 'selected' : '']"
          >
            <div class="plan-header">
              <h3 class="plan-name">{{ plan.name }}</h3>
              <div class="plan-badge">Best Value</div>
            </div>
            
            <div class="plan-price">
              <span class="currency">₹</span>
              <span class="amount">{{ plan.price }}</span>
            </div>
            
            <div class="plan-duration">{{ plan.duration_days }} days</div>
            
            <div class="plan-features">
              <div class="feature">✓ Full Gym Access</div>
              <div class="feature">✓ Equipment Usage</div>
              <div class="feature">✓ Locker Facility</div>
            </div>

            <button 
              @click="selectPlan(plan)"
              :class="['select-btn', selectedPlan?.id === plan.id ? 'selected' : '']"
            >
              {{ selectedPlan?.id === plan.id ? 'Selected ✓' : 'Select Plan' }}
            </button>
          </div>
        </div>

        <div v-if="selectedPlan && !showPaymentFlow" class="payment-method-selector">
          <h3>Choose Payment Method</h3>
          <div class="method-grid">
            <button 
              @click="selectPaymentMethod('UPI')"
              :class="['method-btn', paymentMethod === 'UPI' ? 'selected' : '']"
            >
              <div class="method-icon">📱</div>
              <div class="method-name">UPI Payment</div>
              <div class="method-desc">PhonePe, GPay, Paytm</div>
            </button>

            <button 
              @click="selectPaymentMethod('Cash')"
              :class="['method-btn', paymentMethod === 'Cash' ? 'selected' : '']"
            >
              <div class="method-icon">💵</div>
              <div class="method-name">Cash Payment</div>
              <div class="method-desc">Pay at gym desk</div>
            </button>
          </div>

          <button 
            v-if="paymentMethod"
            @click="showPaymentFlow = true"
            class="continue-btn"
          >
            Continue to Payment →
          </button>
        </div>

        <!-- Payment Flow -->
        <div v-if="showPaymentFlow" class="payment-flow">
          <button @click="resetPaymentFlow" class="back-btn">← Back to Plans</button>

          <div class="payment-summary">
            <h3>Payment Summary</h3>
            <div class="summary-row">
              <span>Plan:</span>
              <strong>{{ selectedPlan.name }}</strong>
            </div>
            <div class="summary-row">
              <span>Duration:</span>
              <strong>{{ selectedPlan.duration_days }} days</strong>
            </div>
            <div class="summary-row total">
              <span>Total Amount:</span>
              <strong class="amount">₹{{ selectedPlan.price }}</strong>
            </div>
          </div>

          <!-- UPI Payment -->
          <div v-if="paymentMethod === 'UPI'" class="upi-payment">
            <div class="qr-section">
              <h4>📱 Scan QR Code to Pay</h4>
              <div class="qr-placeholder">
                <div class="qr-code">
                  <!-- In production, replace with actual UPI QR code image -->
                  <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                    <rect width="200" height="200" fill="white"/>
                    <text x="100" y="100" text-anchor="middle" font-size="12" fill="#333">
                      UPI QR Code
                    </text>
                    <text x="100" y="120" text-anchor="middle" font-size="10" fill="#666">
                      Scan to Pay ₹{{ selectedPlan.price }}
                    </text>
                  </svg>
                </div>
                <p class="qr-instructions">Open any UPI app and scan this code</p>
              </div>
            </div>

            <div class="utr-input-section">
              <h4>Enter Transaction Details</h4>
              <div class="form-group">
                <label>12-Digit UPI Transaction ID (UTR) *</label>
                <input 
                  v-model="paymentForm.txn_ref" 
                  type="text" 
                  pattern="[0-9]{12}"
                  maxlength="12"
                  placeholder="123456789012"
                  class="form-input"
                  @input="validateUTR"
                  required
                />
                <small class="form-hint">
                  Find this in your payment app under transaction details
                </small>
                <div v-if="utrError" class="error-message">{{ utrError }}</div>
              </div>

              <div class="form-group">
                <label>Additional Notes (Optional)</label>
                <textarea 
                  v-model="paymentForm.notes" 
                  rows="3"
                  placeholder="Any additional information..."
                  class="form-input"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Cash Payment -->
          <div v-if="paymentMethod === 'Cash'" class="cash-payment">
            <div class="cash-instructions">
              <div class="instruction-icon">💵</div>
              <h4>Cash Payment Instructions</h4>
              <ol>
                <li>Visit the gym reception desk</li>
                <li>Pay ₹{{ selectedPlan.price }} in cash</li>
                <li>Admin will approve your payment</li>
                <li>Your access will be activated immediately</li>
              </ol>
            </div>

            <div class="form-group">
              <label>Additional Notes (Optional)</label>
              <textarea 
                v-model="paymentForm.notes" 
                rows="3"
                placeholder="Any additional information..."
                class="form-input"
              ></textarea>
            </div>
          </div>

          <div v-if="paymentError" class="alert alert-danger">{{ paymentError }}</div>
          <div v-if="paymentSuccess" class="alert alert-success">{{ paymentSuccess }}</div>

          <button 
            @click="submitPayment"
            :disabled="loading || (paymentMethod === 'UPI' && !isUTRValid)"
            class="submit-payment-btn"
          >
            <span v-if="!loading">Submit for Approval</span>
            <span v-else>⏳ Submitting...</span>
          </button>
        </div>
      </div>

      <!-- Payment History -->
      <div class="history-section">
        <h2>📜 Payment History</h2>
        <div v-if="paymentHistory.length === 0" class="empty-state">
          <p>No payment history yet</p>
        </div>
        <div v-else class="history-list">
          <div v-for="payment in paymentHistory" :key="payment.id" class="history-item">
            <div class="history-info">
              <div class="history-plan">{{ payment.plan }}</div>
              <div class="history-date">{{ formatDateTime(payment.date) }}</div>
            </div>
            <div class="history-details">
              <div class="history-amount">₹{{ payment.amount }}</div>
              <div :class="['history-status', payment.status.toLowerCase()]">
                {{ payment.status }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';

export default {
  name: 'MemberPortal',
  props: {
    user: Object,
    token: String
  },
  emits: ['refresh-user','profile-updated'],
  setup(props,{emit}) {
    const plans = ref([]);
    const selectedPlan = ref(null);
    const paymentMethod = ref('');
    const showPaymentFlow = ref(false);
    const loading = ref(false);
    const paymentError = ref('');
    const paymentSuccess = ref('');
    const utrError = ref('');
    const paymentHistory = ref([]);

    const paymentForm = ref({
      txn_ref: '',
      notes: ''
    });

    const membershipStatus = computed(() => {
      if(!props.user.membership){
        return{
          class: 'status-yellow',
          icon: 'Welcome to MS Fitness! 🎉',
          title: 'Activate Your Membership',
          message: 'Please select a plan and complete payment to start your fitness journey with us!'
        }
      }

      else if(!props.user.membership || !props.user.membership.active) {
        return {
          class: 'status-yellow',
          icon: '🚫',
          title: 'Access Denied',
          message: 'Your membership has expired. Please renew to continue your fitness journey.'
        };
      }
      if (props.user.membership && props.user.membership.active) {
        const daysRemaining = props.user.membership.days_remaining;
        
        if (daysRemaining > 7) {
          return {
            class: 'status-green',
            icon: '✅',
            title: 'Membership Active',
            message: 'Your membership is active and in good standing'
          };
        } else if (daysRemaining > 0) {
          return {
            class: 'status-yellow',
            icon: '⚠️',
            title: 'Expiring Soon',
            message: `Your membership expires in ${daysRemaining} days. Renew now to avoid interruption.`
          };
        }
      }
      
      return {
        class: 'status-red',
        icon: '🚫',
        title: 'Access Denied',
        message: 'Your membership has expired. Please renew to continue your fitness journey.'
      };
    });

    const isUTRValid = computed(() => {
      return paymentForm.value.txn_ref.length === 12 && /^[0-9]{12}$/.test(paymentForm.value.txn_ref);
    });

    const loadPlans = async () => {
      try {
        const response = await fetch('/api/plans');
        plans.value = await response.json();
      } catch (error) {
        console.error('Failed to load plans:', error);
      }
    };

    const loadPaymentHistory = async () => {
      try {
        const response = await fetch('/api/payments/history', {
          headers: {
            'Authentication-Token': props.token
          }
        });
        
        if (response.ok) {
          paymentHistory.value = await response.json();
        }
      } catch (error) {
        console.error('Failed to load payment history:', error);
      }
    };

    const selectPlan = (plan) => {
      selectedPlan.value = plan;
    };

    const selectPaymentMethod = (method) => {
      paymentMethod.value = method;
    };

    const validateUTR = () => {
      const utr = paymentForm.value.txn_ref;
      
      if (utr.length === 0) {
        utrError.value = '';
        return;
      }

      if (!/^[0-9]*$/.test(utr)) {
        utrError.value = 'UTR must contain only numbers';
        paymentForm.value.txn_ref = utr.replace(/[^0-9]/g, '');
        return;
      }

      if (utr.length > 0 && utr.length < 12) {
        utrError.value = `UTR must be exactly 12 digits (${utr.length}/12)`;
      } else {
        utrError.value = '';
      }
    };

    const submitPayment = async () => {
      loading.value = true;
      paymentError.value = '';
      paymentSuccess.value = '';

      // Final validation for UPI
      if (paymentMethod.value === 'UPI' && !isUTRValid.value) {
        paymentError.value = 'Please enter a valid 12-digit UTR';
        loading.value = false;
        return;
      }

      try {
        const response = await fetch('/api/payments/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': props.token
          },
          body: JSON.stringify({
            plan_id: selectedPlan.value.id,
            amount: selectedPlan.value.price,
            payment_method: paymentMethod.value,
            txn_ref: paymentMethod.value === 'UPI' ? paymentForm.value.txn_ref : null,
            notes: paymentForm.value.notes
          })
        });

        const data = await response.json();

        if (response.ok) {
          if (props.user.membership) {
    props.user.membership.active = true;
    props.user.membership.days_remaining = selectedPlan.value.duration_days;
  }

  // 2. Still tell the parent to fetch the "official" data
          emit('profile-updated');
          paymentSuccess.value = 'Payment submitted successfully! Admin will approve shortly.';

          emit('profile-updated');
          setTimeout(() => {
            resetPaymentFlow();
            loadPaymentHistory();
          }, 2000);
        } else {
          paymentError.value = data.error || 'Failed to submit payment';
        }
      } catch (error) {
        paymentError.value = 'Network error. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const resetPaymentFlow = () => {
      showPaymentFlow.value = false;
      selectedPlan.value = null;
      paymentMethod.value = '';
      paymentForm.value = { txn_ref: '', notes: '' };
      paymentError.value = '';
      paymentSuccess.value = '';
      utrError.value = '';
    };

    const getDaysClass = (days) => {
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
      loadPlans();
      loadPaymentHistory();
    });

    return {
      plans,
      selectedPlan,
      paymentMethod,
      showPaymentFlow,
      loading,
      paymentError,
      paymentSuccess,
      utrError,
      paymentForm,
      membershipStatus,
      isUTRValid,
      paymentHistory,
      selectPlan,
      selectPaymentMethod,
      validateUTR,
      submitPayment,
      resetPaymentFlow,
      getDaysClass,
      formatDate,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.member-portal {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.portal-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.status-card {
  border-radius: 20px;
  padding: 3rem;
  margin-bottom: 3rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.status-green {
  background: linear-gradient(135deg, #06D6A0 0%, #05B48B 100%);
  color: white;
}

.status-yellow {
  background: linear-gradient(135deg, #FFD166 0%, #FFB533 100%);
  color: #8B6914;
}

.status-red {
  background: linear-gradient(135deg, #EF476F 0%, #D63D5E 100%);
  color: white;
}

.status-icon {
  font-size: 5rem;
  line-height: 1;
}

.status-content {
  flex: 1;
}

.status-title {
  font-family: 'Archivo Black', sans-serif;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}

.status-message {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  opacity: 0.95;
}

.status-details {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.85rem;
  opacity: 0.9;
}

.detail-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.detail-value.critical {
  color: #FF4444;
}

.detail-value.warning {
  color: #FFB533;
}

.detail-value.good {
  color: white;
}

.payment-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.75rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
}

.section-header p {
  color: var(--gray);
  font-size: 0.95rem;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.plan-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border: 3px solid var(--border);
  border-radius: 16px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.plan-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.plan-card:hover::before,
.plan-card.selected::before {
  transform: scaleX(1);
}

.plan-card:hover {
  transform: translateY(-8px);
  border-color: var(--primary);
  box-shadow: 0 12px 32px rgba(255, 107, 53, 0.2);
}

.plan-card.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, #FFF4F0 0%, #FFFAF8 100%);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.3);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.plan-name {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.5rem;
  color: var(--dark);
}

.plan-badge {
  background: var(--warning);
  color: #8B6914;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.plan-price {
  text-align: center;
  margin: 2rem 0;
}

.currency {
  font-size: 1.5rem;
  color: var(--gray);
  vertical-align: top;
}

.amount {
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary);
}

.plan-duration {
  text-align: center;
  color: var(--gray);
  font-size: 1rem;
  margin-bottom: 2rem;
}

.plan-features {
  margin-bottom: 2rem;
}

.feature {
  padding: 0.5rem 0;
  color: var(--dark);
  font-size: 0.9rem;
}

.select-btn {
  width: 100%;
  padding: 1rem;
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--primary);
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-btn:hover {
  background: var(--primary);
  color: white;
}

.select-btn.selected {
  background: var(--primary);
  color: white;
}

.payment-method-selector {
  margin-top: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 12px;
}

.payment-method-selector h3 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  color: var(--dark);
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.method-btn {
  background: white;
  border: 3px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.method-btn:hover {
  border-color: var(--primary);
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.method-btn.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, #FFF4F0 0%, #FFFAF8 100%);
}

.method-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.method-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
}

.method-desc {
  font-size: 0.85rem;
  color: var(--gray);
}

.continue-btn {
  width: 100%;
  padding: 1.25rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.4);
}

.payment-flow {
  animation: fadeIn 0.4s ease-out;
}

.back-btn {
  background: transparent;
  border: 2px solid var(--gray);
  color: var(--gray);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  cursor: pointer;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.back-btn:hover {
  border-color: var(--dark);
  color: var(--dark);
}

.payment-summary {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.payment-summary h3 {
  font-family: 'Archivo Black', sans-serif;
  margin-bottom: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}

.summary-row:last-child {
  border-bottom: none;
}

.summary-row.total {
  font-size: 1.25rem;
  margin-top: 0.5rem;
}

.summary-row .amount {
  color: var(--primary);
  font-weight: 700;
}

.qr-section {
  text-align: center;
  margin-bottom: 2rem;
}

.qr-section h4 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: var(--dark);
}

.qr-placeholder {
  background: white;
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 2rem;
  margin: 0 auto;
  max-width: 300px;
}

.qr-code {
  width: 200px;
  height: 200px;
  margin: 0 auto 1rem;
  background: white;
  border: 2px solid var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-code svg {
  width: 100%;
  height: 100%;
}

.qr-instructions {
  color: var(--gray);
  font-size: 0.9rem;
}

.utr-input-section,
.cash-payment {
  margin-top: 2rem;
}

.utr-input-section h4,
.cash-instructions h4 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--dark);
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

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--gray);
}

.error-message {
  color: var(--danger);
  font-size: 0.85rem;
  margin-top: 0.5rem;
  font-weight: 600;
}

.cash-instructions {
  background: linear-gradient(135deg, #E6F4FF 0%, #F0F8FF 100%);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.instruction-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.cash-instructions ol {
  text-align: left;
  max-width: 400px;
  margin: 1.5rem auto 0;
  padding-left: 1.5rem;
}

.cash-instructions li {
  padding: 0.5rem 0;
  font-size: 0.95rem;
  color: var(--dark);
}

.submit-payment-btn {
  width: 100%;
  padding: 1.25rem;
  background: linear-gradient(135deg, var(--success) 0%, #05B48B 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 2rem;
}

.submit-payment-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(6, 214, 160, 0.4);
}

.submit-payment-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 0.95rem;
  animation: slideDown 0.3s ease-out;
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

.history-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.history-section h2 {
  font-family: 'Archivo Black', sans-serif;
  font-size: 1.5rem;
  color: var(--dark);
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--gray);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.history-item:hover {
  border-color: var(--primary);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.history-plan {
  font-weight: 700;
  font-size: 1rem;
  color: var(--dark);
  margin-bottom: 0.25rem;
}

.history-date {
  font-size: 0.85rem;
  color: var(--gray);
}

.history-details {
  text-align: right;
}

.history-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.25rem;
}

.history-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  display: inline-block;
}

.history-status.pending {
  background: #FFF4E6;
  color: var(--warning);
}

.history-status.approved {
  background: #E6FFE6;
  color: var(--success);
}

.history-status.rejected {
  background: #FFE6E6;
  color: var(--danger);
}

@media (max-width: 768px) {
  .portal-container {
    padding: 0 1rem;
  }

  .status-card {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
  }

  .status-icon {
    font-size: 4rem;
  }

  .status-title {
    font-size: 2rem;
  }

  .status-details {
    grid-template-columns: 1fr;
  }

  .plans-grid {
    grid-template-columns: 1fr;
  }

  .method-grid {
    grid-template-columns: 1fr;
  }

  .history-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .history-details {
    text-align: center;
  }
}
</style>
