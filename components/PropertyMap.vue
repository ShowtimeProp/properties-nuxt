<template>
  <div ref="mapWrapper" class="w-full h-full">
    <div ref="mapContainer" class="w-full h-full"></div>
    
    
    <!-- Botón Ver Listado -->
    <button 
      ref="toggleButton"
      @click.stop.prevent="togglePropertyList"
      @touchstart.stop.prevent="togglePropertyList"
      type="button"
      class="absolute top-20 right-4 md:top-24 md:right-24 z-20 flex items-center gap-2 px-3 py-2 md:px-4 animated-gradient-bg text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors text-sm md:text-base"
      style="pointer-events: auto;"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <span>Ver Listado</span>
    </button>
    
    <!-- Overlay invisible para capturar clicks fuera del panel lateral -->
    <div 
      v-if="showPropertyList"
      @click="showPropertyList = false"
      style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 25; background: transparent;"
    ></div>
    
    <!-- Panel de Listado de Propiedades -->
    <div 
      ref="propertyListPanel"
      class="fixed top-0 right-0 bg-white shadow-xl z-30 transform transition-transform duration-300 ease-in-out flex flex-col pt-[80px] md:pt-[110px] w-full md:w-[450px] lg:w-[40%] max-w-[750px]"
      style="height: 100vh; box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1)"
      :class="{ 'translate-x-0': showPropertyList, 'translate-x-full': !showPropertyList }"
      @click.stop
    >
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-lg font-semibold">{{ sortedProperties.length }} propiedades en esta zona</h3>
        <button @click="togglePropertyList" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <!-- Lista de Propiedades en Grid -->
      <div ref="scrollContainer" class="flex-1 overflow-y-auto p-4">
        <div v-if="sortedProperties.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4 place-items-center">
          <PropertyCard
            v-for="property in sortedProperties"
            :key="property.id"
            :property="property"
            @toggle-favorite="toggleFavorite(property)"
            @open-modal="openModalFromSlide(property)"
            @login-request="showLoginModal = true"
          />
        </div>
        <div v-else class="h-full flex items-center justify-center p-8 text-gray-500">
          <p>No hay propiedades en esta área</p>
        </div>
      </div>
    </div>

    <!-- Controles de Búsqueda -->
    <div class="absolute bottom-20 left-1/2 -translate-x-1/2 z-10 flex flex-row items-center gap-3">
      <!-- Botón de Búsqueda -->
      <div class="flex items-center gap-2">
        <button @click="searchInCurrentArea" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-lg transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>Buscar en esta zona</span>
        </button>
      </div>
    </div>
  </div>


  <Transition name="property-card">
    <div v-if="selectedProperty && (!isModalOpen || !openedFromSlide)"
      :style="{ position: 'absolute', left: `${cardPosition.x}px`, top: `${cardPosition.y}px`, zIndex: 30, width: '310px' }"
      @click.stop
    >
      <!-- Card con flecha -->
      <div style="position: relative;">
        <PropertyCard 
          :property="selectedProperty" 
          @toggle-favorite="toggleFavorite(selectedProperty)"
          @close="selectedProperty = null"
          @open-modal="isModalOpen = true"
          @login-request="showLoginModal = true"
        />
        <!-- Flecha tipo tooltip -->
        <div v-if="cardPlacement === 'top'" style="position: absolute; left: 50%; top: 100%; transform: translateX(-50%); width: 0; height: 0; z-index: 40;">
          <svg width="32" height="18" viewBox="0 0 32 18">
            <polygon points="16,18 0,0 32,0" fill="#fff" stroke="#e5e7eb" stroke-width="1" />
          </svg>
        </div>
        <div v-else style="position: absolute; left: 50%; bottom: 100%; transform: translateX(-50%) rotate(180deg); width: 0; height: 0; z-index: 40;">
          <svg width="32" height="18" viewBox="0 0 32 18">
            <polygon points="16,18 0,0 32,0" fill="#fff" stroke="#e5e7eb" stroke-width="1" />
          </svg>
        </div>
      </div>
    </div>
  </Transition>

  <!-- Modal de Detalles -->
  <Transition name="fade">
    <PropertyModal 
      v-if="isModalOpen && selectedProperty"
      ref="propertyModalRef"
      :property="selectedProperty"
      :isFavorite="favoritesStore.isFavorite(selectedProperty?.id)"
      @close="handleCloseModal"
      @toggle-favorite="toggleFavorite"
      @login-request="() => { console.log('PropertyMap recibió login-request'); loginModal.open(); console.log('loginModal.isOpen ahora es:', loginModal.isOpen); }"
    />
  </Transition>

  <!-- Modal de login -->
  <LoginModal />

