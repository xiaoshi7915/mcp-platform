<template>
  <div class="layout-wrapper">
    <div class="sidebar">
      <div class="logo">
        <img src="../assets/logo.png" alt="Logo" />
        <h1>MCP管理平台</h1>
      </div>
      <el-menu
        default-active="1"
        class="menu"
        :router="true"
      >
        <el-menu-item index="/">
          <el-icon><odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/tools">
          <el-icon><tools /></el-icon>
          <span>工具管理</span>
        </el-menu-item>
        <el-menu-item index="/configs">
          <el-icon><setting /></el-icon>
          <span>配置管理</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><document /></el-icon>
          <span>日志管理</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><files /></el-icon>
          <span>模板库</span>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="main-content">
      <div class="top-bar">
        <div class="page-title">{{ title }}</div>
        <div class="user-info">
          <el-dropdown>
            <span class="dropdown-link">
              {{ username }}
              <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToSettings">设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <div class="content">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Odometer, 
  Tools, 
  Setting, 
  Document, 
  Files,
  ArrowDown
} from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const username = computed(() => authStore.username || '用户');

// 根据当前路由设置页面标题
const title = computed(() => {
  const currentRoute = route.matched[route.matched.length - 1];
  return currentRoute?.meta?.title || '页面';
});

const goToSettings = () => {
  router.push('/settings');
};

const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout();
    router.push('/login');
    ElMessage.success('已成功退出登录');
  }).catch(() => {});
};
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  width: 100%;
}

.sidebar {
  width: 240px;
  background-color: #304156;
  color: white;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  padding: 20px;
}

.logo img {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.logo h1 {
  font-size: 18px;
  color: white;
  margin: 0;
}

.menu {
  border-right: none;
  background-color: transparent;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item) {
  color: #bfcbd9;
}

:deep(.el-menu-item.is-active) {
  color: #409EFF;
  background-color: #263445;
}

:deep(.el-menu-item:hover) {
  background-color: #263445;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 60px;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
}

.dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background-color: #f0f2f5;
}
</style> 