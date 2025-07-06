<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <LoginModal :show="showLoginModal" @close="showLoginModal = false" />
    <TopNavBar @open-login="showLoginModal = true"/>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import LoginModal from '~/components/LoginModal.vue';
import TopNavBar from '~/components/TopNavBar.vue';

const showLoginModal = ref(false);

// Ya no necesitamos el listener onAuthStateChange aquí.
// La reactividad se manejará directamente en los componentes que lo necesiten (como TopNavBar).
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
