<template>
 <div>
   <q-toolbar class="bg-purple text-white">
     <q-btn flat round dense icon="menu" />
     <q-toolbar-title>
       Open a session
     </q-toolbar-title>
     <q-btn label="Logout" @click="$store.dispatch('logout')"></q-btn>
   </q-toolbar>
   <q-input v-model="name"></q-input>
   <q-btn label="Start session" @click="$store.dispatch('session_start', name)"></q-btn>

   <q-list>
     <q-item v-for="session in sessions" :key="session.id">
       <q-item-section  @click="$store.dispatch('session_open', session.id)">
         {{ session.name }}
       </q-item-section>
     </q-item>
   </q-list>
 </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Recorder',
  data () {
    return {
      name: 'Probe'
    }
  },

  computed: {
    ...mapGetters(['sessions'])
  }
}
</script>
