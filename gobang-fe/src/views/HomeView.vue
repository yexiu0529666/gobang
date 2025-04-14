<template>
  <div class="jumbotron">
    <h1 class="display-4">欢迎来到五子棋对战平台！</h1>
    <p class="lead">一个实时的在线五子棋游戏平台。</p>
    <hr class="my-4">
    <p>与其他玩家实时对战，与对手聊天，并登上排行榜！</p>
    <p>认证状态: {{ isAuthenticated ? '已登录' : '未登录' }}</p>
    <template v-if="isAuthenticated">
      <router-link class="btn btn-primary btn-lg" to="/new-game" role="button">开始新游戏</router-link>
    </template>
    <template v-else>
      <router-link class="btn btn-primary btn-lg" to="/login" role="button">登录游戏</router-link>
      <router-link class="btn btn-secondary btn-lg ms-2" to="/register" role="button">注册账号</router-link>
    </template>
  </div>

  <div class="row mt-4">
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">实时对战</h5>
          <p class="card-text">与其他玩家实时对战，即时更新落子位置。</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">排行榜</h5>
          <p class="card-text">与其他玩家竞争，登上排行榜展示你的实力。</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">游戏历史</h5>
          <p class="card-text">查看过去的对局记录，分析你的表现以提升策略。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(async () => {
  try {
    // 刷新用户信息，但不强制跳转
    await authStore.fetchUser()
  } catch (error) {
    console.error('Error fetching user data:', error)
    // 非401错误不处理，401错误会由拦截器处理
  }
  
  console.log('Auth state:', authStore.isAuthenticated)
  console.log('Current user:', authStore.currentUser)
})
</script> 