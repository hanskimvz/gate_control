<template>
  <div class="user-list-view">
    <div class="container" :class="{ 'panel-open': showEditPanel }">
      <div class="header-section">
        <h1>사용자 관리</h1>
        <button @click="openAddPanel" class="add-button">+ 사용자 추가</button>
      </div>
      
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="total-count">총 {{ filteredUsers.length }}명</span>
          <select v-model="itemsPerPage" class="items-per-page">
            <option :value="10">10개씩</option>
            <option :value="20">20개씩</option>
            <option :value="50">50개씩</option>
            <option :value="100">100개씩</option>
          </select>
        </div>
        <div class="toolbar-right">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="사용자 검색..."
              class="search-input"
            />
            <button @click="performSearch" class="search-button">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.3333 10.3333H10.6267L10.3733 10.0933C11.3333 8.92 11.92 7.40667 11.92 5.76C11.92 2.58 9.34 0 6.16 0C2.98 0 0.4 2.58 0.4 5.76C0.4 8.94 2.98 11.52 6.16 11.52C7.80667 11.52 9.32 10.9333 10.4933 9.97333L10.7333 10.2267V10.9333L14.4 14.5867L15.9467 13.04L11.3333 10.3333ZM6.16 10.3333C3.78 10.3333 1.85333 8.40667 1.85333 6.02667C1.85333 3.64667 3.78 1.72 6.16 1.72C8.54 1.72 10.4667 3.64667 10.4667 6.02667C10.4667 8.40667 8.54 10.3333 6.16 10.3333Z" fill="currentColor"/>
              </svg>
            </button>
          </div>
          <button @click="loadUsers" class="refresh-button">새로고침</button>
        </div>
      </div>
      
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>ID</th>
              <th>이름</th>
              <th>등록일</th>
              <th>API Key</th>
              <th>유효날짜</th>
              <th>유효시간</th>
              <th>상태</th>
              <th>작업</th>
              <th>링크</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(user, index) in paginatedUsers" 
              :key="user._id"
              :class="{ 'highlighted': highlightedRow === user._id }"
              @mouseenter="highlightedRow = user._id"
              @mouseleave="highlightedRow = null"
            >
              <td class="index-cell">{{ (currentPage - 1) * itemsPerPage + index + 1 }}</td>
              <td class="user-id-cell">{{ user.user_id }}</td>
              <td class="user-name-cell">{{ user.name || '-' }}</td>
              <td>{{ formatDate(user.regdate) }}</td>
              <td class="api-key-cell">
                <span :class="{ 'invalid-key': !isValidApiKey(user) }">
                  {{ truncateApiKey(user.api_key) }}
                </span>
              </td>
              <td>{{ formatDateRange(user.date_from, user.date_to) }}</td>
              <td>{{ formatTimeRange(user.hour_from, user.hour_to) }}</td>
              <td>
                <span :class="['status-badge', user.flag === 'y' ? 'active' : 'inactive']">
                  {{ user.flag === 'y' ? '활성' : '비활성' }}
                </span>
              </td>
              <td>
                <button @click="openEditPanel(user._id)" class="edit-button">수정</button>
              </td>
              <td>
                <button @click="showLinkModal(user.api_key)" class="link-button">링크</button>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="10" class="empty-message">
                {{ searchQuery ? '검색 결과가 없습니다.' : '사용자가 없습니다.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="currentPage = 1" 
          :disabled="currentPage === 1"
          class="page-button"
        >
          처음
        </button>
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-button"
        >
          이전
        </button>
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-button"
        >
          다음
        </button>
        <button 
          @click="currentPage = totalPages" 
          :disabled="currentPage === totalPages"
          class="page-button"
        >
          마지막
        </button>
      </div>
    </div>
    
    <!-- 사용자 편집 패널 -->
    <UserEditPanel
      v-model:visible="showEditPanel"
      :user-id="editingUserId"
      :is-new-user="isNewUser"
      @saved="handleUserSaved"
    />
    
    <!-- 링크 모달 -->
    <Modal
      v-model:visible="showLinkModalVisible"
      title="Gate 접근 링크"
    >
      <div class="link-content">
        <p class="link-description">아래 링크를 복사하여 사용하세요:</p>
        <div class="link-box">
          <input
            :value="gateLink"
            readonly
            class="link-input"
            :id="'link-input-' + Date.now()"
          />
          <button @click="copyLink" class="copy-button">복사</button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import UserEditPanel from './UserEditPanel.vue'
import Modal from '@/components/Modal.vue'
import userService from '@/services/user_service'

const users = ref([])
const searchQuery = ref('')
const itemsPerPage = ref(20)
const currentPage = ref(1)
const highlightedRow = ref(null)
const showEditPanel = ref(false)
const editingUserId = ref(null)
const isNewUser = ref(false)
const showLinkModalVisible = ref(false)
const gateLink = ref('')

const loadUsers = async () => {
  try {
    const data = await userService.listUsers()
    users.value = data
    currentPage.value = 1
  } catch (error) {
    console.error('사용자 목록 로딩 실패:', error)
  }
}

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) {
    return users.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.user_id.toLowerCase().includes(query) ||
    (user.name && user.name.toLowerCase().includes(query)) ||
    user.api_key.toLowerCase().includes(query) ||
    (user.regdate && formatDate(user.regdate).toLowerCase().includes(query))
  )
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value)
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredUsers.value.slice(start, end)
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR')
}

