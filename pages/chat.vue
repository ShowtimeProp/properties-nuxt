<template>
  <div>
    <ClientChat />
  </div>
</template>

<script setup>
import ClientChat from '../livekit-examples/ClientChat.vue'

useHead({
  title: 'Chat con Agente Inmobiliario',
  meta: [
    { name: 'description', content: 'Conversa con tu agente inmobiliario inteligente' }
  ]
})
</script>
