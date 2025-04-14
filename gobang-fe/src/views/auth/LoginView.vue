<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">登录</h3>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <input
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': usernameError }"
                  id="username"
                  v-model="username"
                  required
                  @input="clearError"
                >
                <div v-if="usernameError" class="invalid-feedback">
                  {{ usernameError }}
                </div>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input
                  type="password"
                  class="form-control"
                  :class="{ 'is-invalid': passwordError }"
                  id="password"
                  v-model="password"
                  required
                  @input="clearError"
                >
                <div v-if="passwordError" class="invalid-feedback">
                  {{ passwordError }}
                </div>
              </div>
              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="remember"
                  v-model="remember"
                >
                <label class="form-check-label" for="remember">记住我</label>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  登录
                </button>
              </div>
            </form>
          </div>
          <div class="card-footer text-center">
            <p class="mb-0">还没有账号？ <router-link to="/register">注册</router-link></p>
          </div>
        </div>
      </div>
    </div>

    <!-- 登录成功弹窗 -->
    <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="successModalLabel">登录成功</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            登录成功！即将跳转
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Modal } from 'bootstrap'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const remember = ref(false)
const loading = ref(false)
const error = ref('')
const usernameError = ref('')
const passwordError = ref('')

const clearError = () => {
  error.value = ''
  usernameError.value = ''
  passwordError.value = ''
}

const handleSubmit = async () => {
  clearError()
  
  if (!username.value) {
    usernameError.value = '请输入用户名'
    return
  }
  if (!password.value) {
    passwordError.value = '请输入密码'
    return
  }
  
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    // 显示成功弹窗
    const successModal = new Modal(document.getElementById('successModal'))
    successModal.show()
    
    // 2秒后跳转到开始游戏页面
    setTimeout(() => {
      successModal.hide()
      router.push('/')
    }, 500)
  } catch (err) {
    if (err.response) {
      const { data } = err.response
      if (data.error) {
        error.value = data.error === 'Invalid username or password' ? '用户名或密码错误' : data.error
      } else if (data.message) {
        error.value = data.message
      } else {
        error.value = '登录失败，请稍后重试'
      }
    } else {
      error.value = '网络错误，请检查网络连接'
    }
    // 登录失败，跳转到首页
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.alert {
  margin-bottom: 1rem;
}
</style> 