import Vue from 'vue'
// noinspection JSUnusedGlobalSymbols,JSUnusedLocalSymbols
export default {
  state: {
    connected: true,
    osc: {}
  },

  mutations: {

    SOCKET_MIXER_OSC_INPUT (state, data) {
      console.log('Input')
      console.log(data)
      Vue.set(state.osc, data[0], data[1])
    },
    SOCKET_MIXER (state, data) {
      console.log('Input')
      console.log(data)

      Vue.set(state, 'osc', data.osc)
    }
  },

  actions: {
    ocs_send (context, value) {
      this.$socket.send(JSON.stringify({
        action: 'x32_send_value', data: value
      }))
    }
  }
}
