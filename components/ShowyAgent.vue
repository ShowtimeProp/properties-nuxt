<template>
  <ClientOnly>
    <div>
      <!-- Animación flotante tipo Siri (antes de conectar) -->
      <div v-if="mode==='center' && !isConnected" class="fixed inset-0 z-[60] flex items-center justify-center w-full pointer-events-none">
        <div class="siri-wave-container">
          <div class="siri-wave siri-wave-1"></div>
          <div class="siri-wave siri-wave-2"></div>
          <div class="siri-wave siri-wave-3"></div>
          <div class="siri-wave siri-wave-4"></div>
          <div class="siri-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-16 h-16 text-white">
              <path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Animación flotante tipo Siri (conectado y hablando) -->
      <div v-if="mode==='center' && isConnected && isAgentSpeaking" class="fixed inset-0 z-[60] flex items-center justify-center w-full pointer-events-none">
        <div class="siri-wave-container">
          <div class="siri-wave siri-wave-1 active"></div>
          <div class="siri-wave siri-wave-2 active"></div>
          <div class="siri-wave siri-wave-3 active"></div>
          <div class="siri-wave siri-wave-4 active"></div>
          <div class="siri-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-16 h-16 text-white">
              <path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Modal compacto solo cuando está conectado y no habla -->
      <div v-if="mode==='center' && isConnected && !isAgentSpeaking" class="fixed inset-0 z-[60] flex items-center justify-center w-full bg-black/40 px-4 py-2" @click.self="dismissToDock">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-2 sm:p-3 relative text-center">
          <div class="mx-auto mb-2 w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center cursor-pointer" :class="{ 'animate-pulse': listening }" @click="activateAudio">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-10 h-10 text-white">
              <path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/>
            </svg>
          </div>
          <p class="text-sm text-gray-600 mb-3" v-if="listening && audioActivated">Escuchando...</p>
          <p v-else-if="!audioActivated" class="text-sm text-gray-600 mb-3">Haz click en el micrófono para activar el audio</p>
          <p v-else class="text-sm text-gray-600 mb-3">Conectado. El agente te saludará en breve.</p>
          <button @click="dismissToDock" class="text-sm text-gray-500 hover:text-gray-700">Minimizar</button>
        </div>
      </div>

      <!-- Dock abajo‑derecha - siempre en el DOM, visible cuando está en modo dock -->
      <div ref="dockRef" :class="['showy-dock fixed right-4 bottom-4 z-[55] pointer-events-auto transition-all', { 'opacity-0 pointer-events-none invisible': mode !== 'dock', 'opacity-100 pointer-events-auto visible': mode === 'dock' }]">
        <button @click="toggleExpand" class="relative w-16 h-16 rounded-full shadow-2xl border-2 border-indigo-400 bg-white overflow-hidden hover:shadow-2xl transition-all hover:scale-110">
          <span class="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 opacity-20 animate-ping"></span>
          <span class="absolute inset-0 rounded-full flex items-center justify-center z-10 bg-white">
            <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-8 h-8 text-indigo-600"><path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-8 h-8 text-cyan-600 animate-bounce"><path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/></svg>
          </span>
        </button>
      </div>
    </div>
  </ClientOnly>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'
import { Room, RoomEvent, RemoteParticipant, Track } from 'livekit-client'

const mode = ref('center') // center | dock
const listening = ref(false)
const connecting = ref(false)
const isConnected = ref(false)
const isAgentSpeaking = ref(false)
const audioActivated = ref(false)
const dockRef = ref(null)
let room = null
let audioContexts = []
let audioElements = []

