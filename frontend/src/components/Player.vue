<template>
 <div>
   <q-btn  size="35px"
           round
           color="black"
           icon="play_arrow"
           @click="$store.dispatch('play')"
           v-if="recorder_state === 'ready'"></q-btn>
   <q-btn  size="35px"
           round
           color="black"
           icon="stop"
           @click="$store.dispatch('stop')"
           v-if="recorder_state === 'playing'"></q-btn>

   <q-btn  label="Upload"
           icon="cloud_upload"
           @click="session_upload"></q-btn>

   <q-list bordered>
      <Take :take="take" v-for="take in all_takes" :key="take.number"></Take>

   </q-list>

   <q-inner-loading :showing="recorder_state === 'recording'">
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

import Take from './take'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Recorder',
  components: { Take },

  methods: {
    ...mapActions(['session_upload'])
  },

  computed: {
    ...mapGetters(['all_takes', 'recorder_state'])
  }

}
</script>
