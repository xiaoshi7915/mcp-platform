<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo-container">
        <img src="../assets/logo.png" alt="Logo" class="logo" />
        <h1 class="title">MCP管理平台</h1>
      </div>
      <div class="nav-menu">
        <el-menu mode="horizontal" :router="true" :default-active="activeMenu" class="horizontal-menu">
          <el-menu-item index="/">仪表盘</el-menu-item>
          <el-menu-item index="/tools">工具管理</el-menu-item>
          <el-menu-item index="/configs">配置管理</el-menu-item>
          <el-menu-item index="/logs">日志管理</el-menu-item>
          <el-menu-item index="/templates">工具库</el-menu-item>
        </el-menu>
      </div>
      <div class="user-info">
        <el-dropdown trigger="click">
          <span class="user-dropdown">
            {{ username }} <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToSettings">
                <el-icon><setting /></el-icon> 设置
              </el-dropdown-item>
              <el-dropdown-item divided @click="logout">
                <el-icon><switch-button /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="main-container">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="search-box">
          <el-input 
            v-model="searchTerm" 
            placeholder="搜索工具..." 
            prefix-icon="el-icon-search"
            clearable 
          />
        </div>
        <div class="category-list">
          <h3>工具分类</h3>
          <el-menu :default-active="activeCategory" @select="handleCategorySelect">
            <el-menu-item index="all">
              <el-icon><files /></el-icon>
              <span>全部工具</span>
            </el-menu-item>
            <el-menu-item index="filesystem">
              <el-icon><folder /></el-icon>
              <span>文件系统工具</span>
            </el-menu-item>
            <el-menu-item index="network">
              <el-icon><connection /></el-icon>
              <span>网络工具</span>
            </el-menu-item>
            <el-menu-item index="data_analysis">
              <el-icon><data-analysis /></el-icon>
              <span>数据分析工具</span>
            </el-menu-item>
            <el-menu-item index="media">
              <el-icon><picture /></el-icon>
              <span>媒体处理工具</span>
            </el-menu-item>
            <el-menu-item index="system">
              <el-icon><cpu /></el-icon>
              <span>系统工具</span>
            </el-menu-item>
            <el-menu-item index="puppeteer">
              <el-icon><monitor /></el-icon>
              <span>浏览器自动化</span>
            </el-menu-item>
            <el-menu-item index="other">
              <el-icon><more /></el-icon>
              <span>其他工具</span>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="quick-access">
          <h3>快速访问</h3>
          <el-button type="primary" @click="createNewTool" size="small" class="quick-btn">
            <el-icon><plus /></el-icon> 新建工具
          </el-button>
          <el-button type="success" @click="goToTemplates" size="small" class="quick-btn">
            <el-icon><document /></el-icon> 模板库
          </el-button>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- 底部状态栏 -->
    <footer class="footer">
      <div class="status">
        <span class="status-indicator" :class="{ 'connected': connected }"></span>
        {{ connected ? '已连接' : '未连接' }}
      </div>
      <div class="version">版本 v0.1.0</div>
      <div class="links">
        <a href="#" @click.prevent="showHelp">帮助</a>
        <a href="#" @click.prevent="showAbout">关于</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { ArrowDown, Setting, SwitchButton, Files, Folder, Connection, DataAnalysis, Picture, Cpu, Monitor, More, Plus, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 路由和认证
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 用户信息
const username = ref('Admin')

// 连接状态
const connected = ref(true)

// 搜索和分类过滤
const searchTerm = ref('')
const activeCategory = ref('all')

// 计算当前活动菜单
const activeMenu = computed(() => {
  return route.path.startsWith('/tool/') ? '/tools' : 
         route.path.startsWith('/config/') ? '/configs' : 
         route.path.startsWith('/template/') ? '/templates' : route.path
})

// 处理分类选择
const handleCategorySelect = (index) => {
  activeCategory.value = index
  if (route.path !== '/tools') {
    router.push('/tools')
  }
  // TODO: 在工具页面应用分类过滤
}

// 导航方法
const goToSettings = () => {
  router.push('/settings')
}

const createNewTool = () => {
  router.push('/tools?action=create')
}

const goToTemplates = () => {
  router.push('/templates')
}

// 帮助和关于对话框
const showHelp = () => {
  ElMessageBox.alert(
    'MCP管理平台提供了大模型通用协议工具的管理功能。您可以通过此平台创建、配置和监控各种MCP工具。',
    '帮助信息',
    { confirmButtonText: '确定' }
  )
}

const showAbout = () => {
  ElMessageBox.alert(
    'MCP管理平台 v0.1.0\n开发者：MCP团队\n© 2023 MCP团队版权所有',
    '关于',
    { confirmButtonText: '确定' }
  )
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout()
    router.push('/login')
    ElMessage.success('已成功退出登录')
  }).catch(() => {})
}

// 页面加载时检查连接状态
onMounted(() => {
  // 简化版：直接设置为已连接
  connected.value = true
})
</script>

<style scoped lang="scss">
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.horizontal-menu {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 10px;
  color: #606266;
  font-size: 14px;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.search-box {
  padding: 0 15px 15px;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.category-list {
  flex: 1;
  padding: 0 15px;
  overflow-y: auto;
}

.category-list h3 {
  font-size: 14px;
  color: #909399;
  margin: 10px 0;
  padding-left: 5px;
}

.quick-access {
  padding: 15px;
  border-top: 1px solid #eee;
}

.quick-access h3 {
  font-size: 14px;
  color: #909399;
  margin: 0 0 10px;
}

.quick-btn {
  display: block;
  width: 100%;
  margin-bottom: 10px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

.footer {
  height: 40px;
  background-color: #fff;
  border-top: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  font-size: 12px;
  color: #909399;
}

.status {
  display: flex;
  align-items: center;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #f56c6c;
  margin-right: 6px;
}

.status-indicator.connected {
  background-color: #67c23a;
}

.links a {
  color: #909399;
  text-decoration: none;
  margin-left: 15px;
}

.links a:hover {
  color: #409EFF;
}
</style> 