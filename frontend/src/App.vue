<template>
  <div id="q-app" >
    <q-layout view="hHh lpR fFf">

      <q-header elevated class="bg-primary text-white">
        <q-toolbar>
          <q-btn dense flat round icon="menu" @click="left = !left" />

          <q-toolbar-title>
            X32 Mixer

          </q-toolbar-title>
        </q-toolbar>
      </q-header>

      <q-drawer show-if-above v-model="left" side="left" elevated>
        <q-list bordered separator>
          <q-item clickable v-ripple  :active="bus == null" @click="bus = null">
            <q-item-section>Main</q-item-section>
          </q-item>

          <q-item clickable v-ripple
                  v-for="index in 12" :key="index"
                  @click="bus = index"
                  :active="bus == index">
            <q-item-section>{{bus_name(index)}}</q-item-section>
          </q-item>
        </q-list>

      </q-drawer>

      <q-page-container>

        <Mixer :bus="bus"></Mixer>
      </q-page-container>

    </q-layout>

    <q-inner-loading :showing="connection_state !== 'connected'">
      <q-spinner-gears size="50px" color="primary" v-if="connection_state === 'connecting'"></q-spinner-gears>
      <q-btn @click="$store.$socket.reconnect()" label="Verbinden" v-if="connection_state === 'disconnected'"></q-btn>
    </q-inner-loading>

  </div>
</template>
<script>

import { mapGetters } from 'vuex'
import Mixer from './components/Mixer'

export default {
  data () {
    return {
      bus: null,
      left: null
    }
  },
  name: 'App',
  components: { Mixer },
  computed: {
    ...mapGetters(['current_user', 'connection_state'])
  },
  methods: {
    pad (i) {
      return i < 10 ? '0' + i : i
    },
    bus_color (bus) {
      const path = '/bus/' + this.pad(bus) + '/config/color'
      return 'x32-color-' + this.$store.state.mixer.osc[path]
    },
    bus_name (bus) {
      if (bus) {
        const path = '/bus/' + this.pad(bus) + '/config/name'
        return this.$store.state.mixer.osc[path]
      }
      return 'Main L/R'
    }
  }

}
</script>
<style>
  .x32-color-1 {
    background: green;
  }
  .x32-color-2 {
    background: blue;
  }
  .q-item--active {
    background: lightgrey;
  }
</style>
