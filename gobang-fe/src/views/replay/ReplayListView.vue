<template>
  <div class="replay-container">
    <div class="replay-header">
      <h1 class="replay-title">对局回放</h1>
      <p class="replay-subtitle">回顾精彩棋局，学习对弈技巧</p>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>正在加载回放数据...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="replay-content">
      <div class="filter-bar">
        <div class="filter-options">
          <button :class="['filter-btn', { active: filterType === 'all' }]" @click="setFilter('all')">全部</button>
          <button :class="['filter-btn', { active: filterType === 'win' }]" @click="setFilter('win')">我的胜局</button>
          <button :class="['filter-btn', { active: filterType === 'loss' }]" @click="setFilter('loss')">我的败局</button>
        </div>
      </div>
      
      <div class="replay-grid" v-if="filteredReplays.length > 0">
        <div v-for="game in filteredReplays" :key="game.id" class="replay-card">
          <div class="replay-card-header">
            <div class="game-id"><i class="fas fa-hashtag"></i> {{ game.id }}</div>
            <div class="game-result" :class="getResultClass(game)">{{ getResultText(game) }}</div>
          </div>
          
          <div class="replay-card-body">
            <div class="players-info">
              <div class="player black-player">
                <div class="stone stone-black"></div>
                <span class="player-name">{{ game.black_player?.username || '未知' }}</span>
              </div>
              <div class="vs-badge">VS</div>
              <div class="player white-player">
                <div class="stone stone-white"></div>
                <span class="player-name">{{ game.white_player?.username || '未知' }}</span>
              </div>
            </div>
            
            <div class="game-details">
              <div class="detail-item">
                <i class="fas fa-calendar"></i>
                <span>{{ formatDate(game.start_time, 'date') }}</span>
              </div>
              <div class="detail-item">
                <i class="fas fa-clock"></i>
                <span>{{ formatDate(game.start_time, 'time') }}</span>
              </div>
              <div class="detail-item" :class="{ 'in-progress': !game.end_time }">
                <i class="fas fa-hourglass-end"></i>
                <span>{{ game.end_time ? getDuration(game.start_time, game.end_time) : '进行中' }}</span>
              </div>
            </div>
          </div>
          
          <div class="replay-card-footer">
            <router-link :to="`/replay/${game.id}`" class="watch-btn">
              <i class="fas fa-play-circle"></i> 观看回放
            </router-link>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <i class="fas fa-film"></i>
        <p>暂无回放记录</p>
        <p class="empty-subtitle">{{ getEmptyStateMessage() }}</p>
        <router-link to="/new-game" class="start-game-btn">
          <i class="fas fa-gamepad"></i> 开始新游戏
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const replays = ref([])
const filteredReplays = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const filterType = ref('all')

// 获取回放列表
const fetchReplays = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/replays')
    replays.value = response.data || []
    filteredReplays.value = [...replays.value]
    loading.value = false
  } catch (err) {
    console.error('Failed to fetch replays:', err)
    error.value = '无法加载回放数据，请稍后再试'
    loading.value = false
  }
}

// 根据筛选条件过滤对局
const filterReplays = () => {
  const query = searchQuery.value.toLowerCase().trim()
  let filtered = [...replays.value]
  
  // 应用搜索查询
  if (query) {
    filtered = filtered.filter(game => 
      (game.black_player?.username?.toLowerCase().includes(query)) || 
      (game.white_player?.username?.toLowerCase().includes(query)) ||
      game.id.toString().includes(query)
    )
  }
  
  // 应用类型过滤
  const currentUserId = authStore.currentUser?.id
  if (filterType.value === 'win' && currentUserId) {
    filtered = filtered.filter(game => 
      game.winner && game.winner.id === currentUserId
    )
  } else if (filterType.value === 'loss' && currentUserId) {
    filtered = filtered.filter(game => 
      game.winner && game.winner.id !== currentUserId && 
      (game.black_player?.id === currentUserId || game.white_player?.id === currentUserId)
    )
  }
  
  filteredReplays.value = filtered
}

const setFilter = (type) => {
  filterType.value = type
  filterReplays()
}

