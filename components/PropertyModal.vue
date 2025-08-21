<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4" @click.self="handleCloseModal">
    <div class="bg-white shadow-2xl w-full max-w-6xl h-[90vh] max-h-[90vh] flex flex-col relative overflow-hidden rounded-lg">
      <!-- Barra superior: branding, favoritos, compartir, tour -->
      <div class="flex items-center justify-between px-8 pt-12 pb-6 border-b border-gray-200 bg-white/95 backdrop-blur-sm sticky top-0 z-50">
        <div class="flex-1 flex justify-start">
          <span class="text-3xl font-bold tracking-wide text-indigo-700 select-none">Showtime Prop</span>
        </div>
        <div class="flex items-center gap-3">
          <!-- Corazón de favoritos sincronizado y animado -->
          <button @click="toggleFavorite" @click.native="console.log('Click nativo en corazón')" :aria-pressed="isFavorite" class="focus:outline-none" style="cursor: pointer;">
            <svg :class="['w-8 h-8 transition-all duration-300', isFavorite ? 'fill-red-500 animate-fav-pulse' : 'fill-gray-200', 'stroke-indigo-500']" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
          <!-- Compartir -->
          <button @click="shareProperty" class="focus:outline-none">
            <svg class="w-7 h-7 text-indigo-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 4.5a2.5 2.5 0 1 1 .702 1.737L6.97 9.604a2.518 2.518 0 0 1 0 .792l6.733 3.367a2.5 2.5 0 1 1-.671 1.341l-6.733-3.367a2.5 2.5 0 1 1 0-3.475l6.733-3.366A2.52 2.52 0 0 1 13 4.5Z" />
            </svg>
          </button>
          <!-- Botón Solicitar Tour -->
          <button class="ml-2 px-6 py-2 rounded bg-gradient-to-r from-cyan-400 via-indigo-500 to-cyan-500 text-white font-bold text-base shadow-md transition-all duration-200 hover:shadow-lg hover:from-cyan-300 hover:to-indigo-400 focus:outline-none">
            Solicitar Tour
          </button>
          <!-- Botón de cerrar más visible -->
          <button @click="handleCloseModal" class="ml-4 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800 transition-colors focus:outline-none">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      <div class="flex-grow overflow-y-auto flex flex-col">
        <!-- Swiper de paneles principales -->
        <div class="w-full bg-gray-100 flex flex-col items-center group">
          <Swiper
            :modules="[Navigation, Thumbs]"
            :navigation="true"
            :thumbs="{ swiper: thumbsSwiper }"
            :slides-per-view="1"
            class="w-full max-w-5xl h-[480px] rounded-xl shadow-2xl swiper-modal-main mt-2"
            @swiper="setMainSwiper"
          >
            <SwiperSlide v-for="(slide, idx) in slides" :key="idx">
              <template v-if="slide.type === 'image'">
                <img :src="slide.src" class="object-cover w-full h-[480px] rounded-xl" />
              </template>
              <template v-else-if="slide.type === 'virtualTour'">
                <iframe :src="slide.src" width="100%" height="480" frameborder="0" allowfullscreen class="rounded-xl"></iframe>
              </template>
              <template v-else-if="slide.type === 'floorPlan'">
                <img :src="slide.src" class="object-contain w-full h-[480px] rounded-xl bg-white" />
              </template>
            </SwiperSlide>
            <!-- Paginación personalizada -->
            <template #pagination>
              <div class="swiper-pagination swiper-modal-pagination"></div>
            </template>
          </Swiper>
          <!-- Miniaturas -->
          <div class="w-full max-w-5xl mt-3">
            <Swiper
              :modules="[Thumbs]"
              :slides-per-view="Math.min(slides.length, 8)"
              space-between="12"
              watch-slides-progress
              class="h-24"
              @swiper="setThumbsSwiper"
            >
              <SwiperSlide v-for="(slide, idx) in slides" :key="'thumb-' + idx">
                <img v-if="slide.type === 'image' || slide.type === 'floorPlan'" :src="slide.src" class="object-cover w-full h-24 rounded cursor-pointer border border-gray-300 hover:border-indigo-400 transition" />
                <div v-else class="w-full h-24 flex items-center justify-center bg-gray-200 rounded text-xs text-gray-500 cursor-pointer">
                  <span v-if="slide.type === 'virtualTour'">Tour Virtual</span>
                  <!-- Otros tipos -->
                </div>
              </SwiperSlide>
            </Swiper>
          </div>
        </div>

        <!-- Datos principales -->
        <div class="p-4 flex flex-col gap-3">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 class="text-3xl font-bold text-gray-900 mb-1">{{ property.title }}</h2>
              <div class="text-lg text-gray-700 mb-2">{{ property.address }}</div>
              <div class="flex flex-wrap gap-4 text-base font-semibold text-gray-800">
                <span>USD {{ property.price }}</span>
                <span v-if="property.bedrooms">{{ property.bedrooms }} hab.</span>
                <span v-if="property.bathrooms">{{ property.bathrooms }} baños</span>
                <span v-if="property.size">{{ property.size }} m²</span>
              </div>
            </div>
            <div class="flex flex-col gap-2 min-w-[220px]">
              <button class="w-full py-2 rounded bg-blue-600 text-white font-bold text-lg shadow hover:bg-blue-700 transition">Solicitar tour</button>
              <button class="w-full py-2 rounded bg-white border border-blue-600 text-blue-600 font-bold text-lg shadow hover:bg-blue-50 transition">Contactar agente</button>
            </div>
          </div>

          <!-- Etiquetas de amenities -->
          <div v-if="property.amenities && property.amenities.length" class="flex flex-wrap gap-2 mt-2">
            <span v-for="(amenity, idx) in property.amenities" :key="idx" class="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold">{{ amenity }}</span>
          </div>

          <!-- Descripción -->
          <div v-if="property.description" class="mt-4">
            <h3 class="text-xl font-semibold mb-2">Descripción</h3>
            <p class="text-gray-700 leading-relaxed">{{ property.description }}</p>
          </div>

          <!-- Detalles -->
          <div class="mt-4">
            <h3 class="text-xl font-semibold mb-2">Detalles de la Propiedad</h3>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-gray-800">
              <div class="flex flex-col"><span class="font-semibold">Precio</span><span>USD {{ property.price }}</span></div>
              <div class="flex flex-col"><span class="font-semibold">Expensas</span><span>$ {{ property.expenses }}</span></div>
              <div class="flex flex-col"><span class="font-semibold">Dirección</span><span>{{ property.address }}</span></div>
              <div class="flex flex-col"><span class="font-semibold">Superficie</span><span>{{ property.size }} m²</span></div>
              <div class="flex flex-col"><span class="font-semibold">Ambientes</span><span>{{ property.rooms }}</span></div>
              <div class="flex flex-col"><span class="font-semibold">Baños</span><span>{{ property.bathrooms }}</span></div>
              <div class="flex flex-col"><span class="font-semibold">Dormitorios</span><span>{{ property.bedrooms }}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Thumbs } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/thumbs'
