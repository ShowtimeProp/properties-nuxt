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
</style>
