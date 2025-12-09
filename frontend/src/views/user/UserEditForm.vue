<template>
  <form @submit.prevent="handleSubmit" class="user-form">
    <div class="form-row">
      <div class="form-group">
        <label for="user_id">사용자 ID *</label>
        <input
          id="user_id"
          v-model="userData.user_id"
          type="text"
          required
          placeholder="사용자 ID를 입력하세요"
        />
      </div>
      
      <div class="form-group">
        <label for="name">이름</label>
        <input
          id="name"
          v-model="userData.name"
          type="text"
          placeholder="이름을 입력하세요"
        />
      </div>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label for="date_from">시작 날짜</label>
        <input
          id="date_from"
          v-model="userData.date_from"
          type="date"
        />
      </div>
      
      <div class="form-group">
        <label for="date_to">종료 날짜</label>
        <input
          id="date_to"
          v-model="userData.date_to"
          type="date"
        />
      </div>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label for="hour_from">시작 시간</label>
        <input
          id="hour_from"
          v-model="hourFromInput"
          type="time"
          placeholder="HH:mm"
        />
      </div>
      
      <div class="form-group">
        <label for="hour_to">종료 시간</label>
        <input
          id="hour_to"
          v-model="hourToInput"
          type="time"
          placeholder="HH:mm"
        />
      </div>
    </div>
    
    <div class="form-group">
      <label for="plates">차량 번호판</label>
      <input
        id="plates"
        v-model="platesInput"
        type="text"
        placeholder="쉼표로 구분하여 입력 (예: 104하7693, 297너5241)"
      />
      <small class="form-hint">여러 개의 차량 번호판을 쉼표로 구분하여 입력하세요</small>
    </div>
    
    <div class="form-group">
      <label class="checkbox-label">
        <input
          type="checkbox"
          v-model="userData.flag"
          true-value="y"
          false-value="n"
        />
        <span>활성화</span>
      </label>
    </div>
    
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    
    <div class="form-actions">
      <div class="form-actions-left">
        <button 
          v-if="!isNewUser && userId" 
          type="button" 
          @click="handleDelete" 
          class="delete-button"
          :disabled="loading"
        >
          삭제
        </button>
      </div>
      <div class="form-actions-right">
        <button type="button" @click="handleCancel" class="cancel-button">취소</button>
        <button type="submit" :disabled="loading" class="save-button">
          {{ loading ? '저장 중...' : '저장' }}
        </button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'
import userService from '@/services/user_service'

const props = defineProps({
  userId: {
    type: String,
    default: null
  },
  isNewUser: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['saved', 'cancel'])

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const userData = ref({
  user_id: '',
  name: '',
  date_from: '0000-00-00',
  hour_from: 0,
  date_to: '0000-00-00',
  hour_to: 0,
  flag: 'y',
  plates: []
})

const platesInput = ref('')
const hourFromInput = ref('00:00')
const hourToInput = ref('00:00')

// int 시간을 HH:mm 형식으로 변환
const intToTime = (hour) => {
  if (hour === null || hour === undefined) return '00:00'
  const h = String(hour).padStart(2, '0')
  return `${h}:00`
}

// HH:mm 형식을 int로 변환
const timeToInt = (timeString) => {
  if (!timeString) return 0
  const [hour] = timeString.split(':')
  return parseInt(hour, 10) || 0
}

const resetForm = () => {
  userData.value = {
    user_id: '',
    name: '',
    date_from: '0000-00-00',
    hour_from: 0,
    date_to: '0000-00-00',
    hour_to: 0,
    flag: 'y',
    plates: []
  }
  platesInput.value = ''
  hourFromInput.value = '00:00'
  hourToInput.value = '00:00'
  errorMessage.value = ''
  successMessage.value = ''
}

const loadUser = async () => {
  if (props.isNewUser || !props.userId) {
    resetForm()
    return
  }
  
  try {
    const users = await userService.listUsers()
    const user = users.find(u => u._id === String(props.userId))
    if (user) {
      userData.value = {
        user_id: user.user_id,
        name: user.name || '',
        date_from: user.date_from,
        hour_from: user.hour_from,
        date_to: user.date_to,
        hour_to: user.hour_to,
        flag: user.flag,
        plates: user.plates || []
      }
      platesInput.value = (user.plates && user.plates.length > 0) ? user.plates.join(', ') : ''
      hourFromInput.value = intToTime(user.hour_from)
      hourToInput.value = intToTime(user.hour_to)
    } else {
      errorMessage.value = '사용자를 찾을 수 없습니다.'
    }
  } catch (error) {
    console.error('사용자 로딩 실패:', error)
    errorMessage.value = '사용자 정보를 불러오는데 실패했습니다.'
  }
}

const handleSubmit = async () => {
  if (!userData.value.user_id.trim()) {
    errorMessage.value = '사용자 ID를 입력해주세요.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // plates 입력값을 배열로 변환 (쉼표로 분리하고 공백 제거)
    const platesArray = platesInput.value
      .split(',')
      .map(plate => plate.trim())
      .filter(plate => plate.length > 0)
    
    // 시간 입력값을 int로 변환
    const hourFrom = timeToInt(hourFromInput.value)
    const hourTo = timeToInt(hourToInput.value)
    
    const data = {
      _id: props.isNewUser ? null : props.userId,
      user_id: userData.value.user_id,
      name: userData.value.name,
      date_from: userData.value.date_from,
      hour_from: hourFrom,
      date_to: userData.value.date_to,
      hour_to: hourTo,
      flag: userData.value.flag === 'y',
      plates: platesArray
    }

    await userService.modifyUser(data)
    successMessage.value = props.isNewUser ? '사용자가 추가되었습니다.' : '사용자 정보가 수정되었습니다.'
    
    emit('saved')
    
    setTimeout(() => {
      resetForm()
      emit('cancel')
    }, 1500)
  } catch (error) {
    errorMessage.value = error.message || '저장에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  resetForm()
  emit('cancel')
}

const handleDelete = async () => {
  if (!props.userId) {
    errorMessage.value = '삭제할 사용자 ID가 없습니다.'
    return
  }

  // 삭제 확인
  if (!confirm(`정말로 "${userData.value.user_id}" 사용자를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) {
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await userService.deleteUser(props.userId)
    successMessage.value = '사용자가 삭제되었습니다.'
    
    emit('saved')
    
    setTimeout(() => {
      resetForm()
      emit('cancel')
    }, 1500)
  } catch (error) {
    errorMessage.value = error.message || '삭제에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

watch(() => props.userId, () => {
  loadUser()
}, { immediate: true })

defineExpose({
  loadUser,
  resetForm
})
</script>

<style scoped>
.user-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.checkbox-label {
  flex-direction: row;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

input[type="text"],
input[type="number"] {
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input[type="text"]:focus,
input[type="number"]:focus {
  outline: none;
  border-color: #2196F3;
}

input[type="text"]:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  display: block;
}

.error-message {
  padding: 12px;
  background-color: #fee;
  color: #c33;
  border-radius: 4px;
  font-size: 14px;
}

.success-message {
  padding: 12px;
  background-color: #efe;
  color: #3c3;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.form-actions-left {
  display: flex;
  gap: 10px;
}

.form-actions-right {
  display: flex;
  gap: 10px;
}

.cancel-button {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.cancel-button:hover {
  background-color: #5a6268;
}

.save-button {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.save-button:hover:not(:disabled) {
  background-color: #0b7dda;
}

.save-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.delete-button {
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.delete-button:hover:not(:disabled) {
  background-color: #c82333;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

