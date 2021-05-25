<template>
  <div id="q-app" >

    <div>
      <q-toolbar class="bg-purple text-white">
        <q-btn flat round dense icon="menu" />
        <q-toolbar-title>
          Mix
        </q-toolbar-title>
      </q-toolbar>

      <div>

          <Fader v-for="index in 32" :key="index"
                 :target="'/ch/' + pad(index) + '/mix/fader'"
                 :name="index + ' - ' + $store.state.mixer.osc['/ch/' + pad(index) + '/config/name']">
          </Fader>

      </div>
      <div >
        <div v-for="index in 8" :key="index" >

          <Fader :target="'/fxrtn/' + pad(index) + '/mix/fader'" :name="index + ' - ' + $store.state.mixer.osc['/fxrtn/' + pad(index) + '/config/name']"></Fader>

        </div>
      </div>
      <div >
        <div v-for="index in 8" :key="index" >

          <Fader :target="'/auxin/' + pad(index) + '/mix/fader'" :name="index + ' - ' + $store.state.mixer.osc['/auxin/' + pad(index) + '/config/name']"></Fader>

        </div>
      </div>
      <div >
        <div v-for="index in 16" :key="index" >

          <Fader :target="'/bus/' + pad(index) + '/mix/fader'" :name="index + ' - ' + $store.state.mixer.osc['/bus/' + pad(index) + '/config/name']"></Fader>

        </div>
      </div>
    </div>
    <q-inner-loading :showing="connection_state !== 'connected'">
      <q-spinner-gears size="50px" color="primary" v-if="connection_state === 'connecting'"></q-spinner-gears>
      <q-btn @click="$store.$socket.reconnect()" label="Verbinden" v-if="connection_state === 'disconnected'"></q-btn>
    </q-inner-loading>

  </div>
</template>
<script>

import { mapGetters } from 'vuex'
import Fader from './components/Fader'

export default {
  name: 'App',
  components: { Fader },
  computed: {
    ...mapGetters(['current_user', 'recorder_state', 'connection_state'])
  },
  methods: {
    pad (i) {
      return i < 10 ? '0' + i : i
    }
  }
}
</script>
