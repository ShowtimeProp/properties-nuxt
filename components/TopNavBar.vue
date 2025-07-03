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
          <!-- Logo y menú principal -->
          <div class="flex items-center gap-8 flex-1">
            <span class="text-2xl font-bold text-indigo-700 tracking-tight select-none">Showtime Prop</span>
            <div class="flex gap-6 text-sm font-medium text-gray-700">
              <a href="#" class="hover:text-indigo-600">Comprar</a>
              <a href="#" class="hover:text-indigo-600">Alquilar</a>
              <a href="#" class="hover:text-indigo-600">Vender</a>
              <a href="#" class="hover:text-indigo-600">Conseguir crédito</a>
            </div>
          </div>
          <!-- Acciones a la derecha -->
          <div class="flex gap-6 text-sm font-medium text-gray-700">
            <a href="#" class="hover:text-indigo-600">Publicar</a>
            <a href="#" class="hover:text-indigo-600">Ingresar</a>
          </div>
        </div>
      </transition>
      <!-- Barra inferior -->
      <div
        class="flex items-center gap-3 px-6 py-1 bg-white border-b"
      >
        <!-- Mensaje de ayuda -->
        <!-- Buscador principal simple y moderno -->
        <div class="flex items-center w-full max-w-xl mx-auto">
          <input
            v-model="searchText"
            type="text"
            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 shadow-sm transition"
            placeholder="Buscar propiedades con tu voz -->"
            @focus="showHelp = true"
            @blur="showHelp = false"
          />
          <button
            @click="toggleListening"
            :aria-label="listening ? 'Escuchando...' : 'Buscar por voz'"
            class="ml-2 flex items-center justify-center h-10 w-10 rounded-full bg-white border border-gray-300 text-indigo-600 hover:bg-indigo-50 transition"
          >
            <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75v1.5m0 0h3m-3 0h-3m6-6.75a3 3 0 11-6 0v-3a3 3 0 116 0v3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-6 h-6 animate-bounce">
              <path d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4zm5 10a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 9a7 7 0 007-7h-2a5 5 0 01-10 0H5a7 7 0 007 7z"/>
            </svg>
          </button>
        </div>
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
const showHelp = ref(false)

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
      // Disparar búsqueda automáticamente
      onSearch()
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