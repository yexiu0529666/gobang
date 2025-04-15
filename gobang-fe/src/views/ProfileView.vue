<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1 class="profile-title">个人资料</h1>
      <p class="profile-subtitle">查看并管理您的账号信息和游戏数据</p>
    </div>
    
    <div class="profile-card">
      <div class="profile-section user-info-section">
        <div class="section-header">
          <h2><i class="fas fa-user-circle"></i> 基本信息</h2>
          <div class="action-buttons">
            <button class="btn-action email" @click="showEditModal('email')">
              <i class="fas fa-envelope"></i> 修改邮箱
            </button>
            <button class="btn-action password" @click="showEditModal('password')">
              <i class="fas fa-key"></i> 修改密码
            </button>
          </div>
        </div>
        
        <div v-if="user" class="user-info-content">
          <div class="info-group">
            <label>用户名</label>
            <div class="info-value">
              <i class="fas fa-user"></i>
              <span>{{ user.username }}</span>
            </div>
          </div>
          <div class="info-group">
            <label>邮箱</label>
            <div class="info-value">
              <i class="fas fa-envelope"></i>
              <span>{{ user.email || '未设置' }}</span>
            </div>
          </div>
          <div class="info-group">
            <label>账号创建时间</label>
            <div class="info-value">
              <i class="fas fa-calendar-alt"></i>
              <span>{{ user.created_at || '未知' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="profile-section stats-section">
        <div class="section-header">
          <h2><i class="fas fa-chart-line"></i> 游戏统计</h2>
        </div>
        
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-gamepad"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user?.total_games || 0 }}</div>
              <div class="stat-label">总场次</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-trophy"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user?.games_won || 0 }}</div>
              <div class="stat-label">胜场</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-percentage"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ user?.win_rate || 0 }}%</div>
              <div class="stat-label">胜率</div>
            </div>
          </div>
        </div>
        
        <!-- 积分展示 -->
        <div class="rating-card">
          <div class="rating-header">
            <h3><i class="fas fa-star"></i> 当前积分</h3>
          </div>
          <div class="rating-content">
            <div class="rating-value">{{ user?.rating || 1000 }}</div>
            <div class="rating-progress">
              <div class="progress-bar" :style="{ width: `${getRatingPercentage()}%` }"></div>
            </div>
            <div class="rating-tiers">
              <span>新手</span>
              <span>业余</span>
              <span>专业</span>
              <span>大师</span>
            </div>
            <p class="rating-info">初始积分为1000，胜场+10，负场-10</p>
          </div>
        </div>
        
      </div>
    </div>

    <!-- 修改信息弹窗 -->
    <div class="custom-modal" v-if="isModalVisible">
      <div class="modal-overlay" @click="closeModal"></div>
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">{{ modalTitle }}</h3>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- 修改邮箱表单 -->
            <template v-if="editType === 'email'">
              <div class="form-group">
                <label>新邮箱</label>
                <div class="input-with-icon">
                  <i class="fas fa-envelope"></i>
                  <input type="email" v-model="emailForm.newEmail" required>
                </div>
              </div>
              <div class="form-group">
                <label>当前密码</label>
                <div class="input-with-icon">
                  <i class="fas fa-lock"></i>
                  <input type="password" v-model="emailForm.currentPassword" required>
                </div>
              </div>
            </template>

            <!-- 修改密码表单 -->
            <template v-if="editType === 'password'">
              <div class="form-group">
                <label>当前密码</label>
                <div class="input-with-icon">
                  <i class="fas fa-lock"></i>
                  <input type="password" v-model="passwordForm.currentPassword" required>
                </div>
              </div>
              <div class="form-group">
                <label>新密码</label>
                <div class="input-with-icon">
                  <i class="fas fa-key"></i>
                  <input type="password" v-model="passwordForm.newPassword" required>
                </div>
              </div>
              <div class="form-group">
                <label>确认新密码</label>
                <div class="input-with-icon">
                  <i class="fas fa-check-circle"></i>
                  <input type="password" v-model="passwordForm.confirmPassword" required>
                </div>
              </div>
            </template>

            <div class="alert alert-error" v-if="error">
              <i class="fas fa-exclamation-circle"></i> {{ error }}
            </div>
            <div class="alert alert-success" v-if="success">
              <i class="fas fa-check-circle"></i> {{ success }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-submit" @click="handleSubmit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span v-else>确认修改</span>
          </button>
        </div>
      </div>
    </div>
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

const getRatingPercentage = () => {
  const rating = user.value?.rating || 1000
  const min = 800 // 最低分数
  const max = 2000 // 最高分数
  return Math.min(100, Math.max(0, ((rating - min) / (max - min)) * 100))
}

const showEditModal = (type) => {
  editType.value = type
  isModalVisible.value = true
  error.value = ''
  success.value = ''
  
  // 如果是修改邮箱，默认填入当前邮箱
  if (type === 'email' && user.value && user.value.email) {
    emailForm.value.newEmail = user.value.email
  }
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
    
    // 2秒后关闭弹窗
    setTimeout(() => {
      closeModal()
    }, 2000)
  } catch (err) {
    console.error('Error updating profile:', err)
    if (err.response?.data?.error) {
      error.value = err.response.data.error
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
/* 基础样式 */
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
  color: #2c3e50;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out;
}

.profile-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #3498db;
}

.profile-subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.profile-card {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
  animation: slideUp 0.6s ease-out;
}

.profile-section {
  padding: 2rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-header h2 i {
  color: #3498db;
}

/* 用户信息样式 */
.user-info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.info-group {
  margin-bottom: 1rem;
}

.info-group label {
  display: block;
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.75rem 1rem;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 0.5rem;
  border-left: 3px solid #3498db;
}

.info-value i {
  color: #3498db;
}

/* 按钮样式 */
.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-action.email {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.btn-action.password {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.btn-action:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* 统计卡片样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(246, 249, 252, 0.9) 100%);
  border-radius: 1rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3498db 0%, #2ecc71 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.3rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* 积分卡片样式 */
.rating-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 247, 255, 0.95) 100%);
  border-radius: 1rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  overflow: hidden;
}

.rating-header {
  padding: 1.2rem 1.5rem;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  color: white;
}

.rating-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.2rem;
}

.rating-content {
  padding: 2rem 1.5rem;
}

.rating-value {
  font-size: 3rem;
  font-weight: 700;
  color: #3498db;
  text-align: center;
  margin-bottom: 1.5rem;
  text-shadow: 0 2px 5px rgba(52, 152, 219, 0.2);
}

.rating-progress {
  height: 8px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.rating-tiers {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.rating-info {
  text-align: center;
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* 最近游戏样式 */
.recent-games {
  padding: 1.5rem;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 1rem;
}

.recent-games h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.recent-games h3 i {
  color: #3498db;
}

.no-games {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 0.5rem;
}

/* 模态框样式 */
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.modal-container {
  position: relative;
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: modalShow 0.3s ease-out;
  z-index: 1051;
}

.modal-header {
  padding: 1.5rem;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.modal-close:hover {
  transform: scale(1.2);
}

.modal-body {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.input-with-icon {
  position: relative;
}

.input-with-icon i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.input-with-icon input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.5rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-with-icon input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.alert-error {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  background-color: transparent;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  color: #7f8c8d;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-submit {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes modalShow {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-title {
    font-size: 2rem;
  }
  
  .profile-subtitle {
    font-size: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-buttons {
    width: 100%;
  }
  
  .btn-action {
    flex: 1;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .user-info-content {
    grid-template-columns: 1fr;
  }
}
</style> 