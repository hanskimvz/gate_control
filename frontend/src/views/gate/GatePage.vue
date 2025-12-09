<template>
  <div class="gate-view">
    <div class="container">
      <!-- 환영 메시지 -->
      <div class="welcome-section">
        <h1 v-if="userInfo.user_name" class="welcome-message">
          <span class="welcome-text">{{ userInfo.user_name }}님 환영합니다.</span>
        </h1>
        <h1 v-else>
          <span>로딩 중...</span>
        </h1>
        <div v-if="userInfo.valid === false" class="invalid-notice">
          <p>현재 접근 권한이 없습니다. 관리자에게 문의하세요.</p>
        </div>
      </div>
      
      <!-- 컨트롤 버튼 -->
      <div class="controls">
        <button 
          class="open-button" 
          :class="{ 'disabled': !isOpenEnabled }"
          @click="openDoor"
          :disabled="!isOpenEnabled || loading"
        >
          {{ loading ? '처리 중...' : 'OPEN' }}
        </button>
        <button 
          class="refresh-button" 
          @click="refresh"
          :disabled="loading"
        >
          새로고침
        </button>
      </div>
      
      <!-- 카메라 선택 -->
      <div v-if="userInfo.camera_list && userInfo.camera_list.length > 0" class="camera-selector">
        <label for="camera-select">카메라 선택:</label>
        <select 
          id="camera-select"
          v-model="selectedCamera"
          @change="onCameraChange"
          class="camera-select"
        >
          <option 
            v-for="camera in userInfo.camera_list" 
            :key="camera" 
            :value="camera"
          >
            {{ camera }}
          </option>
        </select>
      </div>
      
      <!-- 결과 메시지 -->
      <div v-if="resultMessage" class="result" :class="{ error: hasError }">
        {{ resultMessage }}
      </div>
      
      <!-- 스냅샷 -->
      <div class="snapshot-container">
        <img 
          v-if="snapshot" 
          :src="snapshot" 
          alt="카메라 스냅샷"
          class="snapshot"
          @click="showBigPicture"
        />
        <div v-else class="loading">스냅샷 로딩 중...</div>
      </div>
    </div>
    
    <!-- 큰 이미지 보기 -->
    <div 
      v-if="showBig" 
      class="big-picture-wrapper"
      @click="hideBigPicture"
    >
      <div class="big-picture">
        <img :src="snapshot" alt="큰 이미지" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import gateService from '@/services/gate_service'

const route = useRoute()
const apiKey = ref(route.query.api_key || '')
const userInfo = ref({})
const snapshot = ref(null)
const loading = ref(false)
const resultMessage = ref('')
const hasError = ref(false)
const showBig = ref(false)
const snapshotIntervalId = ref(null)
const snapshotLoading = ref(false)
const selectedCamera = ref('main')

// OPEN 버튼 활성화 여부 계산
const isOpenEnabled = computed(() => {
  return userInfo.value.valid === true && !loading.value
})

const loadUserInfo = async () => {
  try {
    const data = await gateService.ready(apiKey.value)
    userInfo.value = data
    // 카메라 리스트가 있고 기본값이 리스트에 없으면 첫 번째 카메라 선택
    if (data.camera_list && data.camera_list.length > 0) {
      if (!data.camera_list.includes(selectedCamera.value)) {
        selectedCamera.value = data.camera_list[0]
      }
    }
  } catch (error) {
    resultMessage.value = error.message || '사용자 인증 실패'
    hasError.value = true
  }
}

const loadSnapshot = async () => {
  if (snapshotLoading.value) {
    // 이미 로딩 중이면 스킵
    return
  }
  
  snapshotLoading.value = true
  try {
    const imgData = await gateService.getSnapshot(apiKey.value, selectedCamera.value)
    snapshot.value = imgData
  } catch (error) {
    console.error('스냅샷 로딩 실패:', error)
  } finally {
    snapshotLoading.value = false
  }
}

const onCameraChange = () => {
  // 카메라 변경 시 스냅샷 새로고침
  loadSnapshot()
}

const getRequestInfo = () => {
  return {
    user_agent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    screen_width: window.screen.width,
    screen_height: window.screen.height,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timestamp: new Date().toISOString()
  }
}

