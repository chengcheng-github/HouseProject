<template>
  <div class="edit-container">
    <div class="container">
      <el-card class="edit-card" v-loading="houseStore.loading">
        <template #header>
          <div class="card-header">
            <h2>编辑房源</h2>
          </div>
        </template>

        <el-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
          label-width="100px"
        >
          <el-form-item label="标题" prop="title">
            <el-input v-model="editForm.title" placeholder="请输入房屋标题" />
          </el-form-item>

          <el-form-item label="价格" prop="price">
            <el-input-number v-model="editForm.price" :min="0" :precision="2" step="100" style="width: 100%" />
          </el-form-item>

          <el-form-item label="面积" prop="area">
            <el-input-number v-model="editForm.area" :min="0" :precision="1" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item label="房间数" prop="rooms">
            <el-input-number v-model="editForm.rooms" :min="1" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item label="地址" prop="address">
            <el-input v-model="editForm.address" placeholder="请输入详细地址" />
          </el-form-item>

          <el-form-item label="区域" prop="district">
            <el-input v-model="editForm.district" placeholder="请输入区域" />
          </el-form-item>

          <el-form-item label="描述">
            <el-input
              v-model="editForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入房屋描述"
            />
          </el-form-item>

          <el-form-item label="每日最大预约次数">
            <el-input-number v-model="editForm.max_visits_per_day" :min="1" :max="10" step="1" style="width: 100%" />
          </el-form-item>

          <el-form-item label="状态">
            <el-radio-group v-model="editForm.status">
              <el-radio label="0">草稿</el-radio>
              <el-radio label="1">已上架</el-radio>
              <el-radio label="2">已下架</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 图片管理 -->
          <el-divider />
          <h3>图片管理</h3>
          
          <!-- 图片列表 -->
          <div class="image-list" v-if="houseStore.currentHouse?.images.length">
            <div
              v-for="image in houseStore.currentHouse.images"
              :key="image.id"
              class="image-item"
            >
              <el-image :src="image.image_url" fit="cover" />
              <div class="image-actions">
                <el-tag v-if="image.is_primary">主图</el-tag>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeImage(image.id)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>

          <!-- 上传图片 -->
          <el-upload
            class="upload-image"
            action="/api/v1/houses/0/images"
            :auto-upload="false"
            :on-change="handleImageChange"
            :before-upload="beforeUpload"
            multiple
            accept="image/*"
          >
            <el-button type="primary">上传图片</el-button>
          </el-upload>

          <el-form-item>
            <el-button
              type="primary"
              @click="handleSave"
              :loading="saving"
              size="large"
            >
              保存修改
            </el-button>
            <el-button @click="$router.back()">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useHouseStore } from '@/stores/house'
import { HouseStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const houseStore = useHouseStore()
const editFormRef = ref()
const saving = ref(false)

const houseId = Number(route.params.id)

const editForm = reactive({
  title: '',
  price: 0,
  area: 0,
  rooms: 1,
  address: '',
  district: '',
  description: '',
  max_visits_per_day: 3,
  status: HouseStatus.DRAFT
})

const editRules = {
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
onMounted(async () => {
  userStore.init()
  await houseStore.fetchHouseDetail(houseId)
  
  if (houseStore.currentHouse) {
    const house = houseStore.currentHouse
    editForm.title = house.title
    editForm.price = house.price
    editForm.area = house.area
    editForm.rooms = house.rooms
    editForm.address = house.address
    editForm.district = house.district || ''
    editForm.description = house.description || ''
    editForm.max_visits_per_day = house.max_visits_per_day
    editForm.status = house.status
  }
})

// 保存修改
const handleSave = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // 更新房屋信息
        await houseStore.updateHouseInfo(houseId, {
          title: editForm.title,
          price: editForm.price,
          area: editForm.area,
          rooms: editForm.rooms,
          address: editForm.address,
          district: editForm.district,
          description: editForm.description,
          max_visits_per_day: editForm.max_visits_per_day
        })
        
        // 更新状态
        if (editForm.status !== houseStore.currentHouse?.status) {
          await houseStore.changeHouseStatus(houseId, editForm.status)
        }
        
        saving.value = false
        ElMessage.success('保存成功')
        router.push('/my-houses')
      } catch (error: any) {
        saving.value = false
        ElMessage.error(error.response?.data?.msg || '保存失败')
      }
    }
  })
}

// 删除图片
const removeImage = async (imageId: number) => {
  try {
    await houseStore.removeHouseImage(houseId, imageId)
    ElMessage.success('图片删除成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '删除失败')
  }
}

// 图片上传前的校验
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过10MB')
    return false
  }
  
  return true
}

// 处理图片上传
const handleImageChange = async (file: any) => {
  if (file.status === 'ready') {
    try {
      await houseStore.addHouseImage(houseId, file.raw, false)
      ElMessage.success('图片上传成功')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.msg || '上传失败')
    }
  }
}
</script>

<style scoped>
.edit-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.edit-card {
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

.image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.image-item {
  position: relative;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.image-item img {
  width: 100%;
  height: 100px;
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-image {
  margin-bottom: 20px;
}
</style>