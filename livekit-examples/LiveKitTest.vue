<template>
  <div class="livekit-test-container">
    <div class="test-panel">
      <h2>🎯 LiveKit Echo Agent Test</h2>
      
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
          <span class="label">Participantes:</span>
          <span class="value">{{ roomInfo.participants || 0 }}</span>
        </div>
      </div>

      <div class="controls">
        <button 
          @click="connectAgent" 
          :disabled="isConnected"
          class="btn btn-primary"
        >
          {{ isConnected ? 'Conectado' : 'Conectar Echo Agent' }}
        </button>
        
        <button 
          @click="disconnectAgent" 
          :disabled="!isConnected"
          class="btn btn-secondary"
        >
          Desconectar
        </button>
        
        <button 
          @click="sendTestMessage" 
          :disabled="!isConnected"
          class="btn btn-success"
        >
          Enviar Mensaje Test
        </button>
      </div>

      <div class="info-panel">
        <h3>📋 Información de Conexión</h3>
        <div class="info-item">
          <span class="label">URL:</span>
          <span class="value">https://lkit.showtimeprop.com</span>
        </div>
        <div class="info-item">
          <span class="label">Room:</span>
          <span class="value">echo-room</span>
        </div>
        <div class="info-item">
          <span class="label">Agent:</span>
          <span class="value">echo-agent</span>
        </div>
      </div>

      <div class="logs-panel">
        <h3>📝 Logs de Conexión</h3>
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
import { EchoAgent } from '../livekit-examples/echo-agent.js'

// Estado reactivo
const isConnected = ref(false)
const connectionStatus = ref('disconnected')
const roomInfo = ref({})
const logs = ref([])

// Instancia del Echo Agent
let echoAgent = null

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

// Conectar el Echo Agent
const connectAgent = async () => {
  try {
    addLog('🚀 Iniciando conexión del Echo Agent...')
    
    if (!echoAgent) {
      echoAgent = new EchoAgent()
    }
    
    const success = await echoAgent.connect('echo-room', 'echo-agent')
    
    if (success) {
      isConnected.value = true
      connectionStatus.value = 'connected'
      addLog('✅ Echo Agent conectado exitosamente!')
      
      // Actualizar información del room cada segundo
      const interval = setInterval(() => {
        if (echoAgent && isConnected.value) {
          roomInfo.value = echoAgent.getRoomInfo()
        } else {
          clearInterval(interval)
        }
      }, 1000)
      
    } else {
      addLog('❌ Error conectando Echo Agent')
    }
  } catch (error) {
    addLog(`❌ Error: ${error.message}`)
    console.error('Error conectando Echo Agent:', error)
  }
}

// Desconectar el Echo Agent
const disconnectAgent = async () => {
  try {
    addLog('👋 Desconectando Echo Agent...')
    
    if (echoAgent) {
      await echoAgent.disconnect()
    }
    
    isConnected.value = false
    connectionStatus.value = 'disconnected'
    roomInfo.value = {}
    addLog('✅ Echo Agent desconectado')
  } catch (error) {
    addLog(`❌ Error desconectando: ${error.message}`)
    console.error('Error desconectando Echo Agent:', error)
  }
}

// Enviar mensaje de prueba
const sendTestMessage = async () => {
  try {
    addLog('📤 Enviando mensaje de prueba...')
    
    if (echoAgent) {
      const success = await echoAgent.sendTestMessage('Hola! Soy el Echo Agent de LiveKit 🎯')
      
      if (success) {
        addLog('✅ Mensaje enviado exitosamente')
      } else {
        addLog('❌ Error enviando mensaje')
      }
    }
  } catch (error) {
    addLog(`❌ Error: ${error.message}`)
    console.error('Error enviando mensaje:', error)
  }
}

// Limpiar al desmontar el componente
onUnmounted(async () => {
  if (echoAgent && isConnected.value) {
    await disconnectAgent()
  }
})

// Escuchar actualizaciones del room
const handleRoomUpdate = (event) => {
  const roomInfo = event.detail
  roomInfo.value = roomInfo
  addLog(`📊 Room actualizado: ${roomInfo.name} (${roomInfo.participants} participantes)`)
}

// Log inicial
onMounted(() => {
  addLog('🎯 LiveKit Echo Agent Test inicializado')
  addLog('📡 URL: https://lkit.showtimeprop.com')
  addLog('🔑 API Key configurada')
  
  // Escuchar eventos de actualización del room
  window.addEventListener('livekit-room-update', handleRoomUpdate)
})

// Limpiar listeners
onUnmounted(async () => {
  window.removeEventListener('livekit-room-update', handleRoomUpdate)
  
  if (echoAgent && isConnected.value) {
    await disconnectAgent()
  }
})
</script>

<style scoped>
.livekit-test-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-panel {
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

.info-panel, .logs-panel {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-panel h3, .logs-panel h3 {
  color: #374151;
  margin-bottom: 12px;
  font-size: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
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
