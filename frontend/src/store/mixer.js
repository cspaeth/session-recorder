import Vue from 'vue'
// noinspection JSUnusedGlobalSymbols,JSUnusedLocalSymbols

function pad (i) {
  return i < 10 ? '0' + i : i
}
const classPrefix = 'x32-color-'

export default {
  state: {
    connected: true,
    osc: {}
  },

  mutations: {

    SOCKET_MIXER_OSC_INPUT (state, data) {
      Vue.set(state.osc, data[0], data[1])
    },
    SOCKET_MIXER (state, data) {
      Vue.set(state, 'osc', data.osc)
    }
  },

  actions: {
    ocs_send (context, value) {
      this.$socket.send(JSON.stringify({
        action: 'x32_send_value', data: value
      }))
    }
  },
  getters: {

    visible_buses (state) {
      const result = []
      for (let bus = 1; bus < 17; bus++) {
        if (bus % 2 === 0) {
          const path = '/config/buslink/' + (bus - 1) + '-' + bus
          if (state.osc[path] === 1) {
            continue
          }
        }
        result.push(bus)
      }
      return result
    },

    bus_name: (state) => (bus) => {
      if (bus === 'main') {
        return state.osc['/main/st/config/name'] || 'Main Mix'
      }
      if (bus === 'mono') {
        return state.osc['/main/m/config/name'] || 'Mono Mix'
      }

      const path = '/bus/' + pad(bus) + '/config/name'
      return state.osc[path] || 'Bus ' + bus
    },
    channel_name: (state) => (channel) => {
      const path = '/ch/' + pad(channel) + '/config/name'
      return state.osc[path] || 'Ch ' + channel
    },
    auxin_name: (state) => (channel) => {
      const path = '/auxin/' + pad(channel) + '/config/name'
      return state.osc[path] || 'Aux ' + channel
    },
    fxrtn_name: (state) => (channel) => {
      const path = '/fxrtn/' + pad(channel) + '/config/name'
      const fallback = 'Fx ' + (Math.floor((channel + 1) / 2)) + ((channel % 2 === 1) ? 'L' : 'R')
      return state.osc[path] || fallback
    },

    bus_color: (state) => (bus) => {
      if (bus === 'main') {
        return classPrefix + state.osc['/main/st/config/color']
      }
      if (bus === 'mono') {
        return classPrefix + state.osc['/main/m/config/color']
      }

      const path = '/bus/' + pad(bus) + '/config/color'
      return classPrefix + state.osc[path]
    },
    channel_color: (state) => (channel) => {
      const path = '/ch/' + pad(channel) + '/config/color'
      return classPrefix + state.osc[path]
    },
    auxin_color: (state) => (channel) => {
      const path = '/auxin/' + pad(channel) + '/config/color'
      return classPrefix + state.osc[path]
    },

    fxrtn_color: (state) => (channel) => {
      const path = '/fxrtn/' + pad(channel) + '/config/color'
      return classPrefix + state.osc[path]
    },

    master_target: () => (bus) => {
      if (bus === 'main') {
        return '/main/st/mix/fader'
      }
      if (bus === 'mono') {
        return '/main/m/mix/fader'
      }

      return '/bus/' + pad(bus) + '/mix/fader'
    },
    channel_target: () => (bus, channel) => {
      if (bus === 'main') {
        return '/ch/' + pad(channel) + '/mix/fader'
      } else if (bus === 'mono') {
        return '/ch/' + pad(channel) + '/mix/mlevel'
      }
      return '/ch/' + pad(channel) + '/mix/' + pad(bus) + '/level'
    },
    auxin_target: () => (bus, channel) => {
      if (bus === 'main') {
        return '/auxin/' + pad(channel) + '/mix/fader'
      } else if (bus === 'mono') {
        return '/auxin/' + pad(channel) + '/mix/mlevel'
      }
      return '/auxin/' + pad(channel) + '/mix/' + pad(bus) + '/level'
    },
    fxrtn_target: () => (bus, channel) => {
      if (bus === 'main') {
        return '/fxrtn/' + pad(channel) + '/mix/fader'
      } else if (bus === 'mono') {
        return '/fxrtn/' + pad(channel) + '/mix/mlevel'
      }
      return '/fxrtn/' + pad(channel) + '/mix/' + pad(bus) + '/level'
    }

  }
}
