<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div 
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="closeModal"
    ></div>
    
    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b">
          <h2 class="text-xl font-semibold text-gray-900">
            Detalles de la Propiedad
          </h2>
          <button 
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Content -->
        <div class="overflow-y-auto max-h-[calc(90vh-120px)]">
          <!-- Loading State -->
          <div v-if="loading" class="p-8">
            <div class="animate-pulse">
              <div class="bg-gray-200 h-64 rounded-lg mb-6"></div>
              <div class="space-y-4">
                <div class="bg-gray-200 h-8 rounded w-3/4"></div>
                <div class="bg-gray-200 h-4 rounded w-1/2"></div>
                <div class="bg-gray-200 h-4 rounded w-2/3"></div>
              </div>
            </div>
          </div>
          
          <!-- Error State -->
          <div v-else-if="error" class="p-8">
            <div class="bg-red-50 border border-red-200 rounded-lg p-6">
              <div class="flex items-center">
                <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 class="text-lg font-medium text-red-800">Error al cargar la propiedad</h3>
                  <p class="text-red-600 mt-1">{{ error }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Property Details -->
          <div v-else-if="property" class="p-6">
            <!-- Title and Operation Type -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-4">
                <div class="flex-1">
                  <h1 class="text-2xl font-bold text-gray-900 mb-2">
                    {{ property.title || 'Propiedad' }}
                  </h1>
                  <div class="flex items-center space-x-4 mb-4">
                    <span class="text-2xl font-bold text-blue-600">
                      {{ formatCurrency(property.price) }}
                    </span>
                    <span v-if="property.expenses && property.expenses > 0" class="text-lg text-gray-600">
                      + {{ formatCurrency(property.expenses) }} exp.
                    </span>
                  </div>
                  <div class="flex items-center text-gray-600">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>{{ property.address || 'Dirección no disponible' }}</span>
                  </div>
                </div>
                
                <!-- Operation Type and Status -->
                <div v-if="property.tipo_operacion" class="ml-6 flex items-center space-x-3">
                  <span 
                    :class="[
                      'inline-block px-4 py-2 rounded-lg text-lg font-bold text-white shadow-lg',
                      { 
                        'bg-green-500': property.tipo_operacion.toLowerCase().includes('venta'),
                        'bg-orange-500': property.tipo_operacion.toLowerCase().includes('alquiler'),
                        'bg-blue-500': !property.tipo_operacion.toLowerCase().includes('venta') && !property.tipo_operacion.toLowerCase().includes('alquiler')
                      }
                    ]"
                  >
                    {{ property.tipo_operacion }}
                  </span>
                  <span 
                    v-if="property.estado"
                    :class="[
                      'inline-block px-4 py-2 rounded-lg text-lg font-bold text-white shadow-lg',
                      { 
                        'bg-green-600': property.estado.toLowerCase().includes('disponible'),
                        'bg-yellow-500': property.estado.toLowerCase().includes('oportunidad'),
                        'bg-red-500': property.estado.toLowerCase().includes('reservado'),
                        'bg-gray-500': !property.estado.toLowerCase().includes('disponible') && !property.estado.toLowerCase().includes('oportunidad') && !property.estado.toLowerCase().includes('reservado')
                      }
                    ]"
                  >
                    {{ property.estado }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Image Gallery -->
            <div class="mb-6">
              <div v-if="property.images && property.images.length > 0" class="relative">
                <!-- Main Image Swiper -->
                <div class="swiper-container rounded-lg overflow-hidden mb-4">
                  <div class="swiper-wrapper">
                    <div
                      v-for="(image, index) in property.images"
                      :key="index"
                      class="swiper-slide"
                    >
                      <img
                        :src="getImageUrl(index)"
                        :alt="property.title || 'Propiedad'"
                        class="w-full h-80 object-cover"
                      />
                    </div>
                  </div>
                  
                  <!-- Navigation arrows -->
                  <div class="swiper-button-next"></div>
                  <div class="swiper-button-prev"></div>
                </div>
                
                <!-- Thumbnail Swiper -->
                <div v-if="property.images.length > 1" class="swiper-container-thumbs">
                  <div class="swiper-wrapper">
                    <div
                      v-for="(image, index) in property.images"
                      :key="index"
                      class="swiper-slide cursor-pointer"
                    >
                      <img
                        :src="getImageUrl(index)"
                        :alt="`Imagen ${index + 1}`"
                        class="w-full h-12 object-cover rounded-lg"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- No Images Placeholder -->
              <div v-else class="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden bg-gray-200 flex items-center justify-center h-64">
                <div class="text-center text-gray-400">
                  <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm">Sin imágenes disponibles</p>
                </div>
              </div>
            </div>

            <!-- Property Information -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- Main Content -->
              <div class="lg:col-span-2">
                <!-- Property Features -->
                <div class="bg-gray-50 rounded-lg p-6 mb-6">
                  <h2 class="text-lg font-semibold text-gray-900 mb-4">Características</h2>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div v-if="property.bedrooms" class="flex items-center">
                      <svg class="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v11m0-4h18m0 4v-8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8z"/><path d="M7 10m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>
                      </svg>
                      <span class="font-medium">{{ property.bedrooms }} dormitorios</span>
                    </div>
                    <div v-if="property.bathrooms" class="flex items-center">
                      <svg class="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4h-10a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/><path d="M6 12v-7a2 2 0 0 1 2-2h3v2.25"/><path d="M4 21l1-1.5"/><path d="M20 21l-1-1.5"/>
                      </svg>
                      <span class="font-medium">{{ property.bathrooms }} baños</span>
                    </div>
                    <div v-if="property.garage_count > 0" class="flex items-center">
                      <svg class="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6-6h15m-6 0v-5"/>
                      </svg>
                      <span class="font-medium">{{ property.garage_count }} cocheras</span>
                    </div>
                    <div v-if="property.area_m2 || property.total_surface" class="flex items-center">
                      <svg class="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
                      </svg>
                      <span class="font-medium">{{ property.area_m2 || property.total_surface }} m²</span>
                    </div>
                  </div>
                </div>

                <!-- Description -->
                <div v-if="property.description" class="bg-gray-50 rounded-lg p-6 mb-6">
                  <h2 class="text-lg font-semibold text-gray-900 mb-4">Descripción</h2>
                  <p class="text-gray-700 leading-relaxed">{{ property.description }}</p>
                </div>

                <!-- Additional Details -->
                <div class="bg-gray-50 rounded-lg p-6">
                  <h2 class="text-lg font-semibold text-gray-900 mb-4">Detalles Adicionales</h2>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-if="property.property_type" class="flex justify-between">
                      <span class="text-gray-600">Tipo:</span>
                      <span class="font-medium capitalize">{{ property.property_type }}</span>
                    </div>
                    <div v-if="property.tipo_operacion" class="flex justify-between">
                      <span class="text-gray-600">Operación:</span>
                      <span class="font-medium capitalize">{{ property.tipo_operacion }}</span>
                    </div>
                    <div v-if="property.zone" class="flex justify-between">
                      <span class="text-gray-600">Zona:</span>
                      <span class="font-medium">{{ property.zone }}</span>
                    </div>
                    <div v-if="property.localidad" class="flex justify-between">
                      <span class="text-gray-600">Localidad:</span>
                      <span class="font-medium">{{ property.localidad }}</span>
                    </div>
                    <div v-if="property.realty" class="flex justify-between">
                      <span class="text-gray-600">Inmobiliaria:</span>
                      <span class="font-medium">{{ property.realty }}</span>
                    </div>
                    <div v-if="property.price_per_m2" class="flex justify-between">
                      <span class="text-gray-600">Precio por m²:</span>
                      <span class="font-medium">${{ new Intl.NumberFormat('es-AR').format(property.price_per_m2) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Sidebar -->
              <div class="lg:col-span-1">
                <!-- Contact Card -->
                <div class="bg-white border rounded-lg p-6 mb-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">¿Te interesa esta propiedad?</h3>
                  <div class="space-y-3">
                    <button class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                      Contactar Realtor
                    </button>
                    <button class="w-full border border-blue-600 text-blue-600 py-3 px-4 rounded-lg hover:bg-blue-50 transition-colors">
                      Agendar Visita
                    </button>
                  </div>
                </div>

                <!-- Property Summary -->
                <div class="bg-white border rounded-lg p-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Resumen</h3>
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <span class="text-gray-600">Precio:</span>
                      <span class="font-bold text-lg">{{ formatCurrency(property.price) }}</span>
                    </div>
                    <div v-if="property.expenses" class="flex justify-between">
                      <span class="text-gray-600">Expensas:</span>
                      <span class="font-medium">{{ formatCurrency(property.expenses) }}</span>
                    </div>
                    <div v-if="property.area_m2 || property.total_surface" class="flex justify-between">
                      <span class="text-gray-600">Superficie:</span>
                      <span class="font-medium">{{ property.area_m2 || property.total_surface }} m²</span>
                    </div>
                    <div v-if="property.price_per_m2" class="flex justify-between">
                      <span class="text-gray-600">Precio/m²:</span>
                      <span class="font-medium">${{ new Intl.NumberFormat('es-AR').format(property.price_per_m2) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  propertyId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

// Reactive data
const property = ref(null)
const loading = ref(false)
const error = ref(null)

// Fetch property details
const fetchProperty = async () => {
  if (!props.propertyId) return
  
  try {
    loading.value = true
    error.value = null
    
    const backendUrl = 'http://212.85.20.219:8000'
    const response = await fetch(`${backendUrl}/properties/${props.propertyId}`)
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    property.value = data.property
    
    // Initialize Swiper after data is loaded
    if (property.value?.images?.length > 0) {
      setTimeout(initializeSwiper, 500)
    }
    
  } catch (err) {
    console.error('Error fetching property:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Get image URL
const getImageUrl = (index) => {
  if (!property.value?.images || !property.value.images[index]) return ''
  const config = useRuntimeConfig()
  const backendUrl = config.public.apiBaseUrl || 'http://212.85.20.219:8000'
  return `${backendUrl}/properties/images/${props.propertyId}/${index}`
}

// Format currency
const formatCurrency = (price) => {
  if (!price) return ''
  
  let num
  if (typeof price === 'string') {
    num = parseInt(price.replace(/\./g, '').replace(',', '.'), 10)
  } else if (typeof price === 'number') {
    num = price
  } else {
    return ''
  }
  
  if (isNaN(num)) return ''
  
  const formattedPrice = new Intl.NumberFormat('es-AR', { 
    style: 'decimal', 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  }).format(num)
  
  return `U$D ${formattedPrice}`
}

// Initialize Swiper
const initializeSwiper = () => {
  nextTick(() => {
    // Wait a bit more for DOM to be fully ready
    setTimeout(() => {
      // Check if elements exist
      const mainContainer = document.querySelector('.swiper-container')
      const thumbsContainer = document.querySelector('.swiper-container-thumbs')
      
      if (!mainContainer || !thumbsContainer) {
        console.error('Swiper containers not found')
        return
      }

      // Try to load Swiper from CDN as fallback
      if (typeof window !== 'undefined' && !window.Swiper) {
        // Load Swiper CSS first
        const link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css'
        document.head.appendChild(link)
        
        // Load Swiper from CDN
        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js'
        script.onload = () => {
          console.log('Swiper loaded from CDN')
          initializeSwiperInstances()
        }
        script.onerror = () => {
          console.error('Failed to load Swiper from CDN')
        }
        document.head.appendChild(script)
      } else {
        initializeSwiperInstances()
      }
    }, 500)
  })
}

// Initialize Swiper instances
const initializeSwiperInstances = () => {
  const mainContainer = document.querySelector('.swiper-container')
  const thumbsContainer = document.querySelector('.swiper-container-thumbs')
  
  try {
    // Initialize thumbnail swiper first
    const thumbsSwiper = new window.Swiper(thumbsContainer, {
      spaceBetween: 8,
      slidesPerView: 'auto',
      freeMode: true,
      watchSlidesProgress: true,
      breakpoints: {
        320: {
          slidesPerView: 4,
          spaceBetween: 6
        },
        640: {
          slidesPerView: 6,
          spaceBetween: 8
        },
        1024: {
          slidesPerView: 8,
          spaceBetween: 10
        }
      }
    })

    // Then initialize main swiper
    const mainSwiper = new window.Swiper(mainContainer, {
      spaceBetween: 10,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      thumbs: {
        swiper: thumbsSwiper
      }
    })

    console.log('Swiper initialized successfully', { mainSwiper, thumbsSwiper })
    
    // Test if swiper is working
    if (mainSwiper && mainSwiper.slides && mainSwiper.slides.length > 0) {
      console.log('Main swiper has', mainSwiper.slides.length, 'slides')
    }
    if (thumbsSwiper && thumbsSwiper.slides && thumbsSwiper.slides.length > 0) {
      console.log('Thumbs swiper has', thumbsSwiper.slides.length, 'slides')
    }
    
  } catch (error) {
    console.error('Error initializing Swiper instances:', error)
  }
}

// Close modal
const closeModal = () => {
  emit('close')
}

// Watch for property ID changes
watch(() => props.propertyId, (newId) => {
  if (newId && props.isOpen) {
    fetchProperty()
  }
}, { immediate: true })

// Watch for modal open/close
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.propertyId) {
    fetchProperty()
  } else if (!isOpen) {
    // Reset data when modal closes
    property.value = null
    error.value = null
  }
})
</script>

<style scoped>
/* Swiper Styles */
.swiper-container {
  position: relative;
}

.swiper-button-next,
.swiper-button-prev {
  color: white;
  background: rgba(0, 0, 0, 0.5);
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.swiper-button-next:after,
.swiper-button-prev:after {
  font-size: 16px;
}

.swiper-container-thumbs {
  margin-top: 12px;
}

.swiper-container-thumbs {
  overflow: hidden;
}

.swiper-container-thumbs .swiper-wrapper {
  display: flex;
  flex-wrap: nowrap;
}

.swiper-container-thumbs .swiper-slide {
  opacity: 0.6;
  transition: opacity 0.3s;
  width: auto;
  flex-shrink: 0;
}

.swiper-container-thumbs .swiper-slide-thumb-active {
  opacity: 1;
}
</style>
