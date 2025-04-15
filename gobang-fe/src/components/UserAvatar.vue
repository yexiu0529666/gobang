<template>
  <div class="user-avatar" :style="avatarStyle">
    {{ initials }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    default: 40
  }
})

// 生成用户名的首字母
const initials = computed(() => {
  return props.username.charAt(0).toUpperCase()
})

// 生成随机背景色
const getRandomColor = (str) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  const h = hash % 360
  return `hsl(${h}, 70%, 50%)`
}

// 计算头像样式
const avatarStyle = computed(() => {
  return {
    width: `${props.size}px`,
    height: `${props.size}px`,
    backgroundColor: getRandomColor(props.username),
    fontSize: `${props.size * 0.5}px`,
    lineHeight: `${props.size}px`
  }
})
</script>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: bold;
  text-transform: uppercase;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style> 