<template>
  <div class="dashboard-page">
    <RealtorDashboard />
  </div>
</template>

<script setup>
import RealtorDashboard from '~/components/RealtorDashboard.vue'

// Meta tags para SEO
useHead({
  title: 'Dashboard Realtor - ShowtimeProp',
  meta: [
    { name: 'description', content: 'Dashboard profesional para realtores inmobiliarios' }
  ]
})

// Middleware para verificar autenticación de realtor
definePageMeta({
  middleware: 'realtor-auth'
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
}
</style>
