<template>
  <div class="publish-container">
    <div class="container">
      <el-card class="publish-card">
        <template #header>
          <div class="card-header">
            <h2>发布房源</h2>
          </div>
        </template>

        <el-form
          ref="publishFormRef"
          :model="publishForm"
          :rules="publishRules"
          label-width="100px"
        >
          <el-form-item label="标题" prop="title">
            <el-input v-model="publishForm.title" placeholder="请输入房屋标题" />
          </el-form-item>

          <el-form-item label="价格" prop="price">
            <el-input-number v-model="publishForm.price" :min="0" :precision="2" step="100" style="width: 100%" />
          </el-form-item>

          <el-form-item label="面积" prop="area">
            <el-input-number v-model="publishForm.area" :min="0" :precision="1" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item label="房间数" prop="rooms">
            <el-input-number v-model="publishForm.rooms" :min="1" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item label="地址" prop="address">
            <el-input v-model="publishForm.address" placeholder="请输入详细地址" />
          </el-form-item>

          <el-form-item label="区域" prop="district">
            <el-input v-model="publishForm.district" placeholder="请输入区域" />
          </el-form-item>

          <el-form-item label="描述">
            <el-input
              v-model="publishForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入房屋描述"
            />
          </el-form-item>

          <el-form-item label="每日最大预约次数">
            <el-input-number v-model="publishForm.max_visits_per_day" :min="1" :max="10" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              @click="handlePublish"
              :loading="loading"
              size="large"
            >
              发布房源
            </el-button>
            <el-button @click="$router.back()">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useHouseStore } from '@/stores/house'

const router = useRouter()
const userStore = useUserStore()
const houseStore = useHouseStore()
const publishFormRef = ref()
const loading = ref(false)

const publishForm = reactive({
  title: '',
  price: 0,
  area: 0,
  rooms: 1,
  address: '',
  district: '',
  description: '',
  max_visits_per_day: 3
})

const publishRules = {
  title: [
    { required: true, message: '请输入房屋标题', trigger: 'blur' },
    { min: 5, message: '标题长度不能少于5个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格必须大于0', trigger: 'blur' }
  ],
  area: [
    { required: true, message: '请输入面积', trigger: 'blur' },
    { type: 'number', min: 0, message: '面积必须大于0', trigger: 'blur' }
  ],
  rooms: [
    { required: true, message: '请输入房间数', trigger: 'blur' },
    { type: 'number', min: 1, message: '房间数必须大于0', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入地址', trigger: 'blur' },
    { min: 5, message: '地址长度不能少于5个字符', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  userStore.init()
})

// 发布房屋
const handlePublish = async () => {
  if (!publishFormRef.value) return
  
  await publishFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const house = await houseStore.createNewHouse({
          title: publishForm.title,
          price: publishForm.price,
          area: publishForm.area,
          rooms: publishForm.rooms,
          address: publishForm.address,
          district: publishForm.district,
          description: publishForm.description,
          max_visits_per_day: publishForm.max_visits_per_day
        })
        loading.value = false
        ElMessage.success('发布成功')
        router.push(`/edit-house/${house.id}`)
      } catch (error: any) {
        loading.value = false
        ElMessage.error(error.response?.data?.msg || '发布失败')
      }
    }
  })
}
</script>

<style scoped>
.publish-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.publish-card {
  max-width: 800px;
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