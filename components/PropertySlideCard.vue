<template>
  <!-- Stub to prevent parsing errors: use PropertySlideCardClean instead -->
  <div />
</template>

<script setup>
// Component moved to PropertySlideCardClean.vue
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
      images: ['https://via.placeholder.com/344x177?text=1', 'https://via.placeholder.com/344x177?text=2'],
      price: 123456,
      address: 'Calle Falsa 123',
      hasVirtualTour: true,
      tags: ['Nuevo', 'Oportunidad'],
    })
  }
})

const isFavorited = ref(false)
function toggleFavorite() {
  isFavorited.value = !isFavorited.value
}
</script>

<style scoped>
/* stub: no styles */
</style>