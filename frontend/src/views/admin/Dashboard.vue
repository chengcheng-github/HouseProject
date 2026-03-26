<template>
  <div class="dashboard-container">
    <div class="container">
      <el-card class="dashboard-card">
        <template #header>
          <div class="card-header">
            <h2>运维管理</h2>
          </div>
        </template>

        <!-- 数据统计 -->
        <div class="statistics-section">
          <h3>数据统计</h3>
          <div v-loading="loading">
            <div ref="chartRef" class="chart"></div>
          </div>
        </div>

        <!-- 配置管理 -->
        <el-divider />
        <div class="config-section">
          <h3>网站配置</h3>
          <el-table :data="configs" style="width: 100%" border>
            <el-table-column prop="key" label="配置键" />
            <el-table-column prop="value" label="配置值" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="primary" size="small" @click="editConfig(scope.row)">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 操作日志 -->
        <el-divider />
        <div class="logs-section">
          <h3>操作日志</h3>
          <el-table :data="logs" style="width: 100%" border>
            <el-table-column prop="created_at" label="时间" width="180" />
            <el-table-column prop="user_email" label="用户" width="200" />
            <el-table-column prop="action" label="操作" width="100" />
            <el-table-column prop="resource_type" label="资源类型" width="120" />
            <el-table-column prop="resource_id" label="资源ID" width="100" />
            <el-table-column prop="ip_address" label="IP地址" width="150" />
          </el-table>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getStatistics, getConfigs, getOperationLogs } from '@/api'
import { StatisticsData, OperationLog } from '@/types'

const loading = ref(false)
const chartRef = ref()
const configs = ref<any[]>([])
const logs = ref<OperationLog[]>([])

// 初始化
onMounted(async () => {
  await fetchData()
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    // 获取统计数据
    const statsData = await getStatistics() as StatisticsData
    renderChart(statsData)
    
    // 获取配置
    const configData = await getConfigs()
    configs.value = Object.entries(configData).map(([key, value]) => ({
      key,
      value,
      description: ''
    }))
    
    // 获取日志
    const logData = await getOperationLogs({ page: 1, page_size: 10 })
    logs.value = logData.logs
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = (data: StatisticsData) => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['注册量', '发布量', '访问量', '独立访客']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '注册量',
        type: 'line',
        data: data.registrations,
        smooth: true
      },
      {
        name: '发布量',
        type: 'line',
        data: data.publications,
        smooth: true
      },
      {
        name: '访问量',
        type: 'line',
        data: data.page_views,
        smooth: true
      },
      {
        name: '独立访客',
        type: 'line',
        data: data.unique_visitors,
        smooth: true
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 编辑配置
const editConfig = (config: any) => {
  // 这里应该打开编辑对话框
  console.log('编辑配置:', config)
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.dashboard-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.statistics-section,
.config-section,
.logs-section {
  margin-bottom: 30px;
}

.statistics-section h3,
.config-section h3,
.logs-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.chart {
  height: 400px;
}
</style>