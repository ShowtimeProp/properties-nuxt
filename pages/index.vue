<template>
  <div class="flex flex-col h-screen">
    <TopNavBar />
    <div class="flex-1 min-h-0">
      <PropertyMap />
    </div>
  </div>
</template>

<script setup>
import TopNavBar from '~/components/TopNavBar.vue'
import PropertyMap from '~/components/PropertyMap.vue'
</script>

<style>
/* Los estilos ahora están dentro del componente PropertyMap.vue */
</style>