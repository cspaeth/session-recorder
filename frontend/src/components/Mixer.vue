<!---->
<template>
  <q-page>
    <div class="row q-pa-sm">
      <div class="channel"
           v-for="index in 32"
           :key="'ch' + index">
        <q-card flat bordered :class="channel_color(index)">
          <q-card-section >
            <Fader :target="channel_target(bus, index)"
                   :name="index + ' - ' + channel_name(index)">
            </Fader>
          </q-card-section>
        </q-card>
      </div>

      <div class="channel"
           v-for="index in 8"
           :key="'auxin-' + index">
        <q-card flat bordered :class="auxin_color(index)">
          <q-card-section >
            <Fader :target="auxin_target(bus, index)"
                   :name="'Aux ' + index + ' - ' + auxin_name(index)">
            </Fader>
          </q-card-section>
        </q-card>

      </div>
      <div class="channel"
           v-for="index in 8"
           :key="'fxrtn-' + index">
        <q-card flat bordered
                :class="fxrtn_color(index)">
          <q-card-section >
            <Fader :target="fxrtn_target(bus, index)"
                   :name="fxrtn_name(index)">
            </Fader>
          </q-card-section>
        </q-card>
      </div>
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
      'channel_color', 'auxin_color', 'fxrtn_color', 'bus_color', 'channel_mute_target'])
  },
  methods: {
    is_muted (channel) {
      return !this.$store.state.mixer.osc[this.channel_mute_target(this.bus, channel)]
    }
  }

}
</script>
<style >
  .channel{
    flex-basis:25%;
    padding:4px
  }
  .q-card__section--vert {
    padding: 4px 16px;

  }
  .q-slider {
    height: 20px;
  }
  @media screen and (max-width: 600px) {
    .channel {
      flex-basis: 100%;
    }
  }

</style>
