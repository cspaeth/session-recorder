import Vue from 'vue'
import Vuex from 'vuex'
import session from './session'
import webSocketPlugin from './ws'
import auth from './auth'

// import example from './module-example'

Vue.use(Vuex)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export default function (/* { ssrContext } */) {
  const Store = new Vuex.Store({
    state: {
      connectionState: 'disconnected'
    },
    modules: {
      session,
      auth
    },

    actions: {
      update_connection_state (context, connectionState) {
        context.commit('UPDATE_CONNECTION_STATE', connectionState)
      }
    },

    mutations: {
      UPDATE_CONNECTION_STATE (state, connectionState) {
        state.connectionState = connectionState
      }
    },

    getters: {
      connection_state: (state) => state.connectionState
    },

    // enable strict mode (adds overhead!)
    // for dev mode only
    strict: process.env.DEV,
    plugins: [webSocketPlugin]
  })

  return Store
}
