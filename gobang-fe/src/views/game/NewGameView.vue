<template>
  <div class="container py-5">
    <div class="text-center mb-5">
      <h1 class="display-4">开始新游戏</h1>
      <p class="lead">开始一场五子棋对决！</p>
    </div>

    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow-sm mb-4">
          <div class="card-body p-4">
            <h3 class="card-title mb-4">开始游戏</h3>
            
            <div class="alert alert-info mb-4">
              <strong>提示：</strong> 点击"开始匹配"按钮开始匹配对手。
            </div>

            <div class="d-grid gap-2">
              <button @click="startMatchmaking" class="btn btn-primary btn-lg" :disabled="isLoading">
                开始匹配
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 匹配弹窗 -->
    <div class="modal fade" :class="{ 'show d-block': showMatchModal }" tabindex="-1" role="dialog" aria-hidden="true" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ matchFound ? '已找到对手！' : '正在匹配中...' }}
            </h5>
            <button type="button" class="btn-close" @click="cancelMatchmaking"></button>
          </div>
          <div class="modal-body text-center py-4">
            <div v-if="!matchFound">
              <div class="spinner-border text-primary mb-4" style="width: 4rem; height: 4rem;" role="status">
                <span class="visually-hidden">正在匹配...</span>
              </div>
              <h4 class="mt-3">寻找对手中...</h4>
              <p class="text-muted mb-0">请等待，或点击取消停止匹配</p>
              <p class="text-muted mt-3">已匹配时间：{{ Math.floor(matchingTime / 60) }}分 {{ matchingTime % 60 }}秒</p>
            </div>
            <div v-else>
              <div class="mb-4 text-success">
                <i class="bi bi-check-circle" style="font-size: 4rem;"></i>
              </div>
              <h4>匹配成功！</h4>
              <p class="mb-3">对手：<strong>{{ matchedPlayer }}</strong></p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelMatchmaking">
              {{ matchFound ? '取消' : '停止匹配' }}
            </button>
            <button v-if="matchFound" type="button" class="btn btn-primary" @click="enterGame">
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
.modal {
  transition: opacity 0.15s linear;
}
.modal.show {
  opacity: 1;
}
.bi-check-circle {
  color: #28a745;
}
</style> 