async function connect() {
  try {
    connecting.value = true
    const roomName = `showy-${Math.random().toString(36).slice(2, 8)}`
    const participant = `web-${Math.random().toString(36).slice(2, 6)}`
    const res = await fetch('/api/livekit/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roomName, participantName: participant })
    })
    const { token, url } = await res.json()
    room = new Room()
    
    // Escuchar cuando el agente se une a la sala
    room.on(RoomEvent.ParticipantConnected, (participant) => {
      if (participant instanceof RemoteParticipant) {
        console.log('Agente conectado:', participant.identity)
        // El agente debería empezar a hablar automáticamente
        // Mostramos la animación por un tiempo mientras esperamos
        isAgentSpeaking.value = true
        setTimeout(() => {
          isAgentSpeaking.value = false
        }, 5000) // Mostrar animación por 5 segundos inicialmente
      }
    })
    
    // Escuchar eventos de tracks para detectar cuando el agente habla
    room.on(RoomEvent.TrackSubscribed, async (track, publication, participant) => {
      if (track.kind === Track.Kind.Audio && publication.kind === Track.Kind.Audio) {
        if (participant instanceof RemoteParticipant) {
          console.log('🎵 Track de audio del agente suscrito')
          
          // Si el audio ya está activado, reproducir inmediatamente
          if (audioActivated.value) {
            try {
              const audioElement = document.createElement('audio')
              audioElement.autoplay = true
              audioElement.playsInline = true
              track.attach(audioElement)
              audioElements.push(audioElement)
              await audioElement.play()
              console.log('✅ Audio reproducido automáticamente')
            } catch (e) {
              console.error('❌ Error reproduciendo audio:', e)
            }
          }
          
          // Detectar actividad de audio
          const audioTrack = track.mediaStreamTrack
          if (audioTrack && audioTrack.readyState === 'live') {
            if (audioActivated.value) {
              try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)()
                if (audioContext.state === 'suspended') {
                  await audioContext.resume()
                }
                const analyser = audioContext.createAnalyser()
                const source = audioContext.createMediaStreamSource(new MediaStream([audioTrack]))
                source.connect(analyser)
                analyser.fftSize = 256
                const dataArray = new Uint8Array(analyser.frequencyBinCount)
                audioContexts.push(audioContext)
                
                // Detectar actividad de audio periódicamente
                const checkAudio = () => {
                  if (room && room.state === 'connected' && audioTrack.readyState === 'live') {
                    analyser.getByteFrequencyData(dataArray)
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
                    isAgentSpeaking.value = average > 3
                    requestAnimationFrame(checkAudio)
                  } else {
                    isAgentSpeaking.value = false
                  }
                }
                checkAudio()
              } catch (e) {
                console.log('AudioContext no disponible:', e)
                isAgentSpeaking.value = true
                setTimeout(() => {
                  isAgentSpeaking.value = false
                }, 3000)
              }
            } else {
              isAgentSpeaking.value = true
              setTimeout(() => {
                isAgentSpeaking.value = false
              }, 3000)
            }
          }
        }
      }
    })
    
    room.on(RoomEvent.TrackUnsubscribed, (track, publication, participant) => {
      if (track.kind === Track.Kind.Audio && participant instanceof RemoteParticipant) {
        isAgentSpeaking.value = false
      }
    })
    
    await room.connect(url, token)
    
    // Habilitar micrófono y speaker explícitamente
    await room.localParticipant.setMicrophoneEnabled(true)
    
    // Habilitar audio output (speaker)
    if (room.localParticipant.audioTrackPublications.size === 0) {
      // Asegurar que podemos escuchar audio remoto
      room.setE2EEEnabled(false) // Desactivar E2EE si está causando problemas
    }
    
    // Suscribirse automáticamente a todos los tracks remotos cuando se publiquen
    room.on(RoomEvent.TrackPublished, async (publication, participant) => {
      if (participant instanceof RemoteParticipant && publication.kind === Track.Kind.Audio) {
        await publication.setSubscribed(true)
      }
    })
    
    // También suscribirse a tracks ya publicados
    room.on(RoomEvent.ParticipantConnected, async (participant) => {
      if (participant instanceof RemoteParticipant) {
        participant.audioTrackPublications.forEach(async (publication) => {
          await publication.setSubscribed(true)
        })
      }
    })
    
    isConnected.value = true
    listening.value = true
    
    // El agente debería saludar automáticamente después de conectarse
    // Esperamos un poco para que el agente se inicialice
    setTimeout(() => {
      // El agente debería empezar a hablar automáticamente
    }, 2000)
  } catch (e) {
    console.error('LiveKit connect error', e)
    connecting.value = false
  } finally {
    connecting.value = false
  }
}

