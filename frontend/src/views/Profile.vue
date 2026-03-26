<template>
  <div class="profile-container">
    <div class="container">
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <h2>个人中心</h2>
          </div>
        </template>

        <div class="profile-content">
          <!-- 用户信息展示 -->
          <div class="user-info">
            <el-avatar :src="userStore.user?.avatar" :size="100" />
            <div class="info-details">
              <h3>{{ userStore.user?.nickname }}</h3>
              <p>{{ userStore.user?.email }}</p>
              <p>角色：{{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
            </div>
          </div>

          <!-- 编辑表单 -->
          <el-divider />
          <h3>编辑个人信息</h3>
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="handleUpdate"
                :loading="loading"
              >
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateProfile } from '@/api'

const userStore = useUserStore()
const profileFormRef = ref()
const loading = ref(false)

const profileForm = reactive({
  nickname: ''
})

const profileRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, message: '昵称长度不能少于2个字符', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  userStore.init()
  if (userStore.user) {
    profileForm.nickname = userStore.user.nickname || ''
  }
})

// 更新个人信息
const handleUpdate = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const updatedUser = await updateProfile({
          nickname: profileForm.nickname
        })
        userStore.updateUser(updatedUser)
        loading.value = false
        ElMessage.success('修改成功')
      } catch (error: any) {
        loading.value = false
        ElMessage.error(error.response?.data?.msg || '修改失败')
      }
    }
  })
}
</script>

<style scoped>
.profile-container {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.profile-card {
  max-width: 600px;
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

.profile-content {
  padding: 20px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.info-details h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.info-details p {
  margin: 4px 0;
  color: #606266;
}

.el-divider {
  margin: 20px 0;
}

.profile-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}
</style>