<template>
  <LayoutWrapper>
    <div class="configs-container">
      <div class="page-header">
        <div class="page-title">
          <h2>配置管理</h2>
          <p>管理MCP平台系统配置和工具配置</p>
        </div>
        <div class="page-actions">
          <el-button type="primary" @click="showDialog('add')">
            <el-icon><plus /></el-icon> 新建配置
          </el-button>
        </div>
      </div>

      <!-- 搜索和筛选区域 -->
      <el-card shadow="hover" class="filter-card">
        <el-form :inline="true" :model="searchForm" class="filter-form">
          <el-form-item label="配置名称">
            <el-input v-model="searchForm.name" placeholder="请输入配置名称" clearable />
          </el-form-item>
          <el-form-item label="配置类型">
            <el-select v-model="searchForm.type" placeholder="请选择配置类型" clearable>
              <el-option 
                v-for="item in configTypes" 
                :key="item.value" 
                :label="item.label" 
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchConfigs">
              <el-icon><search /></el-icon> 搜索
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><refresh /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 配置列表 -->
      <el-card shadow="hover" class="config-card">
        <el-table
          v-loading="loading"
          :data="configList"
          border
          style="width: 100%"
        >
          <el-table-column label="配置名称" prop="name" min-width="180" show-overflow-tooltip />
          <el-table-column label="配置类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTagType(row.type)">{{ getConfigTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="描述" prop="description" min-width="250" show-overflow-tooltip />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="showDialog('edit', row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="confirmDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>

      <!-- 新增/编辑配置对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogType === 'add' ? '新建配置' : '编辑配置'"
        width="650px"
        destroy-on-close
      >
        <el-form
          ref="configFormRef"
          :model="configForm"
          :rules="configRules"
          label-width="100px"
          status-icon
        >
          <el-form-item label="配置名称" prop="name">
            <el-input v-model="configForm.name" placeholder="请输入配置名称" />
          </el-form-item>
          <el-form-item label="配置类型" prop="type">
            <el-select v-model="configForm.type" placeholder="请选择配置类型" style="width: 100%">
              <el-option
                v-for="item in configTypes"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="configForm.description" type="textarea" rows="2" placeholder="请输入配置描述" />
          </el-form-item>
          <el-form-item label="配置内容" prop="content">
            <el-tabs v-model="activeTab" class="config-tabs">
              <el-tab-pane label="表单视图" name="form">
                <div v-if="configForm.type === 'system'">
                  <!-- 系统配置表单 -->
                  <el-form-item label="日志级别">
                    <el-select v-model="formConfig.log_level" placeholder="请选择日志级别">
                      <el-option label="调试" value="debug" />
                      <el-option label="信息" value="info" />
                      <el-option label="警告" value="warning" />
                      <el-option label="错误" value="error" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="服务端口">
                    <el-input-number v-model="formConfig.port" :min="1" :max="65535" />
                  </el-form-item>
                  <el-form-item label="数据路径">
                    <el-input v-model="formConfig.data_path" />
                  </el-form-item>
                  <el-form-item label="启用调试">
                    <el-switch v-model="formConfig.debug_mode" />
                  </el-form-item>
                </div>
                <div v-else-if="configForm.type === 'tool'">
                  <!-- 工具配置表单 -->
                  <el-form-item label="工具ID">
                    <el-select 
                      v-model="formConfig.tool_id" 
                      placeholder="请选择工具" 
                      filterable
                      @change="handleToolChange"
                    >
                      <el-option 
                        v-for="tool in toolsList" 
                        :key="tool.id" 
                        :label="tool.name" 
                        :value="tool.id" 
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="超时时间">
                    <el-input-number v-model="formConfig.timeout" :min="1" :max="3600" />
                  </el-form-item>
                  <el-form-item label="重试次数">
                    <el-input-number v-model="formConfig.retry_count" :min="0" :max="10" />
                  </el-form-item>
                  <el-form-item label="参数">
                    <el-table :data="formConfig.parameters || []" border style="width: 100%">
                      <el-table-column label="参数名" width="150">
                        <template #default="scope">
                          <el-input v-model="scope.row.name" placeholder="参数名" />
                        </template>
                      </el-table-column>
                      <el-table-column label="参数值">
                        <template #default="scope">
                          <el-input v-model="scope.row.value" placeholder="参数值" />
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="100">
                        <template #default="scope">
                          <el-button type="danger" icon="delete" circle size="small"
                            @click="removeParameter(scope.$index)" />
                        </template>
                      </el-table-column>
                    </el-table>
                    <div style="margin-top: 10px;">
                      <el-button type="primary" size="small" @click="addParameter">添加参数</el-button>
                    </div>
                  </el-form-item>
                </div>
                <div v-else>
                  <el-empty description="请先选择配置类型" />
                </div>
              </el-tab-pane>
              <el-tab-pane label="JSON编辑器" name="json">
                <el-input 
                  v-model="configForm.content" 
                  type="textarea" 
                  rows="10" 
                  placeholder="请输入JSON格式的配置内容"
                  @input="validateJson"
                />
                <div v-if="jsonError" class="json-error">
                  {{ jsonError }}
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm" :loading="submitting">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 删除确认对话框 -->
      <el-dialog
        v-model="deleteDialogVisible"
        title="确认删除"
        width="400px"
      >
        <div>确定要删除配置 <strong>{{ currentConfig?.name }}</strong> 吗？此操作不可恢复！</div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="deleteDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="deleteConfig" :loading="submitting">
              确认删除
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import api from '../api/api'
import LayoutWrapper from '../components/LayoutWrapper.vue'

// 数据加载状态
const loading = ref(false)
const submitting = ref(false)

// 配置列表数据
const configList = ref([])

// 分页信息
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  type: ''
})

