<template>
  <SlidePanel
    v-model:visible="isVisible"
    :title="panelTitle"
    @close="handleClose"
    @update:visible="handleVisibilityChange"
  >
    <UserEditForm
      :user-id="userId"
      :is-new-user="isNewUser"
      @saved="handleSaved"
      @cancel="handleClose"
    />
  </SlidePanel>
</template>

<script setup>
import { computed } from 'vue'
import SlidePanel from '@/components/SlidePanel.vue'
import UserEditForm from './UserEditForm.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  userId: {
    type: String,
    default: null
  },
  isNewUser: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'saved'])

const isVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const panelTitle = computed(() => {
  return props.isNewUser ? '새 사용자 추가' : '사용자 수정'
})

const handleClose = () => {
  isVisible.value = false
}

const handleVisibilityChange = (value) => {
  isVisible.value = value
}

const handleSaved = () => {
  emit('saved')
}
</script>

