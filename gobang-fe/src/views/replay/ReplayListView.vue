<template>
  <div class="container mt-4">
    <h1 class="mb-4">游戏回放记录</h1>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div v-else>
      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead class="table-dark">
            <tr>
              <th scope="col">对局ID</th>
              <th scope="col">黑方</th>
              <th scope="col">白方</th>
              <th scope="col">获胜方</th>
              <th scope="col">开始时间</th>
              <th scope="col">结束时间</th>
              <th scope="col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in replays" :key="game.id">
              <td>{{ game.id }}</td>
              <td>{{ game.black_player?.username || '未知' }}</td>
              <td>{{ game.white_player?.username || '未知' }}</td>
              <td>
                <span v-if="game.winner" :class="getWinnerClass(game)">
                  {{ game.winner.username }}
                </span>
                <span v-else class="text-secondary">平局</span>
              </td>
              <td>{{ formatDate(game.start_time) }}</td>
              <td>{{ game.end_time ? formatDate(game.end_time) : '进行中' }}</td>
              <td>
                <router-link :to="`/replay/${game.id}`" class="btn btn-primary btn-sm">
                  观看回放
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="replays.length === 0" class="text-center my-5">
        <p class="fs-5">暂无回放记录</p>
        <router-link to="/new-game" class="btn btn-primary mt-2">开始新游戏</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const replays = ref([])
const loading = ref(true)
const error = ref(null)

// 获取回放列表
const fetchReplays = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/replays')
    replays.value = response.data || []
    loading.value = false
  } catch (err) {
    console.error('Failed to fetch replays:', err)
    error.value = '无法加载回放数据，请稍后再试'
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 根据获胜方设置样式
const getWinnerClass = (game) => {
  const currentUserId = authStore.currentUser?.id
  if (game.winner && game.winner.id === currentUserId) {
    return 'text-success fw-bold'
  } else {
    return 'text-danger'
  }
}

onMounted(() => {
  fetchReplays()
})
</script>

<style scoped>
.table {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.table-dark th {
  border-color: #343a40;
}
</style> 