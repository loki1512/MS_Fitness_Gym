<!-- MS Power Fitness - Main App Component -->
<template>
  <div id="app" class="app-container">
    <!-- Loading Screen for Cold Starts -->
    <div v-if="isLoading" class="loading-screen">
      <div class="loading-content">
        <div class="gym-logo">
          <div class="dumbbell-icon">
            <div class="weight"></div>
            <div class="bar"></div>
            <div class="weight"></div>
          </div>
        </div>
        <h2 class="loading-text">MS Power Fitness</h2>
        <div class="loading-spinner"></div>
        <p class="loading-subtext">Initializing system...</p>
      </div>
    </div>

    <!-- Main Application -->
    <div v-else class="main-app">
      <!-- Navigation Bar -->
      <nav v-if="user" class="navbar">
        <div class="nav-container">
          <div class="nav-brand">
            <div class="brand-icon">💪</div>
            <span class="brand-name">MS Power</span>
          </div>
          
          <div class="nav-menu">
            <button 
              v-if="user.role === 'admin' || user.role === 'manager'" 
              @click="currentView = 'admin'" 
              :class="['nav-btn', currentView === 'admin' ? 'active' : '']"
            >
              📊 Dashboard
            </button>
            
            <button 
              v-if="user.role === 'admin' || user.role === 'manager'" 
              @click="currentView = 'members'" 
              :class="['nav-btn', currentView === 'members' ? 'active' : '']"
            >
              👥 Member Management
            </button>

            <button 
              v-if="user.role === 'admin' || user.role === 'manager'" 
              @click="currentView = 'transactions'" 
              :class="['nav-btn', currentView === 'transactions' ? 'active' : '']"
            >
              💰 Transactions
            </button>
            
            <button 
              v-if="user.role === 'member'" 
              @click="currentView = 'member'" 
              :class="['nav-btn', currentView === 'member' ? 'active' : '']"
            >
              🏋️ My Access
            </button>
            
            <button 
              @click="currentView = 'profile'" 
              :class="['nav-btn', currentView === 'profile' ? 'active' : '']"
            >
              👤 Profile
            </button>
            
            <button @click="logout" class="nav-btn logout-btn">
              🚪 Logout
            </button>
          </div>
        </div>
      </nav>

      <!-- View Components -->
      <div class="view-container">
        <!-- Login View -->
        <LoginView 
          v-if="!user" 
          @login="handleLogin"
        />

        <!-- Admin Dashboard -->
        <AdminDashboard 
          v-else-if="user && (user.role === 'admin' || user.role === 'manager') && currentView === 'admin'"
          :user="user"
          :token="authToken"
        />

        <!-- Member Management -->
        <MemberManagement 
          v-else-if="user && (user.role === 'admin' || user.role === 'manager') && currentView === 'members'"
          :user="user"
          :token="authToken"
        />

        <!-- Member Portal -->
       <MemberPortal 
        v-else-if="!isLoading && user && user.role === 'member' && currentView === 'member'"
        :key="user.membership?.active" 
        :user="user"
        :token="authToken"
        @profile-updated="refreshUser"
      />

        <!-- Profile View -->
        <ProfileView 
          v-else-if="user && currentView === 'profile'"
          :user="user"
          :token="authToken"
          @profile-updated="refreshUser"
        />

        <!-- Transactions View -->
        <TransactionsView 
          v-else-if="user && (user.role === 'admin' || user.role === 'manager') && currentView === 'transactions'"
          :user="user"
          :token="authToken"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import LoginView from './components/LoginView.vue';
import AdminDashboard from './components/AdminDashboard.vue';
import MemberPortal from './components/MemberPortal.vue';
import MemberManagement from './components/MemberManagement.vue';
import ProfileView from './components/ProfileView.vue';
import TransactionsView from './components/TransactionsView.vue';


export default {
  name: 'App',
  components: {
    LoginView,
    AdminDashboard,
    MemberPortal,
    MemberManagement,
    ProfileView,
    TransactionsView
  },
  setup() {
    const isLoading = ref(true);
    const user = ref(null);
    const authToken = ref(null);
    const currentView = ref('member');

    onMounted(async () => {
      // Simulate cold start loading (for Render.com free tier)
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Check for existing session
      const token = localStorage.getItem('authToken');
      if (token) {
        authToken.value = token;
        await fetchCurrentUser(token);
      }
      
      isLoading.value = false;
    });

    const fetchCurrentUser = async (token) => {
      try {
        const response = await fetch('${this.$apiUrl}/api/me', {
          headers: {
            'Authentication-Token': token
          },
          cache: 'no-store',
          pragma: 'no-cache'
        });
        
        if (response.ok) {
          user.value = await response.json();
          currentView.value = (user.value.role === 'admin' || user.value.role === 'manager') ? 'admin' : 'member';
        } else {
          localStorage.removeItem('authToken');
          authToken.value = null;
        }
      } catch (error) {
        console.error('Failed to fetch user:', error);
      }
    };

    const refreshUser = async () => {
      if (authToken.value) {
        await fetchCurrentUser(authToken.value);
      }
    };

    const handleLogin = (loginData) => {
      user.value = loginData.user;
      authToken.value = loginData.token;
      localStorage.setItem('authToken', loginData.token);
      currentView.value = (loginData.user.role === 'admin' || loginData.user.role === 'manager') ? 'admin' : 'member';
      window.location.reload();
    };

    const logout = () => {
      user.value = null;
      authToken.value = null;
      localStorage.removeItem('authToken');
      currentView.value = 'member';
    };

    return {
      isLoading,
      user,
      authToken,
      currentView,
      handleLogin,
      logout,
      refreshUser
    };
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Fredoka:wght@600;700&display=swap');

:root {
  --primary: #FF6B35;
  --primary-dark: #E85A2B;
  --secondary: #004E89;
  --success: #06D6A0;
  --danger: #EF476F;
  --warning: #FFD166;
  --dark: #1A1A2E;
  --light: #F7F7F7;
  --gray: #6C757D;
  --border: #E0E0E0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
  color: var(--dark);
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
}

/* Loading Screen */
.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
}

.loading-content {
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

.gym-logo {
  margin-bottom: 2rem;
}

.dumbbell-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  animation: lift 1.5s ease-in-out infinite;
}

.weight {
  width: 30px;
  height: 40px;
  background: var(--primary);
  border-radius: 4px;
}

.bar {
  width: 80px;
  height: 10px;
  background: var(--light);
  border-radius: 5px;
}

@keyframes lift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.loading-text {
  font-family: 'Archivo Black', sans-serif;
  font-size: 2.5rem;
  color: var(--light);
  margin-bottom: 1rem;
  letter-spacing: 2px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  margin: 2rem auto;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-subtext {
  color: var(--light);
  opacity: 0.7;
  font-size: 0.9rem;
}

/* Navigation */
.navbar {
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 2px solid var(--primary);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  font-size: 2rem;
}

.brand-name {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.5rem;
  color: var(--light);
  letter-spacing: 1px;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--light);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-family: 'Space Mono', monospace;
  font-size: 0.9rem;
  font-weight: 700;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
}

.nav-btn.active {
  background: var(--primary);
  box-shadow: 0 0 20px rgba(255, 107, 53, 0.6);
}

.logout-btn {
  border-color: var(--danger);
}

.logout-btn:hover {
  background: var(--danger);
  box-shadow: 0 4px 12px rgba(239, 71, 111, 0.4);
}

/* View Container */
.view-container {
  min-height: calc(100vh - 80px);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }

  .nav-menu {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .nav-btn {
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
  }

  .loading-text {
    font-size: 2rem;
  }
}
</style>
