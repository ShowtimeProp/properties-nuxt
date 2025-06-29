<template>
  <div class="card w-full bg-base-100 shadow-md rounded-lg overflow-hidden font-sans">
    <figure class="relative h-[177px] w-full bg-gray-100 m-0 overflow-hidden">
      <client-only>
        <Swiper
          v-if="property.images?.length"
          :modules="[Pagination, Navigation, Autoplay]"
          :pagination="{ clickable: true }"
          :navigation="true"
          :autoplay="{ delay: 3000, disableOnInteraction: false }"
          class="h-full w-full"
        >
          <SwiperSlide v-for="(img, idx) in property.images" :key="idx">
            <img :src="img"
                 :alt="`Foto ${idx + 1}`"
                 class="w-full h-full object-cover"
                 loading="lazy" />
          </SwiperSlide>
        </Swiper>
        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
          Sin imágenes
        </div>
      </client-only>
      <!-- 3D Tour badge -->
      <div v-if="property.tags && property.tags[1]" class="badge absolute top-3 left-3 z-10 bg-black bg-opacity-60 text-white border-none py-3">{{ property.tags[1] }}</div>
      <!-- Favorite button -->
      <button 
        @click.prevent="toggleFavorite" 
        :class="['btn btn-circle btn-ghost absolute top-2 right-2 z-20 heart-button', { 'animate-sonar': playSonar }]"
        @animationend="playSonar = false"
      >
        <svg v-if="!isFavorited" xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-white drop-shadow-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-red-500 drop-shadow-white" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </button>
    </figure>
    <div class="card-body p-4 bg-white rounded-b-lg">
      <h2 class="text-2xl font-bold tracking-tight text-gray-900">
        {{ formatCurrency(property.price) }}
      </h2>
      <div class="flex flex-wrap items-center text-sm text-gray-600 mt-1">
        <span v-if="property.total_surface">{{ property.total_surface }} m² tot.</span>
        
        <template v-if="property.ambience">
            <span class="mx-2 text-gray-300">|</span>
            <span>{{ property.ambience }} amb.</span>
        </template>
        
        <template v-if="property.bedrooms">
            <span class="mx-2 text-gray-300">|</span>
            <span class="flex items-center gap-1" title="Dormitorios">
                {{ property.bedrooms }}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M3 7v11m0 -4h18m0 4v-8a2 2 0 0 0 -2 -2h-8v6" /><path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /></svg>
            </span>
        </template>

        <template v-if="property.bathrooms">
            <span class="mx-2 text-gray-300">|</span>
            <span class="flex items-center gap-1" title="Baños">
                {{ property.bathrooms }}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1 -4 4h-10a4 4 0 0 1 -4 -4v-3a1 1 0 0 1 1 -1z" /><path d="M6 12v-7a2 2 0 0 1 2 -2h3v2.25" /><path d="M4 21l1 -1.5" /><path d="M20 21l-1 -1.5" /></svg>
            </span>
        </template>

        <template v-if="property.garage">
            <span class="mx-2 text-gray-300">|</span>
            <span class="flex items-center gap-1" title="Cocheras">
                {{ property.garage }}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /><path d="M5 17h-2v-6l2 -5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6 -6h15m-6 0v-5" /></svg>
            </span>
        </template>
      </div>
      <p class="text-base text-gray-700 truncate mt-2">{{ property.address }}</p>
      <p class="text-xs text-gray-500 uppercase mt-4">{{ property.realty }}</p>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { Swiper, SwiperSlide } from 'swiper/vue'
  import { Pagination, Navigation, Autoplay } from 'swiper/modules'
  import 'swiper/css'
  import 'swiper/css/navigation'
  import 'swiper/css/pagination'
  
  const props = defineProps({
    property: {
      type: Object,
      default: () => ({
        images: [
          'https://ap.rdcpix.com/f121e1389552599950529b45355a164bl-m2420839945od-w480_h360.jpg',
          'https://ap.rdcpix.com/f121e1389552599950529b45355a164bl-m121588978od-w480_h360.jpg'
        ],
        price: 6100000,
        address: '(undisclosed Address), Davenport, FL 33896',
        total_surface: 800,
        ambience: 4,
        bedrooms: 3,
        bathrooms: 3,
        garage: 1,
        realty: 'LA ROSA REALTY CW PROPERTIES L',
        hasVirtualTour: true,
        tags: ['New construction', 'Basketball court']
      })
    }
  })
  
  const property = props.property
  const formatCurrency = (value) => {
    if (typeof value !== 'number') {
      return value
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const isFavorited = ref(false)
  const playSonar = ref(false)
  
  function toggleFavorite() {
    isFavorited.value = !isFavorited.value
    if (isFavorited.value) {
      playSonar.value = true
    }
  }
  </script>

<style scoped>
.drop-shadow-white {
  filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.4)) drop-shadow(0px 0px 2px rgba(255, 255, 255, 1));
}

.heart-button {
  transition: transform 0.2s ease-in-out;
}

.heart-button:hover {
  animation: pulse-heart 1.2s infinite;
}

@keyframes pulse-heart {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.animate-sonar::after {
  content: '';
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.7);
  animation: sonar-effect 0.6s ease-out 2;
  z-index: -1;
}

@keyframes sonar-effect {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}
</style>
  
  <style scoped>
  .card {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 344px;
    margin: auto;
  }
  .card-body {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 104px;
  }
  figure {
    margin: 0;
    width: 100%;
    height: 177px;
    position: relative;
    overflow: hidden;
    background-color: #f3f4f6;
  }
  /* Swiper overrides */
  :deep(.swiper) { width: 100%; height: 100%; }
  :deep(.swiper-slide img) { object-fit: cover; }
  :deep(.swiper-button-prev), :deep(.swiper-button-next) {
    opacity: 0;
    transition: opacity 0.3s;
    color: #fff;
    z-index: 10;
  }
  .group:hover :deep(.swiper-button-prev),
  .group:hover :deep(.swiper-button-next) {
    opacity: 1;
  }
  :deep(.swiper-pagination-bullet) { background: rgba(255,255,255,0.8); }
  :deep(.swiper-pagination-bullet-active) { background: #fff; }
  </style>