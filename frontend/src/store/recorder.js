export default {
  state: {
    state: 'disconnected',
    current_take: null,
    position: 0
  },

  mutations: {
    SOCKET_RECORDER (state, newState) {
      console.log(newState)
      Object.assign(state, newState)
    }
  },

  actions: {

    take_start (context, title) {
      this.$socket.send(JSON.stringify({
        action: 'take_start',
        data: title
      }))
    },
    take_stop () {
      this.$socket.send(JSON.stringify({
        action: 'take_stop',
        data: null
      }))
    },
    play () {
      this.$socket.send(JSON.stringify({
        action: 'play',
        data: null
      }))
    },
    stop () {
      this.$socket.send(JSON.stringify({
        action: 'stop',
        data: null
      }))
    },
    take_cancel () {

    },

    take_select (context, number) {
      this.$socket.send(JSON.stringify({
        action: 'take_select',
        data: number
      }))
    },

    take_play () {
      this.$socket.send(JSON.stringify({
        action: 'take_play',
        data: null
      }))
    },

    take_seek (context, position) {
      this.$socket.send(JSON.stringify({
        action: 'take_seek',
        data: position
      }))
    }

  },

  getters: {
    position_in_take: state => state.position || 0,
    recorder_state: state => state.state
  }
}
