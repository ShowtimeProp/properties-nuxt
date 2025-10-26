<template>
  <div class="real-estate-agent-container">
    <div class="agent-panel">
      <h2>🏠 Agente Inmobiliario Inteligente</h2>
      
      <div class="status-panel">
        <div class="status-item">
          <span class="label">Estado:</span>
          <span :class="['status', connectionStatus]">{{ statusText }}</span>
        </div>
        <div class="status-item">
          <span class="label">Room:</span>
          <span class="value">{{ roomInfo.name || 'N/A' }}</span>
        </div>
        <div class="status-item">
          <span class="label">Clientes:</span>
          <span class="value">{{ roomInfo.participants || 0 }}</span>
        </div>
      </div>

      <div class="controls">
        <button 
          @click="connectAgent" 
          :disabled="isConnected"
          class="btn btn-primary"
        >
          {{ isConnected ? 'Agente Activo' : 'Activar Agente' }}
        </button>
        
        <button 
          @click="disconnectAgent" 
          :disabled="!isConnected"
          class="btn btn-secondary"
        >
          Desactivar
        </button>
        
        <button 
          @click="sendTestMessage" 
          :disabled="!isConnected"
          class="btn btn-success"
        >
          Mensaje de Bienvenida
        </button>
      </div>

      <div class="info-panel">
        <h3>📋 Información del Agente</h3>
        <div class="info-item">
          <span class="label">URL:</span>
          <span class="value">https://lkit.showtimeprop.com</span>
        </div>
        <div class="info-item">
          <span class="label">Room:</span>
          <span class="value">real-estate-room</span>
        </div>
        <div class="info-item">
          <span class="label">Agente:</span>
          <span class="value">real-estate-agent</span>
        </div>
        <div class="info-item">
          <span class="label">Capacidades:</span>
          <span class="value">Búsqueda de propiedades, Conversación IA</span>
        </div>
      </div>

      <div class="conversation-panel">
        <h3>💬 Conversación</h3>
        <div class="conversation-log" ref="conversationContainer">
          <div v-for="(message, index) in conversationHistory" :key="index" 
               :class="['message', message.sender === 'real-estate-agent' ? 'agent' : 'client']">
            <div class="message-header">
              <span class="sender">{{ message.sender === 'real-estate-agent' ? '🏠 Agente' : '👤 Cliente' }}</span>
              <span class="timestamp">{{ message.timestamp }}</span>
            </div>
            <div class="message-content">{{ message.message }}</div>
          </div>
        </div>
      </div>

      <div class="logs-panel">
        <h3>📝 Logs del Sistema</h3>
        <div class="logs" ref="logsContainer">
          <div v-for="(log, index) in logs" :key="index" class="log-item">
            <span class="timestamp">{{ log.timestamp }}</span>
            <span class="message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { RealEstateAgent } from '../livekit-examples/real-estate-agent.js'

// Estado reactivo
const isConnected = ref(false)
const connectionStatus = ref('disconnected')
const roomInfo = ref({})
const logs = ref([])
const conversationHistory = ref([])

// Instancia del Agente Inmobiliario
let realEstateAgent = null

