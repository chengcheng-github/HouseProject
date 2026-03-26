<template>
  <div class="my-houses-container">
    <div class="container">
      <el-card class="houses-card">
        <template #header>
          <div class="card-header">
            <h2>我的房源</h2>
            <el-button type="primary" @click="$router.push('/publish')">
              <el-icon><Plus /></el-icon> 发布新房源
            </el-button>
          </div>
        </template>

        <!-- 房屋列表 -->
        <div v-loading="houseStore.loading">
          <el-table
            :data="houseStore.myHouses"
            style="width: 100%"
            border
            stripe
          >
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="price" label="价格" width="120">
              <template #default="scope">
                <span class="price">¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="area" label="面积" width="100">
              <template #default="scope">
                {{ scope.row.area }}㎡
              </template>
            </el-table-column>
            <el-table-column prop="rooms" label="房间数" width="100" />
            <el-table-column prop="district" label="区域" width="120" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag
                  :type="
                    scope.row.status === '0'
                      ? 'info'
                      : scope.row.status === '1'
                      ? 'success'
                      : 'warning'
                  "
                >
                  {{
                    scope.row.status === '0'
                      ? '草稿'
                      : scope.row.status === '1'
                      ? '已上架'
                      : '已下架'
                  }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  @click="viewHouse(scope.row.id)"
                >
                  查看
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  @click="editHouse(scope.row.id)"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteHouse(scope.row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.page_size"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="houseStore.myTotal"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useHouseStore } from '@/stores/house'

const router = useRouter()
const userStore = useUserStore()
const houseStore = useHouseStore()

const pagination = reactive({
  page: 1,
  page_size: 10
})

// 初始化
onMounted(() => {
  userStore.init()
  fetchMyHouses()
})

// 获取我的房屋列表
const fetchMyHouses = async () => {
  await houseStore.fetchMyHouses({
    page: pagination.page,
    page_size: pagination.page_size
  })
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  pagination.page = 1
  fetchMyHouses()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchMyHouses()
}

// 查看房屋
const viewHouse = (houseId: number) => {
  router.push(`/house/${houseId}`)
}

// 编辑房屋
const editHouse = (houseId: number) => {
  router.push(`/edit-house/${houseId}`)
}

// 删除房屋
const deleteHouse = async (houseId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个房源吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await houseStore.removeHouse(houseId)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
  }
}
</script>

<style scoped>
.my-houses-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.houses-card {
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

.price {
  color: #f56c6c;
  font-weight: bold;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>