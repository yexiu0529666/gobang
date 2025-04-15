<template>
  <!-- 全局粒子背景 -->
  <ParticlesBackground />
  
  <!-- 导航栏和内容 -->
  <div class="app-container">
    <nav class="navbar navbar-expand-lg">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-grid-3x3-gap-fill me-2"></i>
          五子棋对战平台
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-house-door me-1"></i>
                首页
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/leaderboard">
                <i class="bi bi-trophy me-1"></i>
                排行榜
              </router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/replays">
                <i class="bi bi-play-circle me-1"></i>
                对局回放
              </router-link>
            </li>
          </ul>
          <div class="d-flex align-items-center">
            <template v-if="isAuthenticated">
              <div class="dropdown">
                <button
                  class="btn btn-link nav-link dropdown-toggle d-flex align-items-center"
                  type="button"
                  id="userDropdown"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <i class="bi bi-person-circle me-2"></i>
                  {{ authStore.user?.username }}
                  <span class="badge bg-primary ms-2">{{ authStore.user?.points }}分</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                  <li>
                    <router-link class="dropdown-item" to="/profile">
                      <i class="bi bi-person me-2"></i>
                      个人资料
                    </router-link>
                  </li>
                  <li>
                    <router-link class="dropdown-item" to="/new-game">
                      <i class="bi bi-controller me-2"></i>
                      开始游戏
                    </router-link>
                  </li>
                  <li><hr class="dropdown-divider" /></li>
                  <li>
                    <a class="dropdown-item text-danger" href="#" @click.prevent="logout">
                      <i class="bi bi-box-arrow-right me-2"></i>
                      退出登录
                    </a>
                  </li>
                </ul>
              </div>
            </template>
            <template v-else>
              <router-link class="btn btn-outline-primary me-2" to="/login">
                <i class="bi bi-box-arrow-in-right me-1"></i>
                登录
              </router-link>
              <router-link class="btn btn-primary" to="/register">
                <i class="bi bi-person-plus me-1"></i>
                注册
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <div class="container mt-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import ParticlesBackground from '@/components/ParticlesBackground.vue'
import { onMounted } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const logout = async () => {
  const success = await authStore.logout()
  if (success) {
    router.push('/login')
  }
}

// 加载Bootstrap Icons
function loadBootstrapIcons() {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css'
  document.head.appendChild(link)
}

onMounted(() => {
  loadBootstrapIcons()
})
</script>

<style>
@import '@/assets/main.css';

body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.app-container {
  position: relative;
  z-index: 1;
}

.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.navbar-brand {
  font-weight: 600;
  color: #4a5568;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.navbar-brand:hover {
  color: #667eea;
  transform: translateY(-1px);
}

.nav-link {
  color: #4a5568;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.nav-link i {
  font-size: 1.1rem;
}

.btn-outline-primary {
  border-color: #667eea;
  color: #667eea;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background-color: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.dropdown-menu {
  border: none;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.dropdown-item {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.dropdown-item i {
  font-size: 1.1rem;
  margin-right: 0.5rem;
}

.dropdown-divider {
  margin: 0.5rem 0;
  opacity: 0.1;
}

.badge {
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

@media (max-width: 991.98px) {
  .navbar-collapse {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    margin-top: 1rem;
  }

  .nav-link {
    padding: 0.75rem 1rem;
  }

  .btn {
    width: 100%;
    margin: 0.5rem 0;
  }
}
</style>