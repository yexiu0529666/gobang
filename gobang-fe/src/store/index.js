import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    game: null,
    matchmaking: false,
    socket: null
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_GAME(state, game) {
      state.game = game
    },
    SET_MATCHMAKING(state, status) {
      state.matchmaking = status
    },
    SET_SOCKET(state, socket) {
      state.socket = socket
    }
  },
  actions: {
    login({ commit }, user) {
      commit('SET_USER', user)
    },
    logout({ commit }) {
      commit('SET_USER', null)
    },
    startGame({ commit }, game) {
      commit('SET_GAME', game)
    },
    endGame({ commit }) {
      commit('SET_GAME', null)
    },
    startMatchmaking({ commit }) {
      commit('SET_MATCHMAKING', true)
    },
    stopMatchmaking({ commit }) {
      commit('SET_MATCHMAKING', false)
    },
    setSocket({ commit }, socket) {
      commit('SET_SOCKET', socket)
    }
  },
  getters: {
    isAuthenticated: state => !!state.user,
    currentUser: state => state.user,
    currentGame: state => state.game,
    isMatchmaking: state => state.matchmaking,
    socket: state => state.socket
  }
}) 