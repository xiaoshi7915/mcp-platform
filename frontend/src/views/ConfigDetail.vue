<template>
  <div class="config-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-title">
        <h2>{{ config.name || '配置详情' }}</h2>
        <p>{{ config.description || '查看和管理配置详情' }}</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" :icon="Edit" @click="handleEdit" v-if="config.id">编辑</el-button>
        <el-button type="success" :icon="Check" @click="handleActivate" v-if="config.id && !config.is_active">启用</el-button>
        <el-button type="warning" :icon="Close" @click="handleDeactivate" v-if="config.id && config.is_active">停用</el-button>
        <el-button type="danger" :icon="Delete" @click="handleDelete" v-if="config.id">删除</el-button>
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="skeleton-container">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else>
      <!-- 配置信息卡片 -->
      <el-card class="config-info-card">
        <template #header>
          <div class="card-header">
            <h3>基本信息</h3>
          </div>
        </template>
        <div class="config-info">
          <div class="info-item">
            <div class="label">名称</div>
            <div class="value">{{ config.name }}</div>
          </div>
          <div class="info-item">
            <div class="label">类型</div>
            <div class="value">
              <el-tag :type="getTypeColor(config.type)">{{ getTypeLabel(config.type) }}</el-tag>
            </div>
          </div>
          <div class="info-item">
            <div class="label">描述</div>
            <div class="value">{{ config.description || '暂无描述' }}</div>
          </div>
          <div class="info-item">
            <div class="label">状态</div>
            <div class="value">
              <el-tag :type="getStatusType(config.is_active)">
                {{ getStatusLabel(config.is_active) }}
              </el-tag>
            </div>
          </div>
          <div class="info-item">
            <div class="label">创建时间</div>
            <div class="value">{{ formatDate(config.created_at) }}</div>
          </div>
          <div class="info-item">
            <div class="label">更新时间</div>
            <div class="value">{{ formatDate(config.updated_at) }}</div>
          </div>
        </div>
      </el-card>

      <!-- 配置内容卡片 -->
      <el-card class="config-content-card">
        <template #header>
          <div class="card-header">
            <h3>配置内容</h3>
          </div>
        </template>
        <div class="config-content">
          <pre class="content-json">{{ formatJson(config.content) }}</pre>
        </div>
      </el-card>
    </div>

    <!-- 编辑配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑配置"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="configForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="configForm.type" placeholder="选择配置类型" style="width: 100%">
            <el-option
              v-for="option in typeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="configForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="configForm.is_active"
            :active-value="true"
            :inactive-value="false"
            active-text="已启用"
            inactive-text="已停用"
          />
        </el-form-item>
        <el-form-item label="内容" prop="contentStr">
          <el-tabs v-model="activeContentTab">
            <el-tab-pane label="JSON编辑" name="json">
              <el-input
                v-model="configForm.contentStr"
                type="textarea"
                rows="10"
                placeholder="请输入JSON格式的配置内容"
                :autosize="{ minRows: 10, maxRows: 20 }"
                font-family="monospace"
              />
            </el-tab-pane>
            <el-tab-pane label="表单编辑" name="form">
              <div v-if="parsedContent.length > 0">
                <div v-for="(item, index) in parsedContent" :key="index" class="content-form-item">
                  <el-row :gutter="10">
                    <el-col :span="8">
                      <el-input v-model="item.key" placeholder="键名" @input="updateContentStr" />
                    </el-col>
                    <el-col :span="12">
                      <el-input v-model="item.value" placeholder="值" @input="updateContentStr" />
                    </el-col>
                    <el-col :span="4">
                      <el-button type="danger" icon="Delete" @click="removeContentField(index)" />
                    </el-col>
                  </el-row>
                </div>
              </div>
              <div v-else class="empty-content">
                <p>当前配置内容为空，请添加字段或使用JSON编辑</p>
              </div>
              <div class="add-field">
                <el-button type="primary" @click="showAddFieldDialog">添加字段</el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitConfigForm" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加字段对话框 -->
    <el-dialog
      v-model="addFieldDialogVisible"
      title="添加字段"
      width="500px"
      append-to-body
    >
      <el-form :model="newField" label-width="80px">
        <el-form-item label="键名" required>
          <el-input v-model="newField.key" placeholder="请输入键名" />
        </el-form-item>
        <el-form-item label="值" required>
          <el-input v-model="newField.value" placeholder="请输入值" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addFieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addContentField">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import api from '../api/api'