const formatDateRange = (dateFrom, dateTo) => {
  if (!dateFrom || dateFrom === '0000-00-00') return '-'
  if (!dateTo || dateTo === '0000-00-00') return dateFrom
  return `${dateFrom} ~ ${dateTo}`
}

const formatTimeRange = (hourFrom, hourTo) => {
  const formatHour = (hour) => {
    if (hour === null || hour === undefined) return '00:00'
    const h = String(hour).padStart(2, '0')
    return `${h}:00`
  }
  
  const from = formatHour(hourFrom)
  const to = formatHour(hourTo)
  
  if (from === '00:00' && to === '00:00') return '-'
  return `${from} ~ ${to}`
}

const truncateApiKey = (apiKey) => {
  if (!apiKey) return '-'
  if (apiKey.length > 20) {
    return apiKey.substring(0, 20) + '...'
  }
  return apiKey
}

const isValidApiKey = (user) => {
  if (!user) return false
  return true
}

const performSearch = () => {
  currentPage.value = 1
}

const openEditPanel = (id) => {
  editingUserId.value = id
  isNewUser.value = false
  showEditPanel.value = true
}

const openAddPanel = () => {
  editingUserId.value = null
  isNewUser.value = true
  showEditPanel.value = true
}

const handleUserSaved = () => {
  loadUsers()
}

const showLinkModal = (apiKey) => {
  gateLink.value = `http://gate.amisense.com/gate?api_key=${apiKey}`
  showLinkModalVisible.value = true
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(gateLink.value)
    alert('링크가 복사되었습니다.')
  } catch {
    // 클립보드 API가 지원되지 않는 경우 대체 방법
    const input = document.querySelector('.link-input')
    if (input) {
      input.select()
      document.execCommand('copy')
      alert('링크가 복사되었습니다.')
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-list-view {
  width: 100%;
  min-height: 100%;
  background-color: #f5f5f5;
  padding: 20px;
  box-sizing: border-box;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: margin-right 0.3s ease;
}

.container.panel-open {
  margin-right: 700px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
}

h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.add-button {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
}

.add-button:hover {
  background-color: #1976D2;
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.4);
  transform: translateY(-1px);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-count {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.items-per-page {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  cursor: pointer;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  overflow: hidden;
}

.search-input {
  padding: 8px 12px;
  border: none;
  outline: none;
  font-size: 14px;
  width: 200px;
}

.search-input::placeholder {
  color: #999;
}

.search-button {
  padding: 8px 12px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  transition: color 0.3s;
}

.search-button:hover {
  color: #2196F3;
}

.refresh-button {
  padding: 8px 16px;
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.refresh-button:hover {
  background-color: #f5f5f5;
  border-color: #2196F3;
  color: #2196F3;
}

.table-container {
  overflow-x: auto;
  border-radius: 6px;
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
  padding: 14px 12px;
  text-align: left;
  font-size: 13px;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

td {
  padding: 14px 12px;
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

tbody tr.highlighted {
  background-color: #e3f2fd;
}

.index-cell {
  text-align: center;
  color: #999;
  font-weight: 500;
  width: 50px;
}

.user-id-cell {
  font-weight: 500;
  color: #333;
}

.user-name-cell {
  font-weight: 500;
  color: #333;
}

.api-key-cell {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.invalid-key {
  color: #f44336;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background-color: #ffebee;
  color: #c62828;
}

.edit-button {
  padding: 6px 16px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.edit-button:hover {
  background-color: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
}

.link-button {
  padding: 6px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.link-button:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.link-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.link-description {
  margin: 0;
  color: #555;
  font-size: 14px;
}

.link-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.link-input {
  flex: 1;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'Courier New', monospace;
  background-color: #f9f9f9;
  color: #333;
}

.copy-button {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.copy-button:hover {
  background-color: #1976D2;
}

.empty-message {
  text-align: center;
  color: #999;
  padding: 60px 20px;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.page-button {
  padding: 8px 16px;
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.page-button:hover:not(:disabled) {
  background-color: #2196F3;
  color: white;
  border-color: #2196F3;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  padding: 8px 16px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
</style>

