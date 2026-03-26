<template>
  <div class="my-visits-container">
    <div class="container">
      <el-card class="visits-card">
        <template #header>
          <div class="card-header">
            <h2>我的预约</h2>
          </div>
        </template>

        <div v-loading="loading">
          <el-table
            :data="visits"
            style="width: 100%"
            border
            stripe
          >
            <el-table-column prop="visit_date" label="预约日期" width="120" />
            <el-table-column prop="visit_time_slot" label="时间段" width="100">
              <template #default="scope">
                {{ scope.row.visit_time_slot === 'morning' ? '上午' : '下午' }}
              </template>
            </el-table-column>
            <el-table-column prop="visitor_name" label="访客姓名" width="120" />
            <el-table-column prop="visitor_phone" label="联系电话" width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag
                  :type="
                    scope.row.status === '0'
                      ? 'info'
                      : scope.row.status === '1'
                      ? 'success'
                      : 'danger'
                  "
                >
                  {{
                    scope.row.status === '0'
                      ? '待确认'
                      : scope.row.status === '1'
                      ? '已确认'
                      : '已取消'
                  }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button
                  type="danger"
                  size="small"
                  v-if="scope.row.status === '0'"
                  @click="cancelVisit(scope.row.id)"
                >
                  取消预约
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getMyVisits, updateVisitStatus } from '@/api'
import { HouseVisit, VisitStatus } from '@/types'

const userStore = useUserStore()
const loading = ref(false)
const visits = ref<HouseVisit[]>([])

// 初始化
onMounted(async () => {
  userStore.init()
  await fetchMyVisits()
})

// 获取我的预约
const fetchMyVisits = async () => {
  loading.value = true
  try {
    visits.value = await getMyVisits()
  } finally {
    loading.value = false
  }
}

// 取消预约
const cancelVisit = async (visitId: number) => {
  try {
    await ElMessageBox.confirm('确定要取消这个预约吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateVisitStatus(visitId, VisitStatus.CANCELLED)
    ElMessage.success('预约已取消')
    await fetchMyVisits()
  } catch {
    // 用户取消操作
  }
}
</script>

<style scoped>
.my-visits-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.visits-card {
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
</style>