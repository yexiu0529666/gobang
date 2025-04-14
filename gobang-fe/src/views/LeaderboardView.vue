<template>
  <div class="container mt-4">
    <h1 class="mb-4">积分排行榜</h1>
    
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
              <th scope="col">#</th>
              <th scope="col">用户名</th>
              <th scope="col" class="active-sort">
                积分
                <i class="bi bi-arrow-down"></i>
              </th>
              <th scope="col">胜场</th>
              <th scope="col">总场次</th>
              <th scope="col">胜率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(player, index) in leaderboard" :key="player.id">
              <th scope="row">{{ index + 1 }}</th>
              <td>{{ player.username }}</td>
              <td class="rating-cell">{{ player.rating }}</td>
              <td>{{ player.games_won }}</td>
              <td>{{ player.total_games }}</td>
              <td>{{ player.win_rate.toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="leaderboard.length === 0" class="text-center my-5">
        <p class="fs-5">暂无排行榜数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const leaderboard = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/leaderboard')
    leaderboard.value = response.data || []
    loading.value = false
  } catch (err) {
    console.error('Failed to fetch leaderboard:', err)
    error.value = '无法加载排行榜数据，请稍后再试'
    loading.value = false
  }
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

.active-sort {
  background-color: #1a1e21;
  position: relative;
}

.active-sort i {
  font-size: 0.8rem;
  margin-left: 5px;
}

.rating-cell {
  font-weight: bold;
  color: #0d6efd;
}
</style> 