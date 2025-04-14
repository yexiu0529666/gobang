<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">五子棋</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">首页</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/leaderboard">排行榜</router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/replays">对局回放</router-link>
          </li>
        </ul>
        <ul class="navbar-nav">
          <template v-if="isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/profile">个人资料</router-link>
            </li>
            <li class="nav-item">
              <a class="nav-link" @click.prevent="logout">退出登录</a>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">登录</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">注册</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container mt-4">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const logout = async () => {
  const success = await authStore.logout()
  if (success) {
    router.push('/login')
  }
}
</script>

<style>
@import '@/assets/main.css';
</style>