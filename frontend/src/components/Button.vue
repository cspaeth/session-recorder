<template>
  <div>
    <q-toggle @input="(val) => ocs_send([$props.target, val ? 1 : 0])" :value="ocs_value"></q-toggle>
  </div>

</template>

<script>

import { mapActions } from 'vuex'

export default {

  props: ['target'],

  computed: {
    ocs_value () {
      return this.$store.state.mixer.osc[this.$props.target] === 1
    }
  },
  methods: {
    ...mapActions(['ocs_send'])
  },
  name: 'Recorder'
}
</script>
