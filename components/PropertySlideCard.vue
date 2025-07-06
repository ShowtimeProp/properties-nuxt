<template>
  <div class="property-slide-card w-full max-w-sm rounded-lg overflow-hidden shadow-lg bg-white relative group">
    <img :src="property.images[0] || 'https://via.placeholder.com/400x300'" alt="Property Image" class="w-full h-48 object-cover">
    
    <div @click="toggleFavorite" class="absolute top-3 right-3 cursor-pointer p-1.5 bg-black bg-opacity-40 rounded-full transition-transform duration-200 ease-in-out group-hover:scale-110">
      <Icon 
        :name="isFavorited ? 'mdi:heart' : 'mdi:heart-outline'" 
        :class="isFavorited ? 'text-red-500' : 'text-white'" 
        size="24" 
      />
    </div>

    <div class="p-4">
      <div class="font-bold text-xl mb-2">{{ property.title }}</div>
      <p class="text-gray-700 text-base">
        {{ property.address }}
      </p>
      <div class="mt-4 flex justify-between items-center">
        <span class="text-xl font-semibold text-gray-900">{{ formatPrice(property.price) }}</span>
        <div class="flex space-x-3 text-sm text-gray-600">
            <span><Icon name="mdi:bed-king-outline" class="mr-1" />{{ property.bedrooms }}</span>
            <span><Icon name="mdi:bath-outline" class="mr-1" />{{ property.bathrooms }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useFavoritesStore } from '~/stores/favorites';
import { useToast } from 'vue-toastification';

const props = defineProps({
  property: {
    type: Object,
    required: true,
  },
});

const user = useSupabaseUser();
const favoritesStore = useFavoritesStore();
const toast = useToast();

const isFavorited = computed(() => {
  return favoritesStore.isFavorite(props.property.id);
});

const formatPrice = (price) => {
  if (price == null) return 'N/A';
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(price);
};

const toggleFavorite = async () => {
  if (!user.value) {
    toast.error('Debes iniciar sesión para agregar a favoritos.');
    return;
  }
  await favoritesStore.toggleFavorite(props.property);
  if (isFavorited.value) {
    toast.success('Agregado a favoritos!');
  } else {
    toast.info('Eliminado de favoritos.');
  }
};
</script>

<style scoped>
.property-slide-card {
  transition: box-shadow 0.3s ease-in-out;
}
.property-slide-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