export default {
  name: 'ConfigDetail',
  components: {
    ...ElementPlusIconsVue
  },
  setup() {
    // 路由
    const route = useRoute()
    const router = useRouter()
    
    // 图标
    const Edit = ElementPlusIconsVue.Edit
    const Delete = ElementPlusIconsVue.Delete
    const Check = ElementPlusIconsVue.Check 
    const Close = ElementPlusIconsVue.Close
    const ArrowLeft = ElementPlusIconsVue.ArrowLeft
    
    // 状态变量
    const loading = ref(true)
    const submitting = ref(false)
    const config = ref({})
    const configId = computed(() => route.params.id)
    const dialogVisible = ref(false)
    const configFormRef = ref(null)
    const activeContentTab = ref('json')
    const addFieldDialogVisible = ref(false)
    const newField = reactive({
      key: '',
      value: ''
    })
    
    // 配置表单
    const configForm = reactive({
      name: '',
      type: '',
      description: '',
      is_active: true,
      contentStr: '{}'
    })
    
    // 解析的配置内容
    const parsedContent = ref([])
    
    // 类型选项
    const typeOptions = [
      { value: 'system', label: '系统配置' },
      { value: 'user', label: '用户配置' },
      { value: 'application', label: '应用配置' },
      { value: 'other', label: '其他' }
    ]
    
    // 表单校验规则
    const rules = {
      name: [
        { required: true, message: '请输入配置名称', trigger: 'blur' },
        { min: 2, max: 100, message: '长度在 2 到 100 个字符之间', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择配置类型', trigger: 'change' }
      ],
      contentStr: [
        { required: true, message: '请输入配置内容', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            try {
              JSON.parse(value)
              callback()
            } catch (err) {
              callback(new Error('请输入有效的JSON格式'))
            }
          }, 
          trigger: 'blur' 
        }
      ]
    }
    
    // 加载配置详情
    const loadConfig = async () => {
      if (!configId.value) {
        config.value = {}
        loading.value = false
        return
      }
      
      loading.value = true
      
      try {
        const response = await api.configs.get(configId.value)
        config.value = response
        parseContent()
      } catch (error) {
        ElMessage.error(`加载配置详情失败: ${error}`)
      } finally {
        loading.value = false
      }
    }
    
    // 解析配置内容
    const parseContent = () => {
      try {
        const content = config.value.content || {}
        parsedContent.value = Object.entries(content).map(([key, value]) => ({
          key,
          value: typeof value === 'object' ? JSON.stringify(value) : String(value)
        }))
      } catch (error) {
        console.error('解析配置内容失败', error)
        parsedContent.value = []
      }
    }
    
    // 更新配置内容字符串
    const updateContentStr = () => {
      try {
        const contentObj = {}
        parsedContent.value.forEach(item => {
          contentObj[item.key] = item.value
        })
        configForm.contentStr = JSON.stringify(contentObj, null, 2)
      } catch (error) {
        console.error('更新配置内容字符串失败', error)
      }
    }
    
    // 添加内容字段
    const addContentField = () => {
      if (!newField.key.trim()) {
        ElMessage.warning('键名不能为空')
        return
      }
      
      parsedContent.value.push({
        key: newField.key,
        value: newField.value
      })
      
      // 更新JSON字符串
      updateContentStr()
      
      // 重置新字段表单
      newField.key = ''
      newField.value = ''
      
      // 关闭对话框
      addFieldDialogVisible.value = false
    }
    
    // 移除内容字段
    const removeContentField = (index) => {
      parsedContent.value.splice(index, 1)
      updateContentStr()
    }
    
    // 显示添加字段对话框
    const showAddFieldDialog = () => {
      addFieldDialogVisible.value = true
    }
    
    // 处理编辑按钮
    const handleEdit = () => {
      // 初始化表单数据
      configForm.name = config.value.name || ''
      configForm.type = config.value.type || ''
      configForm.description = config.value.description || ''
      configForm.is_active = config.value.is_active || false
      configForm.contentStr = formatJson(config.value.content)
      
      // 显示对话框
      dialogVisible.value = true
      
      // 默认选择JSON编辑模式
      activeContentTab.value = 'json'
    }
    
    // 处理激活按钮
    const handleActivate = async () => {
      try {
        await api.configs.activate(configId.value)
        ElMessage.success(`配置 "${config.value.name}" 已启用`)
        loadConfig()
      } catch (error) {
        ElMessage.error(`启用配置失败: ${error}`)
      }
    }
    
    // 处理停用按钮
    const handleDeactivate = async () => {
      try {
        await api.configs.deactivate(configId.value)
        ElMessage.success(`配置 "${config.value.name}" 已停用`)
        loadConfig()
      } catch (error) {
        ElMessage.error(`停用配置失败: ${error}`)
      }
    }
    
    // 处理删除按钮
    const handleDelete = () => {
      ElMessageBox.confirm(
        `确定要删除配置 "${config.value.name}" 吗？此操作不可恢复。`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await api.configs.delete(configId.value)
          ElMessage.success(`配置 "${config.value.name}" 已删除`)
          router.push('/configs')
        } catch (error) {
          ElMessage.error(`删除配置失败: ${error}`)
        }
      }).catch(() => {})
    }
    
    // 提交配置表单
    const submitConfigForm = () => {
      configFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        submitting.value = true
        
        try {
          // 构建提交数据
          const submitData = {
            name: configForm.name,
            type: configForm.type,
            description: configForm.description,
            is_active: configForm.is_active
          }
          
          // 解析配置内容
          try {
            submitData.content = JSON.parse(configForm.contentStr)
          } catch (err) {
            ElMessage.error('配置内容JSON格式无效')
            submitting.value = false
            return
          }
          
          // 更新配置
          if (configId.value) {
            await api.configs.update(configId.value, submitData)
            ElMessage.success('配置更新成功')
          } else {
            const response = await api.configs.create(submitData)
            router.replace(`/configs/${response.id}`)
            ElMessage.success('配置创建成功')
          }
          
          // 关闭对话框并刷新详情
          dialogVisible.value = false
          loadConfig()
        } catch (error) {
          ElMessage.error(`保存配置失败: ${error}`)
        } finally {
          submitting.value = false
        }
      })
    }
    
    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    // 工具方法
    const getTypeLabel = (type) => {
      const option = typeOptions.find(opt => opt.value === type)
      return option ? option.label : type
    }
    
    const getTypeColor = (type) => {
      switch (type) {
        case 'system': return 'danger'
        case 'user': return 'warning'
        case 'application': return 'success'
        default: return 'info'
      }
    }
    
    const getStatusLabel = (active) => {
      return active ? '已启用' : '已停用'
    }
    
    const getStatusType = (active) => {
      return active ? 'success' : 'info'
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return '无'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    const formatJson = (json) => {
      if (!json) return '{}'
      try {
        return JSON.stringify(json, null, 2)
      } catch (error) {
        return '{}'
      }
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadConfig()
    })
    
    return {
      config,
      loading,
      configId,
      dialogVisible,
      configFormRef,
      configForm,
      activeContentTab,
      parsedContent,
      addFieldDialogVisible,
      newField,
      typeOptions,
      rules,
      submitting,
      // 图标
      Edit,
      Delete,
      Check,
      Close,
      ArrowLeft,
      // 方法
      getTypeLabel,
      getTypeColor,
      getStatusLabel,
      getStatusType,
      formatDate,
      formatJson,
      loadConfig,
      parseContent,
      updateContentStr,
      addContentField,
      removeContentField,
      showAddFieldDialog,
      handleEdit,
      handleDelete,
      handleActivate,
      handleDeactivate,
      submitConfigForm,
      goBack
    }
  }
}
</script>

<style scoped lang="scss">
.config-detail-container {
  padding: 0 10px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.page-actions {
  display: flex;
  gap: 10px;
}

.skeleton-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    font-size: 18px;
    color: #303133;
  }
  
  .card-actions {
    display: flex;
    gap: 10px;
  }
}

.config-info-card,
.config-content-card {
  margin-bottom: 20px;
}

.config-info {
  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
    
    .label {
      width: 100px;
      color: #606266;
      font-weight: bold;
    }
    
    .value {
      flex: 1;
      color: #303133;
    }
  }
}

.config-content {
  .content-json {
    background-color: #f5f7fa;
    border-radius: 4px;
    padding: 15px;
    margin: 0;
    overflow: auto;
    max-height: 300px;
    font-family: monospace;
    font-size: 14px;
  }
}

.content-form-item {
  margin-bottom: 10px;
}

.empty-content {
  text-align: center;
  color: #909399;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.add-field {
  margin-top: 15px;
  text-align: center;
}
</style> 