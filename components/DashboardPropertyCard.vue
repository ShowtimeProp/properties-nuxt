<template>
  <div 
    class="property-card group rounded-lg shadow border border-gray-200 overflow-hidden flex flex-col cursor-pointer hover:shadow-lg transition-shadow duration-200"
    style="height: 320px; width: 100%; font-family: 'Roboto', Arial, sans-serif;"
    @click="openPropertyDetails"
  >
    <!-- Imagen principal -->
    <div class="relative w-full" style="aspect-ratio: 3/2; min-height: 0;">
      <img
        v-if="property.images && property.images.length > 0"
        :src="getProxyImageUrl(property.property_id, 0)"
        :alt="`Foto de la propiedad`"
        class="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105"
        @error="handleImageError"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-400 bg-gradient-to-br from-gray-50 to-gray-100">
        <div class="text-center">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-sm">Sin imágenes</p>
        </div>
      </div>
      
      <!-- Badge de favorito -->
      <div class="absolute top-3 right-3 z-10">
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          ♥ Favorito
        </span>
      </div>
      
      <!-- Badge de tipo de operación -->
      <div v-if="property.tipo_operacion" class="absolute top-3 left-3 z-10">
        <span 
          :class="[
            'px-2 py-1 rounded-md text-xs font-bold text-white',
            { 
              'bg-green-500': property.tipo_operacion.toLowerCase().includes('venta'),
              'bg-orange-500': property.tipo_operacion.toLowerCase().includes('alquiler')
            }
          ]"
        >
          {{ property.tipo_operacion }}
        </span>
      </div>
    </div>
    
    <!-- Contenido -->
    <div class="flex-1 flex flex-col justify-between px-4 py-3 gap-2 bg-white">
      <!-- Precio y expensas -->
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="text-lg font-bold text-gray-900">{{ formatCurrency(property.price) }}</span>
          <span v-if="property.expenses && property.expenses > 0" class="text-xs text-gray-500">
            + {{ formatCurrency(property.expenses) }} exp.
          </span>
        </div>
      </div>
      
      <!-- Dirección y zona -->
      <div class="flex items-center gap-2 text-xs text-gray-700 mb-1">
        <span class="truncate">{{ property.address || 'Dirección no disponible' }}</span>
        <span v-if="property.zone || property.localidad" class="mx-1 text-gray-300">|</span>
        <span class="truncate">{{ property.zone || property.localidad }}</span>
      </div>
      
      <!-- Características principales -->
      <div class="flex items-center flex-wrap text-sm text-gray-700 mb-2">
        <!-- Dormitorios -->
        <div v-if="property.bedrooms" class="flex items-center pr-2">
          <svg class="h-4 w-4 text-gray-500 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M3 7v11m0-4h18m0 4v-8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8z"/>
            <path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>
          </svg>
          <span class="font-bold">{{ property.bedrooms }}</span>
        </div>
        
        <!-- Baños -->
        <div v-if="property.bathrooms" class="flex items-center border-l border-gray-300 px-2">
          <svg class="h-4 w-4 text-gray-500 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4h-10a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/>
            <path d="M6 12v-7a2 2 0 0 1 2-2h3v2.25"/>
            <path d="M4 21l1-1.5"/>
            <path d="M20 21l-1-1.5"/>
          </svg>
          <span class="font-bold">{{ property.bathrooms }}</span>
        </div>
        
        <!-- Cocheras -->
        <div v-if="property.garage_count > 0" class="flex items-center border-l border-gray-300 px-2">
          <svg class="h-4 w-4 text-gray-500 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <circle cx="7" cy="17" r="2"/>
            <circle cx="17" cy="17" r="2"/>
            <path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6-6h15m-6 0v-5"/>
          </svg>
          <span class="font-bold">{{ property.garage_count }}</span>
        </div>
        
        <!-- Superficie y Precio/m2 -->
        <div v-if="property.area_m2 || property.total_surface" class="flex items-center border-l border-gray-300 px-2">
          <span class="font-bold">{{ property.area_m2 || property.total_surface }}</span>
          <span class="text-gray-500 ml-1">m² Tot.</span>
          <template v-if="property.price_per_m2">
            <span class="text-gray-400 mx-1">-</span>
            <span class="text-gray-500">$</span>
            <span class="font-bold">{{ new Intl.NumberFormat('es-AR').format(property.price_per_m2) }}</span>
            <span class="text-gray-500 ml-1">/m²</span>
          </template>
        </div>
      </div>
      
      <!-- Información del cliente y fecha -->
      <div class="flex justify-between items-center text-xs text-gray-500 pt-2 border-t border-gray-100">
        <span>Cliente: {{ clientEmail || 'N/A' }}</span>
        <span>{{ formatDate(property.created_at) }}</span>
      </div>
      
      <!-- ID clickeable -->
      <div class="text-xs text-blue-600 hover:text-blue-800 cursor-pointer" @click.stop="openPropertyDetails">
        Ver detalles (ID: {{ property.property_id.slice(0, 8) }}...)
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  property: {
    type: Object,
    required: true
  },
  clientEmail: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['open-property'])

// Función para generar URLs del proxy de imágenes
function getProxyImageUrl(propertyId, imageIndex) {
  return `https://fapi.showtimeprop.com/properties/images/${propertyId}/${imageIndex}`
}

// Función para manejar errores de imagen
function handleImageError(event) {
  console.warn(`Error cargando imagen para propiedad ${props.property.property_id}`)
  event.target.src = '/placeholder-property.jpg' // Imagen de fallback
}

// Función para formatear moneda
function formatCurrency(price) {
  if (!price) return 'Precio no disponible'
  
  let num
  if (typeof price === 'string') {
    num = parseInt(price.replace(/\./g, '').replace(',', '.'), 10)
  } else if (typeof price === 'number') {
    num = price
  } else {
    return 'Precio no disponible'
  }
  
  if (isNaN(num)) return 'Precio no disponible'
  
  const formattedPrice = new Intl.NumberFormat('es-AR', { 
    style: 'decimal', 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  }).format(num)
  
  return `U$D ${formattedPrice}`
}

// Función para formatear fecha
function formatDate(dateString) {
  if (!dateString) return 'Fecha no disponible'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-AR')
  } catch (error) {
    return 'Fecha no disponible'
  }
}

// Función para abrir detalles de la propiedad
function openPropertyDetails() {
  // Abrir en nueva pestaña para mantener el contexto del dashboard
  window.open(`/property/${props.property.property_id}`, '_blank')
  
  // También emitir evento para el componente padre si es necesario
  emit('open-property', props.property)
}
</script>

<style scoped>
.property-card {
  transition: all 0.2s ease-in-out;
}

.property-card:hover {
  transform: translateY(-2px);
}
</style>