// 格式化日期
const formatDate = (dateString, format = 'datetime') => {
  if (!dateString) return '未知'
  
  const date = new Date(dateString)
  
  if (format === 'date') {
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
  } else if (format === 'time') {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else {
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
}

// 计算游戏时长
const getDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return '未知'
  
  const start = new Date(startTime)
  const end = new Date(endTime)
  const durationMs = end - start
  
  const minutes = Math.floor(durationMs / (1000 * 60))
  const seconds = Math.floor((durationMs % (1000 * 60)) / 1000)
  
  return `${minutes}分${seconds}秒`
}

// 获取结果文本
const getResultText = (game) => {
  const currentUserId = authStore.currentUser?.id
  
  if (!game.winner) {
    return '平局'
  }
  
  if (currentUserId && game.winner.id === currentUserId) {
    return '你赢了'
  } else if (currentUserId && (game.black_player?.id === currentUserId || game.white_player?.id === currentUserId)) {
    return '你输了'
  } else {
    return `${game.winner.username} 胜`
  }
}

// 获取结果样式类
const getResultClass = (game) => {
  const currentUserId = authStore.currentUser?.id
  
  if (!game.winner) {
    return 'result-draw'
  }
  
  if (currentUserId && game.winner.id === currentUserId) {
    return 'result-win'
  } else if (currentUserId && (game.black_player?.id === currentUserId || game.white_player?.id === currentUserId)) {
    return 'result-loss'
  } else {
    return 'result-other'
  }
}

// 获取空状态消息
const getEmptyStateMessage = () => {
  if (filterType.value !== 'all' || searchQuery.value) {
    return '没有找到符合条件的对局记录，请尝试其他筛选条件'
  } else {
    return '快来开始你的第一场比赛吧！'
  }
}

onMounted(() => {
  fetchReplays()
})
</script>

<style scoped>
/* 基础样式 */
.replay-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  color: #2c3e50;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.replay-header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out;
}

.replay-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #3498db;
}

.replay-subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.replay-content {
  animation: slideUp 0.6s ease-out;
}

/* 筛选栏 */
.filter-bar {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-box {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.search-box input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.5rem;
  border: none;
  border-radius: 100px;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-size: 0.9rem;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  box-shadow: 0 2px 12px rgba(52, 152, 219, 0.2);
}

.filter-options {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 100px;
  background-color: rgba(255, 255, 255, 0.9);
  color: #7f8c8d;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.filter-btn.active {
  background-color: #3498db;
  color: white;
}

/* 对局卡片网格 */
.replay-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.replay-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
}

.replay-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.replay-card-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.game-id {
  font-size: 0.9rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.game-result {
  font-weight: 600;
  padding: 0.3rem 0.8rem;
  border-radius: 100px;
  font-size: 0.8rem;
}

.result-win {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.result-loss {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.result-draw {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.result-other {
  background-color: rgba(52, 73, 94, 0.1);
  color: #34495e;
}

.replay-card-body {
  padding: 1.5rem;
}

.players-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.player {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex: 1;
}

.black-player {
  justify-content: flex-start;
}

.white-player {
  justify-content: flex-end;
}

.stone {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.stone-black {
  background: radial-gradient(circle at 30% 30%, #666, #000);
}

.stone-white {
  background: radial-gradient(circle at 30% 30%, #fff, #ddd);
  border: 1px solid #ddd;
}

.player-name {
  font-weight: 500;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

.vs-badge {
  background-color: rgba(243, 156, 18, 0.1);
  color: #f39c12;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 0.3rem 0.6rem;
  border-radius: 100px;
}

.game-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  margin-top: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.detail-item i {
  color: #3498db;
}

.in-progress {
  color: #e67e22;
}

.in-progress i {
  color: #e67e22;
}

.replay-card-footer {
  padding: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  text-align: center;
}

.watch-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  padding: 0.7rem 1.5rem;
  border-radius: 100px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.watch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 5rem 1rem;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 1.5rem;
}

.empty-state p {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 1rem;
  color: #95a5a6;
  margin-bottom: 2rem;
}

.start-game-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  padding: 0.8rem 2rem;
  border-radius: 100px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.start-game-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 3rem 1rem;
}

.spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 5px solid rgba(189, 195, 199, 0.3);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

/* 错误状态 */
.error-message {
  background-color: rgba(231, 76, 60, 0.05);
  border-left: 4px solid #e74c3c;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin: 2rem 0;
  display: flex;
  align-items: center;
  color: #e74c3c;
}

.error-message i {
  font-size: 2rem;
  margin-right: 1rem;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .replay-title {
    font-size: 2rem;
  }
  
  .replay-subtitle {
    font-size: 1rem;
  }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .filter-options {
    justify-content: center;
  }
  
  .replay-grid {
    grid-template-columns: 1fr;
  }
  
  .player-name {
    max-width: 80px;
  }
}
</style> 