async function activateAudio() {
  // Activar AudioContext después de un gesto del usuario
  audioActivated.value = true
  
  console.log('🎤 Activando audio...')
  
  // Crear un AudioContext temporal para activar el permiso del navegador
  try {
    const tempContext = new (window.AudioContext || window.webkitAudioContext)()
    if (tempContext.state === 'suspended') {
      await tempContext.resume()
      console.log('✅ AudioContext temporal activado')
    }
    // Reproducir un sonido silencioso para activar el audio
    const oscillator = tempContext.createOscillator()
    const gainNode = tempContext.createGain()
    gainNode.gain.value = 0
    oscillator.connect(gainNode)
    gainNode.connect(tempContext.destination)
    oscillator.start()
    oscillator.stop(tempContext.currentTime + 0.01)
    await tempContext.close()
  } catch (e) {
    console.error('❌ Error activando AudioContext temporal:', e)
  }
  
  // Reanudar todos los AudioContexts pausados
  for (const ctx of audioContexts) {
    if (ctx.state === 'suspended') {
      try {
        await ctx.resume()
        console.log('✅ AudioContext reanudado')
      } catch (e) {
        console.error('❌ Error resumiendo AudioContext:', e)
      }
    }
  }
  
  // Asegurar que LiveKit puede reproducir audio remoto
  if (room && room.state === 'connected') {
    console.log('📡 Suscribiéndose a tracks de audio remotos...')
    // Suscribirse a todos los tracks de audio remotos existentes
    for (const participant of room.remoteParticipants.values()) {
      console.log(`👤 Participante remoto encontrado: ${participant.identity}`)
      for (const publication of participant.audioTrackPublications.values()) {
        console.log(`🎵 Track de audio encontrado: ${publication.sid}`)
        await publication.setSubscribed(true)
        // Si el track ya está disponible, forzar reproducción
        if (publication.track) {
          try {
            // Crear elemento audio y reproducir
            const audioElement = document.createElement('audio')
            audioElement.autoplay = true
            audioElement.playsInline = true
            publication.track.attach(audioElement)
            audioElements.push(audioElement) // Guardar referencia
            await audioElement.play()
            console.log('✅ Audio del agente activado y reproduciéndose')
          } catch (e) {
            console.error('❌ Error reproduciendo audio del agente:', e)
            // Intentar nuevamente después de un momento
            setTimeout(async () => {
              try {
                await audioElement.play()
                console.log('✅ Audio reproducido en segundo intento')
              } catch (e2) {
                console.error('❌ Error en segundo intento:', e2)
              }
            }, 500)
          }
        } else {
          console.log('⏳ Track aún no disponible, esperando...')
        }
      }
    }
  } else {
    console.warn('⚠️ Room no conectado o no disponible')
  }
  
  console.log('✅ Audio activado por el usuario')
}

function dismissToDock() {
  console.log('Minimizando a dock, mode actual:', mode.value)
  mode.value = 'dock'
  console.log('Mode cambiado a:', mode.value)
  console.log('Dock debería ser visible ahora')
}

function toggleExpand() {
  console.log('Toggle expand, mode actual:', mode.value)
  mode.value = mode.value === 'dock' ? 'center' : 'dock'
  console.log('Mode cambiado a:', mode.value)
}

function onFirstResults() {
  // al recibir primeros resultados, anclar
  mode.value = 'dock'
}

onMounted(() => {
  window.addEventListener('properties:first-results', onFirstResults)
  // Conectar automáticamente al montar
  connect()
})
onBeforeUnmount(() => {
  window.removeEventListener('properties:first-results', onFirstResults)
  // Limpiar elementos de audio
  audioElements.forEach(el => {
    try {
      el.pause()
      el.srcObject = null
    } catch (e) {
      console.error('Error limpiando audio element:', e)
    }
  })
  audioElements = []
  // Limpiar AudioContexts
  audioContexts.forEach(ctx => {
    try {
      ctx.close()
    } catch (e) {
      console.error('Error cerrando AudioContext:', e)
    }
  })
  audioContexts = []
  if (room) {
    try {
      room.disconnect()
    } catch (e) {
      console.error('Error desconectando:', e)
    }
  }
})
</script>

<style scoped>
/* Animación Siri flotante */
.siri-wave-container {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.siri-icon {
  position: absolute;
  z-index: 10;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

.siri-wave {
  position: absolute;
  border-radius: 50%;
  border: 3px solid rgba(102, 126, 234, 0.3);
  animation: siri-pulse 2s ease-out infinite;
}

.siri-wave-1 {
  width: 100px;
  height: 100px;
  animation-delay: 0s;
}

.siri-wave-2 {
  width: 140px;
  height: 140px;
  animation-delay: 0.3s;
}

.siri-wave-3 {
  width: 180px;
  height: 180px;
  animation-delay: 0.6s;
}

.siri-wave-4 {
  width: 220px;
  height: 220px;
  animation-delay: 0.9s;
}

.siri-wave.active {
  border-color: rgba(102, 126, 234, 0.6);
  animation: siri-pulse-active 1.5s ease-out infinite;
}

@keyframes siri-pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

@keyframes siri-pulse-active {
  0% {
    transform: scale(0.9);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.4;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

/* Tamaño del modal igual que LoginModal */
.bg-white {
  height: fit-content !important;
  max-height: fit-content !important;
  min-height: auto !important;
  overflow: visible !important;
}

.fixed.inset-0 {
  min-height: auto !important;
  height: auto !important;
}

.flex.items-center.justify-center {
  align-items: flex-start !important;
  padding-top: 2rem !important;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Transición del dock */
.dock-enter-active,
.dock-leave-active {
  transition: all 0.3s ease;
}

.dock-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.dock-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.dock-enter-to,
.dock-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* Asegurar que el dock sea siempre visible cuando está presente */
.showy-dock {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}
</style>


