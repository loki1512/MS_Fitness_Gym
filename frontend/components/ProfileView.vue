<!-- Profile View Component -->
<template>
  <div class="profile-view">
    <div class="profile-container">
      <div class="profile-header">
        <h1 class="profile-title">👤 My Profile</h1>
        <p class="profile-subtitle">Manage your personal information</p>
      </div>

      <!-- View Mode -->
      <div v-if="!editMode" class="profile-card">
        <div class="profile-section">
          <h2 class="section-title">Personal Information</h2>
          
          <div class="info-grid">
            <div class="info-item">
              <label>Full Name</label>
              <div class="info-value">{{ profile.name }}</div>
            </div>

            <div class="info-item">
              <label>Phone Number</label>
              <div class="info-value">{{ profile.phone }}</div>
            </div>

            <div class="info-item">
              <label>Email Address</label>
              <div class="info-value">{{ profile.email }}</div>
            </div>

            <div class="info-item" v-if="profile.date_of_birth">
              <label>Date of Birth</label>
              <div class="info-value">{{ formatDate(profile.date_of_birth) }}</div>
            </div>

            <div class="info-item" v-if="profile.gender">
              <label>Gender</label>
              <div class="info-value">{{ profile.gender }}</div>
            </div>
          </div>
        </div>

        <div v-if="profile.membership" class="profile-section">
          <h2 class="section-title">Membership Details</h2>
          
          <div class="membership-info">
            <div class="membership-status" :class="profile.membership.active ? 'active' : 'inactive'">
              <span class="status-icon">{{ profile.membership.active ? '✅' : '🚫' }}</span>
              <span class="status-text">{{ profile.membership.active ? 'Active' : 'Inactive' }}</span>
            </div>

            <div v-if="profile.membership.active" class="membership-details">
              <div class="detail-row">
                <span>Plan:</span>
                <strong>{{ profile.membership.plan }}</strong>
              </div>
              <div class="detail-row">
                <span>Valid Until:</span>
                <strong>{{ formatDate(profile.membership.end_date) }}</strong>
              </div>
              <div class="detail-row">
                <span>Days Remaining:</span>
                <strong :class="getDaysClass(profile.membership.days_remaining)">
                  {{ profile.membership.days_remaining }} days
                </strong>
              </div>
            </div>
          </div>
        </div>

        <button @click="editMode = true" class="edit-btn">
          ✏️ Edit Profile
        </button>
      </div>

      <!-- Edit Mode -->
      <div v-else class="profile-card">
        <form @submit.prevent="saveProfile">
          <div class="profile-section">
            <h2 class="section-title">Edit Personal Information</h2>
            
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <div class="form-grid">
              <div class="form-group">
                <label>Full Name *</label>
                <input 
                  v-model="editForm.name" 
                  type="text" 
                  required 
                  class="form-input"
                  placeholder="Your full name"
                />
              </div>

              <div class="form-group">
                <label>Phone Number *</label>
                <input 
                  v-model="editForm.phone" 
                  type="tel" 
                  pattern="[0-9]{10}"
                  maxlength="10"
                  required 
                  class="form-input"
                  placeholder="10-digit phone number"
                />
              </div>

              <div class="form-group">
                <label>Email Address *</label>
                <input 
                  v-model="editForm.email" 
                  type="email" 
                  required 
                  class="form-input"
                  placeholder="your@email.com"
                />
              </div>

              <div class="form-group">
                <label>New Password (leave blank to keep current)</label>
                <input 
                  v-model="editForm.password" 
                  type="password" 
                  class="form-input"
                  minlength="6"
                  placeholder="New password (optional)"
                />
                <small class="form-hint">Minimum 6 characters</small>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" :disabled="loading" class="save-btn">
              <span v-if="!loading">💾 Save Changes</span>
              <span v-else>⏳ Saving...</span>
            </button>
            <button type="button" @click="cancelEdit" class="cancel-btn">
              ✖️ Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'ProfileView',
  props: {
    user: Object,
    token: String
  },
  emits: ['profile-updated'],
  setup(props, { emit }) {
    const profile = ref({});
    const editMode = ref(false);
    const loading = ref(false);
    const error = ref('');
    const success = ref('');
    
    const editForm = ref({
      name: '',
      phone: '',
      email: '',
      password: ''
    });

    const loadProfile = async () => {
      try {
        const response = await fetch('/api/profile', {
          headers: {
            'Authentication-Token': props.token
          }
        });

        if (response.ok) {
          profile.value = await response.json();
          // Populate edit form
          editForm.value = {
            name: profile.value.name,
            phone: profile.value.phone,
            email: profile.value.email,
            password: ''
          };
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
      }
    };

    const saveProfile = async () => {
      loading.value = true;
      error.value = '';
      success.value = '';

      try {
        const updateData = {
          name: editForm.value.name,
          phone: editForm.value.phone,
          email: editForm.value.email
        };

        if (editForm.value.password) {
          updateData.password = editForm.value.password;
        }

        const response = await fetch('/api/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': props.token
          },
          body: JSON.stringify(updateData)
        });

        const data = await response.json();

        if (response.ok) {
          success.value = 'Profile updated successfully!';
          setTimeout(() => {
            editMode.value = false;
            loadProfile();
            emit('profile-updated');
          }, 1500);
        } else {
          error.value = data.error || 'Failed to update profile';
        }
      } catch (err) {
        error.value = 'Network error. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const cancelEdit = () => {
      editMode.value = false;
      editForm.value = {
        name: profile.value.name,
        phone: profile.value.phone,
        email: profile.value.email,
        password: ''
      };
      error.value = '';
      success.value = '';
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      });
    };

    const getDaysClass = (days) => {
      if (days <= 3) return 'critical';
      if (days <= 7) return 'warning';
      return 'good';
    };

    onMounted(() => {
      loadProfile();
    });

    return {
      profile,
      editMode,
      loading,
      error,
      success,
      editForm,
      saveProfile,
      cancelEdit,
      formatDate,
      getDaysClass
    };
  }
};
</script>

