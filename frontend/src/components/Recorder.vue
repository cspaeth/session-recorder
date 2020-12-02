<template>
  <div>
    <q-select
      v-if="recorder_state === 'ready'"
      fill-input
      use-input
      :value="next_take_name"
      @input-value="(val) => $store.dispatch('set_next_take_name', val)"
      hide-selected
      :options="song_titles"
      label="Name des nächten Takes"></q-select>

    <div v-if="recorder_state === 'recording'" class="text-h3">Take {{ active_take.number }}: {{ active_take.name }} ({{position_in_take}})</div>
    <q-btn  size="35px"
            round
            color="red"
            icon="fiber_manual_record"
            @click="$store.dispatch('take_start', next_take)"
            v-if="recorder_state === 'ready'"></q-btn>
    <q-btn  size="35px"
            round
            color="black"
            icon="stop"
            @click="$store.dispatch('take_stop')"
            v-if="recorder_state === 'recording'"></q-btn>
    <q-btn  size="20px"
            round
            color="red"
            icon="cancel"
            @click="$store.dispatch('take_cancel')"
            v-if="recorder_state === 'recording'"></q-btn>

    <q-toggle @input="(val) => set_metronome_state(val)" :value="$store.state.recorder.metronome === 1">Metronom</q-toggle>
    <q-input  @input="(val) => set_next_take_tempo(val)" :value="$store.state.session.next_take.tempo" label="Tempo (BPM)"></q-input>

    <div v-for="index in 24" :key="index" >
      <span class="text-h6">{{index}}</span>
      <q-toggle @input="(val) => set_track_armed([index - 1, val])" :value="$store.state.recorder.channels[index - 1] === 1">
        {{$store.state.mixer.osc['/ch/' + pad(index) + '/config/name']}}
      </q-toggle>
      <Fader :target="'/headamp/0' + pad($store.state.mixer.osc['/-ha/' + pad(index-1)+ '/index']) + '/gain'"></Fader>

      <Button :target="'/headamp/0' + pad($store.state.mixer.osc['/-ha/' + pad(index-1)+ '/index']) + '/phantom'"
          v-if="$store.state.mixer.osc['/-ha/' + pad(index-1)+ '/index'] !== -1"></Button>

      <Fader :target="'/ch/' + pad(index) + '/mix/fader'" ></Fader>

    </div>

    <q-inner-loading :showing="recorder_state === 'playing'">
      <q-btn  size="35px"
              round
              color="black"
              icon="stop"
              @click="$store.dispatch('stop')"
            ></q-btn>
    </q-inner-loading>
  </div>
</template>

<script>

import { mapGetters, mapActions } from 'vuex'
import Fader from './Fader'
import Button from './Button'

export default {
  name: 'Recorder',
  components: { Fader, Button },
  data: () => {
    return {
      next_take_name: ''
    }
  },

  watch: {
    next_take: {
      immediate: true,
      handler (newValue) {
        this.next_take_name = newValue.name
      }
    }
  },
  computed: {
    ...mapGetters(['recorder_state', 'active_take', 'next_take', 'position_in_take']),
    song_titles () {
      return [...new Set(this.$store.getters.all_takes.map((take) => take.name))]
    }
  },
  methods: {
    pad (i) {
      return i < 10 ? '0' + i : i
    },
    ...mapActions(['set_track_armed', 'set_metronome_state', 'set_next_take_tempo'])

  }
}
</script>