</template>

<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick, computed } from 'vue';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';

import PropertyCard from './PropertyCard.vue';
import PropertyModal from './PropertyModal.vue';
import LoginModal from './LoginModal.vue';

import { useFavoritesStore } from '~/stores/favorites';
import { useLoginModalStore } from '~/stores/loginModal';
import { useSearchStore } from '~/stores/search';
import { useSupabaseUser } from '#imports';

// --- STORES Y ESTADO GENERAL ---
const searchStore = useSearchStore();
const config = useRuntimeConfig();
const user = useSupabaseUser();
const favoritesStore = useFavoritesStore();
const loginModal = useLoginModalStore();

const properties = ref([]);
const pending = ref(true);
const error = ref(null);
const filteredProperties = ref([]);
const isModalOpen = ref(false);
const openedFromSlide = ref(false);
const cardPosition = ref({ x: 0, y: 0 });
const cardPlacement = ref('top');

// dimensiones/posición para tooltip de dibujo (evitar warnings)
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 0);
const windowHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 0);
const mouse = ref({ x: 0, y: 0 });

// --- ESTADO DE UI PARA PANELES ---
const showPropertyList = ref(false);

// --- ESTADO DEL MAPA Y UI ---
const mapContainer = ref(null);
let map = null; // No reactivo para MapLibre
const markerElements = ref({});
const selectedProperty = ref(null);
const isSidePanelOpen = ref(false);
// const showLoginModal = ref(false); // Ya no se usa, se usa el store
let draw = null;

// --- COMPUTED PROPS ---
const sortedProperties = computed(() => {
  // Aquí puedes añadir la lógica de ordenamiento que tenías antes si la necesitas.
  return filteredProperties.value;
});

const apiBaseUrl = computed(() => {
  if (typeof window === 'undefined') return config.public.apiBaseUrl;
  const hostname = window.location.hostname;
  console.log('🔍 Debug apiBaseUrl:', { hostname, configValue: config.public.apiBaseUrl });
  
  if (hostname.endsWith('.vercel.app') || hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('✅ Usando config.public.apiBaseUrl:', config.public.apiBaseUrl);
    return config.public.apiBaseUrl;
  }
  const parts = hostname.split('.');
  if (parts.length > 2) {
    const customUrl = `https://fapi.${parts.slice(-2).join('.')}`;
    console.log('🌐 Usando URL personalizada:', customUrl);
    return customUrl;
  }
  const customUrl = `https://fapi.${hostname}`;
  console.log('🌐 Usando URL personalizada:', customUrl);
  return customUrl;
});

const propertiesApiUrl = computed(() => {
  if (!apiBaseUrl.value) {
    console.log('❌ apiBaseUrl.value es vacío');
    return '';
  }
  const url = new URL('/properties/all', apiBaseUrl.value);
  url.searchParams.set('t', new Date().getTime());
  console.log('🔗 propertiesApiUrl generada:', url.href);
  return url.href;
});

// --- FUNCIONES ---
const formatPriceForBubble = (priceString) => {
    if (!priceString) return '';
    const num = parseInt(String(priceString).replace(/\./g, ''), 10);
    if (isNaN(num)) return '';
    if (num >= 1000000) return (num / 1000000).toFixed(1).replace('.0', '') + 'M';
    if (num >= 1000) return `${Math.round(num / 1000)}K`;
    return num.toString();
};