<style scoped>
.profile-view {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.profile-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.profile-header {
  margin-bottom: 2rem;
  animation: fadeInDown 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.profile-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 2.5rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.profile-subtitle {
  color: var(--gray);
  font-size: 1rem;
}

.profile-card {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.6s ease-out;
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

.profile-section {
  margin-bottom: 2.5rem;
}

.section-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.5rem;
  color: var(--dark);
  margin-bottom: 1.5rem;
  font-weight: 700;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid var(--primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 12px;
  border: 2px solid var(--border);
  transition: all 0.3s ease;
}

.info-item:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
}

.info-item label {
  display: block;
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 1.1rem;
  color: var(--dark);
  font-weight: 600;
}

.membership-info {
  background: linear-gradient(135deg, #f0f8ff 0%, #fff 100%);
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px solid var(--secondary);
}

.membership-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 8px;
}

.membership-status.active {
  background: linear-gradient(135deg, #E6FFE6 0%, #F0FFF0 100%);
  color: var(--success);
}

.membership-status.inactive {
  background: linear-gradient(135deg, #FFE6EB 0%, #FFF5F7 100%);
  color: var(--danger);
}

.status-icon {
  font-size: 1.5rem;
}

.status-text {
  font-size: 1.25rem;
  font-weight: 700;
}

.membership-details {
  padding: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row span {
  color: var(--gray);
}

.detail-row strong {
  color: var(--dark);
  font-weight: 600;
}

.detail-row strong.critical {
  color: var(--danger);
}

.detail-row strong.warning {
  color: var(--warning);
}

.detail-row strong.good {
  color: var(--success);
}

.edit-btn {
  width: 100%;
  padding: 1.25rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 2rem;
}

.edit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
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
  font-size: 0.95rem;
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

.form-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2rem;
}

.save-btn {
  padding: 1.25rem;
  background: linear-gradient(135deg, var(--success) 0%, #05B48B 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
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
  padding: 1.25rem;
  background: transparent;
  color: var(--gray);
  border: 2px solid var(--gray);
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 71, 111, 0.05);
}

@media (max-width: 768px) {
  .profile-container {
    padding: 0 1rem;
  }

  .profile-card {
    padding: 1.5rem;
  }

  .profile-title {
    font-size: 2rem;
  }

  .info-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    grid-template-columns: 1fr;
  }
}
</style>
