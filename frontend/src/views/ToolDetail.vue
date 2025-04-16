<template>
  <LayoutWrapper>
    <div class="tool-detail-container">
      <!-- 加载中状态 -->
      <el-skeleton :loading="loading" animated>
        <template #template>
          <div class="skeleton-container">
            <el-skeleton-item variant="p" style="width: 50%" />
            <el-skeleton-item variant="text" style="width: 100%; margin-top: 20px" />
            <el-skeleton-item variant="text" style="width: 100%" />
            <el-skeleton-item variant="text" style="width: 100%" />
          </div>
        </template>
        
        <!-- 实际内容 -->
        <template #default>
          <div v-if="tool">
            <!-- 页面标题和操作栏 -->
            <div class="page-header">
              <div class="page-title">
                <h2>{{ tool.name }}</h2>
                <p>工具ID: {{ tool.id }}</p>
              </div>
              
              <div class="page-actions">
                <el-button plain @click="goBack">
                  <el-icon><arrow-left /></el-icon> 返回
                </el-button>
                <el-button type="primary" :icon="Edit" @click="handleEdit">编辑</el-button>
                
                <el-button 
                  v-if="tool.status === 'inactive'" 
                  type="success" 
                  :icon="Check"
                  @click="handleActivate"
                >
                  激活
                </el-button>
                
                <el-button 
                  v-else-if="tool.status === 'active'" 
                  type="info" 
                  :icon="Close"
                  @click="handleDeactivate"
                >
                  停用
                </el-button>
                
                <el-button type="danger" :icon="Delete" @click="handleDelete">删除</el-button>
              </div>
            </div>

            <!-- 工具信息卡片 -->
            <el-card class="tool-info-card">
              <template #header>
                <div class="card-header">
                  <h3>基本信息</h3>
                  <el-tag :type="getStatusType(tool.status)">{{ getStatusLabel(tool.status) }}</el-tag>
                </div>
              </template>
              
              <div class="tool-info">
                <div class="info-item">
                  <span class="label">工具类型:</span>
                  <span class="value">{{ getTypeLabel(tool.type) }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">描述:</span>
                  <span class="value">{{ tool.description || '无描述' }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">命令:</span>
                  <el-tag type="info">{{ tool.command }}</el-tag>
                </div>
                
                <div class="info-item">
                  <span class="label">创建时间:</span>
                  <span class="value">{{ formatDate(tool.created_at) }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">更新时间:</span>
                  <span class="value">{{ formatDate(tool.updated_at) }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">调用次数:</span>
                  <span class="value">{{ tool.invocation_count || 0 }}</span>
                </div>
                
                <div class="info-item">
                  <span class="label">上次调用:</span>
                  <span class="value">{{ tool.last_invoked_at ? formatDate(tool.last_invoked_at) : '从未调用' }}</span>
                </div>
              </div>
            </el-card>

            <!-- 工具配置卡片 -->
            <el-card class="tool-config-card">
              <template #header>
                <div class="card-header">
                  <h3>配置信息</h3>
                </div>
              </template>
              
              <div class="tool-config">
                <pre class="config-json">{{ JSON.stringify(tool.config, null, 2) }}</pre>
              </div>
            </el-card>

            <!-- 调用日志卡片 -->
            <el-card class="tool-logs-card">
              <template #header>
                <div class="card-header">
                  <h3>调用日志</h3>
                  <div class="card-actions">
                    <el-button type="primary" size="small" :icon="Refresh" @click="loadLogs">刷新</el-button>
                  </div>
                </div>
              </template>
              
              <div class="tool-logs">
                <el-table
                  v-loading="logsLoading"
                  :data="logs"
                  style="width: 100%"
                  row-key="id"
                  border
                  stripe
                >
                  <el-table-column prop="id" label="日志ID" width="100" />
                  <el-table-column prop="level" label="级别" width="120">
                    <template #default="{ row }">
                      <el-tag :type="getLogLevelType(row.level)">
                        {{ getLogLevelLabel(row.level) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="created_at" label="调用时间" width="180">
                    <template #default="{ row }">
                      {{ formatDate(row.created_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="duration" label="耗时" width="120">
                    <template #default="{ row }">
                      {{ formatDuration(row.duration) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="params" label="调用参数" show-overflow-tooltip>
                    <template #default="{ row }">
                      <el-popover
                        placement="top"
                        width="400"
                        trigger="click"
                      >
                        <template #reference>
                          <el-button type="text">查看</el-button>
                        </template>
                        <pre>{{ formatJson(row.params) }}</pre>
                      </el-popover>
                    </template>
                  </el-table-column>
                  <el-table-column prop="result" label="调用结果" show-overflow-tooltip>
                    <template #default="{ row }">
                      <el-popover
                        placement="top"
                        width="400"
                        trigger="click"
                      >
                        <template #reference>
                          <el-button type="text">查看</el-button>
                        </template>
                        <pre>{{ formatJson(row.result) }}</pre>
                      </el-popover>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button 
                        type="primary" 
                        size="small" 
                        :icon="Document"
                        @click="viewLogDetail(row)"
                      >
                        详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <!-- 分页组件 -->
                <div class="pagination">
                  <el-pagination
                    v-model:current-page="logsPage"
                    v-model:page-size="logsPageSize"
                    :page-sizes="[10, 20, 50, 100]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="logsTotal"
                    @size-change="handleLogsSizeChange"
                    @current-change="handleLogsCurrentChange"
                  />
                </div>
              </div>
            </el-card>

            <!-- 工具调用测试卡片 -->
            <el-card class="tool-test-card">
              <template #header>
                <div class="card-header">
                  <h3>调用测试</h3>
                </div>
              </template>
              
              <div class="tool-test">
                <el-form :model="invokeForm" ref="invokeFormRef" label-width="120px">
                  <el-form-item label="请求参数">
                    <el-input
                      v-model="invokeForm.params"
                      type="textarea"
                      :rows="5"
                      placeholder="请输入JSON格式的请求参数"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      :loading="invoking" 
                      @click="handleInvoke"
                    >
                      调用工具
                    </el-button>
                  </el-form-item>
                </el-form>
                
                <div v-if="invokeResult" class="invoke-result">
                  <h4>调用结果</h4>
                  <pre>{{ formatJson(invokeResult) }}</pre>
                </div>
              </div>
            </el-card>
          </div>
        </template>
      </el-skeleton>
      
      <!-- 编辑工具对话框 -->
      <el-dialog 
        v-model="dialogVisible" 
        title="编辑工具"
        width="600px"
      >
        <el-form 
          :model="toolForm" 
          ref="toolFormRef"
          :rules="rules"
          label-width="100px"
        >
          <el-form-item label="工具名称" prop="name">
            <el-input v-model="toolForm.name" placeholder="请输入工具名称" />
          </el-form-item>
          
          <el-form-item label="工具类型" prop="type">
            <el-select v-model="toolForm.type" placeholder="请选择工具类型" style="width: 100%">
              <el-option
                v-for="option in typeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="描述" prop="description">
            <el-input 
              v-model="toolForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入工具描述"
            />
          </el-form-item>
          
          <el-form-item label="命令" prop="command">
            <el-input v-model="toolForm.command" placeholder="请输入工具命令" />
          </el-form-item>
          
          <el-form-item label="配置" prop="configStr">
            <el-input 
              v-model="toolForm.configStr" 
              type="textarea" 
              :rows="5"
              placeholder="请输入JSON格式的配置"
            />
          </el-form-item>
          
          <el-form-item label="状态" prop="status">
            <el-select v-model="toolForm.status" placeholder="请选择工具状态" style="width: 100%">
              <el-option
                v-for="option in statusOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitToolForm">确定</el-button>
        </template>
      </el-dialog>
      
      <!-- 日志详情对话框 -->
      <el-dialog 
        v-model="logDialogVisible" 
        title="日志详情"
        width="800px"
      >
        <div v-if="currentLog" class="log-detail">
          <div class="info-item">
            <span class="label">日志ID:</span>
            <span class="value">{{ currentLog.id }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">级别:</span>
            <el-tag :type="getLogLevelType(currentLog.level)">
              {{ getLogLevelLabel(currentLog.level) }}
            </el-tag>
          </div>
          
          <div class="info-item">
            <span class="label">消息:</span>
            <span class="value">{{ currentLog.message }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">调用时间:</span>
            <span class="value">{{ formatDate(currentLog.created_at) }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">耗时:</span>
            <span class="value">{{ formatDuration(currentLog.duration) }}</span>
          </div>
          
          <el-divider content-position="left">调用参数</el-divider>
          <pre class="detail-json">{{ formatJson(currentLog.params) }}</pre>
          
          <el-divider content-position="left">调用结果</el-divider>
          <pre class="detail-json">{{ formatJson(currentLog.result) }}</pre>
        </div>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import api from '../api/api'
import LayoutWrapper from '../components/LayoutWrapper.vue'

export default {
  name: 'ToolDetail',
  components: {
    LayoutWrapper,
    ...ElementPlusIconsVue
  },
  setup() {
    // 路由
    const route = useRoute()
    const router = useRouter()
    
    // 工具ID
    const toolId = ref(route.params.id)
    
    // 工具数据
    const tool = ref(null)
    const loading = ref(true)
    
    // 表单相关
    const dialogVisible = ref(false)
    const toolFormRef = ref(null)
    const submitting = ref(false)
    
    // 日志相关
    const logs = ref([])
    const logsLoading = ref(false)
    const logsPage = ref(1)
    const logsPageSize = ref(10)
    const logsTotal = ref(0)
    
    // 日志详情对话框
    const logDialogVisible = ref(false)
    const currentLog = ref(null)
    
    // 调用测试相关
    const invokeFormRef = ref(null)
    const invoking = ref(false)
    const invokeResult = ref(null)
    const invokeForm = reactive({
      params: '{}'
    })
    
    // 工具类型选项
    const typeOptions = [
      { value: 'system', label: '系统工具' },
      { value: 'web', label: 'Web工具' },
      { value: 'data', label: '数据处理' },
      { value: 'ai', label: '人工智能' },
      { value: 'other', label: '其他工具' }
    ]
    
    // 工具状态选项
    const statusOptions = [
      { value: 'active', label: '已激活' },
      { value: 'inactive', label: '未激活' },
      { value: 'error', label: '错误' }
    ]
    
    // 日志级别选项
    const logLevelOptions = [
      { value: 'info', label: '信息' },
      { value: 'warning', label: '警告' },
      { value: 'error', label: '错误' },
      { value: 'debug', label: '调试' }
    ]
    
    // 工具编辑表单
    const toolForm = reactive({
      name: '',
      type: 'other',
      description: '',
      command: '',
      configStr: '{}',
      status: 'inactive'
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入工具名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择工具类型', trigger: 'change' }
      ],
      command: [
        { required: true, message: '请输入工具命令', trigger: 'blur' }
      ],
      configStr: [
        { 
          validator: (rule, value, callback) => {
            try {
              if (value) {
                JSON.parse(value)
              }
              callback()
            } catch (error) {
              callback(new Error('配置必须是有效的JSON格式'))
            }
          }, 
          trigger: 'blur' 
        }
      ],
      status: [
        { required: true, message: '请选择工具状态', trigger: 'change' }
      ]
    }
    
    // 图标
    const Edit = ElementPlusIconsVue.Edit
    const Delete = ElementPlusIconsVue.Delete
    const Check = ElementPlusIconsVue.Check 
    const Close = ElementPlusIconsVue.Close
    const Refresh = ElementPlusIconsVue.Refresh
    const Document = ElementPlusIconsVue.Document
    const ArrowLeft = ElementPlusIconsVue.ArrowLeft
    
    // 监听路由参数变化
    watch(() => route.params.id, (newId) => {
      if (newId !== toolId.value) {
        toolId.value = newId
        loadTool()
      }
    })
    
    // 获取工具类型标签
    const getTypeLabel = (type) => {
      const typeObj = typeOptions.find(t => t.value === type)
      return typeObj ? typeObj.label : type
    }
    
    // 获取工具状态标签
    const getStatusLabel = (status) => {
      const statusObj = statusOptions.find(s => s.value === status)
      return statusObj ? statusObj.label : status
    }
    
    // 获取状态类型（标签颜色）
    const getStatusType = (status) => {
      switch (status) {
        case 'active': return 'success'
        case 'inactive': return 'info'
        case 'error': return 'danger'
        default: return 'info'
      }
    }
    
    // 获取日志级别标签
    const getLogLevelLabel = (level) => {
      const levelObj = logLevelOptions.find(l => l.value === level)
      return levelObj ? levelObj.label : level
    }
    
    // 获取日志级别类型（标签颜色）
    const getLogLevelType = (level) => {
      switch (level) {
        case 'info': return 'info'
        case 'warning': return 'warning'
        case 'error': return 'danger'
        case 'debug': return 'success'
        default: return 'info'
      }
    }
    
    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '无'
      const date = new Date(dateStr)
      return date.toLocaleString()
    }
    
    // 格式化持续时间
    const formatDuration = (ms) => {
      if (!ms || ms <= 0) return '0ms'
      if (ms < 1000) return `${ms}ms`
      return `${(ms / 1000).toFixed(2)}s`
    }
    
    // 格式化JSON
    const formatJson = (json) => {
      try {
        if (typeof json === 'string') {
          return JSON.stringify(JSON.parse(json), null, 2)
        }
        return JSON.stringify(json, null, 2)
      } catch (e) {
        return json
      }
    }
    
    // 加载工具详情
    const loadTool = async () => {
      loading.value = true
      
      try {
        const response = await api.tools.getOne(toolId.value)
        tool.value = response
        
        // 初始化日志列表
        loadLogs()
      } catch (error) {
        ElMessage.error(`加载工具详情失败: ${error}`)
      } finally {
        loading.value = false
      }
    }
    
    // 加载工具日志
    const loadLogs = async () => {
      logsLoading.value = true
      
      try {
        const params = {
          page: logsPage.value,
          per_page: logsPageSize.value,
          tool_id: toolId.value
        }
        
        const response = await api.logs.getToolLogs(toolId.value, params)
        logs.value = response.logs || []
        logsTotal.value = response.total || 0
      } catch (error) {
        ElMessage.error(`加载日志失败: ${error}`)
      } finally {
        logsLoading.value = false
      }
    }
    
    // 处理编辑按钮
    const handleEdit = () => {
      // 初始化表单数据
      toolForm.name = tool.value.name
      toolForm.type = tool.value.type
      toolForm.description = tool.value.description || ''
      toolForm.command = tool.value.command
      toolForm.configStr = JSON.stringify(tool.value.config, null, 2)
      toolForm.status = tool.value.status
      
      // 显示对话框
      dialogVisible.value = true
    }
    
    // 处理激活按钮
    const handleActivate = async () => {
      try {
        await api.tools.activate(toolId.value)
        ElMessage.success(`工具 "${tool.value.name}" 已启用`)
        loadTool()
      } catch (error) {
        ElMessage.error(`启用工具失败: ${error}`)
      }
    }
    
    // 处理停用按钮
    const handleDeactivate = async () => {
      try {
        await api.tools.deactivate(toolId.value)
        ElMessage.success(`工具 "${tool.value.name}" 已停用`)
        loadTool()
      } catch (error) {
        ElMessage.error(`停用工具失败: ${error}`)
      }
    }
    
    // 处理删除按钮
    const handleDelete = () => {
      ElMessageBox.confirm(
        `确定要删除工具 "${tool.value.name}" 吗？此操作不可恢复。`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await api.tools.delete(toolId.value)
          ElMessage.success(`工具 "${tool.value.name}" 已删除`)
          router.push('/tools')
        } catch (error) {
          ElMessage.error(`删除工具失败: ${error}`)
        }
      }).catch(() => {})
    }
    
    // 处理调用测试
    const handleInvoke = async () => {
      invoking.value = true
      
      try {
        // 解析参数JSON
        let params
        try {
          params = JSON.parse(invokeForm.params)
        } catch (err) {
          ElMessage.error('请求参数必须是有效的JSON格式')
          invoking.value = false
          return
        }
        
        // 调用工具
        const response = await api.tools.invoke(toolId.value, params)
        invokeResult.value = response
        
        ElMessage.success('工具调用成功')
        
        // 刷新工具详情和日志
        loadTool()
      } catch (error) {
        ElMessage.error(`工具调用失败: ${error}`)
        invokeResult.value = { error: error.toString() }
      } finally {
        invoking.value = false
      }
    }
    
    // 提交工具表单
    const submitToolForm = () => {
      toolFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        submitting.value = true
        
        try {
          // 构建提交数据
          const submitData = {
            name: toolForm.name,
            type: toolForm.type,
            description: toolForm.description,
            command: toolForm.command,
            status: toolForm.status
          }
          
          // 解析配置JSON
          try {
            submitData.config = JSON.parse(toolForm.configStr)
          } catch (err) {
            ElMessage.error('配置JSON格式无效')
            submitting.value = false
            return
          }
          
          // 更新工具
          await api.tools.update(toolId.value, submitData)
          ElMessage.success('工具更新成功')
          
          // 关闭对话框并刷新详情
          dialogVisible.value = false
          loadTool()
        } catch (error) {
          ElMessage.error(`更新工具失败: ${error}`)
        } finally {
          submitting.value = false
        }
      })
    }
    
    // 查看日志详情
    const viewLogDetail = (log) => {
      currentLog.value = log
      logDialogVisible.value = true
    }
    
    // 分页处理
    const handleLogsSizeChange = (size) => {
      logsPageSize.value = size
      loadLogs()
    }
    
    const handleLogsCurrentChange = (current) => {
      logsPage.value = current
      loadLogs()
    }
    
    // 返回上一页
    const goBack = () => {
      router.back()
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadTool()
    })
    
    return {
      tool,
      loading,
      toolId,
      logs,
      logsLoading,
      logsPage,
      logsPageSize,
      logsTotal,
      logDialogVisible,
      currentLog,
      dialogVisible,
      toolFormRef,
      toolForm,
      typeOptions,
      statusOptions,
      logLevelOptions,
      submitting,
      // 调用测试相关
      invokeFormRef,
      invokeForm,
      invokeResult,
      invoking,
      // 表单验证规则
      rules,
      // 图标
      Edit,
      Delete,
      Check,
      Close,
      Refresh,
      Document,
      ArrowLeft,
      // 方法
      getTypeLabel,
      getStatusLabel,
      getStatusType,
      getLogLevelLabel,
      getLogLevelType,
      formatDate,
      formatDuration,
      formatJson,
      loadTool,
      loadLogs,
      viewLogDetail,
      handleEdit,
      handleDelete,
      handleActivate,
      handleDeactivate,
      handleInvoke,
      submitToolForm,
      handleLogsSizeChange,
      handleLogsCurrentChange,
      goBack
    }
  }
}
</script>

<style scoped lang="scss">
.tool-detail-container {
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

.tool-info-card,
.tool-config-card,
.tool-logs-card,
.tool-test-card {
  margin-bottom: 20px;
}

.tool-info {
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

.tool-config {
  .config-json {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.invoke-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  
  h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #303133;
  }
  
  pre {
    margin: 0;
    font-family: monospace;
    font-size: 14px;
  }
}

.log-detail {
  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    
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
  
  .detail-json {
    background-color: #f5f7fa;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0 20px;
    overflow: auto;
    max-height: 300px;
    font-family: monospace;
    font-size: 14px;
    
    &.error {
      background-color: #fef0f0;
      color: #f56c6c;
    }
  }
  
  .no-error {
    color: #67c23a;
    margin: 10px 0 20px;
  }
}
</style> 