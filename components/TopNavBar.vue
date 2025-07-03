<template>
  <nav class="fixed top-0 left-0 w-full z-50 bg-black shadow-lg" @mouseenter="showTopMenu = true" @mouseleave="maybeHideMenu">
    <!-- Primer renglón: Logo y menú, colapsable -->
    <div class="flex justify-between items-center w-full px-6 pt-3">
    </div>
    <transition name="slide-down">
      <div v-if="showTopMenu" class="flex flex-col items-center w-full bg-black mt-3">
        <span class="text-2xl font-bold text-white tracking-tight select-none mb-1">Showtime Prop</span>
        <div class="flex gap-8 text-sm font-medium text-white mb-2 items-center">
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Comprar</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Alquilar</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Vender</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Créditos Hipotecarios</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Listar Tu Propiedad</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Blog Inmobiliario</a>
          <button class="ml-4 px-4 py-2 rounded-lg animated-gradient-bg text-white font-bold shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors text-sm flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9A3.75 3.75 0 1112 5.25 3.75 3.75 0 0115.75 9zM4.5 19.5a7.5 7.5 0 1115 0v.75a.75.75 0 01-.75.75h-13.5a.75.75 0 01-.75-.75v-.75z" />
            </svg>
            Iniciar Sesión
          </button>
        </div>
      </div>
    </transition>
    <!-- Segundo renglón: Buscador siempre visible -->
    <div class="flex items-center w-full max-w-xl mx-auto py-2 bg-black">
      <input
        v-model="searchText"
        type="text"
        class="flex-1 rounded-lg border border-cyan-400 bg-gray-900 text-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 shadow-sm transition placeholder-gray-400"
        placeholder="Buscar propiedades con tu voz -->"
        @focus="showHelp = true; showTopMenu = true"
        @blur="showHelp = false"
        @mouseenter="showTopMenu = true"
        @mouseleave="maybeHideMenu"
      />
      <button
        @click="toggleListening"
        :aria-label="listening ? 'Escuchando...' : 'Buscar por voz'"
        class="ml-2 flex items-center justify-center h-10 w-10 rounded-full bg-gray-900 border border-gray-700 text-cyan-400 hover:bg-cyan-400 hover:text-black transition"
      >
        <span class="relative z-10 flex items-center justify-center w-full h-full">
          <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="white" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75v1.5m0 0h3m-3 0h-3m6-6.75a3 3 0 11-6 0v-3a3 3 0 116 0v3z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" class="w-6 h-6 animate-bounce">
            <path d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4zm5 10a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 9a7 7 0 007-7h-2a5 5 0 01-10 0H5a7 7 0 007 7z"/>
          </svg>
        </span>
      </button>
      <button
        class="ml-3 px-4 py-2 rounded-lg animated-gradient-bg text-white font-bold shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors"
        @click="onSaveSearch"
      >
        Guardar Esta Búsqueda
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
const searchText = ref('')
const listening = ref(false)
const micSonar = ref(false)
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

function onSaveSearch() {
  // Aquí puedes implementar la lógica para guardar la búsqueda
  alert('¡Búsqueda guardada!')
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  setInterval(() => {
    micSonar.value = false
    setTimeout(() => {
      micSonar.value = true
    }, 50)
  }, 10000)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  if (hideTimeout) clearTimeout(hideTimeout)
})
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
}
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
  max-height: 80px;
  opacity: 1;
}
@keyframes sonar {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.55), 0 0 0 0 rgba(255,255,255,0.12);
  }
  60% {
    box-shadow: 0 0 0 32px rgba(34, 211, 238, 0), 0 0 0 48px rgba(255,255,255,0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 211, 238, 0), 0 0 0 0 rgba(255,255,255,0);
  }
}
.sonar-effect {
  animation: sonar 1.4s;
}
@keyframes animatedGradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
.animated-gradient-bg {
  background: linear-gradient(270deg, #6366f1, #22d3ee, #6366f1, #0ea5e9, #6366f1);
  background-size: 400% 400%;
  animation: animatedGradient 6s ease-in-out infinite;
}
</style> 