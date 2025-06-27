<template>
  <div class="fixed inset-0 bg-black bg-opacity-75 z-40 flex justify-center items-center" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col relative overflow-hidden">
      <!-- Botón de cerrar -->
      <button @click="emit('close')" class="absolute top-3 right-3 bg-gray-200 text-gray-800 rounded-full h-8 w-8 flex items-center justify-center z-50 hover:bg-gray-300 transition-colors">
        &times;
      </button>

      <div class="flex-grow overflow-y-auto">
        <!-- Contenedor del Tour Virtual -->
        <div v-if="property.hasVirtualTour" class="aspect-video w-full bg-gray-200">
          <iframe :src="property.virtualTourUrl" width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
        </div>

        <!-- Contenido del Modal -->
        <div class="p-6">
          <h2 class="text-2xl font-bold mb-4">{{ property.title }}</h2>
          
          <!-- Placeholder para el slider de fotos -->
          <div class="h-64 bg-gray-300 rounded-md mb-4 flex items-center justify-center">
            <p class="text-gray-500">Slider de Fotos Próximamente</p>
          </div>

          <!-- Descripción -->
          <div class="mb-6">
            <h3 class="text-xl font-semibold border-b pb-2 mb-3">Descripción</h3>
            <p class="text-gray-700 leading-relaxed">{{ property.description }}</p>
          </div>

          <!-- Detalles -->
          <div>
            <h3 class="text-xl font-semibold border-b pb-2 mb-3">Detalles de la Propiedad</h3>
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
const props = defineProps({
  property: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);
</script>
