<template>
  <LayoutWrapper>
    <div class="templates-container">
      <!-- 页面标题和操作栏 -->
      <div class="page-header">
        <div class="page-title">
          <h2>模板库</h2>
          <p>管理和部署工具模板</p>
        </div>
        
        <div class="page-actions">
          <el-button type="primary" :icon="Plus" @click="handleCreate">创建模板</el-button>
          <el-button :icon="Upload" @click="uploadDialogVisible = true">导入模板</el-button>
        </div>
      </div>
      
      <!-- 筛选表单 -->
      <el-card class="templates-filters">
        <el-form :model="filterForm" inline @submit.prevent="handleSearch">
          <el-form-item label="模板名称">
            <el-input 
              v-model="filterForm.search" 
              placeholder="搜索模板" 
              clearable 
              @clear="handleSearch"
            />
          </el-form-item>
          
          <el-form-item label="类型">
            <el-select 
              v-model="filterForm.type" 
              placeholder="选择类型" 
              clearable 
              @change="handleSearch"
              style="width: 150px"
            >
              <el-option
                v-for="option in typeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
            <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 模板列表 -->
      <div class="templates-list">
        <el-row :gutter="20">
          <el-col 
            v-for="template in templates" 
            :key="template.id" 
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6" 
            :xl="4"
          >
            <el-card 
              class="template-card" 
              shadow="hover" 
              :body-style="{ padding: '0px' }"
            >
              <div class="template-header">
                <div :class="['template-icon', `type-${template.type}`]">
                  <el-icon><component :is="getTypeIcon(template.type)" /></el-icon>
                </div>
                <div class="template-title">{{ template.name }}</div>
              </div>
              
              <div class="template-content">
                <p class="template-desc">{{ template.description || '无描述' }}</p>
                
                <div class="template-meta">
                  <div class="meta-item">
                    <span class="label">类型:</span>
                    <span class="value">{{ getTypeLabel(template.type) }}</span>
                  </div>
                  
                  <div class="meta-item">
                    <span class="label">创建时间:</span>
                    <span class="value">{{ formatDate(template.created_at) }}</span>
                  </div>
                  
                  <div class="meta-item">
                    <span class="label">部署次数:</span>
                    <span class="value">{{ template.deploy_count || 0 }}</span>
                  </div>
                </div>
              </div>
              
              <div class="template-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleDetail(template)"
                >
                  详情
                </el-button>
                
                <el-button 
                  type="success" 
                  size="small" 
                  @click="handleDeploy(template)"
                >
                  部署
                </el-button>
                
                <el-dropdown trigger="click" size="small">
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="handleEdit(template)">
                        <el-icon><edit /></el-icon>编辑
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleExport(template)">
                        <el-icon><download /></el-icon>导出
                      </el-dropdown-item>
                      <el-dropdown-item divided @click="handleDelete(template)">
                        <el-icon><delete /></el-icon>删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 空状态 -->
        <el-empty 
          v-if="templates.length === 0 && !loading" 
          description="暂无模板" 
        >
          <el-button type="primary" @click="handleCreate">创建模板</el-button>
        </el-empty>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated />
        </div>
        
        <!-- 分页组件 -->
        <div class="pagination" v-if="total > 0">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 48, 96]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
      
      <!-- 创建/编辑模板对话框 -->
      <el-dialog 
        v-model="dialogVisible" 
        :title="dialogType === 'create' ? '创建模板' : '编辑模板'"
        width="600px"
      >
        <el-form 
          :model="templateForm" 
          ref="templateFormRef"
          :rules="rules"
          label-width="100px"
        >
          <el-form-item label="模板名称" prop="name">
            <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
          </el-form-item>
          
          <el-form-item label="模板类型" prop="type">
            <el-select v-model="templateForm.type" placeholder="请选择模板类型" style="width: 100%">
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
              v-model="templateForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入模板描述"
            />
          </el-form-item>
          
          <el-form-item label="命令模板" prop="command_template">
            <el-input 
              v-model="templateForm.command_template" 
              placeholder="请输入命令模板，使用 {变量名} 作为占位符"
            />
          </el-form-item>
          
          <el-form-item label="配置模板" prop="configStr">
            <el-input 
              v-model="templateForm.configStr" 
              type="textarea" 
              :rows="8"
              placeholder="请输入JSON格式的配置模板，使用 {变量名} 作为占位符"
            />
          </el-form-item>
          
          <el-form-item label="变量定义" prop="varsStr">
            <el-input 
              v-model="templateForm.varsStr" 
              type="textarea" 
              :rows="5"
              placeholder="请输入JSON格式的变量定义"
            />
            <div class="form-tip">
              变量格式: { "变量名": { "type": "string|number|boolean|select", "label": "显示名称", "default": "默认值", "options": ["选项1", "选项2"] } }
            </div>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitTemplateForm">确定</el-button>
        </template>
      </el-dialog>
      
      <!-- 导入模板对话框 -->
      <el-dialog 
        v-model="uploadDialogVisible" 
        title="导入模板"
        width="500px"
      >
        <el-upload
          class="template-upload"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">
              请上传JSON格式的模板文件
            </div>
          </template>
        </el-upload>
        
        <template #footer>
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :disabled="!templateFile" 
            :loading="uploading" 
            @click="uploadTemplate"
          >
            导入
          </el-button>
        </template>
      </el-dialog>
      
      <!-- 部署模板对话框 -->
      <el-dialog 
        v-model="deployDialogVisible" 
        title="部署模板"
        width="600px"
      >
        <template v-if="currentTemplate && templateVarsForm">
          <p class="deploy-title">模板: {{ currentTemplate.name }}</p>
          <p class="deploy-desc">{{ currentTemplate.description || '无描述' }}</p>
          
          <el-divider content-position="left">配置变量</el-divider>
          
          <el-form 
            :model="templateVarsForm" 
            ref="templateVarsFormRef"
            label-width="120px"
          >
            <template v-for="(field, key) in templateVars" :key="key">
              <!-- 字符串输入框 -->
              <el-form-item 
                v-if="field.type === 'string'" 
                :label="field.label" 
                :prop="key"
              >
                <el-input v-model="templateVarsForm[key]" :placeholder="`请输入${field.label}`" />
              </el-form-item>
              
              <!-- 数字输入框 -->
              <el-form-item 
                v-else-if="field.type === 'number'" 
                :label="field.label" 
                :prop="key"
              >
                <el-input-number v-model="templateVarsForm[key]" :placeholder="`请输入${field.label}`" style="width: 100%" />
              </el-form-item>
              
              <!-- 布尔值开关 -->
              <el-form-item 
                v-else-if="field.type === 'boolean'" 
                :label="field.label" 
                :prop="key"
              >
                <el-switch v-model="templateVarsForm[key]" />
              </el-form-item>
              
              <!-- 选择框 -->
              <el-form-item 
                v-else-if="field.type === 'select'" 
                :label="field.label" 
                :prop="key"
              >
                <el-select v-model="templateVarsForm[key]" :placeholder="`请选择${field.label}`" style="width: 100%">
                  <el-option
                    v-for="option in field.options"
                    :key="option"
                    :label="option"
                    :value="option"
                  />
                </el-select>
              </el-form-item>
            </template>
          </el-form>
          
          <el-divider content-position="left">预览</el-divider>
          
          <div class="template-preview">
            <div class="preview-item">
              <div class="preview-label">命令:</div>
              <div class="preview-value">{{ previewCommand }}</div>
            </div>
            
            <div class="preview-item">
              <div class="preview-label">配置:</div>
              <pre class="preview-json">{{ previewConfig }}</pre>
            </div>
          </div>
        </template>
        
        <template #footer>
          <el-button @click="deployDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="deploying" 
            @click="confirmDeploy"
          >
            部署
          </el-button>
        </template>
      </el-dialog>
    </div>
  </LayoutWrapper>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, Plus, Upload, UploadFilled, Download,
  Edit, Delete, ArrowDown, Setting, Monitor, DataLine,
  Connection, Cpu, Link, Share
} from '@element-plus/icons-vue'
import api from '../api/api'
import LayoutWrapper from '../components/LayoutWrapper.vue'

