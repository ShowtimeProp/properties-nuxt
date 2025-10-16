<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Procesando autenticación...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

const { handleGoogleAuthCallback } = useRealtorAuth()

onMounted(async () => {
  try {
    console.log('Callback de Google Auth iniciado...')
    await handleGoogleAuthCallback()
  } catch (error) {
    console.error('Error en callback:', error)
    // Redirigir al login si hay error
    await navigateTo('/realtor-login')
  }
})

// Meta para evitar indexación
definePageMeta({
  layout: false
})
</script>
