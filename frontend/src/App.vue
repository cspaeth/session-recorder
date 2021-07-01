<template>
  <div id="q-app" >
    <q-layout view="hHh lpR fFf">

      <q-header elevated :class="bus_color(bus)">
        <q-toolbar >
          <q-btn dense flat round icon="menu" @click="left = !left" />

          <q-toolbar-title >
            <div class="text-h6">{{ bus_name(bus) }}</div>
            <Fader :target="master_target(bus)">
            </Fader>

          </q-toolbar-title>
        </q-toolbar>
      </q-header>

      <q-drawer show-if-above v-model="left" side="left" elevated>
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
            <q-item-section>{{ bus_name('mono') }}</q-item-section>
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
import Fader from './components/Fader'

export default {
  data () {
    return {
      bus: 'main',
      left: null
    }
  },
  name: 'App',
  components: { Mixer, Fader },
  computed: {
    ...mapGetters(['connection_state', 'bus_name', 'bus_color', 'visible_buses', 'master_target'])
  },
  methods: {
    go_to_bus (bus) {
      this.left = false
      this.bus = bus
    }
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
</style>
