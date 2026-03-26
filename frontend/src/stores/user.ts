import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { User, Token } from '@/types'
import { login as loginApi, getCurrentUser } from '@/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 初始化
  const init = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      fetchUserInfo()
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const userInfo = await getCurrentUser()
      user.value = userInfo
    } catch (error) {
      logout()
    }
  }

  // 登录
  const login = async (email: string, password: string) => {
    try {
      const response = await loginApi({ email, password })
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      await fetchUserInfo()
      return true
    } catch (error) {
      return false
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // 更新用户信息
  const updateUser = (userInfo: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userInfo }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    init,
    login,
    logout,
    updateUser
  }
})