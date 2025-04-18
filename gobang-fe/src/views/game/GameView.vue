<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="mt-3">正在加载游戏...</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div v-else class="row">
      <!-- 游戏面板 -->
      <div class="col-md-8">
        <div class="card shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center py-3">
            <div>
              <h4 class="mb-0">五子棋对战</h4>
              <div class="text-muted small" v-if="game">游戏ID: {{ gameId }}</div>
            </div>
            <div class="status-badge" :class="getStatusClass()">
              {{ getStatusText() }}
            </div>
          </div>
          <div class="card-body p-0">
            <div class="game-board">
              <!-- 这里是棋盘 -->
              <div class="board-container">
                <div class="board" ref="boardRef">
                  <!-- 背景网格线 -->
                  <div class="board-grid">
                    <!-- 水平线 -->
                    <div v-for="i in 15" :key="`h-${i}`" class="grid-line horizontal" :style="{ top: `${(i-1) * 100 / 14}%` }"></div>
                    <!-- 垂直线 -->
                    <div v-for="i in 15" :key="`v-${i}`" class="grid-line vertical" :style="{ left: `${(i-1) * 100 / 14}%` }"></div>
                    
                    <!-- 标记点（天元和四星） -->
                    <div class="mark-point" style="top: calc(7 * 100% / 14); left: calc(7 * 100% / 14)"></div>
                    <div class="mark-point" style="top: calc(3 * 100% / 14); left: calc(3 * 100% / 14)"></div>
                    <div class="mark-point" style="top: calc(3 * 100% / 14); left: calc(11 * 100% / 14)"></div>
                    <div class="mark-point" style="top: calc(11 * 100% / 14); left: calc(3 * 100% / 14)"></div>
                    <div class="mark-point" style="top: calc(11 * 100% / 14); left: calc(11 * 100% / 14)"></div>
                  </div>
                  
                  <!-- 棋子和交点 -->
                  <div v-for="i in 15" :key="`row-${i}`" class="board-row">
                    <div v-for="j in 15" :key="`point-${i}-${j}`" 
                         class="board-point"
                         :style="{ top: `${(i-1) * 100 / 14}%`, left: `${(j-1) * 100 / 14}%` }"
                         @click="makeMove(i-1, j-1)">
                      <!-- 棋子 -->
                      <div v-if="getStone(i-1, j-1)" 
                           class="stone" 
                           :class="getStone(i-1, j-1) === 1 ? 'stone-black' : 'stone-white'">
                           <!-- 最后一步标记 -->
                           <div v-if="isLastMove(i-1, j-1)" class="last-move-mark"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 游戏信息面板 -->
      <div class="col-md-4">
        <div class="card shadow-sm mb-4">
          <div class="card-header py-3">
            <h5 class="mb-0">对战信息</h5>
          </div>
          <div class="card-body">
            <div v-if="game" class="player-info">
              <div class="player mb-3">
                <div class="stone-icon stone-black"></div>
                <div class="player-details">
                  <div class="player-name">{{ getPlayer1Name() }}</div>
                  <div class="player-status" v-if="game.current_player_id === game.player1_id">
                    <span class="badge bg-success">轮到此玩家</span>
                  </div>
                </div>
              </div>
              
              <div class="player mb-3">
                <div class="stone-icon stone-white"></div>
                <div class="player-details">
                  <div class="player-name">{{ getPlayer2Name() }}</div>
                  <div class="player-status" v-if="game.current_player_id === game.player2_id">
                    <span class="badge bg-success">轮到此玩家</span>
                  </div>
                </div>
              </div>
              
              <hr>
              
              <div class="game-stats mb-3">
                <div class="stat-item">
                  <span class="stat-label">已下子数：</span>
                  <span class="stat-value">{{ moves.length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">游戏状态：</span>
                  <span class="stat-value">{{ getStatusText() }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">剩余时间：</span>
                  <span class="stat-value" :class="{'text-danger': remainingTime <= 30}">{{ formatTime(remainingTime) }}</span>
                </div>
              </div>
              
              <div v-if="isMyTurn" class="alert alert-info">
                轮到你下棋了！
              </div>
              
              <div v-if="game.status === 'finished'" class="alert alert-success">
                <strong>游戏结束！</strong> 
                <div v-if="game.winner_id">
                  获胜者: {{ game.winner_id === game.player1_id ? getPlayer1Name() : getPlayer2Name() }}
                </div>
                <div v-else>
                  游戏平局！
                </div>
              </div>
              
              <!-- 退出游戏按钮 -->
              <div class="mt-3">
                <button @click="confirmExitGame" class="btn btn-danger w-100">
                  退出游戏
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 获取当前用户
const currentUser = computed(() => authStore.user || {})

// 游戏状态
const gameId = computed(() => route.params.id)
const game = ref(null)
const moves = ref([])
const loading = ref(true)
const error = ref(null)
const isMyTurn = ref(false)
const lastMove = ref(null)
const remainingTime = ref(1800) // 默认30分钟
let timerInterval = null
let gameCheckInterval = null // 轮询游戏状态的定时器

// 心跳间隔（毫秒）
const HEARTBEAT_INTERVAL = 20 * 1000; // 20秒
let heartbeatInterval = null;

// 获取玩家名称
const getPlayer1Name = () => {
  if (!game.value) return 'Player 1'
  return game.value.player1_id === currentUser.value.id ? '你 (黑棋)' : game.value.player1_username + ' (黑棋)'
}

const getPlayer2Name = () => {
  if (!game.value || !game.value.player2_id) return '等待玩家加入...'
  return game.value.player2_id === currentUser.value.id ? '你 (白棋)' : game.value.player2_username + ' (白棋)'
}

// 获取游戏状态
const getStatusText = () => {
  if (!game.value) return '未知'
  
  switch (game.value.status) {
    case 'waiting': return '等待对手加入'
    case 'playing': return '游戏进行中'
    case 'finished': return '游戏结束'
    case 'abandoned': return '游戏已放弃'
    default: return '未知状态'
  }
}

// 获取状态样式
const getStatusClass = () => {
  if (!game.value) return 'status-unknown'
  
  switch (game.value.status) {
    case 'waiting': return 'status-waiting'
    case 'playing': return 'status-playing'
    case 'finished': return 'status-finished'
    case 'abandoned': return 'status-abandoned'
    default: return 'status-unknown'
  }
}

// 获取棋子状态
const getStone = (x, y) => {
  if (!moves.value) return null
  const move = moves.value.find(m => m.x === x && m.y === y)
  return move ? move.player_id === game.value.player1_id ? 1 : 2 : null
}

// 检查是否是最后一步
const isLastMove = (x, y) => {
  if (!lastMove.value) return false
  return lastMove.value.x === x && lastMove.value.y === y
}

// 下棋
const makeMove = async (x, y) => {
  if (!isMyTurn.value || !game.value || game.value.status !== 'playing') return
  if (getStone(x, y)) return // 已有棋子的位置不能下
  
  try {
    const response = await axios.post(`/api/games/${gameId.value}/move`, {
      x: x,
      y: y
    })
    
    if (response.data && response.data.status === 'success') {
      // 如果游戏结束
      if (response.data.game_over) {
        // 更新游戏状态
        //if (response.data.draw) {
          //  alert(`游戏结束，双方平局！`)
        //} else {
          //const isWinner = response.data.winner_id === currentUser.value.id
          //alert(`游戏结束，${isWinner ? '你赢了！' : '你输了。'}\n积分变更: ${response.data.points_change > 0 ? '+' + response.data.points_change : response.data.points_change}`)
        //}

        return
      }
      
      // 落子成功，立即获取最新游戏状态
      await fetchGame()
    } else {
      error.value = response.data?.message || '下棋失败，请重试'
    }
  } catch (err) {
    console.error('Failed to make move:', err)
    
    // 检查是否是"不是您的回合"错误
    const errorMessage = err.response?.data?.message || err.message || '未知错误'
    if (errorMessage.includes('不是您的回合')) {
      // 只显示弹窗提示，不更新error.value
      alert('请不要连击哦~')
    } else if (errorMessage.includes('违反三三禁手')) {
      // 显示三三禁手违规提示
      alert('违反三三禁手规则！')
    } else {
      // 其他错误更新error.value
      error.value = '下棋失败：' + errorMessage
    }
  }
}

// 格式化倒计时
const formatTime = (seconds) => {
  if (typeof seconds !== 'number') return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 退出游戏确认
const confirmExitGame = () => {
  if (confirm('确定要退出游戏吗？如果游戏正在进行中，退出将视为认输并扣除10积分。')) {
    exitGame()
  }
}

// 退出游戏
const exitGame = async () => {
  try {
    const response = await axios.post(`/api/games/${gameId.value}/exit`)
    
    if (response.data && response.data.status === 'success') {
      // 如果有积分变更，显示提示
      if (response.data.points_change) {
        alert(`游戏已结束。您的积分变更: ${response.data.points_change > 0 ? '+' + response.data.points_change : response.data.points_change}`)
      }
      // 退出成功，返回首页
      router.push('/')
    } else {
      error.value = response.data?.message || '退出游戏失败，请重试'
    }
  } catch (err) {
    console.error('Failed to exit game:', err)
    error.value = '退出游戏失败：' + (err.response?.data?.message || err.message || '未知错误')
  }
}

// 更新倒计时
const updateTimer = () => {
  if (remainingTime.value > 0 && game.value && game.value.status === 'playing') {
    remainingTime.value--
    
    // 如果时间到了，自动认输
    if (remainingTime.value === 0) {
      exitGame()
    }
  }
}

// 重置倒计时
const resetTimer = () => {
  if (game.value && game.value.time_limit) {
    remainingTime.value = game.value.time_limit
  } else {
    remainingTime.value = 1800 // 默认30分钟
  }
}

// 获取游戏数据
const fetchGame = async () => {
  try {
    const response = await axios.get(`/api/games/${gameId.value}`)
    
    if (response.data) {
      const oldStatus = game.value?.status
      
      // 更新游戏数据
      game.value = response.data
      moves.value = response.data.moves || []
      
      if (moves.value.length > 0) {
        lastMove.value = moves.value[moves.value.length - 1]
      }
      
      // 检查是否轮到当前用户
      if (game.value.status === 'playing') {
        isMyTurn.value = game.value.current_player_id === currentUser.value.id
      }
      
      // 如果游戏状态从其他状态变为playing，初始化计时器
      if (oldStatus !== 'playing' && game.value.status === 'playing') {
        // 设置倒计时
        if (game.value.time_limit) {
          remainingTime.value = game.value.time_limit
        }
        
        // 启动倒计时
        if (!timerInterval) {
          timerInterval = setInterval(updateTimer, 1000)
        }
      }
      
      // 如果游戏状态变为结束或放弃，处理结束逻辑
      if ((oldStatus === 'playing') && 
          (game.value.status === 'finished' || game.value.status === 'abandoned')) {
        handleGameOver()
      }
    }
    
    if (loading.value) {
      loading.value = false
    }
  } catch (err) {
    console.error('Failed to fetch game:', err)
    if (loading.value) {
      error.value = '获取游戏数据失败：' + (err.response?.data?.message || err.message || '未知错误')
      loading.value = false
    }
  }
}

// 处理游戏结束
const handleGameOver = () => {
  // 清除倒计时
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  // 确保游戏已结束
  if (game.value.status !== 'finished' && game.value.status !== 'abandoned') {
    return // 如果游戏未结束，不显示胜利/失败信息
  }
  
  // 清理可能存在的旧消息
  const existingResultContainer = document.getElementById('game-result-container');
  if (existingResultContainer) {
    existingResultContainer.remove();
  }
  
  if (!game.value.winner_id) {
    return; // 如果没有胜利者（平局或其他情况），不显示胜利/失败信息
  }
  
  // 判断胜负
  const isWinner = game.value.winner_id === currentUser.value.id;
  
  // 创建结果容器
  const resultContainer = document.createElement('div');
  resultContainer.id = 'game-result-container';
  resultContainer.style.position = 'fixed';
  resultContainer.style.top = '0';
  resultContainer.style.left = '0';
  resultContainer.style.width = '100%';
  resultContainer.style.height = '100%';
  resultContainer.style.display = 'flex';
  resultContainer.style.flexDirection = 'column';
  resultContainer.style.justifyContent = 'center';
  resultContainer.style.alignItems = 'center';
  resultContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
  resultContainer.style.zIndex = '9999';
  resultContainer.style.opacity = '0';
  resultContainer.style.transition = 'opacity 0.5s ease';
  
  // 创建结果标题
  const resultTitle = document.createElement('div');
  
  if (isWinner) {
    resultTitle.textContent = '胜利!';
    resultTitle.style.color = '#4CAF50';
    resultTitle.style.textShadow = '0 0 10px rgba(76, 175, 80, 0.7)';
  } else {
    resultTitle.textContent = '失败!';
    resultTitle.style.color = '#F44336';
    resultTitle.style.textShadow = '0 0 10px rgba(244, 67, 54, 0.7)';
  }
  
  resultTitle.style.fontSize = '72px';
  resultTitle.style.fontWeight = 'bold';
  resultTitle.style.marginBottom = '20px';
  resultTitle.style.transform = 'scale(0.1)';
  resultTitle.style.transition = 'transform 0.5s ease';
  
  // 创建结果消息
  const resultMessage = document.createElement('div');
  resultMessage.style.color = '#FFFFFF';
  resultMessage.style.fontSize = '24px';
  resultMessage.style.marginBottom = '30px';
  resultMessage.style.textAlign = 'center';
  resultMessage.style.opacity = '0';
  resultMessage.style.transition = 'opacity 0.5s ease 0.3s';
  
  // 添加积分提示
  let pointsMessage = '';
  if (game.value.status === 'abandoned') {
    if (game.value.points_change) {
      pointsMessage = `积分变更: ${game.value.points_change > 0 ? '+' + game.value.points_change : game.value.points_change}`;
    }
  } else {
    if (isWinner) {
      pointsMessage = '你获得了+10积分！';
    } else {
      pointsMessage = '你失去了10积分。';
    }
  }
  
  const winnerName = isWinner 
    ? '你' 
    : (game.value.winner_id === game.value.player1_id 
       ? game.value.player1_username 
       : game.value.player2_username);
  
  resultMessage.innerHTML = `${winnerName}获胜！<br>${pointsMessage}`;
  
  // 创建倒计时元素
  const countdownElement = document.createElement('div');
  countdownElement.style.color = '#FFFFFF';
  countdownElement.style.fontSize = '18px';
  countdownElement.style.marginTop = '20px';
  countdownElement.style.padding = '10px 20px';
  countdownElement.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
  countdownElement.style.borderRadius = '20px';
  countdownElement.style.opacity = '0';
  countdownElement.style.transition = 'opacity 0.5s ease 0.6s';
  
  // 添加元素到容器
  resultContainer.appendChild(resultTitle);
  resultContainer.appendChild(resultMessage);
  resultContainer.appendChild(countdownElement);
  document.body.appendChild(resultContainer);
  
  // 触发动画
  setTimeout(() => {
    resultContainer.style.opacity = '1';
    resultTitle.style.transform = 'scale(1)';
    
    setTimeout(() => {
      resultMessage.style.opacity = '1';
      
      setTimeout(() => {
        countdownElement.style.opacity = '1';
        
        // 倒计时
        let countdown = 5;
        countdownElement.textContent = `${countdown}秒后返回主页`;
        
        const countdownInterval = setInterval(() => {
          countdown--;
          countdownElement.textContent = `${countdown}秒后返回主页`;
          
          if (countdown <= 0) {
            clearInterval(countdownInterval);
            
            // 淡出动画
            resultContainer.style.opacity = '0';
            
            setTimeout(() => {
              resultContainer.remove();
              router.push('/');
            }, 500);
          }
        }, 1000);
      }, 300);
    }, 300);
  }, 100);
}

// 清除所有定时器
const clearAllIntervals = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  if (gameCheckInterval) {
    clearInterval(gameCheckInterval)
    gameCheckInterval = null
  }
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}

// 发送心跳
const sendHeartbeat = async () => {
  if (!game.value || game.value.status !== 'playing') return;
  
  try {
    await axios.post(`/api/games/${gameId.value}/heartbeat`);
  } catch (err) {
    console.error('Failed to send heartbeat:', err);
  }
};

onMounted(async () => {
  // 确保用户已登录
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    // 获取游戏数据
    await fetchGame()
    
    // 启动游戏状态轮询
    gameCheckInterval = setInterval(fetchGame, 1000)
    
    // 启动心跳
    heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL)
    
    // 添加窗口关闭和页面离开事件监听
    window.addEventListener('beforeunload', handlePageClose)
    window.addEventListener('pagehide', handlePageClose)
  } catch (err) {
    console.error('Error loading game:', err)
    error.value = '加载游戏数据失败，请刷新页面重试'
  }
})

onBeforeUnmount(() => {
  // 清除所有定时器
  clearAllIntervals()
  
  // 移除窗口关闭事件监听
  window.removeEventListener('beforeunload', handlePageClose)
  window.removeEventListener('pagehide', handlePageClose)
})

// 处理页面关闭事件
const handlePageClose = (event) => {
  // 只在游戏进行中且玩家是参与者时才处理
  if (game.value && 
      game.value.status === 'playing' && 
      (game.value.player1_id === currentUser.value.id || 
       game.value.player2_id === currentUser.value.id)) {
    
    // 尝试调用退出游戏API
    try {
      // 首先尝试使用navigator.sendBeacon（更可靠的方式发送页面卸载请求）
      const endpoint = `/api/games/${gameId.value}/exit`;
      const sent = navigator.sendBeacon(endpoint, JSON.stringify({}));
      
      // 如果sendBeacon不可用或发送失败，使用同步XHR作为后备方案
      if (!sent) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', endpoint, false); // false表示同步
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        // 添加凭据以确保会话cookie被发送
        xhr.withCredentials = true;
        xhr.send(JSON.stringify({}));
        
        // 检查响应状态
        if (xhr.status !== 200) {
          console.error('Failed to send exit request on page close, status:', xhr.status);
        }
      }
    } catch (e) {
      console.error('Failed to send exit request on page close:', e);
    }
    
    // 显示提示信息
    event.returnValue = '游戏还在进行中，离开将视为认输！';
    return event.returnValue;
  }
}
</script>