// 对话框状态
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogType = ref('add') // 'add' or 'edit'
const activeTab = ref('form')
const jsonError = ref('')
const currentConfig = ref(null)

// 表单引用
const configFormRef = ref(null)

// 配置表单数据
const configForm = reactive({
  id: null,
  name: '',
  type: '',
  description: '',
  content: '{}'
})

// 表单配置 (用于form视图)
const formConfig = reactive({})

// 配置类型选项
const configTypes = [
  { value: 'system', label: '系统配置' },
  { value: 'tool', label: '工具配置' },
  { value: 'template', label: '模板配置' }
]

// 工具列表
const toolsList = ref([])

// 表单验证规则
const configRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择配置类型', trigger: 'change' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入配置内容', trigger: 'blur' }
  ]
}

// 监听表单视图的变化，同步到JSON
watch(formConfig, (newVal) => {
  if (activeTab.value === 'form') {
    try {
      configForm.content = JSON.stringify(newVal, null, 2)
      jsonError.value = ''
    } catch (error) {
      jsonError.value = '表单数据转换为JSON失败'
    }
  }
}, { deep: true })

// 监听JSON的变化，同步到表单视图
watch(() => configForm.content, (newVal) => {
  if (activeTab.value === 'json') {
    try {
      const parsedConfig = JSON.parse(newVal)
      Object.assign(formConfig, parsedConfig)
      jsonError.value = ''
    } catch (error) {
      jsonError.value = 'JSON格式不正确'
    }
  }
})

// 监听配置类型变化
watch(() => configForm.type, (newVal) => {
  // 根据不同的配置类型，设置不同的默认formConfig
  if (newVal === 'system') {
    Object.assign(formConfig, {
      log_level: 'info',
      port: 5000,
      data_path: '/data',
      debug_mode: false
    })
  } else if (newVal === 'tool') {
    Object.assign(formConfig, {
      tool_id: '',
      timeout: 30,
      retry_count: 3,
      parameters: []
    })
  } else {
    Object.assign(formConfig, {})
  }
  
  // 同步到JSON
  configForm.content = JSON.stringify(formConfig, null, 2)
})

// 生命周期钩子
onMounted(() => {
  loadConfigs()
  loadTools()
})

// 加载配置列表
const loadConfigs = async () => {
  loading.value = true
  try {
    const { configs, total } = await api.configs.getList({
      page: pagination.current,
      per_page: pagination.pageSize,
      search: searchForm.name,
      type: searchForm.type
    })
    configList.value = configs
    pagination.total = total
  } catch (error) {
    ElMessage.error(`加载配置列表失败: ${error}`)
  } finally {
    loading.value = false
  }
}

