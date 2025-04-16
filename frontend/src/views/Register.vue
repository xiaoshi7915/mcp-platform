<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <img src="../assets/logo.png" alt="Logo" class="logo" />
        <h1 class="title">MCP管理平台</h1>
        <p class="subtitle">创建新账户</p>
      </div>
      <div class="register-form">
        <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" @submit.prevent="handleRegister">
          <el-form-item prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="用户名" 
              prefix-icon="user"
              :clearable="true"
            />
          </el-form-item>
          <el-form-item prop="email">
            <el-input 
              v-model="registerForm.email" 
              placeholder="邮箱（可选）" 
              prefix-icon="message"
              :clearable="true"
              type="email"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input 
              v-model="registerForm.password" 
              placeholder="密码" 
              prefix-icon="lock"
              :clearable="true"
              type="password" 
              show-password
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword" 
              placeholder="确认密码" 
              prefix-icon="lock"
              :clearable="true"
              type="password" 
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="register-button" @click="handleRegister">
              注册
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button text type="info" @click="$router.push('/login')">
              已有账户？点击登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="register-footer">
      <p>MCP管理平台 © 2025 MCP管理平台版权所有</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

// 路由信息
const router = useRouter()
const authStore = useAuthStore()

// 注册表单
const registerFormRef = ref(null)
const loading = ref(false)
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 验证密码一致性
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度应为6-30个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 处理注册
const handleRegister = () => {
  registerFormRef.value.validate(valid => {
    if (!valid) {
      return
    }
    
    loading.value = true
    
    // 准备注册数据
    const registerData = {
      username: registerForm.username,
      password: registerForm.password
    }
    
    // 如果提供了邮箱，则添加到注册数据中
    if (registerForm.email) {
      registerData.email = registerForm.email
    }
    
    // 调用注册API
    authStore.register(registerData)
      .then(() => {
        ElMessage.success('注册成功')
        // 注册成功后直接重定向到首页
        router.push('/')
      })
      .catch(error => {
        ElMessage.error(error.message || '注册失败')
      })
      .finally(() => {
        loading.value = false
      })
  })
}
</script>

<style scoped lang="scss">
.register-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
  background-image: linear-gradient(to bottom right, #f5f7fa, #c6e2ff);
}

.register-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-header {
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

.subtitle {
  margin-top: 5px;
  font-size: 16px;
  color: #606266;
}

.register-form {
  .register-button {
    width: 100%;
  }
}

.register-footer {
  margin-top: 20px;
  font-size: 12px;
  color: #909399;
}
</style> 