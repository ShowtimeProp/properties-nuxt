<template>
  <nav class="fixed top-0 left-0 w-full z-50 bg-white">
    <div
      class="group"
      @mouseenter="showTopMenu = true"
      @mouseleave="maybeHideMenu"
      @click="showTopMenu = true"
    >
      <!-- Barra superior (colapsable) -->
      <transition name="slide-down">
        <div v-if="showTopMenu" class="flex items-center justify-between px-6 h-14 border-b bg-white">
          <div class="flex gap-6 text-sm font-medium text-gray-700">
            <a href="#" class="hover:text-indigo-600">Comprar</a>
            <a href="#" class="hover:text-indigo-600">Alquilar</a>
            <a href="#" class="hover:text-indigo-600">Vender</a>
            <a href="#" class="hover:text-indigo-600">Conseguir crédito</a>
            <a href="#" class="hover:text-indigo-600">Encontrar agente</a>
          </div>
          <div class="flex-1 flex justify-center">
            <span class="text-2xl font-bold text-indigo-700 tracking-tight select-none">Propiedades</span>
          </div>
          <div class="flex gap-6 text-sm font-medium text-gray-700">
            <a href="#" class="hover:text-indigo-600">Mis alquileres</a>
            <a href="#" class="hover:text-indigo-600">Publicar</a>
            <a href="#" class="hover:text-indigo-600">Ayuda</a>
            <a href="#" class="hover:text-indigo-600">Ingresar</a>
          </div>
        </div>
      </transition>
      <!-- Barra inferior -->
      <div
        class="flex items-center gap-3 px-6 py-3 bg-white border-b"
      >
        <!-- Buscador principal -->
        <div class="flex items-center flex-1 bg-gray-100 rounded-lg shadow-inner px-3 py-2">
          <input
            v-model="searchText"
            type="text"
            class="flex-1 bg-transparent outline-none text-gray-700 placeholder-gray-400 text-base"
            placeholder="Dirección, barrio, ciudad, código postal"
          />
          <!-- Botón micrófono -->
          <button
            :class="['ml-2 p-2 rounded-full transition', listening ? 'bg-indigo-100 text-indigo-600 animate-pulse' : 'bg-white text-gray-400 hover:bg-indigo-50 hover:text-indigo-600']"
            @click="toggleListening"
            :aria-label="listening ? 'Escuchando...' : 'Buscar por voz'"
          >
            <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75v1.5m0 0h3m-3 0h-3m6-6.75a3 3 0 11-6 0v-3a3 3 0 116 0v3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-6 h-6 animate-bounce">
              <path d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4zm5 10a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 9a7 7 0 007-7h-2a5 5 0 01-10 0H5a7 7 0 007 7z"/>
            </svg>
          </button>
          <!-- Botón buscar -->
          <button class="ml-2 p-2 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white transition" @click="onSearch" aria-label="Buscar">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 104.5 4.5a7.5 7.5 0 0012.15 12.15z" />
            </svg>
          </button>
        </div>
        <!-- Filtros -->
        <div class="flex gap-2">
          <button class="filter-btn">En venta <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></button>
          <button class="filter-btn">Precio <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></button>
          <button class="filter-btn">Ambientes y baños <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></button>
          <button class="filter-btn">Tipo de propiedad <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></button>
          <button class="filter-btn">Más <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></button>
        </div>
        <!-- Guardar búsqueda -->
        <button class="ml-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow transition">Guardar búsqueda</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
const searchText = ref('')
const listening = ref(false)
let recognition = null
const showTopMenu = ref(false)
let hideTimeout = null

function onSearch() {
  // Aquí puedes manejar la búsqueda
  alert('Buscar: ' + searchText.value)
}

function toggleListening() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Tu navegador no soporta reconocimiento de voz.');
    return;
  }
  if (!recognition) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new SpeechRecognition()
    recognition.lang = 'es-ES'
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript
      searchText.value = result
      listening.value = false
    }
    recognition.onerror = () => {
      listening.value = false
    }
    recognition.onend = () => {
      listening.value = false
    }
  }
  if (!listening.value) {
    listening.value = true
    recognition.start()
  } else {
    listening.value = false
    recognition.stop()
  }
}

function maybeHideMenu() {
  // Espera un poco antes de ocultar para permitir click
  hideTimeout = setTimeout(() => {
    showTopMenu.value = false
  }, 300)
}

function handleDocumentClick(e) {
  // Si el click es fuera de la barra, oculta el menú
  const nav = document.querySelector('nav')
  if (nav && !nav.contains(e.target)) {
    showTopMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  if (hideTimeout) clearTimeout(hideTimeout)
})
</script>

<style scoped>
.filter-btn {
  @apply flex items-center gap-1 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow hover:bg-gray-100 text-gray-700 font-medium transition;
}
.slide-down-enter-active, .slide-down-leave-active {
  transition: max-height 0.3s cubic-bezier(0.4,0,0.2,1), opacity 0.3s cubic-bezier(0.4,0,0.2,1);
}
.slide-down-enter-from, .slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-down-enter-to, .slide-down-leave-from {
  max-height: 56px;
  opacity: 1;
}
</style> 