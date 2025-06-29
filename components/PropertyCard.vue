<template>
  <div class="w-[400px] bg-white rounded-lg shadow-xl z-20 flex flex-col font-sans transition-shadow duration-300 hover:shadow-2xl overflow-hidden" style="max-height: 500px">
    <!-- Botón de cerrar eliminado por redundancia -->

    <!-- Imagen principal con Slider -->
    <div class="relative h-[200px] w-full rounded-t-lg overflow-hidden bg-gray-300 group">
      <ClientOnly>
        <Swiper
          ref="swiperRef"
          :modules="modules"
          :navigation="{
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
            disabledClass: 'swiper-button-disabled',
          }"
          :loop="false"
          :slides-per-view="1"
          :space-between="0"
          @slide-change="updateNavigation"
          class="h-full w-full"
        >
          <swiper-slide v-for="(image, index) in property.images" :key="index" @click="onImageClick">
            <img :src="image" :alt="`${property.title} - Foto ${index + 1}`" class="object-cover w-full h-full" />
          </swiper-slide>
        </Swiper>
      </ClientOnly>
      
      <!-- Controles de Navegación Personalizados -->
      <div 
        v-show="showPrevButton"
        class="swiper-button-prev absolute left-2 top-1/2 -translate-y-1/2 z-10 cursor-pointer bg-black/40 hover:bg-black/60 rounded-full w-8 h-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300" 
        @click.stop="slidePrev"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" /></svg>
      </div>
      <div 
        v-show="showNextButton"
        class="swiper-button-next absolute right-2 top-1/2 -translate-y-1/2 z-10 cursor-pointer bg-black/40 hover:bg-black/60 rounded-full w-8 h-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300" 
        @click.stop="slideNext"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>
      </div>

      <!-- Overlay cantidad de fotos -->
      <div class="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white text-sm px-2 py-1 rounded-md flex items-center gap-1.5 z-20">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        <span>48</span>
      </div>
                              <!-- Badge 3D Tour -->
      <div v-if="property.hasVirtualTour" class="absolute top-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2.5 py-1.5 rounded-full flex items-center gap-1.5 z-20 font-bold">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
        </svg>
        <span>3D Tour</span>
      </div>

      <!-- Botón favorito -->
      <button 
        @click="toggleFavorite"
        class="favorite-button absolute top-2 right-2 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 active:scale-95 transition-transform duration-200 ease-in-out z-20"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 transition-colors duration-300" :class="isFavorite ? 'text-red-500' : 'text-gray-800'" fill="currentColor" viewBox="0 0 24 24">
           <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      </button>
    </div>

    <!-- Info principal -->
    <div class="flex flex-col p-4">
      <div>
        <div class="text-2xl font-bold text-gray-900">USD {{ property.price }}</div>
        <div class="text-gray-500 mt-1">$ {{ property.expenses }} Expensas</div>
        <div class="text-lg text-gray-800 font-semibold mt-3">{{ property.address }}</div>
        <div class="flex gap-3 text-sm text-gray-600 mt-2 border-b pb-4">
          <span>{{ property.size }} m² tot.</span>
          <span>{{ property.rooms }} amb.</span>
          <span>{{ property.bathrooms }} baños</span>
          <span>{{ property.bedrooms }} dorm.</span>
        </div>
      </div>
      <div class="flex gap-2 mt-4">
        <button class="p-2.5 border border-gray-400 rounded-lg text-gray-600 hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498A1 1 0 0119 15.72V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
        </button>
        <button class="flex-1 flex items-center justify-center gap-2 bg-[#25D366] hover:bg-[#1EBE57] text-white py-2.5 rounded-lg font-bold">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M16.988 15.139c-.272-.136-1.611-.795-1.859-.885-.249-.09-.429-.136-.609.136-.181.272-.699.885-.857 1.067-.158.181-.314.204-.586.068-.272-.136-1.149-.424-2.188-1.352-.81-.723-1.357-1.616-1.517-1.888-.158-.272-.017-.419.12-.555.124-.123.272-.318.408-.477.136-.158.181-.272.272-.454.09-.181.045-.34-.022-.477-.068-.136-.609-1.47-.834-2.013-.22-.53-.445-.458-.609-.466l-.518-.009c-.181 0-.477.068-.727.34-.25.272-.954.933-.954 2.274 0 1.342.977 2.638 1.113 2.817.136.181 1.922 2.936 4.66 3.998.652.224 1.16.357 1.557.457.654.167 1.249.144 1.72.087.525-.062 1.611-.659 1.839-1.295.227-.636.227-1.182.159-1.295-.068-.113-.25-.181-.522-.317z"/></svg>
          WhatsApp
        </button>
        <button class="flex-1 flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white py-2.5 rounded-lg font-bold">
          Contactar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import { ref, onMounted } from 'vue';

// Este componente recibe la información de la propiedad como un 'prop' y emite un evento 'close' cuando se hace clic en el botón de cerrar.
const props = defineProps({
  property: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'open-modal']);
const modules = [Navigation];
const swiperRef = ref(null);
const swiperInstance = ref(null);
const showPrevButton = ref(false);
const showNextButton = ref(true);

const onImageClick = () => {
  emit('open-modal');
};

const updateNavigation = (swiper) => {
  if (!swiper) return;
  
  // Actualizar visibilidad de las flechas
  showPrevButton.value = swiper.activeIndex > 0;
  showNextButton.value = swiper.activeIndex < swiper.slides.length - 1;
};

const slideNext = () => {
  if (swiperInstance.value) {
    swiperInstance.value.slideNext();
    updateNavigation(swiperInstance.value);
  }
};

const slidePrev = () => {
  if (swiperInstance.value) {
    swiperInstance.value.slidePrev();
    updateNavigation(swiperInstance.value);
  }
};

// Inicializar la instancia de Swiper cuando el componente se monta
onMounted(() => {
  if (swiperRef.value) {
    swiperInstance.value = swiperRef.value.swiper;
    updateNavigation(swiperInstance.value);
    
    // Actualizar navegación cuando cambian las diapositivas
    swiperInstance.value.on('slideChange', () => {
      updateNavigation(swiperInstance.value);
    });
  }
});

const isFavorite = ref(false);

const toggleFavorite = (event) => {
  event.stopPropagation();
  isFavorite.value = !isFavorite.value;
  // Aquí se podría emitir un evento o llamar a una API para guardar el estado
};
</script>

<style>
/* Oculta las flechas por defecto de Swiper */
.swiper-button-prev::after,
.swiper-button-next::after {
  content: '' !important;
}

.property-card-enter-active,
.property-card-leave-active {
  transition: all 0.3s ease;
}

.property-card-enter-from,
.property-card-leave-to {
  opacity: 0;
}

.property-card-enter-to,
.property-card-leave-from {
  opacity: 1;
}

@keyframes heartbeat {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.favorite-button:hover svg {
  animation: heartbeat 0.8s ease-in-out infinite;
}
</style>
