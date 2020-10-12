<template>
  <div>
  <q-toolbar class="bg-purple text-white">
    <q-btn flat round dense icon="menu" />
    <q-toolbar-title>
      {{ session_name }}
    </q-toolbar-title>
    <q-btn label="Close" @click="$store.dispatch('session_close')"></q-btn>

  </q-toolbar>
  <q-input v-model="login"></q-input>
  <q-btn label="Anmelden" @click="$store.dispatch('login', {username: login})"></q-btn>
  </div>
</template>

<script>
export default {
  data () {
    return {
      login: 'cspaeth'
    }
  },
  name: 'Recorder'
}
</script>
