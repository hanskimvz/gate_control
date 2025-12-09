<template>
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/gate">Gate</RouterLink>
      <RouterLink to="/logs">Logs</RouterLink>
      <RouterLink to="/users">Users</RouterLink>
      <div class="nav-right">
        <button v-if="isLoggedIn" @click="handleLogout" class="logout-button">
          로그아웃
        </button>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { computed } from 'vue'
import { getCookie, deleteCookie } from '../utils/cookie'

// Vue 컴포넌트 이름 규칙: multi-word
defineOptions({
  name: 'AppHeader'
})

const router = useRouter()

const isLoggedIn = computed(() => {
  return !!getCookie('api_key')
})

const handleLogout = () => {
  deleteCookie('api_key')
  router.push('/login')
}
</script>

<style scoped>
header {
  background-color: #2c3e50;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 2rem;
  padding: 0 2rem;
  align-items: center;
}

nav a {
  color: #ecf0f1;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

nav a:hover {
  background-color: #34495e;
}

nav a.router-link-exact-active {
  background-color: #3498db;
  color: white;
}

.nav-right {
  margin-left: auto;
}

.logout-button {
  padding: 0.5rem 1rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #c0392b;
}
</style>

