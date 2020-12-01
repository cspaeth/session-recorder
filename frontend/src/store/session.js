// noinspection JSUnusedGlobalSymbols
export default {
  state: () => {
    return {
      name: '',
      takes: [],
      active_take: 0,
      next_take: {
        number: 1,
        name: '',
        tempo: 100
      }
    }
  },

  mutations: {
    SOCKET_SESSION (state, data) {
      Object.assign(state, data)
    }
  },

  actions: {

    set_next_take_name (context, name) {
      this.$socket.send(JSON.stringify({
        action: 'set_next_take_name',
        data: name
      }))
    },
    set_next_take_tempo (context, tempo) {
      this.$socket.send(JSON.stringify({
        action: 'set_next_take_tempo',
        data: tempo
      }))
    },

    session_start (context, name) {
      this.$socket.send(JSON.stringify({
        action: 'session_start',
        data: name
      }))
    },

    session_open (context, id) {
      this.$socket.send(JSON.stringify({
        action: 'session_open',
        data: id
      }))
    },
    session_close () {
      this.$socket.send(JSON.stringify({
        action: 'session_close',
        data: null
      }))
    },
    session_upload () {
      this.$socket.send(JSON.stringify({
        action: 'session_upload',
        data: null
      }))
    },

    take_queue (context, takeNumber) {
      this.$socket.send(JSON.stringify({
        action: 'take_queue',
        data: takeNumber
      }))
    },
    take_unqueue (context, takeNumber) {
      this.$socket.send(JSON.stringify({
        action: 'take_unqueue',
        data: takeNumber
      }))
    },

    logout () {

    }

  },

  getters: {
    next_take: state => state.next_take,
    all_takes: state => state.takes,
    session_name: state => state.name,
    active_take (state) {
      return state.takes.find(x => x.number === state.active_take)
    },
    active_take_number: state => state.active_take

  }
}
