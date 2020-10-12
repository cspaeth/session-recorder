
// noinspection JSUnusedGlobalSymbols,JSUnusedLocalSymbols
export default {
  state: {
    sessions: []
  },

  mutations: {

    SOCKET_SESSIONS (state, sessions) {
      state.sessions = sessions
    }
  },
  getters: {
    sessions: state => state.sessions
  }
}
