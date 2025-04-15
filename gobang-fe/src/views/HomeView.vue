<template>
  <div class="home-container">
    <div class="hero-section">
      <h1 class="main-title">五子棋<span class="accent">对战平台</span></h1>
      <p class="subtitle">挑战全球玩家，提升五子棋技巧</p>
      
      <div class="cta-buttons">
        <template v-if="isAuthenticated">
          <router-link class="cta-button primary-btn" to="/new-game">
            <span class="btn-content">
              <i class="fas fa-play-circle"></i>
              开始新游戏
            </span>
          </router-link>
          <router-link class="cta-button secondary-btn" to="/profile">
            <span class="btn-content">
              <i class="fas fa-user"></i>
              我的资料
            </span>
          </router-link>
        </template>
        <template v-else>
          <router-link class="cta-button primary-btn" to="/login">
            <span class="btn-content">
              <i class="fas fa-sign-in-alt"></i>
              登录游戏
            </span>
          </router-link>
          <router-link class="cta-button secondary-btn" to="/register">
            <span class="btn-content">
              <i class="fas fa-user-plus"></i>
              注册账号
            </span>
          </router-link>
        </template>
      </div>
    </div>
    
    <div class="features-section">
      <div class="section-title">
        <h2>游戏特色</h2>
        <div class="title-underline"></div>
      </div>
      
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-grid-3x3"></i>
          </div>
          <h3>实时对战</h3>
          <p>与全球玩家即时对弈，体验流畅的五子棋对战，无需等待，随时开始游戏。</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-trophy"></i>
          </div>
          <h3>排行榜</h3>
          <p>赢取更多比赛，提升你的排名，登上排行榜展示你的实力与智慧。</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-clock-history"></i>
          </div>
          <h3>游戏历史</h3>
          <p>回顾过去的对局，分析你的表现与策略，提升棋艺水平。</p>
        </div>
        
      </div>
    </div>
    
    <div class="stats-section">
      <div class="stat-item">
        <div class="stat-count">1000+</div>
        <div class="stat-label">活跃玩家</div>
      </div>
      <div class="stat-item">
        <div class="stat-count">5000+</div>
        <div class="stat-label">已完成对局</div>
      </div>
      <div class="stat-item">
        <div class="stat-count">150+</div>
        <div class="stat-label">每日挑战</div>
      </div>
    </div>
    
    <footer class="home-footer">
      <p>© 2025 五子棋对战平台 - 提供最佳在线五子棋体验</p>
    </footer>
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

<style scoped>
/* 基础样式 */
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 英雄区域 */
.hero-section {
  text-align: center;
  padding: 4rem 1rem;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 3rem;
  backdrop-filter: blur(5px);
  animation: fadeIn 1s ease-out;
}

.main-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.accent {
  color: #3498db;
  position: relative;
}

.accent::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 2px;
}

.subtitle {
  font-size: 1.5rem;
  color: #7f8c8d;
  margin-bottom: 2.5rem;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.cta-button {
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 2;
}

.primary-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
}

.primary-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 7px 20px rgba(52, 152, 219, 0.6);
}

.secondary-btn {
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
}

.secondary-btn:hover {
  background: rgba(52, 152, 219, 0.1);
  transform: translateY(-3px);
}

/* 特性部分 */
.features-section {
  padding: 2rem 0 4rem;
}

.section-title {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.section-title h2 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  margin: 0 auto;
  border-radius: 2px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  text-align: center;
  backdrop-filter: blur(5px);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #3498db 0%, #2ecc71 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.feature-card h3 {
  font-size: 1.4rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #7f8c8d;
  line-height: 1.6;
}

/* 统计部分 */
.stats-section {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 3rem;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 1rem;
  margin: 3rem 0;
  backdrop-filter: blur(5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.stat-item {
  text-align: center;
}

.stat-count {
  font-size: 3rem;
  font-weight: 700;
  color: #3498db;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.2rem;
  color: #7f8c8d;
}

/* 页脚 */
.home-footer {
  text-align: center;
  padding: 2rem 0;
  color: #7f8c8d;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  margin-top: 2rem;
}

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stats-section {
    flex-direction: column;
    padding: 2rem 1rem;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
}
</style> 