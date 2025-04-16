<template>
  <LayoutWrapper>
    <div class="tools-container">
      <!-- 页面标题和操作栏 -->
      <div class="page-header">
        <div class="page-title">
          <h2>工具管理</h2>
          <p>管理和监控所有 MCP 工具</p>
        </div>
        <div class="page-actions">
          <el-button type="primary" @click="handleCreate">
            <el-icon><plus /></el-icon> 创建工具
          </el-button>
        </div>
      </div>

      <!-- 搜索和过滤器 -->
      <div class="tools-filters card">
        <el-form :inline="true" :model="filterForm" @submit.prevent>
          <el-form-item label="工具名称">
            <el-input 
              v-model="filterForm.search" 
              placeholder="搜索工具名称或描述" 
              clearable 
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-form-item>
          <el-form-item label="工具类型">
            <el-select v-model="filterForm.type" placeholder="全部类型" clearable @change="handleSearch">
              <el-option v-for="type in toolTypes" :key="type.value" :label="type.label" :value="type.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleSearch">
              <el-option v-for="status in statusOptions" :key="status.value" :label="status.label" :value="status.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 工具列表 -->
      <div class="tools-list card">
        <el-table 
          v-loading="loading" 
          :data="tools" 
          style="width: 100%"
          border
          stripe
        >
          <el-table-column label="工具名称" min-width="200">
            <template #default="{ row }">
              <div class="tool-info">
                <span class="tool-name">{{ row.name }}</span>
                <p v-if="row.description" class="tool-desc">{{ row.description }}</p>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="类型" prop="type" min-width="120">
            <template #default="{ row }">
              <el-tag>{{ getToolTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" effect="plain">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="调用次数" prop="invoke_count" width="100" align="center" />
          <el-table-column label="最近调用" width="160">
            <template #default="{ row }">
              {{ row.last_invoked_at ? formatDate(row.last_invoked_at) : '从未调用' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" align="center">
            <template #default="{ row }">
              <el-button-group>
                <el-button size="small" type="primary" @click="handleDetail(row)">详情</el-button>
                <el-button 
                  size="small" 
                  type="success" 
                  :disabled="row.status === 'active'"
                  @click="handleActivate(row)"
                >
                  启用
                </el-button>
                <el-button 
                  size="small" 
                  type="warning" 
                  :disabled="row.status !== 'active'"
                  @click="handleDeactivate(row)"
                >
                  停用
                </el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:currentPage="page"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 创建/编辑工具对话框 -->
      <el-dialog 
        v-model="dialogVisible" 
        :title="dialogType === 'create' ? '创建工具' : '编辑工具'" 
        width="600px"
      >
        <el-form 
          :model="toolForm" 
          :rules="toolRules"
          ref="toolFormRef"
          label-width="100px"
        >
          <el-form-item label="工具名称" prop="name">
            <el-input v-model="toolForm.name" placeholder="输入工具名称" />
          </el-form-item>
          <el-form-item label="工具类型" prop="type">
            <el-select v-model="toolForm.type" placeholder="选择工具类型" style="width: 100%">
              <el-option v-for="type in toolTypes" :key="type.value" :label="type.label" :value="type.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="工具描述" prop="description">
            <el-input 
              v-model="toolForm.description" 
              type="textarea" 
              rows="3" 
              placeholder="输入工具描述"
            />
          </el-form-item>
          <el-form-item label="命令" prop="command">
            <el-input v-model="toolForm.command" placeholder="工具执行命令(可选)" />
          </el-form-item>
          <el-form-item label="配置" prop="config">
            <el-input 
              v-model="toolForm.configStr" 
              type="textarea" 
              rows="10" 
              placeholder="工具配置(JSON格式)"
            />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="toolForm.status">
              <el-radio label="active">活跃</el-radio>
              <el-radio label="inactive">非活跃</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitToolForm" :loading="submitting">确认</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '../api/api'
import LayoutWrapper from '../components/LayoutWrapper.vue'

// 路由
const router = useRouter()
const route = useRoute()

// 工具列表数据
const tools = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 工具类型选项
const toolTypes = [
  { value: 'filesystem', label: '文件系统工具' },
  { value: 'network', label: '网络工具' },
  { value: 'data_analysis', label: '数据分析工具' },
  { value: 'media', label: '媒体处理工具' },
  { value: 'system', label: '系统工具' },
  { value: 'puppeteer', label: '浏览器自动化' },
  { value: 'other', label: '其他工具' }
]

// 状态选项
const statusOptions = [
  { value: 'active', label: '活跃' },
  { value: 'inactive', label: '非活跃' },
  { value: 'error', label: '错误' }
]

// 过滤表单
const filterForm = reactive({
  search: '',
  type: '',
  status: ''
})

// 工具表单
const toolFormRef = ref(null)
const toolForm = reactive({
  name: '',
  type: 'other',
  description: '',
  command: '',
  configStr: '{}',
  status: 'inactive'
})

// 表单验证规则
const toolRules = {
  name: [
    { required: true, message: '请输入工具名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应为2-50个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择工具类型', trigger: 'change' }
  ]
}

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref('create') // 'create' 或 'edit'
const submitting = ref(false)

// 获取工具类型标签
const getToolTypeLabel = (type) => {
  const typeObj = toolTypes.find(t => t.value === type)
  return typeObj ? typeObj.label : type
}

// 获取状态标签
const getStatusLabel = (status) => {
  const statusObj = statusOptions.find(s => s.value === status)
  return statusObj ? statusObj.label : status
}

// 获取状态类型（用于标签颜色）
const getStatusType = (status) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

// 加载工具列表
const loadTools = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: page.value,
      per_page: pageSize.value
    }
    
    if (filterForm.search) {
      params.search = filterForm.search
    }
    
    if (filterForm.type) {
      params.type = filterForm.type
    }
    
    if (filterForm.status) {
      params.status = filterForm.status
    }
    
    const response = await api.tools.getList(params)
    tools.value = response.tools || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error(`加载工具列表失败: ${error}`)
    tools.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  page.value = 1
  loadTools()
}

// 重置过滤器
const resetFilters = () => {
  filterForm.search = ''
  filterForm.type = ''
  filterForm.status = ''
  handleSearch()
}

// 处理创建工具
const handleCreate = () => {
  // 重置表单
  toolForm.name = ''
  toolForm.type = 'other'
  toolForm.description = ''
  toolForm.command = ''
  toolForm.configStr = '{}'
  toolForm.status = 'inactive'
  
  dialogType.value = 'create'
  dialogVisible.value = true
}

// 处理查看详情
const handleDetail = (tool) => {
  router.push(`/tool/${tool.id}`)
}

// 处理激活工具
const handleActivate = async (tool) => {
  try {
    await api.tools.activate(tool.id)
    ElMessage.success(`工具 "${tool.name}" 已启用`)
    loadTools()
  } catch (error) {
    ElMessage.error(`启用工具失败: ${error}`)
  }
}

// 处理停用工具
const handleDeactivate = async (tool) => {
  try {
    await api.tools.deactivate(tool.id)
    ElMessage.success(`工具 "${tool.name}" 已停用`)
    loadTools()
  } catch (error) {
    ElMessage.error(`停用工具失败: ${error}`)
  }
}

// 处理删除工具
const handleDelete = (tool) => {
  ElMessageBox.confirm(
    `确定要删除工具 "${tool.name}" 吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.tools.delete(tool.id)
      ElMessage.success(`工具 "${tool.name}" 已删除`)
      loadTools()
    } catch (error) {
      ElMessage.error(`删除工具失败: ${error}`)
    }
  }).catch(() => {})
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
      
      // 根据对话框类型执行不同操作
      if (dialogType.value === 'create') {
        await api.tools.create(submitData)
        ElMessage.success('工具创建成功')
      } else {
        // 编辑逻辑（这个例子中未实现）
        // await api.tools.update(editingTool.value.id, submitData)
        // ElMessage.success('工具更新成功')
      }
      
      // 关闭对话框并刷新列表
      dialogVisible.value = false
      loadTools()
    } catch (error) {
      ElMessage.error(`操作失败: ${error}`)
    } finally {
      submitting.value = false
    }
  })
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  loadTools()
}

const handleCurrentChange = (current) => {
  page.value = current
  loadTools()
}

// 组件挂载时加载数据
onMounted(() => {
  loadTools()
  
  // 检查URL查询参数，如果有action=create，则自动打开创建对话框
  if (route.query.action === 'create') {
    handleCreate()
  }
})
</script>

<style scoped lang="scss">
.tools-container {
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

.tools-filters {
  margin-bottom: 20px;
}

.tools-list {
  .tool-info {
    .tool-name {
      font-weight: bold;
      color: #303133;
    }
    
    .tool-desc {
      margin: 5px 0 0;
      color: #909399;
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 400px;
    }
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style> 