export default {
  state: () => {
    return {
      name: null,
      recorder: {
        state: 'closed',
        current_take: 0,
        position: 0
      },
      takes: [],
      next_take: {
        number: 1,
        name: ''
      }
    }
  },

  mutations: {
    SOCKET_UPDATE_FULL_SESSION (state, data) {
      Object.assign(state, data)
    }
  },

  actions: {

    next_take_name (context, name) {
      this.$socket.send(JSON.stringify({
        action: 'next_take_name',
        data: name
      }))
    },

    session_start (context, name) {
      this.$socket.send(JSON.stringify({
        action: 'session_start',
        data: name
      }))
    },
    session_close (name) {

    },

    logout () {

    }

  },

  getters: {

    next_take: state => state.next_take,
    all_takes: state => state.takes,
    session_name: state => state.name

  }
}