import { useSupabaseUser } from '#imports'

const props = defineProps({
  property: {
    type: Object,
    required: true
  },
  isFavorite: Boolean
});
const emit = defineEmits(['close', 'toggle-favorite', 'login-request']);

const thumbsSwiper = ref(null)
const mainSwiper = ref(null)
function setThumbsSwiper(swiper) { thumbsSwiper.value = swiper }
function setMainSwiper(swiper) { mainSwiper.value = swiper }

const slides = computed(() => {
  const arr = []
  if (props.property.images?.length) {
    arr.push(...props.property.images.map(img => ({ type: 'image', src: img })))
  }
  if (props.property.hasVirtualTour && props.property.virtualTourUrl) {
    arr.push({ type: 'virtualTour', src: props.property.virtualTourUrl })
  }
  if (props.property.floorPlan) {
    arr.push({ type: 'floorPlan', src: props.property.floorPlan })
  }
  // Puedes agregar más tipos de paneles aquí
  return arr
})

function shareProperty() {
  if (navigator.share) {
    navigator.share({
      title: props.property.title,
      text: `Mirá esta propiedad: ${props.property.title}`,
      url: window.location.href
    })
  } else {
    alert('Tu navegador no soporta compartir')
  }
}

// Sincronización y animación del favorito
const isFavorite = ref(props.isFavorite)
watch(() => props.isFavorite, (val) => { isFavorite.value = val })

// Verificar si el usuario está logueado
const user = useSupabaseUser()

function toggleFavorite() {
  console.log('toggleFavorite llamado en PropertyModal')
  console.log('user.value:', user.value)
  console.log('props.isFavorite:', props.isFavorite)
  console.log('isFavorite.value:', isFavorite.value)
  
  if (!user.value) {
    console.log('Usuario no logueado, emitiendo login-request')
    // Si no está logueado, emitir evento para mostrar modal de login
    emit('login-request')
    return
  }
  
  console.log('Usuario logueado, procediendo con toggle')
  // Si está logueado, proceder con el toggle
  isFavorite.value = !isFavorite.value
  console.log('Nuevo isFavorite.value:', isFavorite.value)
  emit('toggle-favorite', props.property)
  console.log('Evento toggle-favorite emitido')
}

function handleCloseModal(event) {
  console.log('PropertyModal handleCloseModal llamado');
  if (event) event.stopPropagation();
  emit('close');
  console.log('PropertyModal emit close enviado');
}
</script>

<style scoped>
/* Asegurar que el modal esté bien posicionado */
.fixed.inset-0 {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 40;
}

/* Asegurar que el contenido del modal esté centrado */
.flex.justify-center.items-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

@keyframes fav-pulse {
  0% { transform: scale(1); filter: drop-shadow(0 0 0 #f87171); }
  50% { transform: scale(1.18); filter: drop-shadow(0 0 8px #f87171); }
  100% { transform: scale(1); filter: drop-shadow(0 0 0 #f87171); }
}
.animate-fav-pulse {
  animation: fav-pulse 0.5s;
}
.swiper-modal-main :deep(.swiper-button-next),
.swiper-modal-main :deep(.swiper-button-prev) {
  color: #fff !important;
  opacity: 0;
  transition: opacity 0.2s;
}
.swiper-modal-main:hover :deep(.swiper-button-next),
.swiper-modal-main:hover :deep(.swiper-button-prev) {
  opacity: 1;
}
.swiper-modal-main :deep(.swiper-pagination-bullet) {
  background: #fff !important;
  opacity: 0.7 !important;
}
.swiper-modal-main :deep(.swiper-pagination-bullet-active) {
  background: #fff !important;
  opacity: 1 !important;
}
</style>