export default {
  name: 'TemplatesManagement',
  components: {
    LayoutWrapper
  },
  setup() {
    // 路由
    const router = useRouter()
    
    // 模板数据
    const templates = ref([])
    const loading = ref(true)
    const page = ref(1)
    const pageSize = ref(12)
    const total = ref(0)
    
    // 模板类型选项
    const typeOptions = [
      { value: 'system', label: '系统工具', icon: 'Monitor' },
      { value: 'web', label: 'Web工具', icon: 'Link' },
      { value: 'data', label: '数据处理', icon: 'DataLine' },
      { value: 'ai', label: '人工智能', icon: 'Cpu' },
      { value: 'integration', label: '系统集成', icon: 'Connection' },
      { value: 'other', label: '其他工具', icon: 'Setting' }
    ]
    
    // 筛选表单
    const filterForm = reactive({
      search: '',
      type: ''
    })
    
    // 对话框状态
    const dialogVisible = ref(false)
    const dialogType = ref('create')
    const submitting = ref(false)
    
    // 导入对话框
    const uploadDialogVisible = ref(false)
    const templateFile = ref(null)
    const uploading = ref(false)
    
    // 部署对话框
    const deployDialogVisible = ref(false)
    const currentTemplate = ref(null)
    const templateVars = ref({})
    const templateVarsForm = ref(null)
    const deploying = ref(false)
    
    // 表单ref
    const templateFormRef = ref(null)
    const templateVarsFormRef = ref(null)
    
    // 模板表单
    const templateForm = reactive({
      name: '',
      type: 'other',
      description: '',
      command_template: '',
      configStr: '{}',
      varsStr: '{}'
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入模板名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择模板类型', trigger: 'change' }
      ],
      command_template: [
        { required: true, message: '请输入命令模板', trigger: 'blur' }
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
              callback(new Error('配置模板必须是有效的JSON格式'))
            }
          }, 
          trigger: 'blur' 
        }
      ],
      varsStr: [
        { 
          validator: (rule, value, callback) => {
            try {
              if (value) {
                JSON.parse(value)
              }
              callback()
            } catch (error) {
              callback(new Error('变量定义必须是有效的JSON格式'))
            }
          }, 
          trigger: 'blur' 
        }
      ]
    }
    
    // 预览命令（替换变量）
    const previewCommand = computed(() => {
      if (!currentTemplate.value || !templateVarsForm.value) return ''
      
      let command = currentTemplate.value.command_template
      
      // 替换变量
      for (const [key, value] of Object.entries(templateVarsForm.value)) {
        command = command.replace(new RegExp(`\\{${key}\\}`, 'g'), value)
      }
      
      return command
    })
    
    // 预览配置（替换变量）
    const previewConfig = computed(() => {
      if (!currentTemplate.value || !templateVarsForm.value) return '{}'
      
      let configStr = JSON.stringify(currentTemplate.value.config, null, 2)
      
      // 替换变量
      for (const [key, value] of Object.entries(templateVarsForm.value)) {
        configStr = configStr.replace(new RegExp(`\\{${key}\\}`, 'g'), 
          typeof value === 'string' ? JSON.stringify(value).slice(1, -1) : value)
      }
      
      return configStr
    })
    
    // 获取类型标签
    const getTypeLabel = (type) => {
      const typeObj = typeOptions.find(t => t.value === type)
      return typeObj ? typeObj.label : type
    }
    
    // 获取类型图标
    const getTypeIcon = (type) => {
      const typeObj = typeOptions.find(t => t.value === type)
      return typeObj ? typeObj.icon : 'Setting'
    }
    
    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '无'
      const date = new Date(dateStr)
      return date.toLocaleDateString()
    }
    
    // 加载模板列表
    const loadTemplates = async () => {
      loading.value = true
      
      try {
        // 构建查询参数
        const params = {
          page: page.value,
          per_page: pageSize.value
        }
        
        // 添加筛选条件
        if (filterForm.search) {
          params.search = filterForm.search
        }
        
        if (filterForm.type) {
          params.type = filterForm.type
        }
        
        const response = await api.templates.getList(params)
        templates.value = response.templates || []
        total.value = response.total || 0
      } catch (error) {
        ElMessage.error(`加载模板失败: ${error}`)
        templates.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }
    
    // 处理创建按钮
    const handleCreate = () => {
      // 重置表单
      templateForm.name = ''
      templateForm.type = 'other'
      templateForm.description = ''
      templateForm.command_template = ''
      templateForm.configStr = '{}'
      templateForm.varsStr = '{}'
      
      dialogType.value = 'create'
      dialogVisible.value = true
    }
    
    // 处理编辑按钮
    const handleEdit = (template) => {
      // 初始化表单数据
      templateForm.name = template.name
      templateForm.type = template.type
      templateForm.description = template.description || ''
      templateForm.command_template = template.command_template
      templateForm.configStr = JSON.stringify(template.config, null, 2)
      templateForm.varsStr = JSON.stringify(template.variables, null, 2)
      
      dialogType.value = 'edit'
      dialogVisible.value = true
      
      // 保存当前编辑的模板ID
      templateForm.id = template.id
    }
    
    // 处理详情按钮
    const handleDetail = (template) => {
      router.push(`/template/${template.id}`)
    }
    
    // 处理删除按钮
    const handleDelete = (template) => {
      ElMessageBox.confirm(
        `确定要删除模板 "${template.name}" 吗？此操作不可恢复。`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await api.templates.delete(template.id)
          ElMessage.success(`模板 "${template.name}" 已删除`)
          loadTemplates()
        } catch (error) {
          ElMessage.error(`删除模板失败: ${error}`)
        }
      }).catch(() => {})
    }
    
    // 处理导出按钮
    const handleExport = (template) => {
      try {
        const data = JSON.stringify(template, null, 2)
        const blob = new Blob([data], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        
        const link = document.createElement('a')
        link.href = url
        link.download = `template_${template.name}.json`
        link.click()
        
        URL.revokeObjectURL(url)
        ElMessage.success('模板导出成功')
      } catch (error) {
        ElMessage.error(`导出模板失败: ${error}`)
      }
    }
    
    // 处理文件变更（上传）
    const handleFileChange = (file) => {
      templateFile.value = file.raw
    }
    
    // 上传模板
    const uploadTemplate = async () => {
      if (!templateFile.value) {
        ElMessage.warning('请选择要上传的文件')
        return
      }
      
      uploading.value = true
      
      try {
        // 读取文件内容
        const reader = new FileReader()
        
        const result = await new Promise((resolve, reject) => {
          reader.onload = (e) => resolve(e.target.result)
          reader.onerror = (e) => reject(e)
          reader.readAsText(templateFile.value)
        })
        
        // 解析JSON
        const templateData = JSON.parse(result)
        
        // 提交到API
        await api.templates.create(templateData)
        
        ElMessage.success('模板导入成功')
        uploadDialogVisible.value = false
        templateFile.value = null
        
        // 重新加载模板列表
        loadTemplates()
      } catch (error) {
        ElMessage.error(`导入模板失败: ${error}`)
      } finally {
        uploading.value = false
      }
    }
    
    // 处理部署按钮
    const handleDeploy = async (template) => {
      currentTemplate.value = template
      templateVars.value = template.variables || {}
      
      // 初始化变量表单
      const formData = {}
      
      // 以默认值初始化表单
      for (const [key, field] of Object.entries(templateVars.value)) {
        formData[key] = field.default !== undefined ? field.default : ''
      }
      
      templateVarsForm.value = formData
      deployDialogVisible.value = true
    }
    
    // 确认部署
    const confirmDeploy = async () => {
      if (!currentTemplate.value) return
      
      deploying.value = true
      
      try {
        // 构建部署参数
        const deployData = {
          template_id: currentTemplate.value.id,
          variables: templateVarsForm.value
        }
        
        // 调用导入API
        const response = await api.templates.import(currentTemplate.value.id, deployData)
        
        ElMessage.success('模板部署成功')
        deployDialogVisible.value = false
        
        // 如果成功创建了工具，跳转到工具详情页
        if (response.tool_id) {
          router.push(`/tool/${response.tool_id}`)
        } else {
          // 重新加载模板列表
          loadTemplates()
        }
      } catch (error) {
        ElMessage.error(`部署模板失败: ${error}`)
      } finally {
        deploying.value = false
      }
    }
    
    // 提交模板表单
    const submitTemplateForm = () => {
      templateFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        submitting.value = true
        
        try {
          // 构建提交数据
          const submitData = {
            name: templateForm.name,
            type: templateForm.type,
            description: templateForm.description,
            command_template: templateForm.command_template
          }
          
          // 解析JSON字段
          try {
            submitData.config = JSON.parse(templateForm.configStr)
            submitData.variables = JSON.parse(templateForm.varsStr)
          } catch (err) {
            ElMessage.error('JSON格式无效')
            submitting.value = false
            return
          }
          
          // 根据对话框类型执行不同操作
          if (dialogType.value === 'create') {
            await api.templates.create(submitData)
            ElMessage.success('模板创建成功')
          } else {
            await api.templates.update(templateForm.id, submitData)
            ElMessage.success('模板更新成功')
          }
          
          // 关闭对话框并刷新列表
          dialogVisible.value = false
          loadTemplates()
        } catch (error) {
          ElMessage.error(`操作失败: ${error}`)
        } finally {
          submitting.value = false
        }
      })
    }
    
    // 处理搜索
    const handleSearch = () => {
      page.value = 1
      loadTemplates()
    }
    
    // 重置过滤器
    const resetFilters = () => {
      filterForm.search = ''
      filterForm.type = ''
      handleSearch()
    }
    
    // 分页处理
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadTemplates()
    }
    
    const handleCurrentChange = (current) => {
      page.value = current
      loadTemplates()
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadTemplates()
    })
    
    return {
      templates,
      loading,
      page,
      pageSize,
      total,
      typeOptions,
      filterForm,
      dialogVisible,
      dialogType,
      submitting,
      uploadDialogVisible,
      templateFile,
      uploading,
      deployDialogVisible,
      currentTemplate,
      templateVars,
      templateVarsForm,
      deploying,
      templateFormRef,
      templateVarsFormRef,
      templateForm,
      rules,
      previewCommand,
      previewConfig,
      // 图标
      Search,
      Refresh,
      Plus,
      Upload,
      UploadFilled,
      Download,
      Edit,
      Delete,
      ArrowDown,
      Setting,
      Monitor,
      DataLine,
      Connection,
      Cpu,
      Link,
      Share,
      // 方法
      getTypeLabel,
      getTypeIcon,
      formatDate,
      loadTemplates,
      handleCreate,
      handleEdit,
      handleDetail,
      handleDelete,
      handleExport,
      handleFileChange,
      uploadTemplate,
      handleDeploy,
      confirmDeploy,
      submitTemplateForm,
      handleSearch,
      resetFilters,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped lang="scss">
.templates-container {
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

.templates-filters {
  margin-bottom: 20px;
}

.templates-list {
  .el-row {
    margin-bottom: 20px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .template-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }
    
    .template-header {
      display: flex;
      align-items: center;
      padding: 15px;
      border-bottom: 1px solid #ebeef5;
      
      .template-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-size: 20px;
        color: white;
        
        &.type-system {
          background-color: #409eff;
        }
        
        &.type-web {
          background-color: #67c23a;
        }
        
        &.type-data {
          background-color: #e6a23c;
        }
        
        &.type-ai {
          background-color: #9c27b0;
        }
        
        &.type-integration {
          background-color: #ff9800;
        }
        
        &.type-other {
          background-color: #909399;
        }
      }
      
      .template-title {
        font-size: 16px;
        font-weight: bold;
        color: #303133;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    
    .template-content {
      padding: 15px;
      flex: 1;
      
      .template-desc {
        margin: 0 0 15px;
        color: #606266;
        font-size: 14px;
        height: 40px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
      
      .template-meta {
        .meta-item {
          margin-bottom: 8px;
          font-size: 13px;
          display: flex;
          
          .label {
            color: #909399;
            margin-right: 5px;
            width: 70px;
          }
          
          .value {
            color: #606266;
            flex: 1;
          }
        }
      }
    }
    
    .template-actions {
      padding: 10px 15px;
      border-top: 1px solid #ebeef5;
      display: flex;
      justify-content: space-between;
      
      .el-button {
        padding: 7px 15px;
      }
    }
  }
  
  .loading-container {
    padding: 20px;
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

.template-upload {
  text-align: center;
  
  .el-upload {
    display: block;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  margin-top: 5px;
}

.deploy-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 5px 0;
  color: #303133;
}

.deploy-desc {
  color: #606266;
  margin: 0 0 15px 0;
}

.template-preview {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  
  .preview-item {
    margin-bottom: 15px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .preview-label {
      font-weight: bold;
      margin-bottom: 5px;
      color: #606266;
    }
    
    .preview-value {
      color: #303133;
      word-break: break-all;
    }
    
    .preview-json {
      font-family: monospace;
      margin: 0;
      padding: 10px;
      background-color: #ffffff;
      border-radius: 4px;
      color: #303133;
      overflow: auto;
      max-height: 200px;
    }
  }
}
</style> 