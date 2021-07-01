<!---->
<template>
  <q-page>
    <div>
      <q-card flat bordered
              v-for="index in 32"
              :key="'ch' + index"
              :class="channel_color(index)">
        <q-card-section >
            <Fader :target="channel_target(bus, index)"
                   :name="channel_name(index)">
            </Fader>
        </q-card-section>
      </q-card>

      <q-card flat bordered
              v-for="index in 8"
              :key="'auxin-' + index"
              :class="auxin_color(index)">
        <q-card-section >
          <Fader :target="auxin_target(bus, index)"
                 :name="auxin_name(index)">
          </Fader>
        </q-card-section>
      </q-card>

      <q-card flat bordered
              v-for="index in 8"
              :key="'fxrtn-' + index"
              :class="fxrtn_color(index)">
        <q-card-section >
          <Fader :target="fxrtn_target(bus, index)"
                 :name="fxrtn_name(index)">
          </Fader>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script>

import Fader from './Fader'
import { mapGetters } from 'vuex'

export default {
  name: 'Recorder',
  props: ['bus'],
  components: { Fader },
  computed: {
    ...mapGetters(['bus_name', 'channel_name', 'auxin_name', 'fxrtn_name', 'master_target', 'channel_target', 'auxin_target', 'fxrtn_target',
      'channel_color', 'auxin_color', 'fxrtn_color', 'bus_color'])
  }

}
</script>
<style scoped>

</style>
