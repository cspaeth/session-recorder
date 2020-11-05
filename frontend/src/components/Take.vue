
<template>
  <q-expansion-item
    icon="explore"
    :label="take_label"
    :caption="take.started_at"
    header-class="text-primary"
    :value="active_take_number === take.number"
    @input="$store.dispatch('take_select', take.number)">
    <q-card>

      <q-card-section>
        <q-icon name="cloud_off" v-if="take.state === 'recorded'" @click="take_queue(take.number)" size="md"></q-icon>
        <q-icon name="cloud_queue" v-if="take.state === 'queued'" @click="take_unqueue(take.number)" size="md"></q-icon>
        <q-icon name="cloud_upload" v-if="take.state === 'processing'" size="md"></q-icon>
        <q-icon name="cloud_done" v-if="take.state === 'uploaded'" size="md"></q-icon>
      </q-card-section>
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
    ...mapActions(['take_seek', 'take_queue', 'take_unqueue'])
  },

  computed: {
    take_label () {
      return 'Take ' + this.take.number + ' - ' + this.take.name
    },
    ...mapGetters(['active_take_number', 'position_in_take'])

  }
}
</script>
