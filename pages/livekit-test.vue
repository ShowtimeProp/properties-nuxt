<template>
  <div>
    <LiveKitTest />
  </div>
</template>

<script setup>
import LiveKitTest from '../livekit-examples/LiveKitTest.vue'

// Meta para la página
useHead({
  title: 'LiveKit Echo Agent Test',
  meta: [
    { name: 'description', content: 'Prueba del Echo Agent de LiveKit' }
  ]
})
</script>
