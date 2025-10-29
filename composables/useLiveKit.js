export const useLiveKit = () => {
  const { $fetch } = useNuxtApp()
  const config = useRuntimeConfig()
  
  // Estado del composable
  const room = ref(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const error = ref(null)
  const participant = ref(null)
  const isMuted = ref(true)
  const isAgentConnected = ref(false)

  // Configuración de LiveKit
  const LIVEKIT_URL = 'wss://livekit.showtimeprop.com'
  const ROOM_NAME = 'property-agent'

  // Función para generar token JWT
  const generateToken = async (userId, userName) => {
    try {
      const response = await $fetch(`${config.public.apiBaseUrl}/livekit/generate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          user_id: userId,
          user_name: userName,
          room_name: ROOM_NAME
        }
      })
      
      return response.token
    } catch (err) {
      console.error('Error generando token:', err)
      throw new Error('No se pudo generar el token de acceso')
    }
  }

  // Función para conectar a la sala
  const connectToRoom = async (userId, userName) => {
    try {
      isConnecting.value = true
      error.value = null

      // Importar LiveKit dinámicamente (solo en el cliente)
      if (process.client) {
        const { Room, RoomEvent, ParticipantEvent, Track } = await import('livekit-client')

        // Crear nueva instancia de Room
        room.value = new Room({
          adaptiveStream: true,
          dynacast: true,
          publishDefaults: {
            audioPreset: {
              maxBitrate: 64000,
            },
          },
        })

        // Generar token
        const token = await generateToken(userId, userName)

        // Conectar a la sala
        await room.value.connect(LIVEKIT_URL, token)
        
        // Configurar eventos
        setupRoomEvents()

        // Habilitar micrófono
        await room.value.localParticipant.setMicrophoneEnabled(true)
        isMuted.value = false

        isConnected.value = true
        participant.value = room.value.localParticipant

        console.log('Conectado exitosamente a LiveKit')
        
        return room.value
      }
    } catch (err) {
      error.value = err.message || 'Error conectando a LiveKit'
      console.error('Error conectando a LiveKit:', err)
      throw err
    } finally {
      isConnecting.value = false
    }
  }

  // Configurar eventos de la sala
  const setupRoomEvents = () => {
    if (!room.value) return

    // Evento cuando se conecta un participante
    room.value.on('participantConnected', (participant) => {
      console.log('Participante conectado:', participant.identity)
      
      if (participant.identity === 'agent') {
        isAgentConnected.value = true
        console.log('Agente Showy conectado')
      }

      // Configurar eventos del participante
      participant.on('trackSubscribed', (track, publication, participant) => {
        console.log('Track suscrito:', track.kind)
        
        // Reproducir audio del participante
        if (track.kind === 'audio') {
          const audioElement = track.attach()
          audioElement.play()
        }
      })

      participant.on('trackUnsubscribed', (track) => {
        console.log('Track desuscrito:', track.kind)
        track.detach()
      })
    })

    // Evento cuando se desconecta un participante
    room.value.on('participantDisconnected', (participant) => {
      console.log('Participante desconectado:', participant.identity)
      
      if (participant.identity === 'agent') {
        isAgentConnected.value = false
        console.log('Agente Showy desconectado')
      }
    })

    // Evento cuando cambia la conexión
    room.value.on('connectionStateChanged', (state) => {
      console.log('Estado de conexión:', state)
      
      if (state === 'disconnected') {
        isConnected.value = false
        isAgentConnected.value = false
      }
    })

    // Evento cuando se publica un track
    room.value.on('trackPublished', (publication, participant) => {
      console.log('Track publicado:', publication.kind, 'por', participant.identity)
    })

    // Evento cuando se suscribe a un track
    room.value.on('trackSubscribed', (track, publication, participant) => {
      console.log('Track suscrito:', track.kind, 'de', participant.identity)
    })

    // Evento para recibir mensajes de datos del agente
    room.value.on('dataReceived', (payload, participant) => {
      try {
        const message = new TextDecoder().decode(payload)
        console.log('📨 Mensaje recibido del agente:', message)
        
        // Emitir evento personalizado para que el componente pueda escucharlo
        if (process.client) {
          window.dispatchEvent(new CustomEvent('livekit-agent-message', {
            detail: { message, participant: participant.identity }
          }))
        }
      } catch (error) {
        console.error('❌ Error procesando mensaje del agente:', error)
      }
    })
  }

  // Función para alternar micrófono
  const toggleMicrophone = async () => {
    try {
      if (!room.value) {
        throw new Error('No hay conexión activa')
      }

      await room.value.localParticipant.setMicrophoneEnabled(!isMuted.value)
      isMuted.value = !isMuted.value
      
      console.log('Micrófono:', isMuted.value ? 'muteado' : 'activado')
    } catch (err) {
      console.error('Error alternando micrófono:', err)
      throw err
    }
  }

  // Función para desconectar
  const disconnectFromRoom = async () => {
    try {
      if (room.value) {
        await room.value.disconnect()
        room.value = null
      }
      
      isConnected.value = false
      isAgentConnected.value = false
      isMuted.value = true
      participant.value = null
      
      console.log('Desconectado de LiveKit')
    } catch (err) {
      console.error('Error desconectando:', err)
      throw err
    }
  }

  // Función para enviar mensaje al agente
  const sendMessageToAgent = async (message) => {
    try {
      if (!room.value || !isAgentConnected.value) {
        throw new Error('No hay conexión con el agente')
      }

      // Aquí podrías implementar el envío de mensajes
      // Por ahora, solo log
      console.log('Enviando mensaje al agente:', message)
      
    } catch (err) {
      console.error('Error enviando mensaje al agente:', err)
      throw err
    }
  }

  // Función para verificar si el navegador es compatible
  const checkBrowserCompatibility = () => {
    if (!process.client) return false

    // Verificar soporte para WebRTC
    const hasWebRTC = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
    
    // Verificar soporte para WebSockets
    const hasWebSockets = !!window.WebSocket
    
    return hasWebRTC && hasWebSockets
  }

  // Función para solicitar permisos de micrófono
  const requestMicrophonePermission = async () => {
    try {
      if (!process.client) return false

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      return true
    } catch (err) {
      console.error('Error solicitando permisos de micrófono:', err)
      return false
    }
  }

  // Limpiar recursos al desmontar
  const cleanup = () => {
    if (room.value) {
      disconnect()
    }
  }

  // Cleanup automático cuando se desmonta el componente
  onBeforeUnmount(() => {
    cleanup()
  })

  return {
    // Estado
    room: readonly(room),
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    error: readonly(error),
    participant: readonly(participant),
    isMuted: readonly(isMuted),
    isAgentConnected: readonly(isAgentConnected),

    // Acciones
    connectToRoom,
    disconnectFromRoom,
    toggleMicrophone,
    sendMessageToAgent,
    checkBrowserCompatibility,
    requestMicrophonePermission,
    cleanup
  }
}
