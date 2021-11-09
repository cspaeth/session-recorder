<template>
  <div>
    <q-btn  @click="ocs_send([$props.target, ocs_value ? 0 : 1])" color="red" :outline="!ocs_value">{{title}}</q-btn>
  </div>

</template>

<script>

import { mapActions } from 'vuex'

export default {

  props: ['target', 'title'],

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
