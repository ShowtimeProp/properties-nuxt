<template>
  <div class="bg-white rounded-lg shadow hover:shadow-lg border flex flex-col overflow-hidden cursor-pointer">
    <figure class="relative w-full h-48">
      <ClientOnly>
        <Swiper
          :modules="modules"
          :navigation="{
            nextEl: `.list-item-next-${swiperId}`,
            prevEl: `.list-item-prev-${swiperId}`,
          }"
          :pagination="{ clickable: true }"
          :loop="false"
          :slides-per-view="1"
          class="w-full h-full"
        >
          <SwiperSlide v-for="(image, index) in property.images" :key="index">
            <img :src="image" alt="Property Image" class="object-cover w-full h-full" />
          </SwiperSlide>
          <div :class="`list-item-next-${swiperId} swiper-button-next`"></div>
          <div :class="`list-item-prev-${swiperId} swiper-button-prev`"></div>
        </Swiper>
      </ClientOnly>
      <!-- Badge 3D Tour -->
      <div v-if="property.hasVirtualTour" class="absolute top-2 left-2 bg-white/90 rounded px-2 py-1 flex items-center gap-1 text-xs font-medium z-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
          <path d="M11 17a1 1 0 001.447.894l4-2A1 1 0 0017 15V5a1 1 0 00-1.447-.894l-4 2a1 1 0 00-.553.894v10zM15.211 6.276a1 1 0 000-1.788l-4.764-2.382a1 1 0 00-.894 0L4.789 4.488a1 1 0 000 1.788l4.764 2.382a1 1 0 00.894 0l4.764-2.382zM4.447 8.342A1 1 0 003 9.236V15a1 1 0 00.553.894l4 2A1 1 0 009 17V11.236a1 1 0 00-.553-.894l-4-2z" />
        </svg>
        <span>3D TOUR</span>
      </div>
      <!-- Corazón de favorito -->
      <button
        @click.stop="toggleFavorite(property)"
        class="absolute top-2 right-2 text-white bg-white/70 rounded-full p-1 hover:bg-white/90 transition-colors z-10"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :class="{ 'text-red-500 fill-current': isFavorite(property) }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
      <div class="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded-md">
        {{ property.images.length }} fotos
      </div>
    </figure>
    <div class="p-3 flex flex-col gap-1">
      <div class="text-base font-bold text-gray-900">U$D {{ property.price }}</div>
      <div class="text-xs text-gray-600">
        {{ property.bedrooms || property.rooms }} Dormitorios | {{ property.bathrooms || 1 }} Baño{{ (property.bathrooms !== 1 && property.bathrooms) ? 's' : '' }}
        <template v-if="property.garage_count > 0">
          <span class="mx-1">|</span>
          <span class="flex items-center gap-1 text-sm text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /><path d="M5 17h-2v-6l2 -5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6 -6h15m-6 0v-5" /></svg>
            <span>{{ property.garage_count }} coch.</span>
          </span>
        </template>
        | {{ property.size }} m² - {{ property.status || 'Venta' }}
      </div>
      <div class="text-xs text-gray-700 truncate">{{ property.address || 'Dirección no disponible' }}</div>
      <div class="text-[10px] text-gray-400 mt-1">{{ property.agency || 'Inmobiliaria Ejemplo' }}</div>
    </div>
  </div>
</template>

<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Navigation, Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

const swiperId = `swiper-list-item-${Math.random().toString(36).substring(7)}`;

const props = defineProps({
  property: {
    type: Object,
    required: true,
  },
  isFavorite: {
    type: Function,
    required: true,
  },
  toggleFavorite: {
    type: Function,
    required: true,
  },
});

const modules = [Navigation, Pagination];
</script>

<style scoped>
:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: white;
  --swiper-navigation-size: 32px;
}

:deep(.swiper-pagination-bullet) {
  background-color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
}

:deep(.swiper-pagination-bullet-active) {
  background-color: #ffffff !important;
}
</style>