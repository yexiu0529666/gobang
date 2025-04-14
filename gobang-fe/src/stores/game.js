import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from './auth'

export const useGameStore = defineStore('game', () => {
  // 状态
  const socket = ref(null)
  const currentGame = ref(null)
  const games = ref([])
  const isConnected = ref(false)
  const leaderboard = ref([])


  // 获取游戏列表
  async function fetchGames() {
    try {
      const response = await api.get('/games')
      games.value = response.data.games || []
      return games.value
    } catch (error) {
      console.error('Failed to fetch games:', error)
      throw error
    }
  }

  // 获取单个游戏
  async function fetchGame(gameId) {
    try {
      const response = await api.get(`/games/${gameId}`)
      if (response.data) {
        currentGame.value = response.data
        return response.data
      }
      throw new Error('Invalid response format')
    } catch (error) {
      console.error('Failed to fetch game:', error)
      throw error
    }
  }

  // 创建新游戏
  async function createGame(gameMode = 'normal') {
    try {
      const response = await api.post('/games', { game_mode: gameMode })
      if (response.data && response.data.game) {
        currentGame.value = response.data.game
        return response.data.game
      } else {
        throw new Error('Invalid response format')
      }
    } catch (error) {
      console.error('Failed to create game:', error)
      throw error
    }
  }

  // 下棋
  function makeMove(gameId, x, y) {
    if (!socket.value || !socket.value.connected) {
      console.error('Socket not connected')
      return false
    }

    socket.value.emit('make_move', {
      game_id: gameId,
      x: x,
      y: y
    })

    return true
  }


  return {
    socket,
    currentGame,
    games,
    isConnected,
    leaderboard,
    fetchGames,
    fetchGame,
    createGame,
    makeMove,
  }
}) 