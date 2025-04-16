import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true, title: '仪表盘' }
  },
  {
    path: '/tools',
    name: 'Tools',
    component: () => import('@/views/Tools.vue'),
    meta: { requiresAuth: true, title: '工具管理' }
  },
  {
    path: '/tool/:id',
    name: 'ToolDetail',
    component: () => import('@/views/ToolDetail.vue'),
    meta: { requiresAuth: true, title: '工具详情' }
  },
  {
    path: '/configs',
    name: 'Configs',
    component: () => import('@/views/Configs.vue'),
    meta: { requiresAuth: true, title: '配置管理' }
  },
  {
    path: '/config/:id',
    name: 'ConfigDetail',
    component: () => import('@/views/ConfigDetail.vue'),
    meta: { requiresAuth: true, title: '配置详情' }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/Logs.vue'),
    meta: { requiresAuth: true, title: '日志管理' }
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('@/views/Templates.vue'),
    meta: { requiresAuth: true, title: '模板库' }
  },
  {
    path: '/template/:id',
    name: 'TemplateDetail',
    component: () => import('@/views/TemplateDetail.vue'),
    meta: { requiresAuth: true, title: '模板详情' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true, title: '系统设置' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { requiresAuth: false, title: '404 - 页面未找到' }
  }
]

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - MCP管理平台`

  // 检查是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const authStore = useAuthStore()

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未认证，重定向到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已认证但访问登录页，重定向到首页
    next({ name: 'Home' })
  } else {
    // 放行
    next()
  }
})

export default router 