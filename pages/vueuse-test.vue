<template>
  <div class="p-8 space-y-4">
    <h1 class="text-2xl font-bold">Página de Pruebas</h1>
    
    <!-- Grid de PropertySlideCardClean -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <PropertySlideCardClean v-for="i in 4" :key="i" />
    </div>
  </div>
</template>

<script setup>
import PropertySlideCardClean from '~/components/PropertySlideCardClean.vue'
</script>