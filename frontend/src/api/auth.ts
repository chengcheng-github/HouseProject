import apiClient from './axios'
import { User, Token, UserRegister, UserLogin } from '@/types'

// 用户注册
export const register = async (data: UserRegister): Promise<User> => {
  return apiClient.post('/api/v1/auth/register', data)
}

// 用户登录（JSON格式）
export const login = async (data: UserLogin): Promise<Token> => {
  return apiClient.post('/api/v1/auth/login/json', data)
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User> => {
  return apiClient.get('/api/v1/auth/me')
}