<template>
  <div :class="['zillow-card group bg-white rounded shadow border border-gray-100 overflow-hidden flex flex-col', { 'flipped': isFlipped }]" style="height:282px; width:307px; font-family: 'Roboto', Arial, sans-serif; position:relative;">
    <!-- Cara frontal -->
    <div class="card-face card-front flex flex-col h-full w-full">
      <!-- Imagen principal -->
      <div class="relative w-full" style="aspect-ratio:16/9; min-height:0;">
        <client-only>
          <Swiper
            v-if="property.images?.length"
            :modules="[Pagination, Navigation]"
            :pagination="{ clickable: true, dynamicBullets: true }"
            :navigation="false"
            :slides-per-view="1"
            :space-between="0"
            @swiper="onSwiper"
            @slideChange="onSlideChange"
            ref="swiperRef"
            class="h-full w-full"
          >
            <SwiperSlide v-for="(img, idx) in property.images" :key="idx">
              <img 
                :src="img" 
                :alt="`Foto de la propiedad ${idx + 1}`" 
                @click.stop="handleImageClick"
                class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105 cursor-pointer" 
              />
            </SwiperSlide>
            <!-- Flechas personalizadas dentro del Swiper -->
            <button v-if="showPrevButton && property.images.length > 1" class="swiper-button-prev-custom" @click.stop="slidePrev" aria-label="Anterior">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <button v-if="showNextButton && property.images.length > 1" class="swiper-button-next-custom" @click.stop="slideNext" aria-label="Siguiente">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
            </button>
          </Swiper>
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400 bg-gradient-to-br from-gray-50 to-gray-100">
              <div class="text-center">
              <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p class="text-sm">Sin imágenes</p>
              </div>
          </div>
          <!-- Botón de favorito -->
          <button @click.stop="handleFavoriteClick" class="absolute top-3 right-3 z-20 favorite-btn flex items-center justify-center transition-transform duration-200 hover:scale-110 active:scale-95 group/fav" :aria-pressed="isFavorite">
            <svg :class="['h-10 w-10 transition-all duration-300 heart-outline', isFavorite ? 'fill-red-500' : 'fill-black35', 'group-hover/fav:animate-fav-pulse']" viewBox="0 0 24 24" stroke-width="2" :stroke="'#fff'">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
        </client-only>
        <!-- Badge -->
        <div v-if="property.badge" class="absolute top-3 left-3 z-10 badge-zillow flex items-center gap-1">
          <template v-if="property.badge === '3D TOUR'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M21 7.5l-9-5.25-9 5.25M21 7.5v9l-9 5.25-9-5.25v-9"/><path d="M3.27 6.96l8.73 5.19 8.73-5.19"/></svg>
          </template>
          <span>{{ property.badge }}</span>
        </div>
      </div>
      <!-- Contenido -->
      <div class="flex-1 flex flex-col justify-between px-4 py-2 gap-1" @click.stop="handleContentClick">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="zillow-price">{{ formatCurrency(property.price) }}</span>
            <span v-if="property.expenses" class="zillow-expenses">+ {{ formatCurrency(property.expenses) }} exp.</span>
          </div>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-700 mb-1">
          <span class="truncate">{{ property.address }}</span>
          <span v-if="property.zone || property.localidad" class="mx-1 text-gray-300">|</span>
          <span class="truncate">{{ property.zone || property.localidad }}</span>
        </div>
        <div class="flex items-center gap-3 text-xs text-gray-700 mb-1 zillow-features">
          <span v-if="property.total_surface">{{ property.total_surface }} m² tot.</span>
          <span v-if="property.ambience"><span class="mx-1 text-gray-300">|</span>{{ property.ambience }} amb.</span>
          <span v-if="property.bedrooms"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 7v11m0-4h18m0 4v-8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8z"/><path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/></svg> {{ property.bedrooms }}</span>
          <span v-if="property.bathrooms"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4h-10a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/><path d="M6 12v-7a2 2 0 0 1 2-2h3v2.25"/><path d="M4 21l1-1.5"/><path d="M20 21l-1-1.5"/></svg> {{ property.bathrooms }}</span>
          <span v-if="property.garage_count"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6-6h15m-6 0v-5"/></svg> {{ property.garage_count }}</span>
        </div>
        <div class="text-[10px] text-gray-400 mt-1 truncate">{{ property.realty }}</div>
      </div>
      <!-- Botones de acción -->
      <div class="flex justify-end items-center p-2 border-t border-gray-100">
        <button @click.stop="isFlipped = !isFlipped" class="text-gray-500 hover:text-indigo-600 transition-colors p-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" /></svg>
        </button>
        <button @click.stop="$emit('close')" class="text-gray-500 hover:text-red-600 transition-colors p-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>
        </button>
      </div>
    </div>
    <!-- Cara trasera -->
    <div class="card-face card-back flex flex-col h-full w-full p-4 justify-center items-center text-center bg-gray-50">
      <h3 class="font-bold text-lg mb-2">Contactar</h3>
      <p class="text-sm text-gray-600 mb-4">¿Te interesa esta propiedad?</p>
      <button @click.stop="isFlipped = !isFlipped" class="absolute top-2 right-2 text-gray-400 hover:text-gray-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
      <button class="w-full bg-green-500 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center gap-2 hover:bg-green-600 transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" /></svg>
        Contactar por WhatsApp
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import 'swiper/css/navigation';
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'