<style scoped>
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-waiting {
  background-color: #cff4fc;
  color: #055160;
}

.status-playing {
  background-color: #d1e7dd;
  color: #0f5132;
}

.status-finished {
  background-color: #e2e3e5;
  color: #41464b;
}

.status-abandoned {
  background-color: #f8d7da;
  color: #842029;
}

.status-unknown {
  background-color: #fff3cd;
  color: #664d03;
}

.game-board {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.board-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.board {
  position: relative;
  width: 100%;
  aspect-ratio: 1/1;
  background-color: #e9c08d;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.board-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.grid-line {
  position: absolute;
  background-color: #000;
}

.horizontal {
  width: 100%;
  height: 1px;
}

.vertical {
  height: 100%;
  width: 1px;
}

.mark-point {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #000;
  transform: translate(-50%, -50%);
}

.board-row {
  position: static;
}

.board-point {
  position: absolute;
  width: 24px;
  height: 24px;
  transform: translate(-50%, -50%);
  z-index: 1;
  cursor: pointer;
}

.board-point:hover::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.1);
  z-index: 1;
  transform: translate(-50%, -50%);
  left: 50%;
  top: 50%;
}

.stone {
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  z-index: 2;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.stone-black {
  background: radial-gradient(circle at 30% 30%, #666, #000);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}

.stone-white {
  background: radial-gradient(circle at 30% 30%, #fff, #ddd);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.last-move-mark {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: rgba(255, 0, 0, 0.6);
  z-index: 3;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.player-info {
  margin-bottom: 20px;
}

.player {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stone-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}

.stone-icon.stone-black {
  background: radial-gradient(circle at 30% 30%, #666, #000);
}

.stone-icon.stone-white {
  background: radial-gradient(circle at 30% 30%, #fff, #ddd);
}

.player-details {
  flex-grow: 1;
}

.player-name {
  font-weight: 600;
}

.stat-item {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
}

.stat-label {
  color: #6c757d;
}
</style> 