const addMarkersToMap = () => {
    if (!map || !properties.value || properties.value.length === 0) {
        console.log('addMarkersToMap: sin mapa o sin propiedades', { hasMap: !!map, count: properties.value?.length || 0 });
        return;
    }
    console.log('addMarkersToMap: creando marcadores', properties.value.length);
    Object.values(markerElements.value).forEach(el => el.remove());
    markerElements.value = {};
      properties.value.forEach(property => {
        if (!property || isNaN(property.lat) || isNaN(property.lng)) return;
        const el = document.createElement('div');
        el.className = 'marker-container';
        el.style.zIndex = '5';
        const dot = document.createElement('div');
        dot.className = 'marker-dot';
        const bubble = document.createElement('div');
        bubble.className = 'price-bubble';
        bubble.innerHTML = `
          <div class="price-bubble-container">
            <span class="price-text">${formatPriceForBubble(property.price)}</span>
          </div>
          ${property.hasVirtualTour ? `<div class="bubble-badge-external tour">3D TOUR</div>` : ''}
          ${property.isNew ? '<div class="bubble-badge-external new">NEW</div>' : ''}
        `;
        el.appendChild(dot);
        el.appendChild(bubble);
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          showFloatingCard(property);
        });
        markerElements.value[property.id] = el;
        new maplibregl.Marker({ element: el, anchor: 'bottom' }).setLngLat([property.lng, property.lat]).addTo(map);
    });
    updateMarkersVisibility();
};

const updateFilteredProperties = () => {
    if (!map || !properties.value) {
        filteredProperties.value = [];
        return;
    }
    const bounds = map.getBounds();
    filteredProperties.value = properties.value.filter(p => 
        typeof p.lng === 'number' && typeof p.lat === 'number' && bounds.contains([p.lng, p.lat])
    );
    
    // Auto-activar búsqueda si no hay propiedades en el área visible
    if (filteredProperties.value.length === 0 && properties.value.length > 0) {
        showSearchHint();
    }
};

const updateMarkersVisibility = () => {
  if (!map) return;
  const zoom = map.getZoom();
  const showBubbles = zoom >= 14; // umbral
  Object.values(markerElements.value).forEach((el) => {
    const dot = el.querySelector('.marker-dot');
    const bubble = el.querySelector('.price-bubble');
    if (dot) {
      dot.style.opacity = showBubbles ? '0' : '1';
      dot.style.pointerEvents = showBubbles ? 'none' : 'auto';
    }
    if (bubble) {
      bubble.style.opacity = showBubbles ? '1' : '0';
      bubble.style.pointerEvents = showBubbles ? 'auto' : 'none';
    }
  });
};

const togglePropertyList = (event) => {
  console.log('togglePropertyList llamado', { event, currentState: showPropertyList.value });
  
  // Prevenir cualquier comportamiento por defecto
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  showPropertyList.value = !showPropertyList.value;
  console.log('Estado del panel después del toggle:', showPropertyList.value);
  
  if (showPropertyList.value) {
    // Cerrar el card de propiedad cuando se abre el panel
    selectedProperty.value = null;
    updateFilteredProperties();
  }
};

// Función para mostrar hint de búsqueda con efecto sonoro
const showSearchHint = () => {
    // Efecto sonoro (usando Web Audio API)
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
        gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
        console.log('No se pudo reproducir sonido:', e);
    }
    
    // Mostrar notificación visual
    console.log('🔍 No hay propiedades en esta zona. Usa "Buscar en esta zona" para cargar más.');
};

// Función para buscar en el área actual
const searchInCurrentArea = () => {
    console.log('🔍 Buscando en zona actual...');
    // Aquí podrías implementar lógica para cargar más propiedades del backend
    // Por ahora, simplemente recargamos las propiedades
    updateFilteredProperties();
};

const showFloatingCard = (property) => {
  if (!map) return;
  console.log('showFloatingCard llamado con:', property);
  
  // Si ya hay una propiedad seleccionada, cerrar el panel lateral primero
  if (selectedProperty.value) {
    showPropertyList.value = false;
  }
  
  selectedProperty.value = property;
  openedFromSlide.value = false;
  isModalOpen.value = false;
  const p = map.project([property.lng, property.lat]);
  // centrar card (ancho aprox 310)
  const x = Math.max(10, Math.min(p.x - 155, windowWidth.value - 320));
  const y = Math.max(10, Math.min(p.y - 360, windowHeight.value - 360));
  cardPosition.value = { x, y };
  cardPlacement.value = p.y < 360 ? 'top' : 'bottom';
  console.log('Card posicionada en:', { x, y, placement: cardPlacement.value });
};

