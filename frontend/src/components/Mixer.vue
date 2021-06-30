<!---->
<template>
  <q-page >

    <q-card flat bordered>
      <q-card-section >
        <div class="text-h6">{{ master_name() }}</div>
        <Fader :target="osc_target_master()" name="Master">
        </Fader>
      </q-card-section>

    </q-card>
    <div>
      <q-card flat bordered  v-for="index in 32" :key="index">
        <q-card-section >
            <Fader
                   :target="osc_target(index)"
                   :name="channel_name(index)">
            </Fader>
        </q-card-section>
      </q-card>
      <q-card flat bordered  v-for="index in 8" :key="'aux-' + index">
        <q-card-section >
          <Fader
            :target="osc_aux_target(index)"
            :name="aux_name(index)">
          </Fader>
        </q-card-section>
      </q-card>

    </div>

  </q-page>

</template>

<script>

// import { mapActions } from 'vuex'
import Fader from './Fader'

export default {
  props: ['bus'],

  components: { Fader },

  methods: {
    pad (i) {
      return i < 10 ? '0' + i : i
    },

    osc_target_master () {
      if (this.bus) {
        return '/bus/' + this.pad(this.bus) + '/mix/fader'
      }
      return '/main/st/mix/fader'
    },

    master_name () {
      if (this.bus) {
        const path = '/bus/' + this.pad(this.bus) + '/config/name'
        return this.$store.state.mixer.osc[path]
      }
      return 'Main L/R'
    },

    osc_aux_target (channel) {
      let suffix = '/mix/fader'
      if (this.bus) {
        suffix = '/mix/' + this.pad(this.bus) + '/level'
      }

      return '/auxin/' + this.pad(channel) + suffix
    },

    osc_target (channel) {
      let suffix = '/mix/fader'
      if (this.bus) {
        suffix = '/mix/' + this.pad(this.bus) + '/level'
      }

      return '/ch/' + this.pad(channel) + suffix
    },

    channel_name (channel) {
      const path = '/ch/' + this.pad(channel) + '/config/name'
      return channel + ' - ' + this.$store.state.mixer.osc[path]
    },

    aux_name (channel) {
      const path = '/auxin/' + this.pad(channel) + '/config/name'
      return 'Aux ' + channel + ' - ' + this.$store.state.mixer.osc[path]
    }

  },

  name: 'Recorder'
}
</script>
<style scoped>
  .fadergroup {
    max-width: 400px;
    min-width: 300px;
  }
  @media screen and (max-width: 500px){
    .fadergroup {
      width: 100%;

    }
  }
</style>
