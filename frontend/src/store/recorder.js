// noinspection JSUnusedGlobalSymbols
export default {
  state: {
    state: 'disconnected',
    current_take: null,
    position: 0,
    metronome: 0,
    channels: []
  },

  mutations: {
    SOCKET_RECORDER (state, newState) {
      Object.assign(state, newState)
    }
  },

  actions: {

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
    set_track_armed (context, data) {
      this.$socket.send(JSON.stringify({
        action: 'set_track_armed',
        data: data
      }))
    },
    set_metronome_state (context, enable) {
      this.$socket.send(JSON.stringify({
        action: 'set_metronome_state',
        data: enable
      }))
    }
  },

  getters: {
    position_in_take: state => state.position || 0,
    recorder_state: state => state.state
  }
}
