<template>
  <!-- Botón flotante Showy -->
  <button
    style="position: fixed; bottom: 24px; right: 24px; z-index: 9999;"
    class="bg-white rounded-full p-2 border border-yellow-200 shadow-lg hover:bg-yellow-100 transition flex items-center justify-center animate-float"
    @click="open = true"
    aria-label="Abrir chat Showy"
  >
    <span>
      <img src="/avatars/showy.png" alt="Showy te Ayuda a Buscar la casa de tus sueños" style="width: 74px; height: 74px; border-radius: 50%; object-fit: contain; object-position: center; box-shadow: 0 2px 12px rgba(253,216,53,0.18); background: #fff;" />
    </span>
  </button>

  <!-- Panel de chat -->
  <div v-if="open" ref="chatPanelRef" style="position: fixed; bottom: 80px; right: 24px; z-index: 9999; max-height: 80vh;" class="w-80 bg-white rounded-xl shadow-xl flex flex-col">
    <div class="flex items-center justify-between p-4 border-b font-bold text-red-600">
      <span>Showy - Tu Asistente IA</span>
      <button @click="open = false" class="ml-2 text-gray-400 hover:text-red-600 text-xl font-bold">&times;</button>
    </div>
    <div ref="messagesContainer" class="flex-1 p-4 overflow-y-auto space-y-2 max-h-[55vh] no-scrollbar">
      <div v-for="(msg, i) in messages" :key="i" :class="msg.author === 'user' ? 'chat chat-end' : 'chat chat-start'">
        <!-- Avatar -->
        <div class="chat-image avatar">
          <div class="w-10 rounded-full bg-white flex items-center justify-center">
            <img v-if="msg.author === 'user'" alt="avatar usuario" src="https://img.daisyui.com/images/profile/demo/kenobee@192.webp" />
            <span v-else>
              <img src="/avatars/showy.png" alt="Showy avatar" style="width: 40px; height: 40px; border-radius: 50%; object-fit: contain; object-position: center; background: #fff;" />
            </span>
          </div>
        </div>
        <!-- Header -->
        <div class="chat-header">
          {{ msg.author === 'user' ? 'Tú' : 'Showy' }}
          <time class="text-xs opacity-50 ml-2">{{ msg.time }}</time>
        </div>
        <!-- Burbuja -->
        <div :class="'chat-bubble ' + (msg.author === 'user' ? 'chat-bubble-primary' : 'chat-bubble-secondary')">
          {{ msg.text }}
        </div>
        <!-- Footer -->
        <div class="chat-footer opacity-50">{{ msg.footer }}</div>
      </div>
    </div>
    <form @submit.prevent="sendMessage" class="flex border-t items-center p-2 gap-2">
      <input
        v-model="input"
        class="flex-1 px-3 py-2 outline-none rounded-lg border border-gray-300 text-sm placeholder:text-xs"
        placeholder="Habla o escribe tu mensaje..."
      />
      <button type="button" @click="startListening" :class="['rounded-full p-3 transition flex items-center justify-center border border-indigo-300 shadow-lg text-white font-bold relative overflow-visible', listening ? 'animate-pulse ring-4 ring-cyan-200' : 'hover:from-indigo-400 hover:to-cyan-300', micSonar ? 'sonar-effect' : '']" style="width: 48px; height: 48px; font-size: 2rem;" :aria-label="listening ? 'Escuchando...' : 'Hablar'">
        <span class="mic-gradient-bg absolute inset-0 rounded-full z-0"></span>
        <span class="relative z-10 flex items-center justify-center w-full h-full">
          <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="white" class="w-8 h-8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75v1.5m0 0h3m-3 0h-3m6-6.75a3 3 0 11-6 0v-3a3 3 0 116 0v3z" />
        </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24" class="w-8 h-8 animate-bounce">
          <path d="M12 1a4 4 0 00-4 4v6a4 4 0 008 0V5a4 4 0 00-4-4zm5 10a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 9a7 7 0 007-7h-2a5 5 0 01-10 0H5a7 7 0 007 7z"/>
        </svg>
        </span>
      </button>
      <button class="px-4 text-indigo-600 font-bold" :disabled="loading">Enviar</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const listening = ref(false)
const micSonar = ref(false)
const messages = ref([
  { author: 'bot', text: '¡Hola! Soy Showy 🤖 Y puedo ayudarte a buscar un nuevo hogar, o tu proxima inversion!', time: getCurrentTime(), footer: 'enviado' }
])

const messagesContainer = ref(null)
const chatPanelRef = ref(null)

watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

onMounted(() => {
  setInterval(() => {
    micSonar.value = false
    setTimeout(() => {
      micSonar.value = true
    }, 50)
  }, 10000)

  document.addEventListener('mousedown', handleClickOutsideChat)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutsideChat)
})

function handleClickOutsideChat(e) {
  if (open.value && chatPanelRef.value && !chatPanelRef.value.contains(e.target)) {
    open.value = false
  }
}

let recognition = null

async function sendMessage() {
  if (!input.value.trim()) return
  messages.value.push({ author: 'user', text: input.value, time: getCurrentTime(), footer: 'enviado' })
  loading.value = true
  const userMsg = input.value
  input.value = ''
  // Simulación de respuesta IA
  setTimeout(() => {
    messages.value.push({ author: 'bot', text: 'Showy está pensando... (aquí responderá la IA)', time: getCurrentTime(), footer: 'enviado' })
    loading.value = false
  }, 1200)
}

function startListening() {
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
      input.value = event.results[0][0].transcript
      listening.value = false
      sendMessage() // Enviar automáticamente al terminar de hablar
    }
    recognition.onerror = () => { listening.value = false }
    recognition.onend = () => { listening.value = false }
  }
  listening.value = true
  recognition.start()
}

function getCurrentTime() {
  const now = new Date()
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
@import 'daisyui/dist/full.css';
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
@keyframes float {
  0% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
  100% { transform: translateY(0); }
}
.animate-float {
  animation: float 2.4s ease-in-out infinite;
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
.mic-gradient-bg {
  background: linear-gradient(270deg, #6366f1, #22d3ee, #6366f1, #0ea5e9, #6366f1);
  background-size: 400% 400%;
  animation: gradientMove 6s ease-in-out infinite;
}
@keyframes gradientMove {
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
</style> 