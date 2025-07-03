<template>
  <TopNavBar />
  <NuxtPage />
  <ChatBot />
</template>

<script setup>
import TopNavBar from '~/components/TopNavBar.vue'
import ChatBot from '~/components/ChatBot.vue'
</script>

<style>
html, body, #__nuxt, #__layout {
  height: 100%;
  min-height: 100%;
  margin: 0;
  padding: 0;
}
/* Mover el botón del inspector de Nuxt Devtools al ángulo inferior izquierdo */
#__nuxt-devtools-toggle {
  top: unset !important;
  left: 16px !important;
  bottom: 16px !important;
  right: unset !important;
  z-index: 99999 !important;
}
</style>
