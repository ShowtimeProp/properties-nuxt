<template>
  <div @click.stop class="zillow-card group bg-white rounded shadow border border-gray-100 overflow-hidden flex flex-col" style="height:282px; width:344px; font-family: 'Roboto', Arial, sans-serif;">
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
      </client-only>
      <!-- Badge dinámico -->
      <div v-if="property.badge" class="absolute top-3 left-3 z-10 badge-zillow flex items-center gap-1">
        <template v-if="property.badge === '3D TOUR'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M21 7.5l-9-5.25-9 5.25M21 7.5v9l-9 5.25-9-5.25v-9"/><path d="M3.27 6.96l8.73 5.19 8.73-5.19"/></svg>
        </template>
        <span>{{ property.badge }}</span>
      </div>
    </div>
    <!-- Contenido -->
    <div class="flex-1 flex flex-col justify-between px-4 py-2 gap-1">
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
        <span v-if="property.total_surface">{{ property.total_surface }} m² tot.</span>
        <span v-if="property.ambience"><span class="mx-1 text-gray-300">|</span>{{ property.ambience }} amb.</span>
        <span v-if="property.bedrooms"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 7v11m0-4h18m0 4v-8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8z"/><path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/></svg> {{ property.bedrooms }}</span>
        <span v-if="property.bathrooms"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4h-10a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/><path d="M6 12v-7a2 2 0 0 1 2-2h3v2.25"/><path d="M4 21l1-1.5"/><path d="M20 21l-1-1.5"/></svg> {{ property.bathrooms }}</span>
        <span v-if="property.garage_count"><span class="mx-1 text-gray-300">|</span><svg class="icon-inline" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6-6h15m-6 0v-5"/></svg> {{ property.garage_count }}</span>
      </div>
      <!-- Inmobiliaria (cuarto renglón) -->
      <div class="text-[10px] text-gray-400 mt-1 truncate">{{ property.realty }}</div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, onMounted } from 'vue'
import 'swiper/css/navigation';
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'

const swiperId = `swiper-clean-${Math.random().toString(36).substring(7)}`;
const props = defineProps({
  property: {
    type: Object,
    default: () => ({
      images: [
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=360&h=180&fit=crop',
        'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=360&h=180&fit=crop',
        'https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=360&h=180&fit=crop'
      ],
      price: 150000,
      expenses: 12000,
      title: 'Departamento céntrico moderno',
      address: 'Corrientes 2345, Mar del Plata',
      total_surface: 75,
      ambience: 3,
      bedrooms: 2,
      bathrooms: 2,
      garage_count: 1,
      realty: 'REMAX BIANCA NICOLINI',
      hasVirtualTour: true,
      isNew: true,
      badge: '3D TOUR',
      tags: ['Nueva construcción', 'Balcón', 'Cocina integrada']
    })
  }
})
const property = props.property
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
</script>

<style scoped>
.zillow-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  transition: box-shadow 0.2s, transform 0.2s;
  width: 344px;
  border-radius: 4px;
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
.zillow-features .icon-feat {
  width: 16px;
  height: 16px;
  margin-right: 2px;
}
/* Cambiar color de los bullets de Swiper a blanco */
:deep(.swiper-pagination-bullet) {
  background: #fff !important;
  opacity: 0.7 !important;
}
:deep(.swiper-pagination-bullet-active) {
  background: #fff !important;
  opacity: 1 !important;
}
.zillow-address {
  font-size: 0.93em;
  font-weight: 500;
  color: #444;
  margin-top: 2px;
}
.zillow-realty {
  font-size: 0.8em;
  color: #888;
  margin-top: 1px;
}
/* Flechas ocultas por defecto y visibles solo en hover */
:deep(.swiper-button-prev-custom),
:deep(.swiper-button-next-custom) {
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}
.group:hover :deep(.swiper-button-prev-custom),
.group:hover :deep(.swiper-button-next-custom) {
  opacity: 1;
  pointer-events: auto;
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
  opacity: 0.85;
  transition: opacity 0.2s;
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
.icon-inline {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 2px;
}
</style>