const openModalFromSlide = (property) => {
  console.log('openModalFromSlide llamado con:', property);
  selectedProperty.value = property;
  openedFromSlide.value = true;
  isModalOpen.value = true;
  console.log('Estado del modal después de abrir:', { isModalOpen: isModalOpen.value, selectedProperty: selectedProperty.value });
};

const toggleFavorite = (property) => {
  console.log('toggleFavorite llamado en PropertyMap con:', property);
  console.log('user?.value:', user?.value);
  
  if (!user?.value) {
    console.log('Usuario no logueado, mostrando modal de login');
    showLoginModal.value = true;
    return;
  }
  
  console.log('Usuario logueado, llamando a favoritesStore.toggleFavorite');
  favoritesStore.toggleFavorite(property);
  console.log('favoritesStore.toggleFavorite ejecutado');
};

const handleCloseModal = () => {
  console.log('handleCloseModal llamado');
  isModalOpen.value = false;
  openedFromSlide.value = false;
  selectedProperty.value = null;
  console.log('Estado del modal después de cerrar:', { isModalOpen: isModalOpen.value, selectedProperty: selectedProperty.value });
};

// --- CICLO DE VIDA ---
onMounted(async () => {
  if (propertiesApiUrl.value) {
    console.log('API URL para propiedades:', propertiesApiUrl.value); // LOG PARA DEBUG
    pending.value = true;
    error.value = null;
    try {
      const raw = await $fetch(propertiesApiUrl.value, { cache: 'no-store' });
      let data = [];
      if (Array.isArray(raw)) {
        const normalized = raw.map((property) => {
          let latRaw = property?.lat ?? property?.latitude ?? property?.latitud;
          let lngRaw = property?.lng ?? property?.longitude ?? property?.longitud ?? property?.lon;
          let lat = latRaw != null ? parseFloat(String(latRaw)) : NaN;
          let lng = lngRaw != null ? parseFloat(String(lngRaw)) : NaN;
          if ((!Number.isFinite(lat) || !Number.isFinite(lng)) && typeof property?.location === 'string') {
            const match = property.location.match(/POINT\s*\(\s*(-?[0-9]*\.?[0-9]+)\s+(-?[0-9]*\.?[0-9]+)\s*\)/i);
            if (match) {
              lng = parseFloat(match[1]);
              lat = parseFloat(match[2]);
            }
          }
          return {
            ...property,
            lat,
            lng,
            images: property?.images_array || property?.images || [],
          };
        });
        data = normalized.filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lng));
      }
      console.log('Resultado de la API (fetch directo):', { count: data.length });
      properties.value = data;
    } catch (e) {
      console.error('Error obteniendo propiedades:', e);
      error.value = e;
    } finally {
      pending.value = false;
    }
  } else {
    console.error('La URL de la API de propiedades no está configurada.'); // LOG PARA DEBUG
    pending.value = false;
  }

  if (mapContainer.value) {
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: `https://api.maptiler.com/maps/streets/style.json?key=RqptbBn3gxBTDHGJ4a3O`,
      center: [-57.5425, -38.0179],
      zoom: 15 // Zoom más cercano para cargar menos propiedades inicialmente
    });
    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
    map.on('load', () => {
    updateFilteredProperties();
      if (properties.value.length > 0) addMarkersToMap();
      map.on('moveend', updateFilteredProperties);
      map.on('zoom', updateMarkersVisibility);
      // Cerrar card al hacer click en el mapa (no en marcadores)
      map.on('click', (e) => {
        // Solo cerrar si no hay panel lateral abierto
        if (selectedProperty.value && !showPropertyList.value) {
    selectedProperty.value = null;
  }
      });
    });
  }
});

watch(properties, (newProperties) => {
  if (newProperties && newProperties.length > 0 && map && map.isStyleLoaded()) {
    addMarkersToMap();
    updateFilteredProperties();
  }
}, { deep: true });

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', () => {
      windowWidth.value = window.innerWidth;
      windowHeight.value = window.innerHeight;
    });
    window.addEventListener('mousemove', (e) => {
  mouse.value = { x: e.clientX, y: e.clientY };
    });
  }
});

</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
}
/* Estilos para el contenedor principal del mapa */
.relative {
  position: relative;
  width: 100%;
  height: 100vh; /* Ocupa toda la altura de la ventana */
  min-height: 100%;
  overflow: hidden;
}

