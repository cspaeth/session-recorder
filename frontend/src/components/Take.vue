
<template>
  <q-expansion-item
    icon="explore"
    :label="take_label"
    caption="12:32"
    header-class="text-primary"
    :value="active_take_number === take.number"
    @input="$store.dispatch('take_select', take.number)">
    <q-card>
      <q-card-section>
        <q-slider @input="(val) => take_seek(val/100)" :value="position_in_take*100" :min="0" :max="take.length*100"></q-slider>
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Take',
  props: ['take'],
  data () {
    return {
      position: 0
    }
  },

  methods: {
    ...mapActions(['take_seek'])
  },

  computed: {
    take_label () {
      return 'Take ' + this.take.number + ' - ' + this.take.name
    },
    ...mapGetters(['active_take_number', 'position_in_take'])

  }
}
</script>
