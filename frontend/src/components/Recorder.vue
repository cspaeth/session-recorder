<template>
  <div>
    <q-select
      v-if="recorder_state == 'idle'"
      fill-input
      use-input
      :value="next_take.name"
      @input-value="(val) => $store.dispatch('next_take_name', val)"
      hide-selected
      :options="['Song 1', 'Song 2']"
      label="Takename"></q-select>

    <div v-if="recorder_state == 'record'" class="text-h3">Take {{ active_take.number }}: {{ active_take.name }}</div>
    <q-btn  size="35px"
            round
            color="red"
            icon="fiber_manual_record"
            @click="$store.dispatch('take_start', nexttake)"
            v-if="recorder_state == 'idle'"></q-btn>
    <q-btn  size="35px"
            round
            color="black"
            icon="stop"
            @click="$store.dispatch('take_stop')"
            v-if="recorder_state == 'record'"></q-btn>
  </div>
</template>

<script>

import { mapGetters } from 'vuex'
export default {
  name: 'Recorder',
  data () {
    return { nexttake: 'testtake' }
  },
  computed: {
    ...mapGetters(['recorder_state', 'active_take', 'next_take'])

  }
}
</script>
