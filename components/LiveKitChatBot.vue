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
      <div class="flex items-center gap-2">
        <span>Showy - Tu Asistente IA</span>
        <span v-if="isAgentConnected" class="text-xs bg-green-500 text-white px-2 py-1 rounded-full">Conectado</span>
        <span v-else class="text-xs bg-red-500 text-white px-2 py-1 rounded-full">Desconectado</span>
      </div>
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
      
      <!-- Indicador de conexión -->
      <div v-if="isConnecting" class="chat chat-start">
        <div class="chat-image avatar">
          <div class="w-10 rounded-full bg-white flex items-center justify-center">
            <img src="/avatars/showy.png" alt="Showy avatar" style="width: 40px; height: 40px; border-radius: 50%; object-fit: contain; object-position: center; background: #fff;" />
          </div>
        </div>
        <div class="chat-bubble chat-bubble-secondary">
          Conectando con Showy...
        </div>
      </div>
    </div>
    
    <!-- Controles de LiveKit -->
    <div class="border-t p-3 flex items-center gap-2">
      <button
        @click="toggleMicrophone"
        :class="[
          'rounded-full p-2 transition flex items-center justify-center',
          isMuted ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
        ]"
        :disabled="!isConnected"
      >
        <svg v-if="isMuted" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.007-2.51-.05v-1.49c.806-.043 1.63-.05 2.51-.05h2.24z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 18.75v1.5m0 0h3m-3 0h-3m6-6.75a3 3 0 11-6 0v-3a3 3 0 116 0v3z" />
        </svg>
      </button>
      
      <button
        @click="connectToLiveKit"
        :disabled="isConnected"
        class="px-3 py-1 bg-indigo-500 text-white rounded text-sm hover:bg-indigo-600 disabled:bg-gray-400"
      >
        {{ isConnected ? 'Conectado' : 'Conectar' }}
      </button>
      
      <button
        @click="disconnectFromLiveKit"
        :disabled="!isConnected"
        class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 disabled:bg-gray-400"
      >
        Desconectar
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useLiveKit } from '~/composables/useLiveKit'

// Usar el composable de LiveKit
const {
  room,
  isConnected,
  isConnecting,
  error,
  participant,
  isMuted,
  isAgentConnected,
  connectToRoom,
  disconnectFromRoom,
  toggleMicrophone
} = useLiveKit()

// Estado del componente
const open = ref(false)
const messages = ref([
  { author: 'bot', text: '¡Hola! Soy Showy 🤖 Tu asistente inmobiliario virtual. Conéctate para empezar a buscar propiedades en tiempo real.', time: getCurrentTime(), footer: 'enviado' }
])

const messagesContainer = ref(null)
const chatPanelRef = ref(null)

// Auto-scroll de mensajes
watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

// Manejar clicks fuera del chat
onMounted(() => {
  document.addEventListener('mousedown', handleClickOutsideChat)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutsideChat)
  if (isConnected.value) {
    disconnectFromLiveKit()
  }
})

function handleClickOutsideChat(e) {
  if (open.value && chatPanelRef.value && !chatPanelRef.value.contains(e.target)) {
    open.value = false
  }
}

// Conectar a LiveKit
const connectToLiveKit = async () => {
  try {
    const userId = `user-${Date.now()}`
    const userName = 'Usuario'
    
    await connectToRoom(userId, userName)
    
    messages.value.push({
      author: 'bot',
      text: '¡Conectado exitosamente! Ahora puedes hablar conmigo para buscar propiedades.',
      time: getCurrentTime(),
      footer: 'enviado'
    })
  } catch (err) {
    messages.value.push({
      author: 'bot',
      text: `Error conectando: ${err.message}`,
      time: getCurrentTime(),
      footer: 'error'
    })
  }
}

// Desconectar de LiveKit
const disconnectFromLiveKit = async () => {
  try {
    await disconnectFromRoom()
    
    messages.value.push({
      author: 'bot',
      text: 'Desconectado de LiveKit. ¡Gracias por usar Showy!',
      time: getCurrentTime(),
      footer: 'enviado'
    })
  } catch (err) {
    console.error('Error desconectando:', err)
  }
}

// Función para obtener hora actual
function getCurrentTime() {
  const now = new Date()
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Escuchar mensajes del agente cuando se conecte
watch(isAgentConnected, (connected) => {
  if (connected) {
    messages.value.push({
      author: 'bot',
      text: 'Showy está listo para ayudarte. ¡Habla conmigo para buscar propiedades!',
      time: getCurrentTime(),
      footer: 'enviado'
    })
  }
})

// Escuchar mensajes de datos del agente
onMounted(() => {
  if (process.client) {
    window.addEventListener('livekit-agent-message', (event) => {
      const { message, participant } = event.detail
      
      if (participant === 'agent') {
        // Intentar parsear como JSON para datos de propiedades
        try {
          const data = JSON.parse(message)
          if (data.type === 'properties_found') {
            // Mostrar propiedades encontradas
            messages.value.push({
              author: 'bot',
              text: `Encontré ${data.count} propiedades para ti:`,
              time: getCurrentTime(),
              footer: 'enviado'
            })
            
            // Agregar cada propiedad como mensaje
            data.properties.forEach((prop, index) => {
              messages.value.push({
                author: 'bot',
                text: `${index + 1}. ${prop.title} - ${prop.price} - ${prop.location}`,
                time: getCurrentTime(),
                footer: 'propiedad',
                property: prop
              })
            })
          } else {
            // Mensaje normal del agente
            messages.value.push({
              author: 'bot',
              text: message,
              time: getCurrentTime(),
              footer: 'enviado'
            })
          }
        } catch (e) {
          // Si no es JSON, es un mensaje normal
          messages.value.push({
            author: 'bot',
            text: message,
            time: getCurrentTime(),
            footer: 'enviado'
          })
        }
      }
    })
  }
})

onBeforeUnmount(() => {
  if (process.client) {
    window.removeEventListener('livekit-agent-message', () => {})
  }
})
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
</style>
