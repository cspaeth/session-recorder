export default {
  state: {
    user: null
  },

  mutations: {
    SOCKET_ACTIVE_USER (state, user) {
      state.user = user
    }
  },

  actions: {
    login (context, username) {
      this.$socket.send(JSON.stringify({
        action: 'login', data: 'cspaeth'
      }))
    }
  },

  getters: {
    current_user: state => state.user
  }
}
