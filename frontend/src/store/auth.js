
// noinspection JSUnusedGlobalSymbols,JSUnusedLocalSymbols
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
    login (context, data) {
      this.$socket.send(JSON.stringify({
        action: 'login', data
      }))
    },
    logout () {
      this.$socket.send(JSON.stringify({
        action: 'logout', data: null
      }))
    }
  },

  getters: {
    current_user: state => state.user
  }
}
