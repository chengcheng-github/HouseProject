import apiClient from './axios'

// 创建预约
export const createVisit = async (params: {
  house_id: number
  visitor_name: string
  visitor_phone: string
  visit_date: string
  time_slot: 'morning' | 'afternoon'
  remark?: string
}) => {
  return apiClient.post('/api/v1/visits', null, { params })
}

// 获取房屋预约列表
export const getHouseVisits = async (houseId: number) => {
  return apiClient.get(`/api/v1/visits/house/${houseId}`)
}

// 获取我的预约列表
export const getMyVisits = async () => {
  return apiClient.get('/api/v1/visits/my')
}

// 更新预约状态
export const updateVisitStatus = async (visitId: number, status: '0' | '1' | '2') => {
  return apiClient.patch(`/api/v1/visits/${visitId}/status`, null, {
    params: { status }
  })
}

// 获取房屋可预约日期
export const getAvailableDates = async (houseId: number, days?: number) => {
  return apiClient.get(`/api/v1/visits/house/${houseId}/available-dates`, {
    params: { days }
  })
}