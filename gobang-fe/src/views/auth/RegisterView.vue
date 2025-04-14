<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">注册</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <input
                  type="text"
                  class="form-control"
                  id="username"
                  v-model="username"
                  :class="{ 'is-invalid': usernameError }"
                >
                <div class="invalid-feedback">{{ usernameError }}</div>
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">邮箱（可选）</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="email"
                  :class="{ 'is-invalid': emailError }"
                >
                <div class="invalid-feedback">{{ emailError }}</div>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="password"
                  :class="{ 'is-invalid': passwordError }"
                >
                <div class="invalid-feedback">{{ passwordError }}</div>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">确认密码</label>
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="confirmPassword"
                  :class="{ 'is-invalid': confirmPasswordError }"
                >
                <div class="invalid-feedback">{{ confirmPasswordError }}</div>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  注册
                </button>
              </div>
            </form>
            <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 注册成功弹窗 -->
    <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="successModalLabel">注册成功</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            恭喜您注册成功！即将跳转到登录页面...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Modal } from 'bootstrap'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const usernameError = ref('')
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const clearErrors = () => {
  error.value = ''
  usernameError.value = ''
  emailError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''
}

const handleSubmit = async () => {
  clearErrors()
  
  if (!username.value) {
    usernameError.value = '请输入用户名'
    return
  }
  if (!password.value) {
    passwordError.value = '请输入密码'
    return
  }
  if (!confirmPassword.value) {
    confirmPasswordError.value = '请确认密码'
    return
  }
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  try {
    const success = await authStore.register(username.value, email.value, password.value)
    if (success) {
      // 显示成功弹窗
      const successModal = new Modal(document.getElementById('successModal'))
      successModal.show()
      
      // 3秒后跳转到登录页面
      setTimeout(() => {
        successModal.hide()
        router.push('/login')
      }, 500)
    }
  } catch (err) {
    if (err.response) {
      const { data } = err.response
      if (data.error) {
        error.value = data.error === 'Username already exists' ? '用户名已存在' : 
                     data.error === 'Email already exists' ? '邮箱已被使用' : 
                     data.error
      } else if (data.message) {
        error.value = data.message
      } else {
        error.value = '注册失败，请稍后重试'
      }
    } else {
      error.value = '网络错误，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}
</script> 