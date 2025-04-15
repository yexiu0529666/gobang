<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="text-center mb-4">登录</h1>
      <form @submit.prevent="handleLogin" class="login-form">
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
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <div class="text-center mt-4">
        <p class="mb-0">还没有账号？<router-link to="/register" class="text-primary">立即注册</router-link></p>
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
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (error) {
    alert(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2.5rem;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  animation: fadeIn 0.5s ease-out;
  backdrop-filter: blur(10px);
}

.login-form {
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
  .login-card {
    padding: 2rem;
    margin: 1rem;
  }
}
</style> 