<template>
  <ClientOnly>
    <div>
      <!-- Overlay centrado al inicio -->
      <div v-if="mode==='center'" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/20">
        <div class="relative bg-white rounded-2xl shadow-2xl p-6 w-[92vw] max-w-[520px] text-center">
          <div class="mx-auto mb-4 w-28 h-28 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center animate-pulse">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-14 h-14 text-white"><path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/></svg>
          </div>
          <p class="font-bold text-lg mb-2">Hola, soy Showy. ¿Qué estás buscando?</p>
          <p class="text-sm text-gray-600 mb-4">Activa tu micrófono para hablar conmigo y te mostraré propiedades ideales.</p>
          <div class="flex gap-3 justify-center">
            <button @click="connect" :disabled="connecting" class="px-4 py-2 rounded-lg text-white font-semibold shadow bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60">
              {{ connecting ? 'Conectando…' : 'Activar micrófono' }}
            </button>
            <button @click="dismissToDock" class="px-4 py-2 rounded-lg font-semibold border border-gray-300 hover:bg-gray-50">Más tarde</button>
          </div>
        </div>
      </div>

      <!-- Dock abajo‑derecha -->
      <div v-if="mode==='dock'" class="fixed right-4 bottom-4 z-[55]">
        <button @click="toggleExpand" class="relative w-16 h-16 rounded-full shadow-xl border bg-white overflow-hidden hover:shadow-2xl">
          <span class="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 opacity-20 animate-ping"></span>
          <span class="absolute inset-0 rounded-full flex items-center justify-center">
            <svg v-if="!listening" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-8 h-8 text-indigo-600"><path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-8 h-8 text-cyan-600 animate-bounce"><path fill="currentColor" d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4m5 10a5 5 0 0 1-10 0H5a7 7 0 0 0 14 0zM12 20a7 7 0 0 0 7-7h-2a5 5 0 0 1-10 0H5a7 7 0 0 0 7 7"/></svg>
          </span>
        </button>
      </div>
    </div>
  </ClientOnly>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { Room } from 'livekit-client'

const mode = ref('center') // center | dock
const listening = ref(false)
const connecting = ref(false)
let room = null

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
    await room.connect(url, token)
    await room.localParticipant.setMicrophoneEnabled(true)
    listening.value = true
  } catch (e) {
    console.error('LiveKit connect error', e)
  } finally {
    connecting.value = false
  }
}

function dismissToDock() {
  mode.value = 'dock'
}

function toggleExpand() {
  mode.value = mode.value === 'dock' ? 'center' : 'dock'
}

function onFirstResults() {
  // al recibir primeros resultados, anclar
  mode.value = 'dock'
}

onMounted(() => {
  window.addEventListener('properties:first-results', onFirstResults)
})
onBeforeUnmount(() => {
  window.removeEventListener('properties:first-results', onFirstResults)
  if (room) try { room.disconnect() } catch {}
})
</script>

<style scoped>
</style>


