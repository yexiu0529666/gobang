<template>
  <div class="new-game-container">
    <div class="text-center mb-5">
      <h1 class="display-4 fw-bold text-gradient">开始新游戏</h1>
      <p class="lead text-muted">开始一场精彩的对决！</p>
    </div>

    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="game-card">
          <div class="card-body p-4">
            <div class="d-flex align-items-center mb-4">
              <i class="bi bi-controller me-3 text-primary" style="font-size: 2rem;"></i>
              <h3 class="card-title mb-0">开始游戏</h3>
            </div>
            
            <div class="info-box mb-4">
              <i class="bi bi-info-circle me-2"></i>
              <span>点击"开始匹配"按钮开始匹配对手，系统会自动为您寻找合适的对手。</span>
            </div>

            <div class="d-grid gap-2">
              <button 
                @click="startMatchmaking" 
                class="btn btn-primary btn-lg start-btn" 
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                <span v-else><i class="bi bi-play-fill me-2"></i></span>
                开始匹配
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="error" class="error-box">
          <i class="bi bi-exclamation-circle me-2"></i>
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 匹配弹窗 -->
    <div class="modal fade" :class="{ 'show d-block': showMatchModal }" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi" :class="matchFound ? 'bi-check-circle-fill text-success' : 'bi-hourglass-split text-primary'"></i>
              {{ matchFound ? '已找到对手！' : '正在匹配中...' }}
            </h5>
            <button type="button" class="btn-close" @click="cancelMatchmaking"></button>
          </div>
          <div class="modal-body text-center py-4">
            <div v-if="!matchFound">
              <div class="matching-animation mb-4">
                <div class="spinner-border text-primary" style="width: 4rem; height: 4rem;" role="status">
                  <span class="visually-hidden">正在匹配...</span>
                </div>
              </div>
              <h4 class="mt-3">寻找对手中...</h4>
              <p class="text-muted mb-0">请等待，或点击取消停止匹配</p>
              <div class="matching-time mt-3">
                <i class="bi bi-clock me-2"></i>
                {{ Math.floor(matchingTime / 60) }}分 {{ matchingTime % 60 }}秒
              </div>
            </div>
            <div v-else class="match-found">
              <div class="success-icon mb-4">
                <i class="bi bi-check-circle-fill"></i>
              </div>
              <h4>匹配成功！</h4>
              <div class="opponent-info mt-3">
                <i class="bi bi-person-circle me-2"></i>
                <span class="opponent-name">{{ matchedPlayer }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelMatchmaking">
              <i class="bi bi-x-circle me-2"></i>
              {{ matchFound ? '取消' : '停止匹配' }}
            </button>
            <button v-if="matchFound" type="button" class="btn btn-primary" @click="enterGame">
              <i class="bi bi-play-fill me-2"></i>
              进入游戏
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

// 状态变量
const isLoading = ref(false)
const error = ref(null)
const showMatchModal = ref(false)
const matchFound = ref(false)
const matchedPlayer = ref('')
const matchId = ref(null)
const gameId = ref(null)
const matchingTime = ref(0)
let matchTimer = null

// 开始匹配
async function startMatchmaking() {
  if (isLoading.value) return
  
  try {
    isLoading.value = true
    error.value = null
    
    // 首先检查是否有可用匹配
    const checkResponse = await axios.get('/api/matches/check')
    
    if (checkResponse.data.status === 'match_found') {
      // 找到匹配，加入游戏
      matchId.value = checkResponse.data.match_id
      matchedPlayer.value = checkResponse.data.player1_username
      await joinMatch(matchId.value)
    } else {
      // 没有找到匹配，创建一个新的
      const createResponse = await axios.post('/api/matches/create')
      
      if (createResponse.data.status === 'success') {
        matchId.value = createResponse.data.match_id
        gameId.value = createResponse.data.game_id
        
        // 显示匹配弹窗
        showMatchModal.value = true
        matchFound.value = false
        
        // 开始计时
        matchingTime.value = 0
        matchTimer = setInterval(() => {
          matchingTime.value++
          
          // 每5秒检查一次是否已有玩家加入
          if (matchingTime.value % 1 === 0) {
            checkMatchStatus()
          }
        }, 1000)
      } else {
        error.value = '创建匹配失败，请重试'
      }
    }
  } catch (err) {
    console.error('Failed to start matchmaking:', err)
    error.value = '匹配失败：' + (err.response?.data?.message || err.message || '未知错误')
  } finally {
    isLoading.value = false
  }
}

// 检查匹配状态
async function checkMatchStatus() {
  if (!matchId.value) return
  
  try {
    const response = await axios.get(`/api/matches/${matchId.value}`)
    
    if (response.data.status === 'closed' && response.data.player2_id) {
      // 有玩家加入，匹配成功
      matchFound.value = true
      matchedPlayer.value = response.data.player2_username
      gameId.value = response.data.game_id
      
      // 停止计时
      clearInterval(matchTimer)
    }
  } catch (err) {
    console.error('Failed to check match status:', err)
  }
}

// 取消匹配
async function cancelMatchmaking() {
  if (!showMatchModal.value) return
  
  try {
    if (matchId.value) {
      await axios.post(`/api/matches/cancel/${matchId.value}`)
    }
  } catch (err) {
    console.error('Failed to cancel match:', err)
  } finally {
    // 关闭弹窗，重置状态
    showMatchModal.value = false
    matchFound.value = false
    matchId.value = null
    matchedPlayer.value = ''
    clearInterval(matchTimer)
  }
}

// 加入匹配
async function joinMatch(matchId) {
  try {
    const response = await axios.post(`/api/matches/join/${matchId}`)
    
    if (response.data.status === 'success') {
      gameId.value = response.data.game_id
      
      // 显示匹配成功弹窗
      showMatchModal.value = true
      matchFound.value = true
    } else {
      error.value = '加入游戏失败：' + (response.data.message || '未知错误')
    }
  } catch (err) {
    console.error('Failed to join match:', err)
    error.value = '加入游戏失败：' + (err.response?.data?.message || err.message || '未知错误')
  }
}

// 进入游戏
function enterGame() {
  if (gameId.value) {
    router.push(`/game/${gameId.value}`)
  }
}

// 组件卸载前清理
onBeforeUnmount(() => {
  if (matchTimer) {
    clearInterval(matchTimer)
  }
  
  // 如果还在匹配中，取消匹配
  if (showMatchModal.value && !matchFound.value) {
    cancelMatchmaking()
  }
})
</script>

<style scoped>
.new-game-container {
  padding: 2rem 0;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.text-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.game-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: none;
  transition: transform 0.3s ease;
}

.game-card:hover {
  transform: translateY(-5px);
}

.info-box {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
  color: #4a5568;
  display: flex;
  align-items: center;
}

.start-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.start-btn:disabled {
  opacity: 0.7;
}

.error-box {
  background: rgba(220, 53, 69, 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
  color: #dc3545;
  margin-top: 1rem;
  display: flex;
  align-items: center;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
  transition: opacity 0.3s ease;
}

.modal-content {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  border: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.modal-body {
  padding: 2rem;
}

.modal-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.matching-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.match-found {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon {
  color: #28a745;
  font-size: 4rem;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.opponent-info {
  background: rgba(102, 126, 234, 0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  display: inline-flex;
  align-items: center;
}

.opponent-name {
  font-weight: 500;
  color: #4a5568;
}

.matching-time {
  background: rgba(102, 126, 234, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  display: inline-flex;
  align-items: center;
  font-weight: 500;
}

.btn-close {
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.btn-close:hover {
  opacity: 1;
}

@media (max-width: 768px) {
  .new-game-container {
    padding: 1rem;
  }
  
  .game-card {
    margin: 0 -1rem;
    border-radius: 0;
  }
}
</style> 