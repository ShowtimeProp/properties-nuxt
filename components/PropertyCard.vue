<template>
  <div :class="['zillow-card group bg-white rounded shadow border border-gray-100 overflow-hidden flex flex-col', { 'flipped': isFlipped }]" style="height:282px; width:307px; font-family: 'Roboto', Arial, sans-serif; position:relative;">
    <!-- Cara frontal -->
    <div class="card-face card-front flex flex-col h-full w-full">
      <!-- Imagen principal -->
      <div class="relative w-full" style="aspect-ratio:16/9; min-height:0;">
        <ClientOnly>
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
              <img :src="img" :alt="`Foto de la propiedad ${idx + 1}`" class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105" />
            </SwiperSlide>
            <!-- Flechas personalizadas dentro del Swiper -->
            <button v-if="showPrevButton && property.images.length > 1" class="swiper-button-prev-custom" @click.stop="slidePrev" aria-label="Anterior">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <button v-if="showNextButton && property.images.length > 1" class="swiper-button-next-custom" @click.stop="slideNext" aria-label="Siguiente">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
            </button>
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400 bg-gradient-to-br from-gray-50 to-gray-100">
              <div class="text-center">
                <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-sm">Sin imágenes</p>
              </div>
            </div>
          </Swiper>
          <!-- Botón de favorito SVG puro -->
          <button @click.stop="$emit('toggle-favorite', property)" class="absolute top-3 right-3 z-20 favorite-btn flex items-center justify-center transition-transform duration-200 hover:scale-110 active:scale-95 group/fav" :aria-pressed="isFavorite">
            <svg :class="['h-10 w-10 transition-all duration-300 heart-outline', isFavorite ? 'fill-heart-translucent' : 'fill-black35', 'group-hover/fav:animate-fav-pulse']" viewBox="0 0 24 24" stroke-width="2" :stroke="'#fff'">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
        </ClientOnly>
        <!-- Badge dinámico -->
        <div v-if="property.badge" class="absolute top-3 left-3 z-10 badge-zillow flex items-center gap-1">
          <template v-if="property.badge === '3D TOUR'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M21 7.5l-9-5.25-9 5.25M21 7.5v9l-9 5.25-9-5.25v-9"/><path d="M3.27 6.96l8.73 5.19 8.73-5.19"/></svg>
          </template>
          <span>{{ property.badge }}</span>
        </div>
      </div>
      <!-- Contenido -->
      <div class="flex-1 flex flex-col justify-between px-4 py-2 gap-1 overflow-visible">
        <!-- Precio y expensas (primer renglón) -->
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="zillow-price">{{ formatCurrency(property.price) }}</span>
            <span v-if="property.expenses" class="zillow-expenses">+ {{ formatCurrency(property.expenses) }} exp.</span>
          </div>
        </div>
        <!-- Dirección y zona/localidad (segundo renglón) -->
        <div class="flex items-center gap-2 text-xs text-gray-700 mb-1">
          <span class="truncate">{{ property.address }}</span>
          <span v-if="property.zone || property.localidad" class="mx-1 text-gray-300">|</span>
          <span class="truncate">{{ property.zone || property.localidad }}</span>
        </div>
        <!-- Características principales (tercer renglón) -->
        <div class="flex items-center gap-3 text-xs text-gray-700 mb-1 zillow-features">
          <span>{{ property.total_surface }} m² tot.</span>
          <span class="mx-1 text-gray-300">|</span>
          <span>{{ property.ambience }} amb.</span>
          <span class="mx-1 text-gray-300">|</span>
          <div class="flex items-center gap-4">
            <div class="flex flex-col items-center justify-center">
              <svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 7v11m0-4h18m0 4v-8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8z"/><path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/></svg>
              <span>{{ property.bedrooms }}</span>
            </div>
            <div class="flex flex-col items-center justify-center">
              <svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4h-10a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/><path d="M6 12v-7a2 2 0 0 1 2-2h3v2.25"/><path d="M4 21l1-1.5"/><path d="M20 21l-1-1.5"/></svg>
              <span>{{ property.bathrooms }}</span>
            </div>
            <div class="flex flex-col items-center justify-center">
              <svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6-6h15m-6 0v-5"/></svg>
              <span>{{ property.garage_count }}</span>
            </div>
          </div>
        </div>
        <!-- Inmobiliaria (cuarto renglón) -->
        <div class="text-[10px] text-gray-400 mt-1 truncate">{{ property.realty }}</div>
        <!-- Icono compartir -->
        <div class="absolute bottom-3 right-3 z-20" @click.stop="isFlipped = true">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 opacity-80 transition-all duration-200 cursor-pointer share-icon">
            <path d="M13 4.5a2.5 2.5 0 1 1 .702 1.737L6.97 9.604a2.518 2.518 0 0 1 0 .792l6.733 3.367a2.5 2.5 0 1 1-.671 1.341l-6.733-3.367a2.5 2.5 0 1 1 0-3.475l6.733-3.366A2.52 2.52 0 0 1 13 4.5Z" />
          </svg>
        </div>
      </div>
      <!-- Flecha centrada -->
      <div class="card-arrow" />
    </div>
    <!-- Cara trasera: opciones de compartir (placeholder) -->
    <div class="card-face card-back card-back-animated flex items-center justify-center" style="height:100%; width:100%; background:#f9fafb;">
      <!-- SVG borde doble: base azul + luz animada encima -->
      <svg :key="flipKey" width="100%" height="100%" viewBox="0 0 307 282" style="position:absolute; top:0; left:0; z-index:10; pointer-events:none;">
        <defs>
          <linearGradient id="neon-gradient" x1="0" y1="0" x2="307" y2="282" gradientUnits="userSpaceOnUse">
            <stop stop-color="#38e8ff"/>
            <stop offset="0.3" stop-color="#6366f1"/>
            <stop offset="0.7" stop-color="#06b6d4"/>
            <stop offset="1" stop-color="#38e8ff"/>
          </linearGradient>
        </defs>
        <!-- Borde base gradiente -->
        <rect
          x="1" y="1" width="305" height="280" rx="20"
          stroke="url(#neon-gradient)"
          stroke-width="10"
          fill="none"
        />
        <!-- Luz animada encima -->
        <rect
          x="1" y="1" width="305" height="280" rx="20"
          stroke="url(#neon-gradient)"
          stroke-width="10"
          fill="none"
          class="svg-animated-border"
        />
      </svg>
      <div class="text-lg font-semibold text-gray-700" style="z-index:20; position:relative;">Opciones para compartir</div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, onMounted, watch, onBeforeUnmount } from 'vue'
