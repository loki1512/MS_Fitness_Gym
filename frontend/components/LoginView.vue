<!-- Login View Component -->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-section">
          <div class="logo-icon">💪</div>
          <h1 class="app-title">MS Power Fitness</h1>
          <p class="app-tagline">Retention-First Membership</p>
        </div>
      </div>

      <div class="login-tabs">
        <button 
          @click="activeTab = 'login'" 
          :class="['tab-btn', activeTab === 'login' ? 'active' : '']"
        >
          Login
        </button>
        <button 
          @click="activeTab = 'register'" 
          :class="['tab-btn', activeTab === 'register' ? 'active' : '']"
        >
          Register
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        
        <div class="form-group">
          <label>Email</label>
          <input 
            v-model="loginForm.email" 
            type="email" 
            required 
            placeholder="your@email.com"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            required 
            placeholder="••••••••"
            class="form-input"
          />
        </div>

        <button type="submit" :disabled="loading" class="submit-btn">
          <span v-if="!loading">🔐 Login</span>
          <span v-else>⏳ Logging in...</span>
        </button>
      </form>

      <!-- Register Form -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="form-group">
          <label>Full Name</label>
          <input 
            v-model="registerForm.name" 
            type="text" 
            required 
            placeholder="Rahul Sharma"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Phone Number</label>
          <input 
            v-model="registerForm.phone" 
            type="tel" 
            pattern="[0-9]{10}" 
            required 
            placeholder="9123456789"
            maxlength="10"
            class="form-input"
          />
          <small class="form-hint">10 digits without country code</small>
        </div>

        <div class="form-group">
          <label>Email</label>
          <input 
            v-model="registerForm.email" 
            type="email" 
            required 
            placeholder="your@email.com"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Date of Birth</label>
          <input 
            v-model="registerForm.date_of_birth" 
            type="date" 
            required 
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Gender</label>
          <select 
            v-model="registerForm.gender" 
            required 
            class="form-input"
          >
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            required 
            minlength="6"
            placeholder="••••••••"
            class="form-input"
          />
          <small class="form-hint">Minimum 6 characters</small>
        </div>

        <button type="submit" :disabled="loading" class="submit-btn">
          <span v-if="!loading">✨ Register</span>
          <span v-else>⏳ Creating account...</span>
        </button>
      </form>
    </div>

    <div class="login-footer">
      <p>🇮🇳 Built for Indian Micro-Enterprises | Zero Gateway Fees</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'LoginView',
  emits: ['login'],
  setup(props, { emit }) {
    const activeTab = ref('login');
    const loading = ref(false);
    const error = ref('');
    const success = ref('');

    const loginForm = ref({
      email: '',
      password: ''
    });

    const registerForm = ref({
      name: '',
      phone: '',
      email: '',
      password: '',
      date_of_birth: '',
      gender: ''
    });

    const handleLogin = async () => {
      loading.value = true;
      error.value = '';

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loginForm.value)
        });

        const data = await response.json();

        if (response.ok) {
          emit('login', data);
        } else {
          error.value = data.error || 'Login failed';
        }
      } catch (err) {
        error.value = 'Network error. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const handleRegister = async () => {
      loading.value = true;
      error.value = '';
      success.value = '';

      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(registerForm.value)
        });

        const data = await response.json();

        if (response.ok) {
          success.value = 'Registration successful! Please login.';
          setTimeout(() => {
            activeTab.value = 'login';
            loginForm.value.email = registerForm.value.email;
            registerForm.value = { name: '', phone: '', email: '', password: '', date_of_birth: '', gender: '' };
          }, 2000);
        } else {
          error.value = data.error || 'Registration failed';
        }
      } catch (err) {
        error.value = 'Network error. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    return {
      activeTab,
      loading,
      error,
      success,
      loginForm,
      registerForm,
      handleLogin,
      handleRegister
    };
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  max-width: 450px;
  width: 100%;
  overflow: hidden;
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

.login-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 3rem 2rem;
  text-align: center;
}

.logo-section {
  animation: fadeIn 0.8s ease-out 0.2s backwards;
}

.logo-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.app-title {
  font-family: 'Archivo Black', sans-serif;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}

.app-tagline {
  font-size: 0.9rem;
  opacity: 0.9;
}

.login-tabs {
  display: flex;
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  padding: 1.25rem;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  color: var(--gray);
  transition: all 0.3s ease;
  position: relative;
}

.tab-btn:hover {
  background: rgba(255, 107, 53, 0.05);
}

.tab-btn.active {
  color: var(--primary);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.auth-form {
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

.form-hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--gray);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
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

.login-footer {
  margin-top: 2rem;
  text-align: center;
  color: var(--light);
  opacity: 0.7;
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .login-card {
    border-radius: 12px;
  }

  .login-header {
    padding: 2rem 1.5rem;
  }

  .app-title {
    font-size: 1.75rem;
  }

  .auth-form {
    padding: 1.5rem;
  }
}
</style>
