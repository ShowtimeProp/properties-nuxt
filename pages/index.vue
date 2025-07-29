<template>
  <div class="relative min-h-screen bg-gray-50">
    <TopNavBar />
    <ClientOnly>
      <PropertyMap />
    </ClientOnly>
    <LoginModal />
    <ChatBot />
  </div>
</template>

<script setup>
import TopNavBar from '~/components/TopNavBar.vue'
import PropertyMap from '~/components/PropertyMap.vue'
import LoginModal from '~/components/LoginModal.vue'
import ChatBot from '~/components/ChatBot.vue'

// Define el layout si es necesario, o déjalo por defecto.
// definePageMeta({
//   layout: 'default' 
// });
</script>

<style scoped>
/* Estilos específicos para esta página si son necesarios */
</style>