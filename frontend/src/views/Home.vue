<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container">
        <h1 class="logo">房屋介绍网站</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link active">首页</router-link>
          <router-link to="/publish" v-if="userStore.isAuthenticated" class="nav-link">发布房源</router-link>
          <router-link to="/my-houses" v-if="userStore.isAuthenticated" class="nav-link">我的房源</router-link>
          <router-link to="/my-visits" v-if="userStore.isAuthenticated" class="nav-link">我的预约</router-link>
          <router-link to="/admin" v-if="userStore.isAdmin" class="nav-link">运维管理</router-link>
          <router-link to="/profile" v-if="userStore.isAuthenticated" class="nav-link">个人中心</router-link>
          <router-link to="/login" v-else class="nav-link">登录</router-link>
        </nav>
      </div>
    </header>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="container">
        <el-card>
          <el-form :model="filterForm" inline>
            <el-form-item label="标题">
              <el-input v-model="filterForm.title" placeholder="请输入房屋标题" clearable />
            </el-form-item>
            <el-form-item label="区域">
              <el-input v-model="filterForm.district" placeholder="请输入区域" clearable />
            </el-form-item>
            <el-form-item label="价格区间">
              <el-input-number v-model="filterForm.min_price" :min="0" placeholder="最低" style="width: 100px" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.max_price" :min="0" placeholder="最高" style="width: 100px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="resetFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>

    <!-- 房屋列表 -->
    <main class="main-content">
      <div class="container">
        <el-card v-loading="houseStore.loading">
          <div class="house-grid">
            <el-card
              v-for="house in houseStore.houses"
              :key="house.id"
              class="house-card"
              shadow="hover"
              @click="goToDetail(house.id)"
            >
              <div class="house-image">
                <el-image
                  :src="house.primary_image || '/placeholder.jpg'"
                  fit="cover"
                  :alt="house.title"
                >
                  <template #error>
                    <div class="image-error">暂无图片</div>
                  </template>
                </el-image>
              </div>
              <div class="house-info">
                <h3 class="house-title">{{ house.title }}</h3>
                <div class="house-meta">
                  <span class="price">¥{{ house.price }}</span>
                  <span>{{ house.area }}㎡</span>
                  <span>{{ house.rooms }}室</span>
                </div>
                <div class="house-address">{{ house.address }}</div>
                <div class="house-footer">
                  <span class="district">{{ house.district }}</span>
                  <span class="user">{{ house.user_nickname }}</span>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.page_size"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="houseStore.total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useHouseStore } from '@/stores/house'

const router = useRouter()
const userStore = useUserStore()
const houseStore = useHouseStore()

const filterForm = reactive({
  title: '',
  district: '',
  min_price: undefined as number | undefined,
  max_price: undefined as number | undefined
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

// 初始化
onMounted(() => {
  userStore.init()
  fetchHouses()
})

// 获取房屋列表
const fetchHouses = async () => {
  await houseStore.fetchHouses({
    page: pagination.page,
    page_size: pagination.page_size,
    title: filterForm.title,
    district: filterForm.district,
    min_price: filterForm.min_price,
    max_price: filterForm.max_price
  })
}

// 查询
const handleSearch = () => {
  pagination.page = 1
  fetchHouses()
}

// 重置
const resetFilter = () => {
  filterForm.title = ''
  filterForm.district = ''
  filterForm.min_price = undefined
  filterForm.max_price = undefined
  pagination.page = 1
  fetchHouses()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  pagination.page = 1
  fetchHouses()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchHouses()
}

// 跳转到详情页
const goToDetail = (houseId: number) => {
  router.push(`/house/${houseId}`)
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.header {
  background: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin: 0;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: #606266;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-link:hover,
.nav-link.active {
  color: #409eff;
  background-color: #ecf5ff;
}

.filter-section {
  padding: 20px 0;
  background: #f5f7fa;
}

.main-content {
  padding: 20px 0;
}

.house-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.house-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.house-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.house-image {
  height: 200px;
  overflow: hidden;
  border-radius: 4px 4px 0 0;
}

.house-image img {
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.house-card:hover .house-image img {
  transform: scale(1.05);
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}

.house-info {
  padding: 16px;
}

.house-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 12px 0;
  color: #303133;
}

.house-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.house-address {
  color: #606266;
  margin-bottom: 8px;
}

.house-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>