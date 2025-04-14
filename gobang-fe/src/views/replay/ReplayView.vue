<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-md-8">
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="mb-0">游戏回放</h3>
            <router-link to="/replays" class="btn btn-outline-secondary btn-sm">
              返回列表
            </router-link>
          </div>
          
          <div class="card-body p-0">
            <div class="game-board">
              <!-- 棋盘 -->
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
                         :style="{ top: `${(i-1) * 100 / 14}%`, left: `${(j-1) * 100 / 14}%` }">
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
      
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h4 class="mb-0">回放控制</h4>
          </div>
          <div class="card-body">
            <!-- 游戏信息 -->
            <div class="game-info mb-4">
              <div class="d-flex justify-content-between mb-2">
                <span>黑方:</span>
                <strong>{{ game?.black_player?.username || '未知' }}</strong>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span>白方:</span>
                <strong>{{ game?.white_player?.username || '未知' }}</strong>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span>获胜方:</span>
                <strong v-if="game?.winner">{{ game.winner.username }}</strong>
                <strong v-else class="text-secondary">平局</strong>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span>落子总数:</span>
                <strong>{{ movesHistory.length }}</strong>
              </div>
              <div class="d-flex justify-content-between">
                <span>当前步数:</span>
                <strong>{{ currentMoveIndex + 1 }} / {{ movesHistory.length }}</strong>
              </div>
            </div>
            
            <!-- 播放进度条 -->
            <div class="progress mb-3" style="height: 10px">
              <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            
            <!-- 播放速度控制 -->
            <div class="mb-3">
              <label class="form-label">播放速度: {{ playbackSpeed }}x</label>
              <input type="range" class="form-range" min="0.5" max="3" step="0.5" v-model="playbackSpeed">
            </div>
            
            <!-- 控制按钮 -->
            <div class="d-flex justify-content-between mb-3">
              <button class="btn btn-outline-secondary" @click="skipToStart" :disabled="currentMoveIndex === -1">
                <i class="bi bi-skip-start-fill"></i> 开始
              </button>
              <button class="btn btn-outline-secondary" @click="previousMove" :disabled="currentMoveIndex === -1">
                <i class="bi bi-skip-backward-fill"></i> 上一步
              </button>
              <button class="btn" :class="isPlaying ? 'btn-danger' : 'btn-primary'" @click="togglePlay">
                <i class="bi" :class="isPlaying ? 'bi-pause-fill' : 'bi-play-fill'"></i>
                {{ isPlaying ? '暂停' : '播放' }}
              </button>
              <button class="btn btn-outline-secondary" @click="nextMove" :disabled="currentMoveIndex >= movesHistory.length - 1">
                <i class="bi bi-skip-forward-fill"></i> 下一步
              </button>
              <button class="btn btn-outline-secondary" @click="skipToEnd" :disabled="currentMoveIndex >= movesHistory.length - 1">
                <i class="bi bi-skip-end-fill"></i> 结束
              </button>
            </div>
            
            <!-- 状态提示 -->
            <div v-if="statusMessage" class="alert" :class="statusClass">
              {{ statusMessage }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const gameId = computed(() => route.params.id)

// 棋盘和游戏状态
const boardRef = ref(null)
const game = ref(null)
const stones = ref(Array(15).fill().map(() => Array(15).fill(0))) // 0:无子, 1:黑子, 2:白子
const movesHistory = ref([])
const currentMoveIndex = ref(-1) // -1表示初始状态，没有展示任何落子
const lastMoveCoord = ref(null) // 保存最后一步的坐标

// 回放控制状态
const isPlaying = ref(false)
const playbackSpeed = ref(1)
const playbackInterval = ref(null)
const statusMessage = ref('')
const statusClass = ref('alert-info')
const loading = ref(true)
const error = ref(null)

// 获取游戏回放数据
const fetchReplayData = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/api/replay/${gameId.value}`)
    game.value = response.data
    
    // 整理棋步历史
    // 根据move_number排序
    const sortedMoves = [...response.data.moves].sort((a, b) => a.move_number - b.move_number)
    
    // 转换为更易于处理的格式
    movesHistory.value = sortedMoves.map(move => ({
      x: move.x,
      y: move.y,
      player_id: move.player_id,
      color: move.move_number % 2 === 1 ? 1 : 2, // 1:黑子, 2:白子
      timestamp: new Date(move.timestamp),
      move_number: move.move_number
    }))
    
    loading.value = false
    showStatus('回放准备就绪，点击播放按钮开始回放', 'alert-info')
  } catch (err) {
    console.error('Failed to fetch replay data:', err)
    error.value = '无法加载回放数据，请稍后再试'
    loading.value = false
    showStatus('加载回放数据失败', 'alert-danger')
  }
}

// 棋盘操作函数
const getStone = (x, y) => stones.value[x][y]

const isLastMove = (x, y) => {
  return lastMoveCoord.value && lastMoveCoord.value.x === x && lastMoveCoord.value.y === y
}

// 重置棋盘
const resetBoard = () => {
  stones.value = Array(15).fill().map(() => Array(15).fill(0))
  lastMoveCoord.value = null
}

// 播放控制函数
const togglePlay = () => {
  if (isPlaying.value) {
    pausePlayback()
  } else {
    startPlayback()
  }
}

const startPlayback = () => {
  if (isPlaying.value) return
  
  if (currentMoveIndex.value >= movesHistory.value.length - 1) {
    // 已经到达最后，重新开始
    resetBoard()
    currentMoveIndex.value = -1
  }
  
  isPlaying.value = true
  showStatus('正在播放回放', 'alert-info')
  
  // 设置定时器，根据播放速度展示棋局
  const intervalTime = 1000 / playbackSpeed.value
  playbackInterval.value = setInterval(() => {
    nextMove()
    
    if (currentMoveIndex.value >= movesHistory.value.length - 1) {
      pausePlayback()
      showStatus('回放结束', 'alert-success')
    }
  }, intervalTime)
}

const pausePlayback = () => {
  if (!isPlaying.value) return
  
  isPlaying.value = false
  if (playbackInterval.value) {
    clearInterval(playbackInterval.value)
    playbackInterval.value = null
  }
  
  showStatus('回放已暂停', 'alert-warning')
}

const nextMove = () => {
  if (currentMoveIndex.value >= movesHistory.value.length - 1) {
    showStatus('已经是最后一步', 'alert-warning')
    return
  }
  
  currentMoveIndex.value++
  const move = movesHistory.value[currentMoveIndex.value]
  
  // 放置棋子
  stones.value[move.x][move.y] = move.color
  lastMoveCoord.value = { x: move.x, y: move.y }
}

const previousMove = () => {
  if (currentMoveIndex.value < 0) {
    showStatus('已经是第一步', 'alert-warning')
    return
  }
  
  // 移除当前步骤的棋子
  const move = movesHistory.value[currentMoveIndex.value]
  stones.value[move.x][move.y] = 0
  
  currentMoveIndex.value--
  
  // 更新最后一步标记
  if (currentMoveIndex.value >= 0) {
    const prevMove = movesHistory.value[currentMoveIndex.value]
    lastMoveCoord.value = { x: prevMove.x, y: prevMove.y }
  } else {
    lastMoveCoord.value = null
  }
}

const skipToStart = () => {
  pausePlayback()
  resetBoard()
  currentMoveIndex.value = -1
  showStatus('回到开始位置', 'alert-info')
}

const skipToEnd = () => {
  pausePlayback()
  resetBoard()
  
  // 依次展示所有棋步
  for (let i = 0; i < movesHistory.value.length; i++) {
    const move = movesHistory.value[i]
    stones.value[move.x][move.y] = move.color
  }
  
  // 设置最后一步的标记
  if (movesHistory.value.length > 0) {
    const lastMove = movesHistory.value[movesHistory.value.length - 1]
    lastMoveCoord.value = { x: lastMove.x, y: lastMove.y }
    currentMoveIndex.value = movesHistory.value.length - 1
  }
  
  showStatus('跳转到结束位置', 'alert-info')
}

// 计算进度百分比
const progressPercentage = computed(() => {
  if (movesHistory.value.length === 0) return 0
  return ((currentMoveIndex.value + 1) / movesHistory.value.length) * 100
})

// 显示状态消息
const showStatus = (message, className = 'alert-info') => {
  statusMessage.value = message
  statusClass.value = className
  
  // 3秒后自动清除信息消息，错误和警告消息保留
  if (className === 'alert-info') {
    setTimeout(() => {
      if (statusMessage.value === message) {
        statusMessage.value = ''
      }
    }, 3000)
  }
}

// 监听播放速度变化
watch(playbackSpeed, (newSpeed) => {
  if (isPlaying.value) {
    // 重新启动播放器以应用新速度
    pausePlayback()
    startPlayback()
  }
})

onMounted(() => {
  fetchReplayData()
})

onBeforeUnmount(() => {
  if (playbackInterval.value) {
    clearInterval(playbackInterval.value)
  }
})
</script>

<style scoped>
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

/* 控制按钮样式 */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.progress {
  height: 8px;
  border-radius: 4px;
}

.progress-bar {
  background-color: #007bff;
  transition: width 0.3s ease;
}
</style> 