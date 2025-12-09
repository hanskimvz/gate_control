<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import Header from './components/Header.vue'

const route = useRoute()
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const isLoginPage = computed(() => {
  return route.name === 'login'
})

const isGatePage = computed(() => {
  return route.name === 'gate'
})

const showHeader = computed(() => {
  // 로그인 페이지는 항상 헤더 숨김
  if (isLoginPage.value) {
    return false
  }
  // Gate 페이지는 모바일일 때만 헤더 숨김
  if (isGatePage.value) {
    return !isMobile.value
  }
  // 나머지 페이지는 항상 헤더 표시
  return true
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<template>
  <div id="app" :class="{ 'login-page': isLoginPage, 'gate-page': isGatePage }">
    <Header v-if="showHeader" />

    <main :class="{ 'no-header': isLoginPage || isGatePage }">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  min-height: calc(100vh - 60px);
}

main.no-header {
  min-height: 100vh;
  padding: 0;
  margin: 0;
}
</style>
