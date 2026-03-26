import apiClient from './axios'
import { House, HouseList, HouseCreate, HouseUpdate, HouseStatus, PaginatedData } from '@/types'

// 创建房屋
export const createHouse = async (data: HouseCreate): Promise<House> => {
  return apiClient.post('/api/v1/houses', data)
}

// 获取房屋列表
export const getHouses = async (params: {
  page?: number
  page_size?: number
  title?: string
  district?: string
  min_price?: number
  max_price?: number
}): Promise<PaginatedData<HouseList>> => {
  return apiClient.get('/api/v1/houses', { params })
}

// 获取我的房屋列表
export const getMyHouses = async (params: {
  page?: number
  page_size?: number
}): Promise<PaginatedData<HouseList>> => {
  return apiClient.get('/api/v1/houses/my', { params })
}

// 获取房屋详情
export const getHouseDetail = async (houseId: number): Promise<House> => {
  return apiClient.get(`/api/v1/houses/${houseId}`)
}

// 更新房屋信息
export const updateHouse = async (houseId: number, data: HouseUpdate): Promise<House> => {
  return apiClient.put(`/api/v1/houses/${houseId}`, data)
}

// 更新房屋状态
export const updateHouseStatus = async (houseId: number, status: HouseStatus): Promise<House> => {
  return apiClient.patch(`/api/v1/houses/${houseId}/status`, { status })
}

// 删除房屋
export const deleteHouse = async (houseId: number): Promise<void> => {
  return apiClient.delete(`/api/v1/houses/${houseId}`)
}

// 上传房屋图片
export const uploadHouseImage = async (houseId: number, file: File, isPrimary: boolean = false): Promise<void> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('is_primary', isPrimary.toString())
  
  return apiClient.post(`/api/v1/houses/${houseId}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除房屋图片
export const deleteHouseImage = async (houseId: number, imageId: number): Promise<void> => {
  return apiClient.delete(`/api/v1/houses/${houseId}/images/${imageId}`)
}