<!---->
<template>
  <div >
    <span >{{name}}</span>
    <q-slider @input="(val) => ocs_send([$props.target, val/1000])" :value="ocs_value"  :min="0" :max="1000"> </q-slider>
  </div>

</template>

<script>

import { mapActions } from 'vuex'

export default {
  props: ['target', 'name'],

  computed: {
    ocs_value () {
      return this.$store.state.mixer.osc[this.$props.target] * 1000
    }
  },

  methods: {
    ...mapActions(['ocs_send'])
  },

  name: 'Recorder'
}
</script>
