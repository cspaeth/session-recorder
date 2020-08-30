<template>
  <div id="q-app" >

    <Login v-if="current_user == null"></Login>
    <StartSession v-else-if="recorder_state === 'connected'"></StartSession>
    <Session v-else></Session>

    <q-inner-loading :showing="connection_state !== 'connected'">
      <q-spinner-gears size="50px" color="primary" v-if="connection_state === 'connecting'"></q-spinner-gears>
      <q-btn @click="$store.$socket.reconnect()" label="Erneut Verbinden" v-if="connection_state === 'disconnected'"></q-btn>
    </q-inner-loading>

  </div>
</template>
<script>

import Login from './components/Login'
import StartSession from './components/StartSession'
import Session from './components/Session'
import { mapGetters } from 'vuex'
export default {
  name: 'App',
  components: { Login, Session, StartSession },

  computed: {
    ...mapGetters(['current_user', 'recorder_state', 'connection_state'])
  }

}
</script>