// 加载工具列表（用于工具配置选择）
const loadTools = async () => {
  try {
    const { tools } = await api.tools.getList({ pageSize: 1000 })
    toolsList.value = tools
  } catch (error) {
    ElMessage.error(`加载工具列表失败: ${error}`)
  }
}

// 搜索配置
const searchConfigs = () => {
  pagination.current = 1
  loadConfigs()
}

// 重置搜索
const resetSearch = () => {
  searchForm.name = ''
  searchForm.type = ''
  pagination.current = 1
  loadConfigs()
}

// 显示对话框
const showDialog = (type, config) => {
  dialogType.value = type
  resetForm()
  
  if (type === 'edit' && config) {
    configForm.id = config.id
    configForm.name = config.name
    configForm.type = config.type
    configForm.description = config.description
    configForm.content = config.content
    
    // 解析JSON到表单配置
    try {
      const parsedConfig = JSON.parse(config.content)
      Object.assign(formConfig, parsedConfig)
    } catch (error) {
      ElMessage.warning('配置内容JSON格式不正确')
    }
  }
  
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  if (configFormRef.value) {
    configFormRef.value.resetFields()
  }
  
  configForm.id = null
  configForm.name = ''
  configForm.type = ''
  configForm.description = ''
  configForm.content = '{}'
  
  Object.keys(formConfig).forEach(key => {
    delete formConfig[key]
  })
  
  activeTab.value = 'form'
  jsonError.value = ''
}

// 验证JSON格式
const validateJson = (value) => {
  try {
    if (value) {
      JSON.parse(value)
      jsonError.value = ''
    }
  } catch (error) {
    jsonError.value = 'JSON格式不正确'
  }
}

// 处理工具选择变化
const handleToolChange = async (toolId) => {
  if (!toolId) return
  
  try {
    const tool = await api.tools.getOne(toolId)
    if (tool && tool.config_template) {
      try {
        const templateConfig = JSON.parse(tool.config_template)
        // 合并现有参数和模板参数
        formConfig.parameters = templateConfig.parameters || []
      } catch (error) {
        // 忽略解析错误
      }
    }
  } catch (error) {
    ElMessage.error(`获取工具配置模板失败: ${error}`)
  }
}

// 添加参数
const addParameter = () => {
  if (!formConfig.parameters) {
    formConfig.parameters = []
  }
  formConfig.parameters.push({ name: '', value: '' })
}

// 移除参数
const removeParameter = (index) => {
  formConfig.parameters.splice(index, 1)
}

// 提交表单
const submitForm = async () => {
  if (jsonError.value) {
    ElMessage.error('请先修复JSON格式错误')
    return
  }
  
  configFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (dialogType.value === 'add') {
          await api.configs.create({
            name: configForm.name,
            type: configForm.type,
            description: configForm.description,
            content: configForm.content
          })
          ElMessage.success('创建配置成功')
        } else {
          await api.configs.update(configForm.id, {
            name: configForm.name,
            type: configForm.type,
            description: configForm.description,
            content: configForm.content
          })
          ElMessage.success('更新配置成功')
        }
        
        dialogVisible.value = false
        loadConfigs()
      } catch (error) {
        ElMessage.error(`操作失败: ${error}`)
      } finally {
        submitting.value = false
      }
    } else {
      return false
    }
  })
}

// 确认删除
const confirmDelete = (config) => {
  currentConfig.value = config
  deleteDialogVisible.value = true
}

// 删除配置
const deleteConfig = async () => {
  if (!currentConfig.value || !currentConfig.value.id) return
  
  submitting.value = true
  try {
    await api.configs.delete(currentConfig.value.id)
    ElMessage.success('删除配置成功')
    deleteDialogVisible.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error(`删除失败: ${error}`)
  } finally {
    submitting.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadConfigs()
}

const handleCurrentChange = (current) => {
  pagination.current = current
  loadConfigs()
}

// 工具方法
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleString()
}

const getConfigTypeLabel = (type) => {
  const typeObj = configTypes.find(t => t.value === type)
  return typeObj ? typeObj.label : type
}

const getTagType = (type) => {
  switch (type) {
    case 'system': return 'danger'
    case 'tool': return 'primary'
    case 'template': return 'success'
    default: return ''
  }
}
</script>

<style scoped lang="scss">
.configs-container {
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

.filter-card {
  margin-bottom: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.config-tabs {
  width: 100%;
}

.json-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
}
</style> 