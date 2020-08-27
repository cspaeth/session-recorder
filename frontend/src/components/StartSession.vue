<template>
 <div>
   <q-input v-model="name"></q-input>
   <q-btn label="Start session" @click="$store.dispatch('session_start', name)"></q-btn>
 </div>
</template>

<script>
export default {
  name: 'Recorder',
  data () {
    return {
      name: 'Probe'
    }
  }
}
</script>
