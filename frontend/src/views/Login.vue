<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="../assets/logo.png" alt="Logo" class="logo" />
        <h1 class="title">MCP管理平台</h1>
      </div>
      <div class="login-form">
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="用户名" 
              prefix-icon="user"
              :clearable="true"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              placeholder="密码" 
              prefix-icon="lock"
              :clearable="true"
              type="password" 
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="login-button" @click="handleLogin">
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="login-footer">
      <p>MCP管理平台 © 2025 MCP管理平台版权所有</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'
import { User, Lock } from '@element-plus/icons-vue'

// 路由信息
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 登录表单
const loginFormRef = ref(null)
const loading = ref(false)
const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度应为6-30个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = () => {
  loginFormRef.value.validate(valid => {
    if (!valid) {
      return
    }
    
    loading.value = true
    
    authStore.login({
      username: loginForm.username,
      password: loginForm.password,
      remember: loginForm.remember
    })
      .then(() => {
        ElMessage.success('登录成功')
        const redirectPath = route.query.redirect || '/'
        router.push(redirectPath)
      })
      .catch(error => {
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

// 组件挂载时，检查是否有保存的登录信息
onMounted(() => {
  // 在实际项目中，这里可以检查本地存储的用户信息，或尝试进行令牌刷新
  const savedUsername = localStorage.getItem('username')
  if (savedUsername) {
    loginForm.username = savedUsername
    loginForm.remember = true
  }
})
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
  background-image: linear-gradient(to bottom right, #f5f7fa, #c6e2ff);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  height: 80px;
}

.title {
  margin-top: 15px;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.login-form {
  .login-button {
    width: 100%;
  }
}

.login-footer {
  margin-top: 20px;
  font-size: 12px;
  color: #909399;
}
</style> 