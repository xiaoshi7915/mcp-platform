<template>
  <div class="settings-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h2>系统设置</h2>
        <p>管理系统和用户配置</p>
      </div>
    </div>
    
    <!-- 设置内容 -->
    <el-row :gutter="20">
      <!-- 侧边栏 -->
      <el-col :span="6">
        <el-card class="settings-menu">
          <el-menu
            v-model:default-active="activeTab"
            class="settings-menu-list"
            @select="handleTabChange"
          >
            <el-menu-item index="system">
              <el-icon><setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
            <el-menu-item index="user">
              <el-icon><user /></el-icon>
              <span>用户设置</span>
            </el-menu-item>
            <el-menu-item index="notification">
              <el-icon><bell /></el-icon>
              <span>通知设置</span>
            </el-menu-item>
            <el-menu-item index="security">
              <el-icon><lock /></el-icon>
              <span>安全设置</span>
            </el-menu-item>
            <el-menu-item index="api">
              <el-icon><connection /></el-icon>
              <span>API设置</span>
            </el-menu-item>
            <el-menu-item index="backup">
              <el-icon><download /></el-icon>
              <span>备份与恢复</span>
            </el-menu-item>
            <el-menu-item index="about">
              <el-icon><info-filled /></el-icon>
              <span>关于系统</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      
      <!-- 设置内容 -->
      <el-col :span="18">
        <el-card class="settings-content" v-loading="loading">
          <!-- 系统设置 -->
          <div v-if="activeTab === 'system'">
            <h3 class="settings-title">系统设置</h3>
            
            <el-form
              :model="systemForm"
              ref="systemFormRef"
              label-width="150px"
              class="settings-form"
            >
              <el-form-item label="系统名称">
                <el-input v-model="systemForm.systemName" placeholder="请输入系统名称" />
              </el-form-item>
              
              <el-form-item label="超时设置(秒)">
                <el-input-number 
                  v-model="systemForm.timeout" 
                  :min="1" 
                  :max="300"
                  placeholder="请设置默认超时时间"
                />
              </el-form-item>
              
              <el-form-item label="最大并发任务数">
                <el-input-number 
                  v-model="systemForm.maxConcurrentTasks" 
                  :min="1" 
                  :max="100"
                  placeholder="请设置最大并发任务数"
                />
              </el-form-item>
              
              <el-form-item label="日志保留天数">
                <el-input-number 
                  v-model="systemForm.logRetentionDays" 
                  :min="1" 
                  :max="365"
                  placeholder="请设置日志保留天数"
                />
              </el-form-item>
              
              <el-form-item label="开启调试模式">
                <el-switch v-model="systemForm.debugMode" />
              </el-form-item>
              
              <el-form-item label="自动清理日志">
                <el-switch v-model="systemForm.autoCleanLogs" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveSystemSettings" :loading="saving.system">
                  保存设置
                </el-button>
                <el-button @click="resetSystemSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 用户设置 -->
          <div v-else-if="activeTab === 'user'">
            <h3 class="settings-title">用户设置</h3>
            
            <el-form
              :model="userForm"
              ref="userFormRef"
              label-width="150px"
              class="settings-form"
            >
              <el-form-item label="用户名">
                <el-input v-model="userForm.username" disabled />
              </el-form-item>
              
              <el-form-item label="显示名称">
                <el-input v-model="userForm.displayName" placeholder="请输入显示名称" />
              </el-form-item>
              
              <el-form-item label="电子邮箱">
                <el-input v-model="userForm.email" placeholder="请输入电子邮箱" />
              </el-form-item>
              
              <el-divider content-position="left">修改密码</el-divider>
              
              <el-form-item label="当前密码">
                <el-input 
                  v-model="userForm.currentPassword" 
                  type="password" 
                  placeholder="请输入当前密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="新密码">
                <el-input 
                  v-model="userForm.newPassword" 
                  type="password" 
                  placeholder="请输入新密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="确认新密码">
                <el-input 
                  v-model="userForm.confirmPassword" 
                  type="password" 
                  placeholder="请确认新密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveUserSettings" :loading="saving.user">
                  保存设置
                </el-button>
                <el-button @click="resetUserSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 通知设置 -->
          <div v-else-if="activeTab === 'notification'">
            <h3 class="settings-title">通知设置</h3>
            
            <el-form
              :model="notificationForm"
              ref="notificationFormRef"
              label-width="150px"
              class="settings-form"
            >
              <el-form-item label="启用电子邮件通知">
                <el-switch v-model="notificationForm.enableEmail" />
              </el-form-item>
              
              <template v-if="notificationForm.enableEmail">
                <el-form-item label="SMTP服务器">
                  <el-input v-model="notificationForm.smtpServer" placeholder="请输入SMTP服务器地址" />
                </el-form-item>
                
                <el-form-item label="SMTP端口">
                  <el-input-number v-model="notificationForm.smtpPort" :min="1" :max="65535" />
                </el-form-item>
                
                <el-form-item label="SMTP用户名">
                  <el-input v-model="notificationForm.smtpUsername" placeholder="请输入SMTP用户名" />
                </el-form-item>
                
                <el-form-item label="SMTP密码">
                  <el-input 
                    v-model="notificationForm.smtpPassword" 
                    type="password" 
                    placeholder="请输入SMTP密码"
                    show-password
                  />
                </el-form-item>
                
                <el-form-item label="发件人地址">
                  <el-input v-model="notificationForm.fromEmail" placeholder="请输入发件人地址" />
                </el-form-item>
              </template>
              
              <el-divider content-position="left">通知事件</el-divider>
              
              <el-form-item label="工具执行失败">
                <el-switch v-model="notificationForm.notifyOnFailure" />
              </el-form-item>
              
              <el-form-item label="工具执行成功">
                <el-switch v-model="notificationForm.notifyOnSuccess" />
              </el-form-item>
              
              <el-form-item label="系统错误">
                <el-switch v-model="notificationForm.notifyOnSystemError" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings" :loading="saving.notification">
                  保存设置
                </el-button>
                <el-button @click="resetNotificationSettings">重置</el-button>
                <el-button type="info" @click="testNotification" :loading="testing.notification">
                  测试通知
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 安全设置 -->
          <div v-else-if="activeTab === 'security'">
            <h3 class="settings-title">安全设置</h3>
            
            <el-form
              :model="securityForm"
              ref="securityFormRef"
              label-width="180px"
              class="settings-form"
            >
              <el-form-item label="登录尝试失败次数限制">
                <el-input-number 
                  v-model="securityForm.maxLoginAttempts" 
                  :min="1" 
                  :max="10"
                />
              </el-form-item>
              
              <el-form-item label="登录锁定时间(分钟)">
                <el-input-number 
                  v-model="securityForm.lockoutDuration" 
                  :min="1" 
                  :max="60"
                />
              </el-form-item>
              
              <el-form-item label="会话超时时间(分钟)">
                <el-input-number 
                  v-model="securityForm.sessionTimeout" 
                  :min="1" 
                  :max="1440"
                />
              </el-form-item>
              
              <el-form-item label="启用双因素认证">
                <el-switch v-model="securityForm.enable2FA" />
              </el-form-item>
              
              <el-form-item label="强制密码复杂度要求">
                <el-switch v-model="securityForm.enforcePasswordComplexity" />
              </el-form-item>
              
              <el-form-item label="启用IP白名单">
                <el-switch v-model="securityForm.enableIpWhitelist" />
              </el-form-item>
              
              <template v-if="securityForm.enableIpWhitelist">
                <el-form-item label="IP白名单">
                  <el-input 
                    v-model="securityForm.ipWhitelist" 
                    type="textarea" 
                    :rows="3"
                    placeholder="每行输入一个IP地址或CIDR"
                  />
                </el-form-item>
              </template>
              
              <el-form-item>
                <el-button type="primary" @click="saveSecuritySettings" :loading="saving.security">
                  保存设置
                </el-button>
                <el-button @click="resetSecuritySettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- API设置 -->
          <div v-else-if="activeTab === 'api'">
            <h3 class="settings-title">API设置</h3>
            
            <el-form
              :model="apiForm"
              ref="apiFormRef"
              label-width="150px"
              class="settings-form"
            >
              <el-form-item label="启用API访问">
                <el-switch v-model="apiForm.enableApi" />
              </el-form-item>
              
              <template v-if="apiForm.enableApi">
                <el-form-item label="API访问令牌">
                  <div class="api-token-input">
                    <el-input v-model="apiForm.apiToken" readonly />
                    <el-button type="primary" @click="generateApiToken" :loading="generating">
                      生成新令牌
                    </el-button>
                  </div>
                </el-form-item>
                
                <el-form-item label="API速率限制(每分钟)">
                  <el-input-number v-model="apiForm.rateLimit" :min="1" :max="1000" />
                </el-form-item>
                
                <el-form-item label="允许的HTTP方法">
                  <el-checkbox-group v-model="apiForm.allowedMethods">
                    <el-checkbox label="GET">GET</el-checkbox>
                    <el-checkbox label="POST">POST</el-checkbox>
                    <el-checkbox label="PUT">PUT</el-checkbox>
                    <el-checkbox label="DELETE">DELETE</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                
                <el-form-item label="启用CORS">
                  <el-switch v-model="apiForm.enableCors" />
                </el-form-item>
                
                <template v-if="apiForm.enableCors">
                  <el-form-item label="允许的来源">
                    <el-input 
                      v-model="apiForm.allowedOrigins" 
                      type="textarea" 
                      :rows="3"
                      placeholder="每行输入一个来源URL"
                    />
                  </el-form-item>
                </template>
              </template>
              
              <el-form-item>
                <el-button type="primary" @click="saveApiSettings" :loading="saving.api">
                  保存设置
                </el-button>
                <el-button @click="resetApiSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 备份与恢复 -->
          <div v-else-if="activeTab === 'backup'">
            <h3 class="settings-title">备份与恢复</h3>
            
            <el-form
              :model="backupForm"
              ref="backupFormRef"
              label-width="150px"
              class="settings-form"
            >
              <el-form-item label="启用自动备份">
                <el-switch v-model="backupForm.enableAutoBackup" />
              </el-form-item>
              
              <template v-if="backupForm.enableAutoBackup">
                <el-form-item label="备份频率">
                  <el-select v-model="backupForm.backupFrequency" placeholder="请选择备份频率">
                    <el-option label="每天" value="daily" />
                    <el-option label="每周" value="weekly" />
                    <el-option label="每月" value="monthly" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="保留备份数量">
                  <el-input-number v-model="backupForm.backupRetention" :min="1" :max="100" />
                </el-form-item>
                
                <el-form-item label="备份存储路径">
                  <el-input v-model="backupForm.backupPath" placeholder="请输入备份存储路径" />
                </el-form-item>
                
                <el-form-item label="压缩备份文件">
                  <el-switch v-model="backupForm.compressBackup" />
                </el-form-item>
              </template>
              
              <el-divider content-position="left">手动备份与恢复</el-divider>
              
              <el-form-item label="备份内容">
                <el-checkbox-group v-model="backupForm.backupContent">
                  <el-checkbox label="tools">工具配置</el-checkbox>
                  <el-checkbox label="templates">模板库</el-checkbox>
                  <el-checkbox label="logs">系统日志</el-checkbox>
                  <el-checkbox label="settings">系统设置</el-checkbox>
                  <el-checkbox label="users">用户数据</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveBackupSettings" :loading="saving.backup">
                  保存设置
                </el-button>
                <el-button @click="resetBackupSettings">重置</el-button>
                <el-button type="success" @click="createBackup" :loading="creating">
                  创建备份
                </el-button>
              </el-form-item>
              
              <el-form-item label="恢复备份">
                <el-upload
                  class="backup-upload"
                  action="#"
                  :auto-upload="false"
                  :on-change="handleBackupFileChange"
                >
                  <el-button type="warning" :loading="restoring">选择备份文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      请上传MCP备份文件(.zip或.json格式)
                    </div>
                  </template>
                </el-upload>
                
                <el-button 
                  v-if="backupFile" 
                  type="danger" 
                  @click="restoreBackup" 
                  :loading="restoring"
                >
                  恢复备份
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 关于系统 -->
          <div v-else-if="activeTab === 'about'">
            <h3 class="settings-title">关于系统</h3>
            
            <div class="about-system">
              <div class="system-logo">
                <img src="../assets/logo.png" alt="MCP Platform Logo" />
              </div>
              
              <h2 class="system-name">MCP 管理平台</h2>
              <p class="system-version">版本: v1.0.0</p>
              
              <div class="system-info">
                <div class="info-item">
                  <span class="label">系统运行时间:</span>
                  <span class="value">{{ systemInfo.uptime || '获取中...' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">服务器操作系统:</span>
                  <span class="value">{{ systemInfo.os || '获取中...' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">API版本:</span>
                  <span class="value">{{ systemInfo.apiVersion || '获取中...' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">数据库类型:</span>
                  <span class="value">{{ systemInfo.dbType || '获取中...' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">缓存状态:</span>
                  <span class="value">{{ systemInfo.cacheStatus || '获取中...' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">注册工具数量:</span>
                  <span class="value">{{ systemInfo.toolsCount || '获取中...' }}</span>
                </div>
              </div>
              
              <div class="about-actions">
                <el-button type="primary" @click="checkForUpdates" :loading="checking">
                  检查更新
                </el-button>
                <el-button type="info" @click="viewLicense">
                  查看许可证
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, User, Bell, Lock, Connection, Download, InfoFilled
} from '@element-plus/icons-vue'
import api from '../api/api'
import { useAuthStore } from '../store/auth'

export default {
  name: 'SystemSettings',
  setup() {
    // Auth store
    const authStore = useAuthStore()
    
    // 当前激活的标签页
    const activeTab = ref('system')
    const loading = ref(false)
    
    // 保存按钮状态
    const saving = reactive({
      system: false,
      user: false,
      notification: false,
      security: false,
      api: false,
      backup: false
    })
    
    // 其他按钮状态
    const testing = reactive({ notification: false })
    const generating = ref(false)
    const creating = ref(false)
    const restoring = ref(false)
    const checking = ref(false)
    
    // 表单引用
    const systemFormRef = ref(null)
    const userFormRef = ref(null)
    const notificationFormRef = ref(null)
    const securityFormRef = ref(null)
    const apiFormRef = ref(null)
    const backupFormRef = ref(null)
    
    // 系统设置表单
    const systemForm = reactive({
      systemName: 'MCP管理平台',
      timeout: 60,
      maxConcurrentTasks: 5,
      logRetentionDays: 30,
      debugMode: false,
      autoCleanLogs: true
    })
    
    // 用户设置表单
    const userForm = reactive({
      username: authStore.user?.username || '',
      displayName: authStore.user?.displayName || '',
      email: authStore.user?.email || '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // 通知设置表单
    const notificationForm = reactive({
      enableEmail: false,
      smtpServer: '',
      smtpPort: 587,
      smtpUsername: '',
      smtpPassword: '',
      fromEmail: '',
      notifyOnFailure: true,
      notifyOnSuccess: false,
      notifyOnSystemError: true
    })
    
    // 安全设置表单
    const securityForm = reactive({
      maxLoginAttempts: 5,
      lockoutDuration: 15,
      sessionTimeout: 60,
      enable2FA: false,
      enforcePasswordComplexity: true,
      enableIpWhitelist: false,
      ipWhitelist: ''
    })
    
    // API设置表单
    const apiForm = reactive({
      enableApi: false,
      apiToken: '',
      rateLimit: 60,
      allowedMethods: ['GET', 'POST'],
      enableCors: false,
      allowedOrigins: ''
    })
    
    // 备份设置表单
    const backupForm = reactive({
      enableAutoBackup: false,
      backupFrequency: 'daily',
      backupRetention: 7,
      backupPath: '/opt/mcp/backups',
      compressBackup: true,
      backupContent: ['tools', 'templates', 'settings']
    })
    
    // 备份文件
    const backupFile = ref(null)
    
    // 系统信息
    const systemInfo = reactive({
      uptime: '',
      os: '',
      apiVersion: '',
      dbType: '',
      cacheStatus: '',
      toolsCount: ''
    })
    
    // 加载系统设置
    const loadSystemSettings = async () => {
      loading.value = true
      
      try {
        const settings = await api.settings.getSystemSettings()
        
        // 更新系统设置表单
        systemForm.systemName = settings.systemName || 'MCP管理平台'
        systemForm.timeout = settings.timeout || 60
        systemForm.maxConcurrentTasks = settings.maxConcurrentTasks || 5
        systemForm.logRetentionDays = settings.logRetentionDays || 30
        systemForm.debugMode = settings.debugMode || false
        systemForm.autoCleanLogs = settings.autoCleanLogs || true
        
      } catch (error) {
        console.error('加载系统设置失败:', error)
        ElMessage.error('加载系统设置失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载用户设置
    const loadUserSettings = async () => {
      try {
        const user = await api.settings.getUserSettings()
        
        userForm.username = user.username || authStore.user?.username || ''
        userForm.displayName = user.displayName || authStore.user?.displayName || ''
        userForm.email = user.email || authStore.user?.email || ''
        
      } catch (error) {
        console.error('加载用户设置失败:', error)
      }
    }
    
    // 加载通知设置
    const loadNotificationSettings = async () => {
      try {
        const settings = await api.settings.getNotificationSettings()
        
        notificationForm.enableEmail = settings.enableEmail || false
        notificationForm.smtpServer = settings.smtpServer || ''
        notificationForm.smtpPort = settings.smtpPort || 587
        notificationForm.smtpUsername = settings.smtpUsername || ''
        notificationForm.smtpPassword = settings.smtpPassword || ''
        notificationForm.fromEmail = settings.fromEmail || ''
        notificationForm.notifyOnFailure = settings.notifyOnFailure !== false
        notificationForm.notifyOnSuccess = settings.notifyOnSuccess || false
        notificationForm.notifyOnSystemError = settings.notifyOnSystemError !== false
        
      } catch (error) {
        console.error('加载通知设置失败:', error)
      }
    }
    
    // 加载安全设置
    const loadSecuritySettings = async () => {
      try {
        const settings = await api.settings.getSecuritySettings()
        
        securityForm.maxLoginAttempts = settings.maxLoginAttempts || 5
        securityForm.lockoutDuration = settings.lockoutDuration || 15
        securityForm.sessionTimeout = settings.sessionTimeout || 60
        securityForm.enable2FA = settings.enable2FA || false
        securityForm.enforcePasswordComplexity = settings.enforcePasswordComplexity !== false
        securityForm.enableIpWhitelist = settings.enableIpWhitelist || false
        securityForm.ipWhitelist = settings.ipWhitelist || ''
        
      } catch (error) {
        console.error('加载安全设置失败:', error)
      }
    }
    
    // 加载API设置
    const loadApiSettings = async () => {
      try {
        const settings = await api.settings.getApiSettings()
        
        apiForm.enableApi = settings.enableApi || false
        apiForm.apiToken = settings.apiToken || ''
        apiForm.rateLimit = settings.rateLimit || 60
        apiForm.allowedMethods = settings.allowedMethods || ['GET', 'POST']
        apiForm.enableCors = settings.enableCors || false
        apiForm.allowedOrigins = settings.allowedOrigins || ''
        
      } catch (error) {
        console.error('加载API设置失败:', error)
      }
    }
    
    // 加载备份设置
    const loadBackupSettings = async () => {
      try {
        const settings = await api.settings.getBackupSettings()
        
        backupForm.enableAutoBackup = settings.enableAutoBackup || false
        backupForm.backupFrequency = settings.backupFrequency || 'daily'
        backupForm.backupRetention = settings.backupRetention || 7
        backupForm.backupPath = settings.backupPath || '/opt/mcp/backups'
        backupForm.compressBackup = settings.compressBackup !== false
        backupForm.backupContent = settings.backupContent || ['tools', 'templates', 'settings']
        
      } catch (error) {
        console.error('加载备份设置失败:', error)
      }
    }
    
    // 加载系统信息
    const loadSystemInfo = async () => {
      try {
        const info = await api.settings.getSystemInfo()
        
        systemInfo.uptime = info.uptime || '未知'
        systemInfo.os = info.os || '未知'
        systemInfo.apiVersion = info.apiVersion || '未知'
        systemInfo.dbType = info.dbType || '未知'
        systemInfo.cacheStatus = info.cacheStatus || '未知'
        systemInfo.toolsCount = info.toolsCount || '未知'
        
      } catch (error) {
        console.error('加载系统信息失败:', error)
      }
    }
    
    // 根据当前标签页加载设置
    const loadCurrentTabSettings = () => {
      switch (activeTab.value) {
        case 'system':
          loadSystemSettings()
          break
        case 'user':
          loadUserSettings()
          break
        case 'notification':
          loadNotificationSettings()
          break
        case 'security':
          loadSecuritySettings()
          break
        case 'api':
          loadApiSettings()
          break
        case 'backup':
          loadBackupSettings()
          break
        case 'about':
          loadSystemInfo()
          break
      }
    }
    
    // 保存系统设置
    const saveSystemSettings = async () => {
      saving.system = true
      
      try {
        await api.settings.updateSystemSettings(systemForm)
        ElMessage.success('系统设置已保存')
      } catch (error) {
        ElMessage.error(`保存系统设置失败: ${error}`)
      } finally {
        saving.system = false
      }
    }
    
    // 保存用户设置
    const saveUserSettings = async () => {
      // 验证新密码
      if (userForm.newPassword) {
        if (userForm.newPassword !== userForm.confirmPassword) {
          ElMessage.error('两次输入的新密码不一致')
          return
        }
        
        if (!userForm.currentPassword) {
          ElMessage.error('请输入当前密码')
          return
        }
      }
      
      saving.user = true
      
      try {
        await api.settings.updateUserSettings({
          displayName: userForm.displayName,
          email: userForm.email,
          currentPassword: userForm.currentPassword,
          newPassword: userForm.newPassword
        })
        
        ElMessage.success('用户设置已保存')
        
        // 清空密码字段
        userForm.currentPassword = ''
        userForm.newPassword = ''
        userForm.confirmPassword = ''
        
        // 更新认证状态
        if (userForm.displayName) {
          authStore.updateUserInfo({ displayName: userForm.displayName })
        }
      } catch (error) {
        ElMessage.error(`保存用户设置失败: ${error}`)
      } finally {
        saving.user = false
      }
    }
    
    // 保存通知设置
    const saveNotificationSettings = async () => {
      saving.notification = true
      
      try {
        await api.settings.updateNotificationSettings(notificationForm)
        ElMessage.success('通知设置已保存')
      } catch (error) {
        ElMessage.error(`保存通知设置失败: ${error}`)
      } finally {
        saving.notification = false
      }
    }
    
    // 保存安全设置
    const saveSecuritySettings = async () => {
      saving.security = true
      
      try {
        await api.settings.updateSecuritySettings(securityForm)
        ElMessage.success('安全设置已保存')
      } catch (error) {
        ElMessage.error(`保存安全设置失败: ${error}`)
      } finally {
        saving.security = false
      }
    }
    
    // 保存API设置
    const saveApiSettings = async () => {
      saving.api = true
      
      try {
        await api.settings.updateApiSettings(apiForm)
        ElMessage.success('API设置已保存')
      } catch (error) {
        ElMessage.error(`保存API设置失败: ${error}`)
      } finally {
        saving.api = false
      }
    }
    
    // 保存备份设置
    const saveBackupSettings = async () => {
      saving.backup = true
      
      try {
        await api.settings.updateBackupSettings(backupForm)
        ElMessage.success('备份设置已保存')
      } catch (error) {
        ElMessage.error(`保存备份设置失败: ${error}`)
      } finally {
        saving.backup = false
      }
    }
    
    // 重置系统设置
    const resetSystemSettings = () => {
      loadSystemSettings()
    }
    
    // 重置用户设置
    const resetUserSettings = () => {
      loadUserSettings()
      userForm.currentPassword = ''
      userForm.newPassword = ''
      userForm.confirmPassword = ''
    }
    
    // 重置通知设置
    const resetNotificationSettings = () => {
      loadNotificationSettings()
    }
    
    // 重置安全设置
    const resetSecuritySettings = () => {
      loadSecuritySettings()
    }
    
    // 重置API设置
    const resetApiSettings = () => {
      loadApiSettings()
    }
    
    // 重置备份设置
    const resetBackupSettings = () => {
      loadBackupSettings()
    }
    
    // 测试通知
    const testNotification = async () => {
      testing.notification = true
      
      try {
        await api.settings.testNotification(notificationForm)
        ElMessage.success('测试通知已发送')
      } catch (error) {
        ElMessage.error(`发送测试通知失败: ${error}`)
      } finally {
        testing.notification = false
      }
    }
    
    // 生成API令牌
    const generateApiToken = async () => {
      generating.value = true
      
      try {
        const response = await api.settings.generateApiToken()
        apiForm.apiToken = response.token || ''
        ElMessage.success('已生成新的API令牌')
      } catch (error) {
        ElMessage.error(`生成API令牌失败: ${error}`)
      } finally {
        generating.value = false
      }
    }
    
    // 创建备份
    const createBackup = async () => {
      creating.value = true
      
      try {
        const response = await api.settings.createBackup({
          content: backupForm.backupContent,
          compress: backupForm.compressBackup
        })
        
        // 下载备份文件
        if (response.downloadUrl) {
          const link = document.createElement('a')
          link.href = response.downloadUrl
          link.download = response.filename || 'mcp-backup.zip'
          link.click()
        }
        
        ElMessage.success('备份创建成功')
      } catch (error) {
        ElMessage.error(`创建备份失败: ${error}`)
      } finally {
        creating.value = false
      }
    }
    
    // 处理备份文件变更
    const handleBackupFileChange = (file) => {
      backupFile.value = file.raw
    }
    
    // 恢复备份
    const restoreBackup = async () => {
      if (!backupFile.value) {
        ElMessage.warning('请选择备份文件')
        return
      }
      
      // 确认恢复
      try {
        await ElMessageBox.confirm(
          '恢复备份将覆盖当前系统数据，确定要继续吗？',
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch (e) {
        return
      }
      
      restoring.value = true
      
      try {
        // 创建FormData
        const formData = new FormData()
        formData.append('file', backupFile.value)
        
        await api.settings.restoreBackup(formData)
        
        ElMessage.success('备份恢复成功，系统将在3秒后刷新')
        
        // 3秒后刷新页面
        setTimeout(() => {
          window.location.reload()
        }, 3000)
      } catch (error) {
        ElMessage.error(`恢复备份失败: ${error}`)
      } finally {
        restoring.value = false
      }
    }
    
    // 检查更新
    const checkForUpdates = async () => {
      checking.value = true
      
      try {
        const response = await api.settings.checkForUpdates()
        
        if (response.hasUpdate) {
          ElMessageBox.confirm(
            `发现新版本: ${response.latestVersion}\n${response.updateInfo}`,
            '更新可用',
            {
              confirmButtonText: '更新',
              cancelButtonText: '忽略',
              type: 'info'
            }
          ).then(() => {
            // 执行更新
            ElMessage.info('开始更新，请稍候...')
          }).catch(() => {})
        } else {
          ElMessage.info('您当前使用的是最新版本')
        }
      } catch (error) {
        ElMessage.error(`检查更新失败: ${error}`)
      } finally {
        checking.value = false
      }
    }
    
    // 查看许可证
    const viewLicense = () => {
      ElMessageBox.alert(
        '本软件基于MIT许可证发布\n\n' +
        'MIT License\n\n' +
        'Copyright (c) 2023 MCP Platform\n\n' +
        'Permission is hereby granted, free of charge, to any person obtaining a copy ' +
        'of this software and associated documentation files (the "Software"), to deal ' +
        'in the Software without restriction, including without limitation the rights ' +
        'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell ' +
        'copies of the Software, and to permit persons to whom the Software is ' +
        'furnished to do so, subject to the following conditions:\n\n' +
        'The above copyright notice and this permission notice shall be included in all ' +
        'copies or substantial portions of the Software.\n\n' +
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR ' +
        'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, ' +
        'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE ' +
        'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER ' +
        'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, ' +
        'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE ' +
        'SOFTWARE.',
        '许可证信息',
        {
          confirmButtonText: '确定'
        }
      )
    }
    
    // 处理标签页切换
    const handleTabChange = (tab) => {
      activeTab.value = tab
      loadCurrentTabSettings()
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadCurrentTabSettings()
    })
    
    return {
      activeTab,
      loading,
      saving,
      testing,
      generating,
      creating,
      restoring,
      checking,
      systemFormRef,
      userFormRef,
      notificationFormRef,
      securityFormRef,
      apiFormRef,
      backupFormRef,
      systemForm,
      userForm,
      notificationForm,
      securityForm,
      apiForm,
      backupForm,
      backupFile,
      systemInfo,
      // 图标
      Setting,
      User,
      Bell,
      Lock,
      Connection,
      Download,
      InfoFilled,
      // 方法
      handleTabChange,
      saveSystemSettings,
      saveUserSettings,
      saveNotificationSettings,
      saveSecuritySettings,
      saveApiSettings,
      saveBackupSettings,
      resetSystemSettings,
      resetUserSettings,
      resetNotificationSettings,
      resetSecuritySettings,
      resetApiSettings,
      resetBackupSettings,
      testNotification,
      generateApiToken,
      createBackup,
      handleBackupFileChange,
      restoreBackup,
      checkForUpdates,
      viewLicense
    }
  }
}
</script>

<style scoped lang="scss">
.settings-container {
  padding: 0 10px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  h2 {
    margin: 0;
    font-size: 24px;
    color: #303133;
  }
  
  p {
    margin: 5px 0 0;
    color: #909399;
    font-size: 14px;
  }
}

.settings-menu {
  .settings-menu-list {
    border-right: none;
  }
}

.settings-content {
  min-height: 600px;
}

.settings-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.settings-form {
  max-width: 600px;
  
  .el-divider {
    margin: 24px 0;
  }
}

.api-token-input {
  display: flex;
  gap: 10px;
  
  .el-input {
    flex: 1;
  }
}

.backup-upload {
  margin-bottom: 10px;
}

.about-system {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  
  .system-logo {
    margin-bottom: 20px;
    
    img {
      width: 100px;
      height: 100px;
    }
  }
  
  .system-name {
    margin: 0;
    font-size: 24px;
    color: #303133;
  }
  
  .system-version {
    margin: 5px 0 20px;
    color: #909399;
  }
  
  .system-info {
    width: 100%;
    max-width: 500px;
    margin-bottom: 30px;
    
    .info-item {
      margin-bottom: 10px;
      display: flex;
      
      .label {
        width: 150px;
        color: #606266;
        font-weight: bold;
      }
      
      .value {
        flex: 1;
        color: #303133;
      }
    }
  }
  
  .about-actions {
    display: flex;
    gap: 10px;
  }
}
</style> 