<template>
  <div class="leaderboard-container">
    <div class="leaderboard-header">
      <h1 class="leaderboard-title">积分排行榜</h1>
      <p class="leaderboard-subtitle">查看棋手们的积分和战绩表现</p>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>正在加载排行榜数据...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="leaderboard-content">
      <div class="leaderboard-card">
        <div class="top-players" v-if="leaderboard.length > 0">
          <div class="player-podium second-place" v-if="leaderboard.length > 1">
            <div class="podium-avatar">
              <UserAvatar :username="leaderboard[1].username" :size="70" />
              <div class="medal"><i class="fas fa-medal"></i></div>
            </div>
            <div class="podium-info">
              <div class="podium-rank">2</div>
              <div class="podium-name">{{ leaderboard[1].username }}</div>
              <div class="podium-rating">{{ leaderboard[1].rating }} 分</div>
            </div>
          </div>
          
          <div class="player-podium first-place" v-if="leaderboard.length > 0">
            <div class="podium-avatar">
              <UserAvatar :username="leaderboard[0].username" :size="90" />
              <div class="medal"><i class="fas fa-crown"></i></div>
            </div>
            <div class="podium-info">
              <div class="podium-rank">1</div>
              <div class="podium-name">{{ leaderboard[0].username }}</div>
              <div class="podium-rating">{{ leaderboard[0].rating }} 分</div>
            </div>
          </div>
          
          <div class="player-podium third-place" v-if="leaderboard.length > 2">
            <div class="podium-avatar">
              <UserAvatar :username="leaderboard[2].username" :size="70" />
              <div class="medal"><i class="fas fa-medal"></i></div>
            </div>
            <div class="podium-info">
              <div class="podium-rank">3</div>
              <div class="podium-name">{{ leaderboard[2].username }}</div>
              <div class="podium-rating">{{ leaderboard[2].rating }} 分</div>
            </div>
          </div>
        </div>
        
        <div class="table-container">
          <table class="leaderboard-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>用户名</th>
                <th class="active-sort">
                  积分
                  <i class="fas fa-sort-down"></i>
                </th>
                <th>胜场</th>
                <th>总场次</th>
                <th>胜率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(player, index) in leaderboard" :key="player.id" 
                  :class="{'highlighted': index < 3}">
                <td class="rank-cell">
                  <span class="rank-badge" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
                </td>
                <td class="name-cell">{{ player.username }}</td>
                <td class="rating-cell">{{ player.rating }}</td>
                <td>{{ player.games_won }}</td>
                <td>{{ player.total_games }}</td>
                <td class="win-rate-cell">
                  <div class="progress-container">
                    <div class="progress-bar" :style="{width: `${player.win_rate}%`}"></div>
                    <span class="progress-text">{{ player.win_rate.toFixed(2) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="leaderboard.length === 0" class="empty-state">
          <i class="fas fa-trophy"></i>
          <p>暂无排行榜数据</p>
          <p class="empty-subtitle">快来开始你的第一场比赛吧！</p>
        </div>
      </div>
      
      <div class="leaderboard-info">
        <div class="info-card">
          <div class="info-header">
            <i class="fas fa-info-circle"></i>
            <h3>排行榜说明</h3>
          </div>
          <div class="info-content">
            <p>排行榜根据玩家积分排名，积分由对战结果决定：</p>
            <ul>
              <li>初始积分：1000分</li>
              <li>胜利：+10分</li>
              <li>失败：-10分</li>
            </ul>
            <p>积极参与对战，提升你的排名吧！</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import UserAvatar from '@/components/UserAvatar.vue'

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
/* 基础样式 */
.leaderboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  color: #2c3e50;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.leaderboard-header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out;
}

.leaderboard-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #3498db;
}

.leaderboard-subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

.leaderboard-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 992px) {
  .leaderboard-content {
    grid-template-columns: 3fr 1fr;
  }
}

/* 卡片样式 */
.leaderboard-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
  animation: slideUp 0.6s ease-out;
}

/* 顶部选手展示 */
.top-players {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding: 2rem 1rem 1rem;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  position: relative;
}

