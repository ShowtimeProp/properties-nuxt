<template>
  <div class="relative min-h-screen bg-gray-50">
    <ClientOnly>
      <div v-if="isDashboardSubdomain">
        <DashboardRedirect />
      </div>
      <div v-else>
        <TopNavBar />
        <PropertyMap />
        <LoginModal />
      </div>
    </ClientOnly>
  </div>
</template>

<script setup>
import TopNavBar from '~/components/TopNavBar.vue'
import PropertyMap from '~/components/PropertyMap.vue'
import LoginModal from '~/components/LoginModal.vue'
// Ocultamos el ChatBot antiguo; será reemplazado por LiveKit
import DashboardRedirect from '~/components/DashboardRedirect.vue'

// Check if we're on the dashboard subdomain
const isDashboardSubdomain = computed(() => {
  if (process.client) {
    return window.location.hostname === 'dash.bnicolini.showtimeprop.com'
  }
  return false
})
</script>

<style scoped>
/* Estilos específicos para esta página si son necesarios */
</style>