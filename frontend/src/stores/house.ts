import { defineStore } from 'pinia'
import { ref } from 'vue'
import { House, HouseList, HouseCreate, HouseUpdate, HouseStatus, PaginatedData } from '@/types'
import {
  createHouse,
  getHouses,
  getMyHouses,
  getHouseDetail,
  updateHouse,
  updateHouseStatus,
  deleteHouse,
  uploadHouseImage,
  deleteHouseImage
} from '@/api'

export const useHouseStore = defineStore('house', () => {
  // 状态
  const houses = ref<HouseList[]>([])
  const myHouses = ref<HouseList[]>([])
  const currentHouse = ref<House | null>(null)
  const total = ref(0)
  const myTotal = ref(0)
  const loading = ref(false)

  // 获取房屋列表
  const fetchHouses = async (params: {
    page?: number
    page_size?: number
    title?: string
    district?: string
    min_price?: number
    max_price?: number
  }) => {
    loading.value = true
    try {
      const response = await getHouses(params)
      houses.value = response.items
      total.value = response.total
      return response
    } finally {
      loading.value = false
    }
  }

  // 获取我的房屋列表
  const fetchMyHouses = async (params: {
    page?: number
    page_size?: number
  }) => {
    loading.value = true
    try {
      const response = await getMyHouses(params)
      myHouses.value = response.items
      myTotal.value = response.total
      return response
    } finally {
      loading.value = false
    }
  }

  // 获取房屋详情
  const fetchHouseDetail = async (houseId: number) => {
    loading.value = true
    try {
      const house = await getHouseDetail(houseId)
      currentHouse.value = house
      return house
    } finally {
      loading.value = false
    }
  }

  // 创建房屋
  const createNewHouse = async (data: HouseCreate) => {
    loading.value = true
    try {
      const house = await createHouse(data)
      return house
    } finally {
      loading.value = false
    }
  }

  // 更新房屋信息
  const updateHouseInfo = async (houseId: number, data: HouseUpdate) => {
    loading.value = true
    try {
      const house = await updateHouse(houseId, data)
      if (currentHouse.value?.id === houseId) {
        currentHouse.value = house
      }
      return house
    } finally {
      loading.value = false
    }
  }

  // 更新房屋状态
  const changeHouseStatus = async (houseId: number, status: HouseStatus) => {
    loading.value = true
    try {
      const house = await updateHouseStatus(houseId, status)
      if (currentHouse.value?.id === houseId) {
        currentHouse.value = house
      }
      return house
    } finally {
      loading.value = false
    }
  }

  // 删除房屋
  const removeHouse = async (houseId: number) => {
    loading.value = true
    try {
      await deleteHouse(houseId)
      // 更新列表
      houses.value = houses.value.filter(h => h.id !== houseId)
      myHouses.value = myHouses.value.filter(h => h.id !== houseId)
      if (currentHouse.value?.id === houseId) {
        currentHouse.value = null
      }
    } finally {
      loading.value = false
    }
  }

  // 上传图片
  const addHouseImage = async (houseId: number, file: File, isPrimary: boolean = false) => {
    loading.value = true
    try {
      await uploadHouseImage(houseId, file, isPrimary)
      // 重新获取房屋详情
      if (currentHouse.value?.id === houseId) {
        await fetchHouseDetail(houseId)
      }
    } finally {
      loading.value = false
    }
  }

  // 删除图片
  const removeHouseImage = async (houseId: number, imageId: number) => {
    loading.value = true
    try {
      await deleteHouseImage(houseId, imageId)
      // 重新获取房屋详情
      if (currentHouse.value?.id === houseId) {
        await fetchHouseDetail(houseId)
      }
    } finally {
      loading.value = false
    }
  }

  return {
    houses,
    myHouses,
    currentHouse,
    total,
    myTotal,
    loading,
    fetchHouses,
    fetchMyHouses,
    fetchHouseDetail,
    createNewHouse,
    updateHouseInfo,
    changeHouseStatus,
    removeHouse,
    addHouseImage,
    removeHouseImage
  }
})