// A websocket plugin with auto reconnect
// Will try to reconnect every RETRY_INTERVAL msecs for RETRY_TIMEOUT msecs
// Reconnect can be triggered by calling store.$socket.reconnect()

const RETRY_TIMEOUT = 5000
const RETRY_INTERVAL = 1000

export default function webSocketPlugin (store) {
  let retry = true
  let giveUpTimeout = null

  function onMessage (e) {
    const data = JSON.parse(e.data)
    store.commit('SOCKET_' + data.action, data.data)
  }
  function onOpen () {
    store.dispatch('update_connection_state', 'connected')
  }

  function onClose () {
    if (retry) {
      store.dispatch('update_connection_state', 'connecting')
      setTimeout(openConnection, RETRY_INTERVAL)
    } else {
      store.dispatch('update_connection_state', 'disconnected')
    }
  }

  function giveUp () {
    giveUpTimeout = null
    if (store.$socket.readyState !== 1) {
      retry = false
    }
  }

  function connect () {
    if (store.state.connectionState === 'disconnected') {
      retry = true
      openConnection()
    }
  }

  function openConnection () {
    if (store.$socket && store.$socket.readyState === 1) {
      console.log('already connected!')
      return
    }

    if (!giveUpTimeout) {
      giveUpTimeout = setTimeout(giveUp, RETRY_TIMEOUT)
    }

    console.log('connecting web socket')
    store.dispatch('update_connection_state', 'connecting')
    // TODO Hardcoded URL
    store.$socket = new WebSocket('ws://' + window.location.hostname + ':8000/ws/remote/')
    store.$socket.onmessage = onMessage
    store.$socket.onopen = onOpen
    store.$socket.onclose = onClose
    store.$socket.reconnect = connect
  }
  connect()
}
