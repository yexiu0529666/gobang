<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="text-center mb-4">注册</h1>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-person"></i>
            </span>
            <input
              type="text"
              id="username"
              v-model="username"
              class="form-control"
              placeholder="请输入用户名"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-envelope"></i>
            </span>
            <input
              type="email"
              id="email"
              v-model="email"
              class="form-control"
              placeholder="请输入邮箱"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-lock"></i>
            </span>
            <input
              type="password"
              id="password"
              v-model="password"
              class="form-control"
              placeholder="请输入密码"
              required
            />
          </div>
        </div>
        <div class="form-group">
          <label for="verificationCode">验证码</label>
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-shield-check"></i>
            </span>
            <input
              type="text"
              id="verificationCode"
              v-model="verificationCode"
              class="form-control"
              placeholder="请输入验证码"
              required
            />
            <button
              type="button"
              class="btn btn-outline-primary"
              @click="sendVerificationCode"
              :disabled="sendingCode || countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
            </button>
          </div>
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="text-center mt-4">
        <p class="mb-0">已有账号？<router-link to="/login" class="text-primary">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const verificationCode = ref('')
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)

const sendVerificationCode = async () => {
  if (!email.value) {
    alert('请输入邮箱')
    return
  }

  sendingCode.value = true
  try {
    await authStore.sendVerificationCode(email.value)
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    alert(error.message || '发送验证码失败')
  } finally {
    sendingCode.value = false
  }
}

const handleRegister = async () => {
  if (!username.value || !email.value || !password.value || !verificationCode.value) {
    alert('请填写所有字段')
    return
  }

  loading.value = true
  try {
    const registerData = {
      username: username.value,
      email: email.value,
      password: password.value,
      verificationCode: verificationCode.value
    }
    console.log('注册数据:', registerData)
    await authStore.register(registerData)
    router.push('/login')
  } catch (error) {
    alert(error.response?.data?.error || error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2.5rem;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  animation: fadeIn 0.5s ease-out;
  backdrop-filter: blur(10px);
}

.register-form {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
}

.input-group {
  position: relative;
}

.input-group-text {
  background-color: rgba(248, 250, 252, 0.8);
  border-right: none;
  color: #64748b;
}

.form-control {
  border-left: none;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.8);
}

.form-control:focus {
  box-shadow: none;
  border-color: #ced4da;
  background-color: white;
}

.form-control:focus + .input-group-text {
  border-color: #ced4da;
}

.btn-primary {
  padding: 0.75rem;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: linear-gradient(135deg, #a5b1fc 0%, #b8a6d4 100%);
  transform: none;
  box-shadow: none;
}

.btn-outline-primary {
  border-color: #667eea;
  color: #667eea;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background-color: #667eea;
  color: white;
}

.btn-outline-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 576px) {
  .register-card {
    padding: 2rem;
    margin: 1rem;
  }
}
</style> 