/* Estilos para el contenedor del mapa */
.absolute.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.marker-container {
  /* Contenedor invisible que sirve de ancla. Su parte inferior es el punto geográfico. */
  width: 120px;
  height: 80px;
  cursor: pointer;
  /* background: rgba(0,255,0,0.2); /* Descomentar para depurar y ver el área del contenedor */
}

.marker-dot, .price-bubble {
  /* Todo se posiciona hacia arriba desde la parte inferior del contenedor */
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%); /* Solo centrado horizontal, no vertical */
  will-change: opacity;
  transition: opacity 0.2s ease-in-out;
}

.marker {
  position: relative; /* Requerido para la animación del pseudo-elemento */
  background-color: #EF4444; /* Tailwind's red-500 */
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  cursor: pointer;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
}

.active-marker::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: transparent;
  box-shadow: 0 0 1px 2px rgba(239, 68, 68, 0.7);
  animation: sonar 1.5s infinite;
}

@keyframes sonar {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

.marker-dot {
  /* Ajustamos la posición para que su centro esté en el ancla */
  transform: translate(-50%, -50%);
  position: relative;
  background-color: #EF4444;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
}

.price-bubble {
  /* Este ya está centrado, solo definimos su apariencia */
  display: flex;
  flex-direction: column;
  align-items: center;
}

.price-bubble-container {
  position: relative;
  background-color: #c00;
  color: white;
  padding: 5px 12px;
  border-radius: 16px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  gap: 5px;
  border: 2px solid white;
}

.price-bubble-container::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #c00;
}

.bubble-badge-internal {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 4px;
  background-color: rgba(0,0,0,0.2);
  line-height: 1;
}

.bubble-badge-external {
  position: absolute;
  background: white;
  color: #c00;
  padding: 1px 7px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  border: 2px solid #c00;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  z-index: 1;
  white-space: nowrap;
}

.bubble-badge-external.new {
  top: -20px;
  left: 50%;
  transform: translateX(-50%) translateX(-25px); /* Centra y luego desplaza */
}

.bubble-badge-external.tour {
  top: -20px;
  left: 50%;
  transform: translateX(-50%) translateX(25px); /* Centra y luego desplaza */
}

.marker-container.selected .price-bubble-container,
.marker-container.selected .marker-dot {
  background-color: #333;
}
.marker-container.selected .price-bubble-container::after {
  border-top-color: #333;
}

.marker-container.selected::after {
  content: '';
  position: absolute;
  bottom: 10px; /* Posicionado cerca del ancla */
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #333;
  animation: sonar-wave 1.5s infinite ease-out;
  z-index: -1;
}

@keyframes sonar-wave {
  0% {
    transform: translateX(-50%) scale(0.5);
    opacity: 0.6;
  }
  100% {
    transform: translateX(-50%) scale(2.5);
    opacity: 0;
  }
}

.marker-container.viewed .marker-dot, 
.marker-container.viewed .price-bubble-container {
  background-color: #38e8ff !important; /* Turquesa claro */
  border-color: #fff !important; /* Borde blanco */
}
.marker-container.viewed .price-bubble-container {
  color: #222 !important;
}

/* Efecto sonar activo para marcadores */
.marker-dot.sonar-active::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 60px;
  height: 60px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background-color: transparent;
  box-shadow: 0 0 1px 2px rgba(239, 68, 68, 0.7);
  animation: sonar 1.5s infinite;
  pointer-events: none;
  z-index: -1; /* Detrás del marcador */
}

.price-bubble.sonar-active .price-bubble-container {
  background-color: #333;
}
.price-bubble.sonar-active .price-bubble-container::after {
  border-top-color: #333;
}

/* Ocultar controles flotantes de MapLibre */
.maplibregl-ctrl-bottom-right,
.maplibregl-ctrl-logo,
.maplibregl-ctrl-attrib {
  display: none !important;
}

@keyframes animatedGradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animated-gradient-bg {
  background: linear-gradient(270deg, #6366f1, #22d3ee, #6366f1, #0ea5e9, #6366f1);
  background-size: 400% 400%;
  animation: animatedGradient 6s ease-in-out infinite;
}
</style>