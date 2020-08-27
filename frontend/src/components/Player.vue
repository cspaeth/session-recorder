<template>
 <div>
   <q-list bordered>
      <Take :take="take" v-for="take in all_takes" :key="take.number"></Take>

   </q-list>

 </div>
</template>

<script>

import Take from './take'
import { mapGetters } from 'vuex'

export default {
  name: 'Recorder',
  components: { Take },
  computed: {
    ...mapGetters(['all_takes'])
  }
}
</script>
