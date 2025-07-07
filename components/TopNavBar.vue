<template>
  <nav class="fixed top-0 left-0 w-full z-50 bg-black shadow-lg" @mouseenter="showTopMenu = true" @mouseleave="maybeHideMenu">
    <!-- Primer renglón: Logo y menú, colapsable -->
    <div class="flex justify-between items-center w-full px-6 pt-3">
    </div>
    <transition name="slide-down">
      <div v-if="showTopMenu" class="flex flex-col items-center w-full bg-black mt-3">
        <span class="text-2xl font-bold text-white tracking-tight select-none mb-1 logo-glow">Showtime Prop</span>
        <div class="flex gap-8 text-sm font-medium text-white mb-2 items-center justify-end">
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Comprar</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Alquilar</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Vender</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Créditos Hipotecarios</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Listar Tu Propiedad</a>
          <a href="#" class="hover:text-cyan-300 hover:underline hover:underline-offset-8 transition font-bold">Blog Inmobiliario</a>
          
          <!-- Lógica Condicional para Botón de Sesión -->
          <div v-if="user" class="flex items-center gap-4">
            <span class="text-white">Bienvenido, {{ user.email?.split('@')[0] }}</span>
            <button @click="handleLogout" class="ml-4 px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white font-bold shadow-lg transition-colors text-sm">
              Salir
            </button>
          </div>
          <button v-else @click="handleLoginClick" class="ml-4 px-4 py-2 rounded-lg animated-gradient-bg text-white font-bold shadow-lg transition-colors text-sm flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9A3.75 3.75 0 1112 5.25 3.75 3.75 0 0115.75 9zM4.5 19.5a7.5 7.5 0 1115 0v.75a.75.75 0 01-.75.75h-13.5a.75.75 0 01-.75-.75v-.75z" />
            </svg>
            Iniciar Sesión
          </button>

          <button
            class="ml-2 px-4 py-2 rounded-lg animated-gradient-bg text-white font-bold shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors text-sm flex items-center gap-2"
            @click="onSaveSearch"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 16v2a2 2 0 01-2 2H9a2 2 0 01-2-2v-2m10-6V7a2 2 0 00-2-2H7a2 2 0 00-2 2v3m12 0l-6 6-6-6" />
            </svg>
            Guardar Esta Búsqueda
          </button>
        </div>
      </div>
    </transition>
    <!-- Segundo renglón: Buscador siempre visible -->
    <div class="flex items-center justify-center max-w-xl mx-auto py-2 bg-black">
      <span class="text-white text-sm font-bold mx-auto">Menú</span>
    </div>
  </nav>
  <LoginModal v-model="showLoginModal" />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useSupabaseUser } from '#imports'
import LoginModal from '~/components/LoginModal.vue'
import { useLoginModalStore } from '~/stores/loginModal'
import { storeToRefs } from 'pinia'

// Estas funciones están disponibles globalmente gracias a la auto-importación de Nuxt
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const router = useRouter()
const loginModalStore = useLoginModalStore()
const { isOpen: showLoginModal } = storeToRefs(loginModalStore)

const searchText = ref('')
const listening = ref(false)
const micSonar = ref(false)
let recognition = null
const showTopMenu = ref(false)
let hideTimeout = null
const showHelp = ref(false)

const handleLogout = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Error al cerrar sesión:', error)
    return;
  }
  // Redirige al inicio después de cerrar sesión
  await router.push('/')
};

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

const handleLoginClick = () => {
  loginModalStore.open()
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
@keyframes logoGlow {
  0% {
    text-shadow: 0 0 16px #22d3ee, 0 0 32px #6366f1, 0 0 64px #0ea5e9, 0 0 24px #22d3ee;
  }
  33% {
    text-shadow: 0 0 32px #6366f1, 0 0 64px #22d3ee, 0 0 96px #0ea5e9, 0 0 32px #6366f1;
  }
  66% {
    text-shadow: 0 0 32px #0ea5e9, 0 0 64px #6366f1, 0 0 96px #22d3ee, 0 0 32px #0ea5e9;
  }
  100% {
    text-shadow: 0 0 16px #22d3ee, 0 0 32px #6366f1, 0 0 64px #0ea5e9, 0 0 24px #22d3ee;
  }
}
.logo-glow {
  animation: logoGlow 3s ease-in-out infinite;
}
</style>