// Función para agregar logs
const addLog = (message) => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({ timestamp, message })
  
  // Mantener solo los últimos 20 logs
  if (logs.value.length > 20) {
    logs.value.shift()
  }
  
  // Scroll automático a los logs más recientes
  nextTick(() => {
    const container = document.querySelector('.logs')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// Función para agregar mensaje a la conversación
const addConversationMessage = (sender, message) => {
  const timestamp = new Date().toLocaleTimeString()
  conversationHistory.value.push({ 
    sender, 
    message, 
    timestamp 
  })
  
  // Scroll automático a los mensajes más recientes
  nextTick(() => {
    const container = document.querySelector('.conversation-log')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// Conectar el Agente Inmobiliario
const connectAgent = async () => {
  try {
    addLog('🚀 Iniciando conexión del Agente Inmobiliario...')
    
    if (!realEstateAgent) {
      realEstateAgent = new RealEstateAgent()
    }
    
    const success = await realEstateAgent.connect('real-estate-room', 'real-estate-agent')
    
    if (success) {
      isConnected.value = true
      connectionStatus.value = 'connected'
      addLog('✅ Agente Inmobiliario conectado exitosamente!')
      
      // Actualizar información del room cada segundo
      const interval = setInterval(() => {
        if (realEstateAgent && isConnected.value) {
          roomInfo.value = realEstateAgent.getRoomInfo()
        } else {
          clearInterval(interval)
        }
      }, 1000)
      
    } else {
      addLog('❌ Error conectando Agente Inmobiliario')
    }
  } catch (error) {
    addLog(`❌ Error: ${error.message}`)
    console.error('Error conectando Agente Inmobiliario:', error)
  }
}

// Desconectar el Agente Inmobiliario
const disconnectAgent = async () => {
  try {
    addLog('👋 Desconectando Agente Inmobiliario...')
    
    if (realEstateAgent) {
      await realEstateAgent.disconnect()
    }
    
    isConnected.value = false
    connectionStatus.value = 'disconnected'
    roomInfo.value = {}
    conversationHistory.value = []
    addLog('✅ Agente Inmobiliario desconectado')
  } catch (error) {
    addLog(`❌ Error desconectando: ${error.message}`)
    console.error('Error desconectando Agente Inmobiliario:', error)
  }
}

// Enviar mensaje de prueba
const sendTestMessage = async () => {
  try {
    addLog('📤 Enviando mensaje de bienvenida...')
    
    if (realEstateAgent) {
      const success = await realEstateAgent.sendTestMessage('¡Hola! Soy tu agente inmobiliario inteligente 🏠')
      
      if (success) {
        addLog('✅ Mensaje de bienvenida enviado')
        addConversationMessage('real-estate-agent', '¡Hola! Soy tu agente inmobiliario inteligente 🏠')
      } else {
        addLog('❌ Error enviando mensaje')
      }
    }
  } catch (error) {
    addLog(`❌ Error: ${error.message}`)
    console.error('Error enviando mensaje:', error)
  }
}

// Escuchar actualizaciones del room
const handleRoomUpdate = (event) => {
  try {
    const roomInfo = event.detail
    roomInfo.value = roomInfo
    addLog(`📊 Room actualizado: ${roomInfo.name} (${roomInfo.participants} participantes)`)
  } catch (error) {
    console.error('❌ Error manejando actualización del room:', error)
    addLog(`❌ Error actualizando room: ${error.message}`)
  }
}

// Log inicial
onMounted(() => {
  addLog('🏠 Agente Inmobiliario Inteligente inicializado')
  addLog('📡 URL: https://lkit.showtimeprop.com')
  addLog('🔑 API Key configurada')
  addLog('🧠 Capacidades: Búsqueda de propiedades, Conversación IA')
  
  // Escuchar eventos de actualización del room
  window.addEventListener('livekit-room-update', handleRoomUpdate)
})

// Limpiar listeners
onUnmounted(async () => {
  window.removeEventListener('livekit-room-update', handleRoomUpdate)
  
  if (realEstateAgent && isConnected.value) {
    await disconnectAgent()
  }
})
</script>

<style scoped>
.real-estate-agent-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.agent-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #2563eb;
  margin-bottom: 20px;
  text-align: center;
}

.status-panel {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #374151;
}

.value {
  color: #6b7280;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status.connected {
  background: #dcfce7;
  color: #166534;
}

.status.disconnected {
  background: #fef2f2;
  color: #dc2626;
}

.controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.info-panel, .conversation-panel, .logs-panel {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-panel h3, .conversation-panel h3, .logs-panel h3 {
  color: #374151;
  margin-bottom: 12px;
  font-size: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.conversation-log {
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border-radius: 4px;
  padding: 12px;
  border: 1px solid #e5e7eb;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
}

.message.agent {
  background: #dbeafe;
  border-left: 4px solid #2563eb;
}

.message.client {
  background: #f0fdf4;
  border-left: 4px solid #10b981;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.sender {
  font-weight: 600;
  color: #374151;
}

.timestamp {
  color: #6b7280;
  font-family: monospace;
}

.message-content {
  color: #374151;
  line-height: 1.5;
  white-space: pre-wrap;
}

.logs {
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border-radius: 4px;
  padding: 12px;
  border: 1px solid #e5e7eb;
}

.log-item {
  display: flex;
  margin-bottom: 4px;
  font-size: 14px;
}

.timestamp {
  color: #6b7280;
  margin-right: 8px;
  font-family: monospace;
}

.message {
  color: #374151;
}
</style>
