<template>
  <div :class="['zillow-card group rounded shadow border border-gray-100 overflow-hidden flex flex-col', { 'flipped': isFlipped }]" style="height:282px; width:307px; font-family: 'Roboto', Arial, sans-serif; position:relative;">
    <div class="card-inner">
      <!-- Cara frontal -->
      <div class="card-face card-front flex flex-col h-full w-full" style="background:#fff;">
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
                <img
                  :src="img"
                  :alt="`Foto de la propiedad ${idx + 1}`"
                  class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105 cursor-pointer"
                  @click="$emit('open-modal', property)"
                />
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
            <button @click="handleFavoriteClick" class="absolute top-3 right-3 z-20 favorite-btn flex items-center justify-center transition-transform duration-200 hover:scale-110 active:scale-95 group/fav" :aria-pressed="isFavorite">
              <svg :class="['h-10 w-10 transition-all duration-300 heart-outline', isFavorite ? 'fill-rose-600' : 'fill-black35', 'group-hover/fav:animate-fav-pulse']" viewBox="0 0 24 24" stroke-width="2" :stroke="'#fff'">
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
      <!-- Cara trasera: título, input, botón y compartir -->
      <div class="card-face card-back flex flex-col items-center justify-center w-full bg-white text-gray-800 p-6">
        <div class="text-lg font-semibold text-gray-800 mb-6">¡Enterate si baja de precio!</div>
        <div class="w-full max-w-xs flex flex-col items-center">
          <input
            v-model="whatsapp"
            type="text"
            placeholder="+549 223 353-3333 <-Tu WhatsApp"
            class="rounded px-3 py-2 w-full bg-gray-200 text-gray-800 placeholder-gray-400 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-cyan-400 mb-4"
            style="box-sizing: border-box;"
          />
          <button
            v-if="whatsapp"
            @click="setPriceDropAlert"
            class="w-full py-2 rounded bg-gradient-to-r from-cyan-400 via-indigo-500 to-cyan-500 text-white font-semibold shadow-md transition-all duration-200 hover:shadow-lg hover:from-cyan-300 hover:to-indigo-400 focus:outline-none mb-4"
          >Enviar Alerta de Precio</button>
          <!-- Botón de compartir -->
          <button
            @click.stop="setPriceDropAlert"
            class="w-full py-2 rounded bg-green-500 text-white font-semibold shadow-lg transition duration-300 ease-in-out transform hover:-translate-y-1 hover:bg-green-600 focus:outline-none flex items-center justify-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12s-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.368a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
            Compartir Propiedad
          </button>
        </div>
        <button @click.stop="isFlipped = false" class="absolute top-2 right-2 text-gray-400 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import 'swiper/css/navigation';
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'
import { Share2, X, Heart } from 'lucide-vue-next';
import { useFavoritesStore } from '~/stores/favorites';
import { useLoginModalStore } from '~/stores/loginModal';
import { storeToRefs } from 'pinia';
import { useSupabaseUser } from '#imports';
import { useToast } from 'vue-toastification';

const user = useSupabaseUser();
const store = useFavoritesStore();
const { isFavorite } = storeToRefs(store);
const { toggleFavorite } = store;
const toast = useToast();
const loginModal = useLoginModalStore();

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
const whatsapp = ref("")
const emit = defineEmits(['toggle-favorite', 'open-modal', 'login-request'])

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

function setPriceDropAlert() {
  if (!user.value) {
    loginModal.open();
    toast.info("Debes iniciar sesión para crear una alerta.");
    return;
  }
  
  const link = `https://properties-nuxt.vercel.app/property/${props.property.id}`;
  const text = `¡Hola! Me interesa la propiedad en ${props.property.address}. Quisiera recibir una alerta si baja de precio. Mi número es ${whatsapp.value}. Enlace: ${link}`;

  // ... existing code ...
}

function handleFavoriteClick(event) {
  event.stopPropagation()
  if (!user.value) {
    loginModal.open();
    toast.info("Debes iniciar sesión para guardar favoritos");
    return;
  }
  toggleFavorite(props.property)
}
</script>

<style scoped>
.zillow-card {
  perspective: 1000px;
}

.zillow-card.flipped .card-inner {
  transform: rotateY(180deg);
}

.zillow-card.flipped .card-front {
  pointer-events: none;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
  border-radius: inherit;
  overflow: hidden;
}

.card-back {
  transform: rotateY(180deg);
}

.card-arrow {
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-bottom: 15px solid #fff;
  z-index: 10;
}

.swiper-button-prev-custom, .swiper-button-next-custom {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 32px;
  height: 32px;
  background-color: rgba(0,0,0,0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.swiper-button-prev-custom:hover, .swiper-button-next-custom:hover {
  background-color: rgba(0,0,0,0.7);
}

.swiper-button-prev-custom {
  left: 10px;
}

.swiper-button-next-custom {
  right: 10px;
}

.favorite-btn {
  background: none;
  border: none;
  padding: 0;
}

.heart-outline {
  stroke-width: 1.5; /* Grosor del borde */
}

.fill-black35 {
  fill: rgba(0,0,0,0.35); /* Relleno semi-transparente */
}

.badge-zillow {
  background-color: rgba(0,0,0,0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
  backdrop-filter: blur(2px);
}

.zillow-price {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a1a;
}

.zillow-expenses {
  font-size: 12px;
  color: #555;
  font-weight: 500;
}

.zillow-features .icon-inline {
  margin-right: 4px; /* Espacio entre icono y texto */
  vertical-align: middle;
}

.zillow-features > span:not(.mx-1) {
  display: flex;
  align-items: center;
}

.share-icon:hover {
  transform: scale(1.2);
  color: #38bdf8;
}

@keyframes fav-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25); }
}

.share-btn-anim:hover {
  box-shadow: 0 0 16px #38e8ff, 0 0 32px #6366f1;
}
</style>
