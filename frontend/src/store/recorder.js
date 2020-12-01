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
