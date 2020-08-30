<template>
  <div>
    <q-select
      v-if="recorder_state === 'ready'"
      fill-input
      use-input
      :value="next_take.name"
      @input-value="(val) => $store.dispatch('next_take_name', val)"
      hide-selected
      :options="song_titles"
      label="Takename"></q-select>

    <div v-if="recorder_state === 'recording'" class="text-h3">Take {{ active_take.number }}: {{ active_take.name }} ({{position_in_take}})</div>
    <q-btn  size="35px"
            round
            color="red"
            icon="fiber_manual_record"
            @click="$store.dispatch('take_start', nexttake)"
            v-if="recorder_state === 'ready'"></q-btn>
    <q-btn  size="35px"
            round
            color="black"
            icon="stop"
            @click="$store.dispatch('take_stop')"
            v-if="recorder_state === 'recording'"></q-btn>
    <q-inner-loading :showing="recorder_state === 'playing'">
      <q-btn  size="35px"
              round
              color="black"
              icon="stop"
              @click="$store.dispatch('take_stop')"
            ></q-btn>
    </q-inner-loading>
  </div>
</template>

<script>

import { mapGetters } from 'vuex'
export default {
  name: 'Recorder',

  computed: {
    ...mapGetters(['recorder_state', 'active_take', 'next_take', 'position_in_take']),
    song_titles () {
      return this.$store.getters.all_takes.map((take) => take.name)
    }
  }
}
</script>
