<template>
  <div class="client-chat-container">
    <div class="chat-panel">
      <h2>💬 Conversa con tu Agente Inmobiliario</h2>
      
      <div class="connection-status">
        <span :class="['status-badge', connectionStatus]">{{ statusText }}</span>
        <span v-if="roomInfo.name" class="room-name">Room: {{ roomInfo.name }}</span>
      </div>

      <!-- Chat Messages -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" 
             :class="['message', message.role]">
          <div class="message-avatar">
            <span v-if="message.role === 'agent'">🏠</span>
            <span v-else>👤</span>
          </div>
          <div class="message-content">
            <div class="message-sender">{{ message.sender }}</div>
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="chat-input-area">
        <div class="input-container">
          <input 
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            placeholder="Escribe tu mensaje aquí... (Ej: Busco un departamento de 2 ambientes)"
            class="message-input"
            :disabled="!isConnected"
          />
          <button 
            @click="sendMessage" 
            class="send-button"
            :disabled="!isConnected || !inputMessage.trim()"
          >
            📤 Enviar
          </button>
        </div>
        
        <div class="quick-actions">
          <button @click="sendQuickMessage('Busco un departamento de 2 ambientes cerca del mar')" 
                  class="quick-button">
            🔍 Buscar Propiedades
          </button>
          <button @click="sendQuickMessage('¿Qué puedes hacer?')" 
                  class="quick-button">
            ❓ Ayuda
          </button>
          <button @click="sendQuickMessage('Hola')" 
                  class="quick-button">
            👋 Saludar
          </button>
        </div>
      </div>

      <!-- Connection Controls -->
      <div class="controls">
        <button 
          @click="connectToRoom" 
          :disabled="isConnected"
          class="btn btn-primary"
        >
          {{ isConnected ? 'Conectado' : 'Conectar al Room' }}
        </button>
        
        <button 
          @click="disconnectFromRoom" 
          :disabled="!isConnected"
          class="btn btn-secondary"
        >
          Desconectar
        </button>
      </div>

      <div class="info-section">
        <p class="info-text">
          💡 <strong>Consejo:</strong> Una vez conectado, puedes escribir preguntas sobre propiedades en Mar del Plata.
          El agente inmobiliario te ayudará a encontrar lo que buscas.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Room, RoomEvent } from 'livekit-client'

// Estado
const isConnected = ref(false)
const connectionStatus = ref('disconnected')
const roomInfo = ref({})
const messages = ref([])
const inputMessage = ref('')

// Instancia del Room
let room = null

// Función para agregar mensaje
const addMessage = (text, role, sender) => {
  const time = new Date().toLocaleTimeString()
  messages.value.push({
    text,
    role, // 'agent' o 'user'
    sender,
    time
  })
  
  // Scroll al final
  nextTick(() => {
    const container = document.querySelector('.chat-messages')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// Conectar al room
const connectToRoom = async () => {
  try {
    if (isConnected.value) {
      console.log('Ya conectado')
      return
    }

    // Obtener token
    const response = await fetch('/api/livekit/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        roomName: 'real-estate-room',
        participantName: 'client-user-' + Date.now()
      })
    })

    if (!response.ok) {
      throw new Error('Error obteniendo token')
    }

    const tokenData = await response.json()
    console.log('✅ Token obtenido:', tokenData)

    // Crear room
    room = new Room()

    // Escuchar mensajes del agente
    room.on(RoomEvent.DataReceived, (payload, participant) => {
      try {
        const message = new TextDecoder().decode(payload)
        console.log('📨 Mensaje recibido del agente:', message)
        addMessage(message, 'agent', '🏠 Agente Inmobiliario')
      } catch (error) {
        console.error('❌ Error procesando mensaje:', error)
      }
    })

    // Escuchar cambios de conexión
    room.on(RoomEvent.Connected, () => {
      console.log('✅ Conectado al room:', room.name)
      isConnected.value = true
      connectionStatus.value = 'connected'
      roomInfo.value = {
        name: room.name,
        participants: room.participants?.size || 0
      }
      addMessage('¡Conectado al room!', 'system', 'Sistema')
    })

    room.on(RoomEvent.Disconnected, (reason) => {
      console.log('❌ Desconectado:', reason)
      isConnected.value = false
      connectionStatus.value = 'disconnected'
      addMessage('Desconectado del room', 'system', 'Sistema')
    })

    // Conectar
    await room.connect(tokenData.url, tokenData.token, {
      participantName: tokenData.participantName,
      roomName: tokenData.roomName
    })

    addMessage('Listo para conversar. Escribe tu mensaje abajo! 👇', 'system', 'Sistema')

  } catch (error) {
    console.error('❌ Error conectando:', error)
    addMessage('Error de conexión: ' + error.message, 'system', 'Sistema')
  }
}

// Desconectar del room
const disconnectFromRoom = async () => {
  try {
    if (room) {
      await room.disconnect()
      isConnected.value = false
      connectionStatus.value = 'disconnected'
      addMessage('Desconectado del room', 'system', 'Sistema')
    }
  } catch (error) {
    console.error('❌ Error desconectando:', error)
  }
}

// Enviar mensaje
const sendMessage = async () => {
  if (!inputMessage.value.trim() || !isConnected.value) {
    return
  }

  const message = inputMessage.value.trim()
  
  try {
    // Mostrar mensaje del usuario
    addMessage(message, 'user', 'Tú')
    
    // Enviar al room
    if (room && room.localParticipant) {
      await room.localParticipant.publishData(
        new TextEncoder().encode(message),
        { reliable: true }
      )
      console.log('📤 Mensaje enviado:', message)
    }
    
    // Limpiar input
    inputMessage.value = ''
    
  } catch (error) {
    console.error('❌ Error enviando mensaje:', error)
    addMessage('Error enviando mensaje', 'system', 'Sistema')
  }
}

// Enviar mensaje rápido
const sendQuickMessage = (message) => {
  inputMessage.value = message
  sendMessage()
}

// Limpiar al desmontar
onUnmounted(async () => {
  if (room && isConnected.value) {
    await disconnectFromRoom()
  }
})

// Inicializar
onMounted(() => {
  addMessage('Conecta al room para empezar a conversar', 'system', 'Sistema')
})
</script>

<style scoped>
.client-chat-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

h2 {
  color: #2563eb;
  margin-bottom: 20px;
  text-align: center;
}

.connection-status {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.connected {
  background: #dcfce7;
  color: #166534;
}

.status-badge.disconnected {
  background: #fef2f2;
  color: #dc2626;
}

.room-name {
  color: #6b7280;
  font-size: 14px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 20px;
  min-height: 300px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-sender {
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.message-text {
  color: #374151;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message.user .message-text {
  background: #dbeafe;
}

.message.agent .message-text {
  background: #f0fdf4;
}

.message.system .message-text {
  background: #fef3c7;
  font-style: italic;
}

.message-time {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.chat-input-area {
  margin-bottom: 20px;
}

.input-container {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
}

.message-input:focus {
  outline: none;
  border-color: #2563eb;
}

.send-button {
  padding: 12px 24px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-button {
  padding: 8px 16px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-button:hover {
  background: #e5e7eb;
}

.controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.info-section {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
}

.info-text {
  color: #374151;
  margin: 0;
  font-size: 14px;
}
</style>
