<template>
  <div id="particles-js" class="particles-container"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue';

// 加载particles.js脚本
function loadParticlesScript() {
  return new Promise((resolve, reject) => {
    if (window.particlesJS) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

onMounted(async () => {
  try {
    await loadParticlesScript();
    // 使用外部配置文件 - 从public目录下加载
    window.particlesJS.load('particles-js', '/particles.json', function() {
      console.log('粒子效果加载完成');
    });
  } catch (error) {
    console.error('Failed to load particles.js:', error);
  }
});

onBeforeUnmount(() => {
  // 清理粒子效果资源（如果有清理方法的话）
  // 注：particles.js没有明确的销毁方法，由浏览器自动清理
});
</script>

<style scoped>
.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background-color: #f8f9fa;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style> 