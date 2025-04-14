<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="mb-0">个人资料</h3>
            <div>
              <button class="btn btn-outline-primary me-2" @click="showEditModal('email')">
                修改邮箱
              </button>
              <button class="btn btn-primary" @click="showEditModal('password')">
                修改密码
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="user" class="profile-info">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input type="text" class="form-control" v-model="user.username" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input type="email" class="form-control" v-model="user.email" disabled>
              </div>
            </div>
            
            <div class="stats mt-4">
              <h4>游戏统计</h4>
              <div class="row">
                <div class="col-md-4">
                  <div class="stat-card">
                    <h5>总场次</h5>
                    <p class="stat-number">{{ user?.total_games || 0 }}</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-card">
                    <h5>胜场</h5>
                    <p class="stat-number">{{ user?.games_won || 0 }}</p>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-card">
                    <h5>胜率</h5>
                    <p class="stat-number">{{ user?.win_rate || 0 }}%</p>
                  </div>
                </div>
              </div>
              
              <!-- 积分展示 -->
              <div class="row mt-3">
                <div class="col-md-12">
                  <div class="stat-card special-card">
                    <h5>当前积分</h5>
                    <p class="stat-number rating">{{ user?.rating || 1000 }}</p>
                    <p class="text-muted small">初始积分为1000，胜场+10，负场-10</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改信息弹窗 -->
    <div class="modal fade" :class="{ show: isModalVisible }" tabindex="-1" v-if="isModalVisible">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <!-- 修改邮箱表单 -->
              <template v-if="editType === 'email'">
                <div class="mb-3">
                  <label class="form-label">新邮箱</label>
                  <input type="email" class="form-control" v-model="emailForm.newEmail" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">当前密码</label>
                  <input type="password" class="form-control" v-model="emailForm.currentPassword" required>
                </div>
              </template>

              <!-- 修改密码表单 -->
              <template v-if="editType === 'password'">
                <div class="mb-3">
                  <label class="form-label">当前密码</label>
                  <input type="password" class="form-control" v-model="passwordForm.currentPassword" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">新密码</label>
                  <input type="password" class="form-control" v-model="passwordForm.newPassword" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">确认新密码</label>
                  <input type="password" class="form-control" v-model="passwordForm.confirmPassword" required>
                </div>
              </template>

              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              <div v-if="success" class="alert alert-success">
                {{ success }}
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
            <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              确认修改
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="isModalVisible"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const user = ref(null)
const isLoading = ref(false)
const error = ref('')
const success = ref('')
const isModalVisible = ref(false)
const editType = ref('') // 'email' 或 'password'

const modalTitle = computed(() => {
  return editType.value === 'email' ? '修改邮箱' : '修改密码'
})

const emailForm = ref({
  newEmail: '',
  currentPassword: ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showEditModal = (type) => {
  editType.value = type
  isModalVisible.value = true
  error.value = ''
  success.value = ''
}

const closeModal = () => {
  isModalVisible.value = false
  // 重置表单和消息
  emailForm.value = {
    newEmail: '',
    currentPassword: ''
  }
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  error.value = ''
  success.value = ''
}

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  
  if (editType.value === 'email') {
    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(emailForm.value.newEmail)) {
      error.value = '请输入有效的邮箱地址'
      return
    }
  } else if (editType.value === 'password') {
    // 验证新密码是否匹配
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      error.value = '新密码和确认密码不匹配'
      return
    }
    
    // 验证密码长度
    if (passwordForm.value.newPassword.length < 6) {
      error.value = '新密码长度至少为6个字符'
      return
    }
  }
  
  try {
    isLoading.value = true
    const data = editType.value === 'email' 
      ? { email: emailForm.value.newEmail, current_password: emailForm.value.currentPassword }
      : { current_password: passwordForm.value.currentPassword, new_password: passwordForm.value.newPassword }
    
    const response = await axios.put('/api/me', data)
    
    success.value = editType.value === 'email' ? '邮箱修改成功' : '密码修改成功'
    
    // 更新用户信息
    if (editType.value === 'email') {
      user.value.email = emailForm.value.newEmail
    }
    
    // 0.5秒后关闭弹窗
    setTimeout(() => {
      closeModal()
    }, 500)
  } catch (error) {
    if (error.response?.data?.error) {
      error.value = error.response.data.error
    } else {
      error.value = editType.value === 'email' ? '修改邮箱失败，请稍后重试' : '修改密码失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  try {
    await authStore.fetchUser()
    user.value = authStore.currentUser
    
    // 如果用户信息为空，则显示错误提示，但不跳转
    if (!user.value) {
      error.value = '获取用户信息失败，请刷新页面重试'
    }
  } catch (err) {
    console.error('Error loading profile:', err)
    error.value = '获取用户信息失败，请刷新页面重试'
  }
})
</script>

<style scoped>
.profile-info {
  margin-bottom: 20px;
}

.stats {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 5px;
}

.stat-card {
  text-align: center;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0 0;
  color: #007bff;
}

.special-card {
  background-color: #f0f8ff;
  border-left: 4px solid #007bff;
}

.rating {
  color: #007bff;
  font-size: 32px;
}

.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal.show {
  display: block;
  opacity: 1;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}
</style> 