.player-podium {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 1rem;
  transition: transform 0.3s ease;
}

.player-podium:hover {
  transform: translateY(-5px);
}

.first-place {
  z-index: 3;
  margin-bottom: -2rem;
}

.second-place, .third-place {
  z-index: 2;
}

.podium-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
  border: 4px solid white;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  position: relative;
}

.first-place .podium-avatar {
  width: 100px;
  height: 100px;
  border-color: #ffd700;
}

.second-place .podium-avatar {
  border-color: #c0c0c0;
}

.third-place .podium-avatar {
  border-color: #cd7f32;
}

.podium-avatar i {
  font-size: 2rem;
  color: #3498db;
}

.first-place .podium-avatar i {
  font-size: 2.5rem;
  color: #f39c12;
}

.medal {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 30px;
  height: 30px;
  background-color: #f39c12;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.first-place .medal {
  background-color: #f1c40f;
}

.medal i {
  font-size: 0.9rem !important;
  color: white !important;
}

.podium-info {
  text-align: center;
  padding: 1rem;
  background-color: white;
  border-radius: 0.5rem;
  width: 120px;
  margin-top: 0.5rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.first-place .podium-info {
  width: 140px;
}

.podium-rank {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e74c3c;
  margin-bottom: 0.3rem;
}

.first-place .podium-rank {
  color: #f1c40f;
}

.second-place .podium-rank {
  color: #95a5a6;
}

.third-place .podium-rank {
  color: #e67e22;
}

.podium-name {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.podium-rating {
  font-size: 1rem;
  color: #3498db;
  font-weight: 700;
}

/* 表格样式 */
.table-container {
  padding: 2rem 1rem 1rem;
  overflow-x: auto;
}

.leaderboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.leaderboard-table th, 
.leaderboard-table td {
  padding: 1rem;
  text-align: center;
}

.leaderboard-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  position: sticky;
  top: 0;
  border-bottom: 2px solid #e9ecef;
}

.active-sort {
  color: #3498db !important;
  background-color: #ebf5fb !important;
}

.active-sort i {
  margin-left: 0.5rem;
  color: #3498db;
}

.leaderboard-table tbody tr {
  transition: all 0.2s ease;
  border-bottom: 1px solid #f1f1f1;
}

.leaderboard-table tbody tr:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.leaderboard-table tbody tr.highlighted {
  background-color: #f8f9fa;
}

.rank-cell {
  position: relative;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #333;
  font-weight: 600;
}

.rank-1 {
  background-color: #f1c40f;
  color: white;
}

.rank-2 {
  background-color: #bdc3c7;
  color: white;
}

.rank-3 {
  background-color: #cd7f32;
  color: white;
}

.name-cell {
  text-align: left;
  font-weight: 500;
}

.rating-cell {
  font-weight: 700;
  color: #3498db;
  font-size: 1.1rem;
}

.win-rate-cell {
  width: 180px;
}

.progress-container {
  height: 20px;
  background-color: #f1f1f1;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 10px;
}

.progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 0.9rem;
  color: #95a5a6;
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

/* 排行榜信息卡片 */
.info-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.8s ease-out;
}

.info-header {
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
}

.info-header i {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.info-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.info-content {
  padding: 1.5rem;
}

.info-content p {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.info-content ul {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.info-content li {
  margin-bottom: 0.5rem;
  color: #2c3e50;
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
  .leaderboard-title {
    font-size: 2rem;
  }
  
  .leaderboard-subtitle {
    font-size: 1rem;
  }
  
  .top-players {
    padding: 1.5rem 0.5rem;
  }
  
  .player-podium {
    margin: 0 0.5rem;
  }
  
  .podium-avatar {
    width: 60px;
    height: 60px;
  }
  
  .first-place .podium-avatar {
    width: 80px;
    height: 80px;
  }
  
  .podium-info {
    width: 100px;
  }
  
  .first-place .podium-info {
    width: 120px;
  }
  
  .win-rate-cell {
    width: 120px;
  }
  
  .leaderboard-table th, 
  .leaderboard-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
}
</style> 