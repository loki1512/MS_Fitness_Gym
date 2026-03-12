import { createApp } from 'vue';
import App from './App.vue';

const app = createApp(App);
app.config.globalProperties.$apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
app.mount('#app');