import 'swiper/css/navigation';
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'

const props = defineProps({
  property: {
    type: Object,
    required: true
  },
  isFavorite: {
    type: Boolean,
    default: false
  }
})
const swiperRef = ref(null)
const swiperInstance = ref(null)
const showPrevButton = ref(false)
const showNextButton = ref(false)
const isFlipped = ref(false)
const flipKey = ref(0)

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
  document.addEventListener('mousedown', handleClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
function handleClickOutside(event) {
  const card = event.target.closest('.zillow-card');
  if (!card) {
    isFlipped.value = false;
  }
}
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

watch(isFlipped, (val) => {
  if (val) {
    flipKey.value++
  }
})
</script>

<style scoped>
.zillow-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  transition: box-shadow 0.2s, transform 0.2s;
  width: 307px;
  border-radius: 4px;
  position: relative;
  perspective: 1200px;
}
@media (max-width: 640px) {
  .zillow-card {
    width: 100% !important;
    min-width: 0;
  }
}
.zillow-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.13);
  transform: translateY(-2px) scale(1.01);
}
.zillow-fav-btn, .zillow-heart, .sonar-effect, .pulse {
  display: none !important;
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
}
.zillow-price {
  font-size: 1.08rem;
  font-weight: 700;
  color: #222;
}
.zillow-expenses {
  font-size: 0.85rem;
  color: #888;
  font-weight: 400;
  margin-left: 2px;
}
.text-xs {
  font-size: 0.85rem;
}
.zillow-features {
  font-size: 0.85rem;
}
.text-[10px] {
  font-size: 0.68rem;
}
.card-arrow {
  position: absolute;
  left: 50%;
  bottom: -18px;
  transform: translateX(-50%);
  width: 32px;
  height: 18px;
  z-index: 40;
  pointer-events: none;
  background: none;
}
.card-arrow::after {
  content: '';
  display: block;
  width: 32px;
  height: 18px;
  background: none;
  mask: url('data:image/svg+xml;utf8,<svg width="32" height="18" viewBox="0 0 32 18" xmlns="http://www.w3.org/2000/svg"><polygon points="16,18 0,0 32,0" fill="white" stroke="%23e5e7eb" stroke-width="1"/></svg>') no-repeat center/contain;
  -webkit-mask: url('data:image/svg+xml;utf8,<svg width="32" height="18" viewBox="0 0 32 18" xmlns="http://www.w3.org/2000/svg"><polygon points="16,18 0,0 32,0" fill="white" stroke="%23e5e7eb" stroke-width="1"/></svg>') no-repeat center/contain;
  background-color: #fff;
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
  transition: opacity 0.2s;
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
.fill-heart-translucent {
  fill: rgba(239,68,68,0.55);
}
.fill-black35 {
  fill: rgba(0,0,0,0.22);
}
.share-icon:hover {
  transform: translateY(-4px) scale(1.18);
  opacity: 1;
  filter: drop-shadow(0 0 6px #38e8ff) drop-shadow(0 0 12px #6366f1);
}
.card-face {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0; left: 0;
  backface-visibility: hidden;
  transition: transform 0.6s cubic-bezier(.4,2,.6,1);
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  overflow: hidden;
}
.card-front {
  z-index: 2;
  transform: rotateY(0deg);
}
.card-back {
  z-index: 3;
  transform: rotateY(180deg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 12px;
  background: #f9fafb;
  border: none !important;
  box-shadow: none !important;
}
.zillow-card.flipped .card-front {
  transform: rotateY(-180deg);
}
.zillow-card.flipped .card-back {
  transform: rotateY(0deg);
}
.card-back-animated {
  position: relative;
  z-index: 1;
  overflow: visible;
}
.svg-animated-border {
  stroke-dasharray: 400 800;
  stroke-dashoffset: 0;
  animation: scanBorder 6s linear infinite;
  filter: drop-shadow(0 0 8px #38e8ff) drop-shadow(0 0 16px #6366f1);
}
@keyframes scanBorder {
  to {
    stroke-dashoffset: -1200;
  }
}
</style>
