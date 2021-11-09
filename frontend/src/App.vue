<template>
  <div id="q-app" >
    <q-layout view="lHh lpR fFf">

      <q-header elevated :class="bus_color(bus)">
        <q-toolbar >
          <q-btn dense flat round icon="menu" @click="left = !left" />

          <q-toolbar-title >
            <div class="text-h6">{{ bus_name(bus) }}</div>
            <Fader :target="master_target(bus)">
            </Fader>

          </q-toolbar-title>
          <q-btn dense flat round icon="menu" @click="right = !right" />

        </q-toolbar>
      </q-header>

      <q-drawer show-if-above v-model="left" side="left" elevated ref="leftDrawer">
        <q-list bordered separator class="bus-list">
          <q-item clickable v-ripple
                  :active="bus == 'main'"
                  @click="go_to_bus('main')"
                  :class="bus_color('main')">
            <q-item-section>{{ bus_name('main') }}</q-item-section>
          </q-item>
          <q-item clickable v-ripple
                  :active="bus == 'mono'"
                  @click="go_to_bus('mono')"
                  :class="bus_color('mono')">
            <q-item-section>{{ bus_name('mono') }}  </q-item-section>
          </q-item>

          <q-item clickable v-ripple
                  v-for="index in visible_buses" :key="index"
                  @click="go_to_bus(index)"
                  :active="bus == index"
                  :class="bus_color(index)">
            <q-item-section>{{ bus_name(index) }}</q-item-section>
          </q-item>
        </q-list>

      </q-drawer>

      <q-drawer  v-model="right" side="right" elevated >

        <Button target="/config/routing/routswitch" title="Multitrack Playback"></Button>
        <br>
        <Button target="/config/mute/1" title="Talkback"></Button>
        <Button target="/config/mute/2" title="DAW Playback"></Button>
        <Button target="/config/mute/3" title="DAW Main"></Button>
        <Button target="/config/mute/4" title="Input Channels"></Button>
        <Button target="/config/mute/5" title="Mix Buses"></Button>
        <br>
        <q-btn @click="store_mix()" label="Store Mix"></q-btn>
        <q-btn @click="load_mix()" label="Restore Mix"></q-btn>

      </q-drawer>
      <q-page-container >

        <Mixer :bus="bus"></Mixer>
        <q-page-sticky position="bottom-right" :offset="[18, 18]">
          <Button target="/config/mute/1" title="Talkback"></Button>
        </q-page-sticky>
      </q-page-container>

    </q-layout>

    <q-inner-loading :showing="connection_state !== 'connected'">
      <q-spinner-gears size="50px" color="primary" v-if="connection_state === 'connecting'"></q-spinner-gears>
      <q-btn @click="$store.$socket.reconnect()" label="Verbinden" v-if="connection_state === 'disconnected'"></q-btn>
    </q-inner-loading>

  </div>
</template>
<script>

import { mapGetters, mapActions } from 'vuex'
import Mixer from './components/Mixer'
import Fader from './components/Fader'
import Button from './components/Button'

export default {
  data () {
    return {
      bus: 'mono',
      left: null,
      right: false
    }
  },
  name: 'App',
  components: { Mixer, Fader, Button },
  computed: {
    ...mapGetters(['connection_state', 'bus_name', 'bus_color', 'visible_buses', 'master_target', 'channel_target'])
  },
  methods: {
    go_to_bus (bus) {
      if (this.$refs.leftDrawer.belowBreakpoint) {
        this.left = false
      }
      this.bus = bus
    },

    store_mix () {
      // console.log(this.$q.localSt  orage.getItem('test'))

      const mix = []
      mix.push(this.$store.state.mixer.osc[this.master_target(this.bus)])

      for (let ch = 1; ch <= 32; ch++) {
        mix.push(this.$store.state.mixer.osc[this.channel_target(this.bus, ch)])
      }

      console.log(mix)
      this.$q.localStorage.set('mix', mix)
    },

    load_mix () {
      const mix = this.$q.localStorage.getItem('mix')
      console.log(mix)

      this.ocs_send([this.master_target(this.bus), mix.shift()])
      //
      for (let ch = 1; ch <= 32; ch++) {
        this.ocs_send([this.channel_target(this.bus, ch), mix.shift()])
      }

      // console.log(mix)
      // this.$q.localStorage.set('mix', mix)
    },

    ...mapActions(['ocs_send'])
  }
}
</script>
<style>
  .q-layout__section--marginal {
    color: inherit;
  }
  .x32-color-0 {
    background: black;
    color: lightgray;
  }
  .x32-color-1 {
    background: red;
  }
  .x32-color-2 {
    background: limegreen;
  }
  .x32-color-3 {
    background: yellow;
  }
  .x32-color-4 {
    background: dodgerblue;
  }
  .x32-color-5 {
    background: deeppink;
  }
  .x32-color-6 {
    background: lightblue;
  }
  .x32-color-7 {
    background: white;
  }
  .x32-color-8 {
    background: lightgray;
  }

  .x32-color-9 {
    background: black;
    color: red;
  }
  .x32-color-10 {
    background: black;
    color: limegreen;
  }

  .x32-color-11 {
    background: black;
    color: yellow;
  }
  .x32-color-12 {
    background: black;
    color: dodgerblue;
  }
  .x32-color-13 {
    background: black;
    color:deeppink;
  }
  .x32-color-14 {
    background: black;
    color: lightblue;
  }
  .x32-color-15 {
    background: black;
    color: white;
  }
  .x32-color-16 {
    background: black;
    color: lightgray;
  }

  .bus-list {
    font-weight: bold;
  }

  .q-item--active {
    color: inherit;
    border-left: 5px solid indigo;
  }
  .q-inner-loading {
    z-index: 10000;
  }
</style>
