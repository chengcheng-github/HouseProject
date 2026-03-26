import apiClient from './axios'
import { User } from '@/types'

// 更新个人信息
export const updateProfile = async (data: Partial<User>): Promise<User> => {
  return apiClient.put('/api/v1/users/me', data)
}

// 获取用户信息
export const getUser = async (userId: number): Promise<User> => {
  return apiClient.get(`/api/v1/users/${userId}`)
}