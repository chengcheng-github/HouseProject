import apiClient from './axios'

// 获取所有配置
export const getConfigs = async () => {
  return apiClient.get('/api/v1/admin/configs')
}

// 更新配置
export const updateConfig = async (key: string, value: string, description?: string) => {
  return apiClient.post('/api/v1/admin/configs', null, {
    params: { key, value, description }
  })
}

// 获取统计数据
export const getStatistics = async () => {
  return apiClient.get('/api/v1/admin/statistics')
}

// 获取操作日志
export const getOperationLogs = async (params: {
  start_date?: string
  end_date?: string
  user_id?: number
  action?: string
  page?: number
  page_size?: number
}) => {
  return apiClient.get('/api/v1/admin/logs', { params })
}