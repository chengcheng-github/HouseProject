<template>
  <div class="house-detail-container">
    <!-- 返回按钮 -->
    <div class="container">
      <el-button @click="$router.back()" class="back-btn">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
    </div>

    <!-- 房屋详情 -->
    <div class="container" v-loading="houseStore.loading">
      <el-card v-if="houseStore.currentHouse" class="detail-card">
        <!-- 图片展示 -->
        <div class="image-gallery">
          <el-carousel height="400px" trigger="click">
            <el-carousel-item v-for="(image, index) in houseStore.currentHouse.images" :key="image.id">
              <el-image :src="image.image_url" fit="cover" />
            </el-carousel-item>
          </el-carousel>
        </div>

        <!-- 房屋信息 -->
        <div class="house-info">
          <h1 class="house-title">{{ houseStore.currentHouse.title }}</h1>
          
          <div class="price-section">
            <span class="price">¥{{ houseStore.currentHouse.price }}</span>
            <span class="area">{{ houseStore.currentHouse.area }}㎡</span>
            <span class="rooms">{{ houseStore.currentHouse.rooms }}室</span>
          </div>

          <div class="address-section">
            <el-icon><Location /></el-icon>
            <span>{{ houseStore.currentHouse.address }}</span>
            <span v-if="houseStore.currentHouse.district" class="district">{{ houseStore.currentHouse.district }}</span>
          </div>

          <!-- 房东信息 -->
          <div class="owner-info">
            <h3>房东信息</h3>
            <div class="owner-details">
              <el-avatar :src="houseStore.currentHouse.user?.avatar" :size="60" />
              <div>
                <div class="owner-name">{{ houseStore.currentHouse.user?.nickname }}</div>
                <div class="owner-email">{{ houseStore.currentHouse.user?.email }}</div>
              </div>
            </div>
          </div>

          <!-- 房屋描述 -->
          <div class="description-section">
            <h3>房屋描述</h3>
            <div class="description">
              {{ houseStore.currentHouse.description || '暂无描述' }}
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              v-if="userStore.isAuthenticated && userStore.user?.id === houseStore.currentHouse.user_id"
              @click="$router.push(`/edit-house/${houseStore.currentHouse.id}`)"
            >
              编辑房源
            </el-button>
            <el-button
              type="success"
              size="large"
              v-if="userStore.isAuthenticated"
              @click="showVisitDialog = true"
            >
              预约看房
            </el-button>
          </div>

          <!-- 预约对话框 -->
          <el-dialog v-model="showVisitDialog" title="预约看房" width="500px">
            <el-form
              ref="visitFormRef"
              :model="visitForm"
              :rules="visitRules"
              label-width="100px"
            >
              <el-form-item label="访客姓名" prop="visitor_name">
                <el-input v-model="visitForm.visitor_name" placeholder="请输入访客姓名" />
              </el-form-item>
              <el-form-item label="联系电话" prop="visitor_phone">
                <el-input v-model="visitForm.visitor_phone" placeholder="请输入联系电话" />
              </el-form-item>
              <el-form-item label="预约日期" prop="visit_date">
                <el-date-picker
                  v-model="visitForm.visit_date"
                  type="date"
                  placeholder="选择日期"
                  :min-date="new Date()"
                  :max-date="new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="时间段" prop="visit_time_slot">
                <el-radio-group v-model="visitForm.visit_time_slot">
                  <el-radio label="morning">上午</el-radio>
                  <el-radio label="afternoon">下午</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="备注">
                <el-input
                  v-model="visitForm.remark"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入备注（可选）"
                />
              </el-form-item>
            </el-form>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="showVisitDialog = false">取消</el-button>
                <el-button type="primary" @click="handleVisit" :loading="visiting">
                  提交预约
                </el-button>
              </span>
            </template>
          </el-dialog>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useHouseStore } from '@/stores/house'
import { createVisit } from '@/api'

const route = useRoute()
const userStore = useUserStore()
const houseStore = useHouseStore()
const visitFormRef = ref()
const showVisitDialog = ref(false)
const visiting = ref(false)

// 获取房屋ID
const houseId = Number(route.params.id)

// 预约表单
const visitForm = reactive({
  visitor_name: '',
  visitor_phone: '',
  visit_date: null,
  visit_time_slot: 'morning' as 'morning' | 'afternoon',
  remark: ''
})

// 表单验证规则
const visitRules = {
  visitor_name: [
    { required: true, message: '请输入访客姓名', trigger: 'blur' },
    { min: 2, message: '姓名长度不能少于2个字符', trigger: 'blur' }
  ],
  visitor_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  visit_date: [
    { required: true, message: '请选择预约日期', trigger: 'change' }
  ],
  visit_time_slot: [
    { required: true, message: '请选择时间段', trigger: 'change' }
  ]
}

// 初始化
onMounted(async () => {
  userStore.init()
  await houseStore.fetchHouseDetail(houseId)
})

// 提交预约
const handleVisit = async () => {
  if (!visitFormRef.value) return
  
  await visitFormRef.value.validate(async (valid) => {
    if (valid) {
      visiting.value = true
      try {
        await createVisit({
          house_id: houseId,
          visitor_name: visitForm.visitor_name,
          visitor_phone: visitForm.visitor_phone,
          visit_date: visitForm.visit_date.toISOString().split('T')[0],
          time_slot: visitForm.visit_time_slot,
          remark: visitForm.remark
        })
        visiting.value = false
        ElMessage.success('预约成功')
        showVisitDialog.value = false
        
        // 重置表单
        visitForm.visitor_name = ''
        visitForm.visitor_phone = ''
        visitForm.visit_date = null
        visitForm.visit_time_slot = 'morning'
        visitForm.remark = ''
      } catch (error: any) {
        visiting.value = false
        ElMessage.error(error.response?.data?.msg || '预约失败')
      }
    }
  })
}</script>

<style scoped>
.house-detail-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.back-btn {
  margin-bottom: 20px;
}

.detail-card {
  background: white;
}

.image-gallery {
  margin-bottom: 20px;
}

.house-info {
  padding: 0 20px;
}

.house-title {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 20px 0;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.price {
  color: #f56c6c;
  font-size: 32px;
  font-weight: bold;
}

.area,
.rooms {
  font-size: 16px;
  color: #606266;
}

.address-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
  color: #606266;
}

.district {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.owner-info {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.owner-info h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.owner-details {
  display: flex;
  align-items: center;
  gap: 16px;
}

.owner-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.owner-email {
  color: #606266;
  font-size: 14px;
}

.description-section {
  margin-bottom: 30px;
}

.description-section h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.description {
  line-height: 1.8;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 30px;
}
</style>