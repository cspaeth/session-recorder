
<template>
  <q-expansion-item
    icon="explore"
    :label="take_label"
    caption="12:32"
    header-class="text-primary"
    :value="active_take == take.number"
    @input="$store.dispatch('take_select', take.number)">
    <q-card>
      <q-card-section>
        <q-slider v-model="position" :min="0" :max="50"></q-slider>
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Take',
  props: ['take'],
  data () {
    return {
      position: 0
    }
  },

  methods: {
    test () {
    }
  },

  computed: {
    take_label () {
      return 'Take ' + this.take.number + ' - ' + this.take.name
    },
    ...mapGetters(['active_take'])

  }
}
</script>