const openDoor = async () => {
  loading.value = true
  hasError.value = false
  resultMessage.value = ''
  
  try {
    // 원격 접속 정보 수집
    const requestInfo = getRequestInfo()
    const data = await gateService.openDoor(apiKey.value, requestInfo)
    resultMessage.value = data.message || '문이 열렸습니다'
    hasError.value = false
    // 문 열기 후 스냅샷 새로고침
    await loadSnapshot()
  } catch (error) {
    resultMessage.value = error.message || '문 열기 실패'
    hasError.value = true
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  resultMessage.value = ''
  hasError.value = false
  loadSnapshot()
}

const showBigPicture = () => {
  showBig.value = true
}

const hideBigPicture = () => {
  showBig.value = false
}

onMounted(() => {
  if (!apiKey.value) {
    resultMessage.value = 'API 키가 필요합니다'
    hasError.value = true
    return
  }
  
  loadUserInfo()
  loadSnapshot()
  
  // 20초 동안 2초마다 스냅샷 새로고침 (이전 요청 완료 후 다음 요청)
  let count = 0
  const scheduleNextSnapshot = async () => {
    if (count >= 10) {
      // 10번 실행 후 (20초 후) 중지
      snapshotIntervalId.value = null
      return
    }
    
    count++
    await loadSnapshot()
    
    // 다음 요청 스케줄링 (2초 후)
    snapshotIntervalId.value = setTimeout(() => {
      scheduleNextSnapshot()
    }, 2000)
  }
  
  // 첫 번째 요청은 2초 후 시작
  snapshotIntervalId.value = setTimeout(() => {
    scheduleNextSnapshot()
  }, 2000)
})

onBeforeUnmount(() => {
  // 컴포넌트 언마운트 시 timeout 정리
  if (snapshotIntervalId.value) {
    clearTimeout(snapshotIntervalId.value)
    snapshotIntervalId.value = null
  }
})
</script>

<style scoped>
.gate-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  max-width: 900px;
  width: 100%;
  background: white;
  border-radius: 16px;
  padding: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.welcome-section {
  text-align: center;
  margin-top: 5px;
  margin-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.welcome-message {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

.welcome-message .welcome-text {
  display: block;
  font-size: 28px;
  font-weight: 500;
  color: #666;
  margin-top: 8px;
}

.invalid-notice {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  color: #856404;
}

.invalid-notice p {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.controls {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.open-button {
  width: 320px;
  height: 220px;
  font-size: 64px;
  font-weight: bold;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.open-button:hover:not(:disabled):not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.open-button:active:not(:disabled):not(.disabled) {
  transform: translateY(0);
}

.open-button:disabled,
.open-button.disabled {
  background: linear-gradient(135deg, #cccccc 0%, #999999 100%);
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.6;
}

.refresh-button {
  width: 320px;
  height: 60px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #2196F3 0%, #0b7dda 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.refresh-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.refresh-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.6;
}

.camera-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.camera-selector label {
  font-size: 16px;
  font-weight: 500;
  color: #555;
}

.camera-select {
  padding: 8px 16px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background-color: white;
  color: #333;
  cursor: pointer;
  transition: border-color 0.3s;
  min-width: 150px;
}

.camera-select:focus {
  outline: none;
  border-color: #2196F3;
}

.result {
  text-align: center;
  padding: 16px;
  margin-bottom: 25px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #4CAF50;
  background-color: #e8f5e9;
  border: 1px solid #4CAF50;
}

.result.error {
  color: #f44336;
  background-color: #ffebee;
  border-color: #f44336;
}

.snapshot-container {
  text-align: center;
  margin-top: 30px;
}

.snapshot {
  width: 100%;
  max-width: 100%;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.snapshot:hover {
  transform: scale(1.02);
}

.loading {
  padding: 60px;
  color: #666;
  font-size: 18px;
  font-weight: 500;
}

.big-picture-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  cursor: pointer;
}

.big-picture {
  max-width: 95%;
  max-height: 95%;
}

.big-picture img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .container {
    padding: 25px;
  }

  .welcome-message {
    font-size: 24px;
  }

  .welcome-message .welcome-text {
    font-size: 20px;
  }

  .controls {
    flex-direction: column;
  }

  .open-button {
    width: 100%;
    height: 100px;
    font-size: 48px;
  }

  .refresh-button {
    width: 100%;
    height: 50px;
  }
}
</style>

