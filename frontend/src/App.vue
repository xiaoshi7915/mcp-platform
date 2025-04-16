<template>
  <div class="app-container">
    <!-- 使用router-view展示路由页面 -->
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './store/auth'

// 挂载时初始化认证状态
onMounted(() => {
  const authStore = useAuthStore()
  authStore.initAuth()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style> 