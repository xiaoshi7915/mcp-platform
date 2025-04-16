<template>
  <LayoutWrapper>
    <div class="dashboard-container">
      <div class="page-header">
        <div class="page-title">
          <h2>仪表盘</h2>
          <p>查看MCP平台概览和工具使用统计</p>
        </div>
        <div class="page-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><refresh /></el-icon> 刷新数据
          </el-button>
        </div>
      </div>

      <!-- 数据卡片 -->
      <div class="stat-cards">
        <el-row :gutter="20">
          <!-- 工具统计 -->
          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-icon tool-icon">
                <el-icon><tools /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-title">工具总数</div>
                <div class="stat-value">{{ stats.tools.total || 0 }}</div>
                <div class="stat-details">
                  <el-tag type="success" size="small">活跃: {{ stats.tools.active || 0 }}</el-tag>
                  <el-tag type="info" size="small">非活跃: {{ stats.tools.inactive || 0 }}</el-tag>
                  <el-tag type="danger" size="small">错误: {{ stats.tools.error || 0 }}</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 日志统计 -->
          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-icon log-icon">
                <el-icon><document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-title">日志记录</div>
                <div class="stat-value">{{ stats.logs.total || 0 }}</div>
                <div class="stat-details">
                  <el-tag class="log-info" size="small">信息: {{ stats.logs.info || 0 }}</el-tag>
                  <el-tag class="log-warning" size="small">警告: {{ stats.logs.warning || 0 }}</el-tag>
                  <el-tag class="log-error" size="small">错误: {{ stats.logs.error || 0 }}</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- CPU使用率 -->
          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-icon cpu-icon">
                <el-icon><cpu /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-title">CPU使用率</div>
                <div class="stat-value">{{ stats.system.cpu_usage || 0 }}%</div>
                <div class="stat-details">
                  <el-progress 
                    :percentage="stats.system.cpu_usage || 0" 
                    :color="getCpuColor(stats.system.cpu_usage)" 
                    :stroke-width="8"
                  />
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 内存使用率 -->
          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-icon memory-icon">
                <el-icon><odometer /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-title">内存使用率</div>
                <div class="stat-value">{{ stats.system.memory_usage || 0 }}%</div>
                <div class="stat-details">
                  <el-progress 
                    :percentage="stats.system.memory_usage || 0" 
                    :color="getMemoryColor(stats.system.memory_usage)" 
                    :stroke-width="8"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表部分 -->
      <div class="chart-container">
        <el-row :gutter="20">
          <!-- 调用统计图表 -->
          <el-col :xs="24" :lg="16">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>调用统计（过去30天）</span>
                </div>
              </template>
              <div id="callsChart" class="chart"></div>
            </el-card>
          </el-col>

          <!-- 工具类型分布 -->
          <el-col :xs="24" :lg="8">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>工具类型分布</span>
                </div>
              </template>
              <div id="typeChart" class="chart"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 最活跃工具列表 -->
      <el-card shadow="hover" class="active-tools-card">
        <template #header>
          <div class="card-header">
            <span>最活跃工具</span>
          </div>
        </template>
        <el-table :data="stats.active_tools || []" style="width: 100%" border>
          <el-table-column label="工具名称" prop="name" min-width="200" />
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
          <el-table-column label="调用次数" prop="invoke_count" width="120" sortable />
          <el-table-column label="最近调用时间" width="180">
            <template #default="{ row }">
              {{ row.last_invoked_at ? formatDate(row.last_invoked_at) : '从未调用' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewToolDetails(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 最近活动 -->
      <el-card shadow="hover" class="recent-activities-card">
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="activity in activities"
            :key="activity.id"
            :type="getActivityType(activity.level)"
            :timestamp="formatDate(activity.timestamp)"
          >
            <p class="activity-title">
              <span :class="`log-${activity.level}`">【{{ activity.level === 'info' ? '信息' : activity.level === 'warning' ? '警告' : '错误' }}】</span>
              <span>工具：{{ activity.tool }}</span>
            </p>
            <p class="activity-message">{{ activity.message }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </LayoutWrapper>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Tools, Document, Cpu, Odometer } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import LayoutWrapper from '../components/LayoutWrapper.vue'
import api from '../api/api'

// 注册echarts组件
echarts.use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, LineChart, PieChart, CanvasRenderer])

// 路由
const router = useRouter()

// 数据
const stats = ref({
  tools: { total: 0, active: 0, inactive: 0, error: 0 },
  logs: { total: 0, info: 0, warning: 0, error: 0 },
  system: { cpu_usage: 0, memory_usage: 0, disk_usage: 0 },
  active_tools: []
})
const activities = ref([])
const dailyStats = ref([])
const typeStats = ref([])
const loading = ref(true)

// 图表实例
let callsChart = null
let typeChart = null

// 工具类型映射
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

// 获取数据的函数
const fetchData = async () => {
  loading.value = true
  try {
    // 获取概览数据
    const overview = await api.dashboard.getOverview()
    stats.value = overview

    // 获取每日统计数据
    const daily = await api.dashboard.getDailyStats()
    dailyStats.value = daily

    // 获取工具类型分布
    const types = await api.dashboard.getToolTypes()
    typeStats.value = types

    // 获取最近活动
    const activities_data = await api.dashboard.getRecentActivities()
    activities.value = activities_data

    // 初始化图表
    initCharts()
  } catch (error) {
    ElMessage.error(`获取数据失败: ${error}`)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchData()
}

// 初始化图表
const initCharts = () => {
  // 调用统计图表
  if (callsChart) {
    callsChart.dispose()
  }
  callsChart = echarts.init(document.getElementById('callsChart'))
  
  const dates = dailyStats.value.map(item => item.date)
  const calls = dailyStats.value.map(item => item.calls)
  const errors = dailyStats.value.map(item => item.errors)

  const callsOption = {
    title: {
      text: '每日工具调用与错误统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['调用次数', '错误次数'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '调用次数',
        type: 'line',
        data: calls,
        smooth: true,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '错误次数',
        type: 'line',
        data: errors,
        smooth: true,
        itemStyle: {
          color: '#f56c6c'
        }
      }
    ]
  }
  callsChart.setOption(callsOption)

  // 工具类型分布图表
  if (typeChart) {
    typeChart.dispose()
  }
  typeChart = echarts.init(document.getElementById('typeChart'))
  
  const typeOption = {
    title: {
      text: '工具类型分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: typeStats.value.map(item => getToolTypeLabel(item.type))
    },
    series: [
      {
        name: '工具类型',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: typeStats.value.map(item => ({
          name: getToolTypeLabel(item.type),
          value: item.count
        }))
      }
    ]
  }
  typeChart.setOption(typeOption)
}

// 响应式调整图表大小
const resizeCharts = () => {
  if (callsChart) {
    callsChart.resize()
  }
  if (typeChart) {
    typeChart.resize()
  }
}

// 辅助函数
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

const getToolTypeLabel = (type) => {
  const typeObj = toolTypes.find(t => t.value === type)
  return typeObj ? typeObj.label : type
}

const getStatusLabel = (status) => {
  const statusObj = statusOptions.find(s => s.value === status)
  return statusObj ? statusObj.label : status
}

const getStatusType = (status) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getActivityType = (level) => {
  switch (level) {
    case 'error': return 'danger'
    case 'warning': return 'warning'
    case 'info': return 'primary'
    default: return 'info'
  }
}

const getCpuColor = (usage) => {
  if (usage > 90) return '#f56c6c'
  if (usage > 70) return '#e6a23c'
  return '#67c23a'
}

const getMemoryColor = (usage) => {
  if (usage > 90) return '#f56c6c'
  if (usage > 70) return '#e6a23c'
  return '#67c23a'
}

const viewToolDetails = (tool) => {
  router.push(`/tool/${tool.id}`)
}

// 生命周期钩子
onMounted(() => {
  fetchData()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (callsChart) {
    callsChart.dispose()
  }
  if (typeChart) {
    typeChart.dispose()
  }
})
</script>

<style scoped lang="scss">
.dashboard-container {
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

.stat-cards {
  margin-bottom: 20px;
  
  .stat-card {
    height: 150px;
    margin-bottom: 20px;
    display: flex;
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    
    .el-icon {
      font-size: 24px;
      color: white;
    }
    
    &.tool-icon {
      background-color: #409eff;
    }
    
    &.log-icon {
      background-color: #67c23a;
    }
    
    &.cpu-icon {
      background-color: #e6a23c;
    }
    
    &.memory-icon {
      background-color: #f56c6c;
    }
  }
  
  .stat-content {
    flex: 1;
    
    .stat-title {
      font-size: 16px;
      color: #606266;
      margin-bottom: 8px;
    }
    
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 15px;
    }
    
    .stat-details {
      display: flex;
      gap: 10px;
    }
  }
}

.chart-container {
  margin-bottom: 20px;
  
  .chart-card {
    margin-bottom: 20px;
    height: 400px;
  }
  
  .chart {
    height: 320px;
  }
}

.active-tools-card, .recent-activities-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  span {
    font-size: 16px;
    font-weight: bold;
  }
}

.activity-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.activity-message {
  color: #606266;
}

/* 日志级别样式 */
.log-info {
  color: #409eff;
}

.log-warning {
  color: #e6a23c;
}

.log-error {
  color: #f56c6c;
}
</style> 