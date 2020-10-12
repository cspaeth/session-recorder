<template>
  <div>
    <q-toolbar class="bg-purple text-white">
      <q-btn flat round dense icon="menu" />
      <q-toolbar-title>
        {{ session_name }}
      </q-toolbar-title>
      <q-btn label="Close" @click="$store.dispatch('session_close')"></q-btn>

    </q-toolbar>

    <div style="max-width: 600px">
      <q-tabs v-model="mode">
        <q-tab name="record" icon="mail" label="Record"></q-tab>
        <q-tab name="play" icon="alarm" label="Playback"></q-tab>
        <q-tab name="upload" icon="cloud" label="Upload"></q-tab>
      </q-tabs>

      <q-tab-panels v-model="mode" animated >
        <q-tab-panel name="record">
          <Recorder></Recorder>
        </q-tab-panel>
        <q-tab-panel name="play">
          <Player></Player>
        </q-tab-panel>
        <q-tab-panel name="upload">

        </q-tab-panel>
      </q-tab-panels>
    </div>
  </div>
</template>

<script>

import Recorder from './Recorder'
import Player from './Player'
import { mapGetters } from 'vuex'

export default {
  name: 'Session',
  components: { Recorder, Player },
  data () {
    return { mode: 'record' }
  },
  computed: {
    ...mapGetters(['session_name', 'recorder_state'])
  }
}
</script>
