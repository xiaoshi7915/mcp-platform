<template>
  <LayoutWrapper>
    <div class="template-detail container">
      <div class="page-header">
        <div class="page-title">
          <h2>模板详情</h2>
          <p>查看和编辑模板详细信息</p>
        </div>
        <div class="page-actions">
          <el-button plain @click="goBack">
            <el-icon><arrow-left /></el-icon> 返回
          </el-button>
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <template v-else>
        <!-- 基本信息卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><edit /></el-icon> 编辑
              </el-button>
            </div>
          </template>
          
          <div class="info-list">
            <div class="info-item">
              <span class="label">模板名称:</span>
              <span class="value">{{ template.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">类型:</span>
              <span class="value">{{ template.type || '未分类' }}</span>
            </div>
            <div class="info-item">
              <span class="label">版本:</span>
              <span class="value">{{ template.version || '1.0.0' }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ formatDate(template.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">更新时间:</span>
              <span class="value">{{ formatDate(template.updated_at) }}</span>
            </div>
            <div class="info-item full-width">
              <span class="label">描述:</span>
              <span class="value">{{ template.description || '无描述' }}</span>
            </div>
          </div>
        </el-card>

        <!-- 模板内容卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>模板内容</span>
              <div>
                <el-button type="primary" size="small" @click="handleImport">
                  <el-icon><plus /></el-icon> 从模板导入
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="template-content">
            <pre v-highlightjs><code class="json">{{ prettyTemplate }}</code></pre>
          </div>
        </el-card>

        <!-- 操作卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>操作</span>
            </div>
          </template>
          
          <div class="action-buttons">
            <el-button type="danger" @click="handleDelete">
              <el-icon><delete /></el-icon> 删除模板
            </el-button>
          </div>
        </el-card>
      </template>

      <!-- 编辑对话框 -->
      <el-dialog 
        v-model="editDialogVisible" 
        title="编辑模板" 
        width="600px"
      >
        <el-form 
          :model="editForm" 
          :rules="rules"
          ref="editFormRef"
          label-width="100px"
        >
          <el-form-item label="模板名称" prop="name">
            <el-input v-model="editForm.name" placeholder="请输入模板名称" />
          </el-form-item>
          <el-form-item label="模板类型" prop="type">
            <el-input v-model="editForm.type" placeholder="请输入模板类型" />
          </el-form-item>
          <el-form-item label="模板版本" prop="version">
            <el-input v-model="editForm.version" placeholder="请输入版本号" />
          </el-form-item>
          <el-form-item label="模板描述" prop="description">
            <el-input 
              v-model="editForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入模板描述"
            />
          </el-form-item>
          <el-form-item label="模板内容" prop="contentStr">
            <el-input 
              v-model="editForm.contentStr" 
              type="textarea" 
              :rows="10"
              placeholder="请输入JSON格式的模板内容"
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitEdit">确定</el-button>
        </template>
      </el-dialog>

      <!-- 导入对话框 -->
      <el-dialog 
        v-model="importDialogVisible" 
        title="从模板导入" 
        width="500px"
      >
        <el-form 
          :model="importForm" 
          label-width="100px"
        >
          <el-form-item label="目标类型">
            <el-select v-model="importForm.targetType" style="width: 100%">
              <el-option label="工具" value="tool" />
              <el-option label="配置" value="config" />
            </el-select>
          </el-form-item>
          <el-form-item label="名称前缀">
            <el-input v-model="importForm.namePrefix" placeholder="可选，导入时添加的前缀" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitImport">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete, Plus } from '@element-plus/icons-vue'
import api from '../api/api'
import { formatDate } from '../utils/format'
import LayoutWrapper from '../components/LayoutWrapper.vue'

// 路由
const route = useRoute()
const router = useRouter()

// 模板数据
const template = ref({})
const loading = ref(true)
const submitting = ref(false)

// 编辑对话框
const editDialogVisible = ref(false)
const editFormRef = ref(null)
const editForm = ref({
  name: '',
  type: '',
  version: '',
  description: '',
  contentStr: '{}'
})

// 导入对话框
const importDialogVisible = ref(false)
const importForm = ref({
  targetType: 'tool',
  namePrefix: ''
})

// 验证规则
const rules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  contentStr: [
    { required: true, message: '请输入模板内容', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        try {
          if (value) {
            JSON.parse(value)
          }
          callback()
        } catch (error) {
          callback(new Error('模板内容必须是有效的JSON格式'))
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 格式化模板内容为美化的JSON
const prettyTemplate = computed(() => {
  try {
    if (template.value && template.value.content) {
      return JSON.stringify(template.value.content, null, 2)
    }
    return '{}'
  } catch (e) {
    return '{}'
  }
})

// 加载模板详情
const loadTemplate = async () => {
  const templateId = route.params.id
  loading.value = true
  try {
    const data = await api.templates.getOne(templateId)
    template.value = data
  } catch (error) {
    ElMessage.error(`加载模板失败: ${error}`)
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 处理编辑按钮
const handleEdit = () => {
  editForm.value = {
    name: template.value.name,
    type: template.value.type || '',
    version: template.value.version || '1.0.0',
    description: template.value.description || '',
    contentStr: JSON.stringify(template.value.content || {}, null, 2)
  }
  editDialogVisible.value = true
}

// 提交编辑
const submitEdit = () => {
  editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 构建提交数据
      const submitData = {
        name: editForm.value.name,
        type: editForm.value.type,
        version: editForm.value.version,
        description: editForm.value.description
      }
      
      // 解析JSON
      try {
        submitData.content = JSON.parse(editForm.value.contentStr)
      } catch (err) {
        ElMessage.error('模板内容JSON格式无效')
        submitting.value = false
        return
      }
      
      // 提交更新
      await api.templates.update(template.value.id, submitData)
      
      ElMessage.success('模板更新成功')
      editDialogVisible.value = false
      
      // 重新加载模板
      loadTemplate()
    } catch (error) {
      ElMessage.error(`更新模板失败: ${error}`)
    } finally {
      submitting.value = false
    }
  })
}

// 处理导入
const handleImport = () => {
  importForm.value = {
    targetType: 'tool',
    namePrefix: template.value.name + '_'
  }
  importDialogVisible.value = true
}

// 提交导入
const submitImport = async () => {
  submitting.value = true
  
  try {
    await api.templates.import(template.value.id, {
      target_type: importForm.value.targetType,
      name_prefix: importForm.value.namePrefix
    })
    
    ElMessage.success('导入成功')
    importDialogVisible.value = false
  } catch (error) {
    ElMessage.error(`导入失败: ${error}`)
  } finally {
    submitting.value = false
  }
}

// 删除模板
const handleDelete = () => {
  ElMessageBox.confirm(
    `确定要删除模板 "${template.value.name}" 吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.templates.delete(template.value.id)
      ElMessage.success('模板已删除')
      router.push('/templates')
    } catch (error) {
      ElMessage.error(`删除模板失败: ${error}`)
    }
  }).catch(() => {})
}

// 组件挂载时加载数据
onMounted(() => {
  loadTemplate()
})
</script>

<style scoped>
.template-detail {
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

.detail-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
    color: #303133;
  }
}

.info-list {
  .info-item {
    margin-bottom: 12px;
    font-size: 14px;
    display: flex;
    
    &.full-width {
      display: block;
      
      .label {
        margin-bottom: 5px;
        display: block;
      }
    }
    
    .label {
      color: #909399;
      width: 100px;
      margin-right: 12px;
    }
    
    .value {
      color: #303133;
      flex: 1;
    }
  }
}

.template-content {
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow: auto;
  max-height: 400px;
  
  pre {
    margin: 0;
    padding: 12px;
  }
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px;
}
</style> 