const props = defineProps({
  property: {
    type: Object,
    default: () => ({})
  },
  isFavorite: {
    type: Boolean,
    default: false
  },
  isLoggedIn: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-favorite', 'close', 'open-modal', 'login-request'])

const isFlipped = ref(false)
const swiperRef = ref(null)
const swiperInstance = ref(null)
const showPrevButton = ref(false)
const showNextButton = ref(false)

function onSwiper(swiper) {
  swiperInstance.value = swiper
  updateNav(swiper)
}
function onSlideChange(swiper) {
  updateNav(swiper)
}
function updateNav(swiper) {
  if (!swiper) return
  showPrevButton.value = swiper.activeIndex > 0
  showNextButton.value = swiper.activeIndex < swiper.slides.length - 1
}
function slidePrev() {
  if (swiperInstance.value) {
    swiperInstance.value.slidePrev()
  }
}
function slideNext() {
  if (swiperInstance.value) {
    swiperInstance.value.slideNext()
  }
}

onMounted(() => {
  if (swiperRef.value && swiperRef.value.swiper) {
    swiperInstance.value = swiperRef.value.swiper
    updateNav(swiperInstance.value)
    swiperInstance.value.on('slideChange', () => updateNav(swiperInstance.value))
  }
})

function formatCurrency(price) {
  let num;
  if (typeof price === 'string') {
    num = parseInt(price.replace(/\./g, '').replace(',', '.'), 10);
  } else if (typeof price === 'number') {
    num = price;
  } else {
    return '';
  }
  if (isNaN(num)) return '';
  const formattedPrice = new Intl.NumberFormat('es-AR', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(num);
  return `U$D ${formattedPrice}`;
}

function handleFavoriteClick() {
  if (!props.isLoggedIn) {
    emit('login-request')
  } else {
    emit('toggle-favorite')
  }
}

function handleImageClick(event) {
  event.stopPropagation();
  emit('open-modal');
}

function handleContentClick(event) {
  // Solo abrir modal si no se hizo clic en un botón dentro del contenido
  if (event.target.closest('button')) return;
  emit('open-modal');
}
</script>

<style scoped>
.zillow-card {
  perspective: 1000px;
  transition: box-shadow 0.2s, transform 0.2s;
  border-radius: 4px;
}
.zillow-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.13);
  transform: translateY(-2px) scale(1.01);
}
.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  transition: transform 0.6s;
}
.card-front {
  transform: rotateY(0deg);
}
.card-back {
  transform: rotateY(180deg);
  background-color: #f9fafb; /* bg-gray-50 */
}
.zillow-card.flipped .card-front {
  transform: rotateY(-180deg);
}
.zillow-card.flipped .card-back {
  transform: rotateY(0deg);
}
.badge-zillow {
  background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.zillow-price {
  font-size: 1.15rem;
  font-weight: 700;
  color: #222;
  letter-spacing: -0.5px;
}
.zillow-expenses {
  font-size: 0.85rem;
  color: #888;
  font-weight: 400;
}
.zillow-features .icon-inline {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 2px;
}
:deep(.swiper-pagination-bullet) {
  background: #fff !important;
  opacity: 0.7 !important;
}
:deep(.swiper-pagination-bullet-active) {
  background: #fff !important;
  opacity: 1 !important;
}
.swiper-button-prev-custom,
.swiper-button-next-custom {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 30;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}
.group:hover .swiper-button-prev-custom,
.group:hover .swiper-button-next-custom {
  opacity: 1;
  pointer-events: auto;
}
.swiper-button-prev-custom {
  left: 8px;
}
.swiper-button-next-custom {
  right: 8px;
}
.swiper-button-prev-custom:hover,
.swiper-button-next-custom:hover {
  opacity: 1;
}
.favorite-btn {
  border: none;
  background: transparent;
  padding: 0.35rem;
}
.heart-outline {
  filter: drop-shadow(0 1px 4px rgba(0,0,0,0.10));
}
.group-hover\/fav\:animate-fav-pulse:hover {
  animation: fav-pulse 0.7s;
}
@keyframes fav-pulse {
  0% { transform: scale(1); }
  30% { transform: scale(1.18); }
  50% { transform: scale(1.08); }
  100% { transform: scale(1); }
}
.fill-red-500 {
  fill: #ef4444;
}
.fill-black35 {
  fill: rgba(0,0,0,0.35);
}
</style>
