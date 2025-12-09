<template>
  <div class="log-view">
    <div class="container">
      <div class="header-section">
        <h1>로그 목록</h1>
        <div class="header-right">
          <div class="info-badge">전체 {{ total }}개</div>
          <button @click="loadLogs" class="refresh-button">새로고침</button>
        </div>
      </div>
      
      <div class="pagination">
        <button 
          @click="prevPage" 
          :disabled="page === 1"
          class="page-button"
        >
          이전
        </button>
        <span class="page-info">페이지 {{ page }} / {{ totalPages }}</span>
        <button 
          @click="nextPage" 
          :disabled="page * offset >= total"
          class="page-button"
        >
          다음
        </button>
      </div>
      
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>날짜</th>
              <th>사용자</th>
              <th>이벤트</th>
              <th>IP</th>
              <th>스냅샷</th>
              <th>User Agent</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="log in logs" 
              :key="log.pk"
              class="log-row"
            >
              <td class="id-cell">{{ log.pk }}</td>
              <td class="date-cell">{{ formatDate(log.regdate) }}</td>
              <td class="user-cell">{{ log.user_id || '-' }}</td>
              <td class="event-cell">
                <span :class="['event-badge', getEventModeClass(log.eventinfo?.mode)]">
                  {{ log.eventinfo?.mode || '-' }}
                </span>
              </td>
              <td class="ip-cell">{{ log.eventinfo?.ip || '-' }}</td>
              <td class="snapshot-cell">
                <img 
                  v-if="log.snapshot" 
                  :src="log.snapshot" 
                  alt="스냅샷"
                  class="thumbnail"
                  @click="showBigPicture(log.snapshot)"
                />
                <span v-else class="no-image">-</span>
              </td>
              <td class="user-agent-cell">{{ truncateUserAgent(log.user_agent) }}</td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="7" class="empty-message">로그가 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 큰 이미지 보기 -->
    <div 
      v-if="bigPicture" 
      class="big-picture-wrapper"
      @click="hideBigPicture"
    >
      <div class="big-picture">
        <img :src="bigPicture" alt="큰 이미지" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiService from '@/services/api'

const logs = ref([])
const page = ref(1)
const offset = ref(20)
const total = ref(0)
const bigPicture = ref(null)

const loadLogs = async () => {
  try {
    const data = await apiService.listLogs(page.value, offset.value)
    logs.value = data.logs
    total.value = data.total
  } catch (error) {
    console.error('로그 로딩 실패:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const truncateUserAgent = (userAgent) => {
  if (!userAgent) return '-'
  if (userAgent.length > 50) {
    return userAgent.substring(0, 50) + '...'
  }
  return userAgent
}

const getEventModeClass = (mode) => {
  if (!mode) return ''
  const modeMap = {
    'open': 'mode-open',
    'exit': 'mode-exit',
    'close': 'mode-close'
  }
  return modeMap[mode.toLowerCase()] || ''
}

const showBigPicture = (src) => {
  bigPicture.value = src
}

const hideBigPicture = () => {
  bigPicture.value = null
}

const prevPage = () => {
  if (page.value > 1) {
    page.value--
    loadLogs()
  }
}

const nextPage = () => {
  if (page.value * offset.value < total.value) {
    page.value++
    loadLogs()
  }
}

const totalPages = computed(() => {
  return Math.ceil(total.value / offset.value)
})

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.log-view {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-badge {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.refresh-button {
  padding: 10px 20px;
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.refresh-button:hover {
  background-color: #f5f5f5;
  border-color: #2196F3;
  color: #2196F3;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.page-button {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.page-button:hover:not(:disabled) {
  background-color: #0b7dda;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.page-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.page-info {
  font-size: 15px;
  font-weight: 500;
  color: #555;
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
  padding: 16px 12px;
  text-align: left;
  font-size: 13px;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

td {
  padding: 16px 12px;
  font-size: 14px;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
}

tbody tr {
  transition: background-color 0.2s;
}

tbody tr:hover {
  background-color: #f8f9fa;
}

.id-cell {
  font-weight: 500;
  color: #666;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.date-cell {
  white-space: nowrap;
  color: #555;
}

.user-cell {
  font-weight: 500;
  color: #333;
}

.event-cell {
  text-align: center;
}

.event-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.event-badge.mode-open {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.event-badge.mode-exit {
  background-color: #fff3e0;
  color: #e65100;
}

.event-badge.mode-close {
  background-color: #fce4ec;
  color: #c2185b;
}

.ip-cell {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #666;
}

.snapshot-cell {
  text-align: center;
}

.thumbnail {
  width: 120px;
  height: 80px;
  object-fit: cover;
  cursor: pointer;
  border-radius: 6px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
}

.thumbnail:hover {
  border-color: #2196F3;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.no-image {
  color: #999;
  font-style: italic;
}

.user-agent-cell {
  font-size: 12px;
  color: #666;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
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
</style>

