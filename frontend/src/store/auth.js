import { defineStore } from 'pinia'
import axios from 'axios'
import api from '../api/api'

// 定义认证状态管理
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || '',
    isAuthenticated: !!localStorage.getItem('token'),
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
  }),
  
  getters: {
    // 获取认证头信息，用于API请求
    authHeader: (state) => {
      return state.token ? { Authorization: `Bearer ${state.token}` } : {}
    },
    // 获取用户角色
    userRole: (state) => {
      return state.userInfo.role || 'viewer'
    },
    // 检查用户是否有指定角色
    hasRole: (state) => (role) => {
      return state.userInfo.role === role
    },
    // 检查用户是否是管理员
    isAdmin: (state) => {
      return state.userInfo.role === 'admin'
    }
  },
  
  actions: {
    // 初始化认证状态
    initAuth() {
      this.token = localStorage.getItem('token') || null
      this.username = localStorage.getItem('username') || ''
      this.userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      this.isAuthenticated = !!this.token

      // 配置全局请求拦截器，添加认证头
      axios.interceptors.request.use(config => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      })
      
      // 如果已登录，自动获取最新的用户信息
      if (this.isAuthenticated) {
        this.fetchUserInfo().catch(() => {
          // 如果获取用户信息失败（令牌可能已过期），则注销
          this.clearAuthData()
        })
      }
    },
    
    // 登录
    async login(userData) {
      try {
        const response = await api.auth.login(userData)
        const { token, user } = response
        this.setAuthData(token, user.username, user, userData.remember)
        return Promise.resolve(response)
      } catch (error) {
        return Promise.reject(error)
      }
    },
    
    // 获取用户信息
    async fetchUserInfo() {
      try {
        const user = await api.auth.getInfo()
        this.setUserInfo(user)
        return Promise.resolve(user)
      } catch (error) {
        return Promise.reject(error)
      }
    },
    
    // 设置认证数据
    setAuthData(token, username, userInfo, remember = false) {
      this.token = token
      this.username = username
      this.userInfo = userInfo
      this.isAuthenticated = true
      
      // 根据"记住我"选项决定是否持久化存储
      if (remember) {
        localStorage.setItem('token', token)
        localStorage.setItem('username', username)
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
      } else {
        sessionStorage.setItem('token', token)
        sessionStorage.setItem('username', username)
        sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
      }
      
      // 配置API请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    },
    
    // 设置用户信息
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    
    // 注销
    async logout() {
      // 清除认证数据
      this.clearAuthData()
      return Promise.resolve()
    },
    
    // 清除认证数据
    clearAuthData() {
      this.token = null
      this.username = ''
      this.userInfo = {}
      this.isAuthenticated = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userInfo')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('username')
      sessionStorage.removeItem('userInfo')
      
      // 清除API请求头
      delete axios.defaults.headers.common['Authorization']
    },
    
    // 修改密码
    async changePassword(oldPassword, newPassword) {
      try {
        const response = await api.auth.changePassword({
          old_password: oldPassword,
          new_password: newPassword
        })
        return Promise.resolve(response)
      } catch (error) {
        return Promise.reject(error)
      }
    }
  }
}) 