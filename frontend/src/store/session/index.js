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
    take_start (context, title) {
      this.$socket.send(JSON.stringify({
        action: 'take_start',
        data: title
      }))
    },
    take_stop (context) {
      this.$socket.send(JSON.stringify({
        action: 'take_stop',
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
    recorder_state: state => state.recorder.state,
    active_take: state => state.recorder.current_take,
    next_take: state => state.next_take,
    all_takes: state => state.takes,
    session_name: state => state.name

  }
}
