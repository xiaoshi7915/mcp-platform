<template>
  <LayoutWrapper>
    <div class="logs-container">
      <!-- 页面标题和操作栏 -->
      <div class="page-header">
        <div class="page-title">
          <h2>日志管理</h2>
          <p>查看和管理系统操作日志</p>
        </div>
        
        <div class="page-actions">
          <el-button type="danger" :icon="Delete" @click="handleClearLogs">清空日志</el-button>
        </div>
      </div>
      
      <!-- 筛选表单 -->
      <el-card class="logs-filters">
        <el-form :model="filterForm" inline @submit.prevent="handleSearch">
          <el-form-item label="日志ID">
            <el-input 
              v-model="filterForm.id" 
              placeholder="按日志ID搜索" 
              clearable 
              @clear="handleSearch"
            />
          </el-form-item>
          
          <el-form-item label="工具">
            <el-select 
              v-model="filterForm.tool_id" 
              placeholder="选择工具" 
              clearable 
              filterable 
              @change="handleSearch"
              style="width: 200px"
            >
              <el-option
                v-for="tool in tools"
                :key="tool.id"
                :label="tool.name"
                :value="tool.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="级别">
            <el-select 
              v-model="filterForm.level" 
              placeholder="选择级别" 
              clearable 
              @change="handleSearch"
              style="width: 150px"
            >
              <el-option
                v-for="option in levelOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DDTHH:mm:ss"
              @change="handleSearch"
              style="width: 380px"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
            <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 日志列表 -->
      <el-card class="logs-list">
        <el-table
          v-loading="loading"
          :data="logs"
          style="width: 100%"
          row-key="id"
          border
          stripe
        >
          <el-table-column prop="id" label="日志ID" width="80" sortable />
          <el-table-column label="工具" min-width="150">
            <template #default="{ row }">
              <el-link 
                v-if="row.tool_id" 
                type="primary" 
                @click="navigateToTool(row.tool_id)"
              >
                {{ getToolName(row.tool_id) }}
              </el-link>
              <span v-else>系统</span>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="级别" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)">
                {{ getLevelLabel(row.level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="180" sortable>
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
          <el-table-column prop="duration" label="耗时" width="120">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column label="调用参数" width="100">
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
          <el-table-column label="调用结果" width="100">
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
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                :icon="Document"
                @click="viewLogDetail(row)"
              >
                详情
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete"
                @click="handleDeleteLog(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
      
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
            <span class="label">工具:</span>
            <span class="value">
              <el-link 
                v-if="currentLog.tool_id" 
                type="primary" 
                @click="navigateToTool(currentLog.tool_id)"
              >
                {{ getToolName(currentLog.tool_id) }}
              </el-link>
              <span v-else>系统</span>
            </span>
          </div>
          
          <div class="info-item">
            <span class="label">级别:</span>
            <el-tag :type="getLevelType(currentLog.level)">
              {{ getLevelLabel(currentLog.level) }}
            </el-tag>
          </div>
          
          <div class="info-item">
            <span class="label">消息:</span>
            <span class="value">{{ currentLog.message }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">时间:</span>
            <span class="value">{{ formatDate(currentLog.created_at) }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">耗时:</span>
            <span class="value">{{ formatDuration(currentLog.duration) }}</span>
          </div>
          
          <div class="info-item" v-if="currentLog.caller">
            <span class="label">调用者:</span>
            <span class="value">{{ currentLog.caller }}</span>
          </div>
          
          <el-divider content-position="left">调用参数</el-divider>
          <pre class="detail-json">{{ formatJson(currentLog.params) }}</pre>
          
          <el-divider content-position="left">调用结果</el-divider>
          <pre class="detail-json">{{ formatJson(currentLog.result) }}</pre>
        </div>
      </el-dialog>
      
      <!-- 清空日志确认对话框 -->
      <el-dialog
        v-model="clearDialogVisible"
        title="警告"
        width="400px"
      >
        <span>确定要清空所有日志吗？此操作不可恢复。</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="clearDialogVisible = false">取消</el-button>
            <el-button type="danger" :loading="clearing" @click="confirmClearLogs">
              确认清空
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete, Document } from '@element-plus/icons-vue'
import api from '../api/api'
import LayoutWrapper from '../components/LayoutWrapper.vue'

// 路由
const router = useRouter()
    
// 日志数据
const logs = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
    
// 工具列表
const tools = ref([])
    
// 日志级别选项
const levelOptions = [
  { value: 'info', label: '信息' },
  { value: 'warning', label: '警告' },
  { value: 'error', label: '错误' },
  { value: 'debug', label: '调试' }
]
    
// 筛选表单
const filterForm = reactive({
  id: '',
  tool_id: '',
  level: '',
  dateRange: null
})
    
// 日志详情
const logDialogVisible = ref(false)
const currentLog = ref(null)
    
// 清空日志
const clearDialogVisible = ref(false)
const clearing = ref(false)
    
// 获取工具名称
const getToolName = (toolId) => {
  const tool = tools.value.find(t => t.id === toolId)
  return tool ? tool.name : toolId
}
    
// 获取级别标签
const getLevelLabel = (level) => {
  const levelObj = levelOptions.find(l => l.value === level)
  return levelObj ? levelObj.label : level
}
    
// 获取级别类型（标签颜色）
const getLevelType = (level) => {
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
    return json || '无数据'
  }
}
    
// 加载日志
const loadLogs = async () => {
  loading.value = true
  
  try {
    // 构建查询参数
    const params = {
      page: page.value,
      per_page: pageSize.value
    }
    
    // 添加筛选条件
    if (filterForm.id) {
      params.id = filterForm.id
    }
    
    if (filterForm.tool_id) {
      params.tool_id = filterForm.tool_id
    }
    
    if (filterForm.level) {
      params.level = filterForm.level
    }
    
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }
    
    const response = await api.logs.getList(params)
    logs.value = response.logs || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error(`加载日志失败: ${error}`)
    logs.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}
    
// 加载工具列表
const loadTools = async () => {
  try {
    const response = await api.tools.getList({ per_page: 1000 })
    tools.value = response.tools || []
  } catch (error) {
    console.error(`加载工具列表失败: ${error}`)
    tools.value = []
  }
}
    
// 跳转到工具详情
const navigateToTool = (toolId) => {
  if (logDialogVisible.value) {
    logDialogVisible.value = false
  }
  router.push(`/tool/${toolId}`)
}
    
// 查看日志详情
const viewLogDetail = (log) => {
  currentLog.value = log
  logDialogVisible.value = true
}
    
// 处理删除单条日志
const handleDeleteLog = (log) => {
  ElMessageBox.confirm(
    `确定要删除ID为 "${log.id}" 的日志吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.logs.delete(log.id)
      ElMessage.success(`日志已删除`)
      loadLogs()
    } catch (error) {
      ElMessage.error(`删除日志失败: ${error}`)
    }
  }).catch(() => {})
}
    
// 处理清空日志
const handleClearLogs = () => {
  clearDialogVisible.value = true
}
    
// 确认清空日志
const confirmClearLogs = async () => {
  clearing.value = true
  
  try {
    // 构建清空参数
    const params = {}
    
    if (filterForm.tool_id) {
      params.tool_id = filterForm.tool_id
    }
    
    if (filterForm.level) {
      params.level = filterForm.level
    }
    
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      const daysAgo = Math.ceil((new Date() - new Date(filterForm.dateRange[0])) / (1000 * 60 * 60 * 24))
      params.days_before = daysAgo
    }
    
    await api.logs.clear(params)
    
    ElMessage.success('日志已清空')
    clearDialogVisible.value = false
    
    // 重新加载日志
    loadLogs()
  } catch (error) {
    ElMessage.error(`清空日志失败: ${error}`)
  } finally {
    clearing.value = false
  }
}
    
// 处理搜索
const handleSearch = () => {
  page.value = 1
  loadLogs()
}
    
// 重置过滤器
const resetFilters = () => {
  filterForm.id = ''
  filterForm.tool_id = ''
  filterForm.level = ''
  filterForm.dateRange = null
  handleSearch()
}
    
// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  loadLogs()
}
    
const handleCurrentChange = (current) => {
  page.value = current
  loadLogs()
}
    
// 组件挂载时加载数据
onMounted(() => {
  loadLogs()
  loadTools()
})
</script>

<style scoped lang="scss">
.logs-container {
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

.logs-filters {
  margin-bottom: 20px;
}

.logs-list {
  .el-table {
    margin-bottom: 20px;
  }
  
  .pagination {
    display: flex;
    justify-content: flex-end;
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