<template>
  <div class="replay-container">
    <div class="replay-header">
      <h1 class="replay-title">游戏回放</h1>
      <p class="replay-subtitle">重温精彩对局，学习对弈技巧</p>
    </div>
    
    <div class="replay-content">
      <div class="row">
        <div class="col-md-8">
          <div class="game-board-card">
            <div class="card-header">
              <div class="header-content">
                <h3>对局棋盘</h3>
                <router-link to="/replays" class="back-btn">
                  <i class="bi bi-arrow-left"></i> 返回列表
                </router-link>
              </div>
            </div>
            
            <div class="card-body">
              <div class="game-board">
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
          <div class="control-panel">
            <div class="game-info-section">
              <h4>对局信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">黑方</div>
                  <div class="info-value">{{ game?.black_player?.username || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">白方</div>
                  <div class="info-value">{{ game?.white_player?.username || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">获胜方</div>
                  <div class="info-value" :class="getWinnerClass()">
                    {{ game?.winner ? game.winner.username : '平局' }}
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">落子总数</div>
                  <div class="info-value">{{ movesHistory.length }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">当前步数</div>
                  <div class="info-value">{{ currentMoveIndex + 1 }} / {{ movesHistory.length }}</div>
                </div>
              </div>
            </div>
            
            <div class="playback-controls">
              <h4>回放控制</h4>
              
              <!-- 播放进度条 -->
              <div class="progress-section">
                <div class="progress-info">
                  <span>播放进度</span>
                  <span>{{ Math.round(progressPercentage) }}%</span>
                </div>
                <div class="progress-bar-container">
                  <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
                </div>
              </div>
              
              <!-- 播放速度控制 -->
              <div class="speed-control">
                <label>播放速度: {{ playbackSpeed }}x</label>
                <div class="speed-slider">
                  <input type="range" min="0.5" max="3" step="0.5" v-model="playbackSpeed">
                  <div class="speed-marks">
                    <span>0.5x</span>
                    <span>1x</span>
                    <span>1.5x</span>
                    <span>2x</span>
                    <span>2.5x</span>
                    <span>3x</span>
                  </div>
                </div>
              </div>
              
              <!-- 控制按钮 -->
              <div class="control-buttons">
                <button class="control-btn" @click="skipToStart" :disabled="currentMoveIndex === -1">
                  <i class="bi bi-skip-start-fill"></i>
                </button>
                <button class="control-btn" @click="previousMove" :disabled="currentMoveIndex === -1">
                  <i class="bi bi-skip-backward-fill"></i>
                </button>
                <button class="control-btn play-btn" :class="{ 'playing': isPlaying }" @click="togglePlay">
                  <i :class="isPlaying ? 'bi bi-pause-fill' : 'bi bi-play-fill'"></i>
                </button>
                <button class="control-btn" @click="nextMove" :disabled="currentMoveIndex >= movesHistory.length - 1">
                  <i class="bi bi-skip-forward-fill"></i>
                </button>
                <button class="control-btn" @click="skipToEnd" :disabled="currentMoveIndex >= movesHistory.length - 1">
                  <i class="bi bi-skip-end-fill"></i>
                </button>
              </div>
            </div>
            
            <!-- 状态提示 -->
            <div v-if="statusMessage" class="status-message" :class="statusClass">
              <i :class="getStatusIcon()"></i>
              <span>{{ statusMessage }}</span>
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

// 获取状态图标
const getStatusIcon = () => {
  switch (statusClass.value) {
    case 'alert-info':
      return 'bi bi-info-circle'
    case 'alert-success':
      return 'bi bi-check-circle'
    case 'alert-warning':
      return 'bi bi-exclamation-circle'
    case 'alert-danger':
      return 'bi bi-x-circle'
    default:
      return 'bi bi-info-circle'
  }
}

// 获取获胜方样式类
const getWinnerClass = () => {
  if (!game.value?.winner) return 'text-secondary'
  return game.value.winner.id === game.value.black_player?.id ? 'text-dark' : 'text-light'
}

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
/* 基础样式 */
.replay-container {
  max-width: 1400px;
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
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.replay-subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.replay-content {
  animation: slideUp 0.6s ease-out;
}

/* 游戏棋盘卡片 */
.game-board-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
}

.card-header {
  padding: 1.2rem;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.back-btn {
  color: white;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 100px;
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateX(-3px);
}

.card-body {
  padding: 2rem;
}

/* 棋盘样式 */
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
  border-radius: 0.5rem;
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
  transition: all 0.3s ease;
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

/* 控制面板 */
.control-panel {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  height: 100%;
}

.game-info-section {
  margin-bottom: 2rem;
}

.game-info-section h4 {
  color: #3498db;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  background-color: rgba(52, 152, 219, 0.05);
  padding: 0.8rem;
  border-radius: 0.5rem;
}

.info-label {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 0.3rem;
}

.info-value {
  font-weight: 600;
  color: #2c3e50;
}

/* 回放控制 */
.playback-controls {
  margin-bottom: 1.5rem;
}

.playback-controls h4 {
  color: #3498db;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.progress-section {
  margin-bottom: 1.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.progress-bar-container {
  height: 8px;
  background-color: rgba(52, 152, 219, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.speed-control {
  margin-bottom: 2rem;
}

.speed-control label {
  display: block;
  margin-bottom: 0.5rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.speed-slider {
  position: relative;
}

.speed-slider input[type="range"] {
  width: 100%;
  margin-bottom: 0.5rem;
}

.speed-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.control-buttons {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.control-btn {
  width: 45px;
  height: 45px;
  border: none;
  border-radius: 50%;
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background-color: rgba(52, 152, 219, 0.2);
  transform: translateY(-2px);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-btn {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  font-size: 1.2rem;
}

.play-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.play-btn.playing {
  background: linear-gradient(135deg, #e74c3c, #f39c12);
}

.status-message {
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 1rem;
  animation: slideIn 0.3s ease;
}

.status-message i {
  font-size: 1.2rem;
}

.alert-info {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.alert-warning {
  background-color: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.alert-danger {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
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

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
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
  
  .card-body {
    padding: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .control-buttons {
    flex-wrap: wrap;
  }
  
  .control-btn {
    width: 40px;
    height: 40px;
  }
  
  .play-btn {
    width: 50px;
    height: 50px;
  }
}
</style> 