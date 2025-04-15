import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router'

// 创建 axios 实例
export const api = axios.create({
  baseURL: '/api'
})

// 添加响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 清除认证信息
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      
      // 获取当前路由路径
      const currentPath = window.location.hash.replace('#', '')
      
      // 如果不是登录页面和注册页面，才显示提示
      if (currentPath !== '/login' && currentPath !== '/register') {
        if (confirm('登录无效，请验证登录信息！')) {
          // 用户选择返回登录页
          router.push('/login')
        }
      } else {
        // 已经在登录页面，直接跳转
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    api  // 将 api 实例添加到 state 中
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  
  actions: {
    async initialize() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const response = await api.get('/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          this.token = token
          this.user = response.data
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        } catch (error) {
          localStorage.removeItem('token')
          delete api.defaults.headers.common['Authorization']
        }
      }
    },

    async login(username, password) {
      try {
        const response = await api.post('/auth/login', { username, password })
        if (response.data.error) {
          throw new Error(response.data.error)
        }
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    
    async register(data) {
      try {
        const response = await api.post('/auth/register', data)
        if (response.data.error) {
          throw new Error(response.data.error)
        }
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      }
    },
    
    async logout() {
      try {
        await api.post('/auth/logout', {}, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        this.token = null
        this.user = null
        localStorage.removeItem('token')
        delete api.defaults.headers.common['Authorization']
        return true
      } catch (error) {
        console.error('Logout failed:', error)
        return false
      }
    },
    
    async fetchUser() {
      if (this.token) {
        try {
          const response = await api.get('/auth/me')
          this.user = response.data
        } catch (error) {
          console.error('Failed to fetch user:', error)
          // 只有当响应状态为401时才清除认证信息
          if (error.response && error.response.status === 401) {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            delete api.defaults.headers.common['Authorization']
          }
        }
      }
    },

    async sendVerificationCode(email) {
      try {
        const response = await api.post('/auth/send-verification-code', { email })
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || '发送验证码失败')
      }
    }
  }
}) 