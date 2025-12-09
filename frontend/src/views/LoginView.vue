<template>
  <div class="login-view">
    <div class="login-container">
      <h1>Gate 관리 시스템</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="userId">사용자 ID</label>
          <input
            id="userId"
            v-model="userId"
            type="text"
            placeholder="사용자 ID를 입력하세요"
            required
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
            :disabled="loading"
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" :disabled="loading" class="login-button">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { setCookie } from '../utils/cookie'
import userService from '../services/user_service'

const router = useRouter()
const userId = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!userId.value.trim() || !password.value.trim()) {
    errorMessage.value = '사용자 ID와 비밀번호를 입력해주세요'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const data = await userService.login(userId.value, password.value)
    
    // 쿠키에 저장
    setCookie('api_key', data.api_key, 7) // 7일간 유지
    
    // 홈으로 리다이렉트
    router.push('/')
  } catch (error) {
    errorMessage.value = error.message || '로그인 실패: 사용자 ID 또는 비밀번호가 올바르지 않습니다'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
}

.login-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

input {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  padding: 12px;
  background-color: #fee;
  color: #c33;
  border-radius: 6px;
  font-size: 14px;
  text-align: center;
}

.login-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
