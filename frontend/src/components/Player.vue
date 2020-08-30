<template>
 <div>
   <q-btn  size="35px"
           round
           color="black"
           icon="play"
           @click="$store.dispatch('take_play', nexttake)"
           v-if="recorder_state === 'ready'"></q-btn>
   <q-btn  size="35px"
           round
           color="black"
           icon="stop"
           @click="$store.dispatch('take_stop')"
           v-if="recorder_state === 'playing'"></q-btn>

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
import { mapGetters } from 'vuex'

export default {
  name: 'Recorder',
  components: { Take },
  computed: {
    ...mapGetters(['all_takes', 'recorder_state'])
  }

}
</script>
