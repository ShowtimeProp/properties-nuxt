<template>
  <div ref="mapWrapper" id="mapWrapper" class="w-full h-full">
    <div ref="mapContainer" id="mapContainer" class="w-full h-full"></div>
    
    
    <!-- Botón Ver Listado - Solo visible en desktop -->
    <button 
      ref="toggleButton"
      @click.stop.prevent="togglePropertyList"
      @touchstart.stop.prevent="togglePropertyList"
      type="button"
      class="hidden md:flex absolute top-24 right-24 z-20 items-center gap-2 px-4 animated-gradient-bg text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors text-base"
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
            class="fixed top-0 right-0 bg-white shadow-xl z-30 transform transition-transform duration-300 ease-in-out flex flex-col pt-[20px] md:pt-[110px] w-full md:w-[450px] lg:w-[40%] max-w-[750px]"
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
            @hover-start="highlightMarker(property)"
            @hover-end="unhighlightMarker(property)"
          />
        </div>
        <div v-else class="h-full flex items-center justify-center p-8 text-gray-500">
          <p>No hay propiedades en esta área</p>
        </div>
      </div>
    </div>

  </div>


  <Transition name="property-card">
    <div v-if="selectedProperty && (!isModalOpen || !openedFromSlide)"
      :style="{ position: 'absolute', left: `${cardPosition.x}px`, top: `${cardPosition.y}px`, zIndex: 30, width: '310px' }"
      @click.stop
    >
      <!-- Card sin flecha -->
        <PropertyCard 
          :property="selectedProperty" 
          @toggle-favorite="toggleFavorite(selectedProperty)"
          @close="selectedProperty = null"
          @open-modal="isModalOpen = true"
          @login-request="showLoginModal = true"
        />
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

// --- ESTADO PARA CARGA OPTIMIZADA ---
let fetchController = null; // Para cancelar requests anteriores
let fetchTimer = null; // Para debounce
const isLoadingProperties = ref(false);

// --- COMPUTED PROPS ---
const sortedProperties = computed(() => {
  // Aquí puedes añadir la lógica de ordenamiento que tenías antes si la necesitas.
  return filteredProperties.value;
});

const apiBaseUrl = computed(() => {
  // Forzar el uso de la IP del backend
  const backendUrl = 'https://212.85.20.219:8000';
  console.log('🔍 Debug apiBaseUrl:', { backendUrl, configValue: config.public.apiBaseUrl });
  console.log('✅ Usando backend URL:', backendUrl);
  return backendUrl;
});

const propertiesApiUrl = computed(() => {
  if (!apiBaseUrl.value) {
    console.log('❌ apiBaseUrl.value es vacío');
    return '';
  }
  const url = new URL('/properties/geojson', apiBaseUrl.value);
  console.log('🔗 propertiesApiUrl base generada:', url.href);
  return url.href;
});

// --- FUNCIONES ---
const formatPriceForBubble = (priceString) => {
    if (!priceString) return 'Consultar Precio';
    const num = parseInt(String(priceString).replace(/\./g, ''), 10);
    if (isNaN(num)) return 'Consultar Precio';
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
        const priceText = formatPriceForBubble(property.price);
        const isConsultarPrecio = priceText === 'Consultar Precio';
        
        bubble.innerHTML = `
        <div class="price-bubble-container ${isConsultarPrecio ? 'consultar-precio' : ''}">
            <span class="price-text">${priceText}</span>
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
        if (maplibreglInstance) {
          new maplibreglInstance.Marker({ element: el, anchor: 'bottom' }).setLngLat([property.lng, property.lat]).addTo(map);
    } else {
          console.error('MapLibre instance not available for creating marker');
        }
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

// Funciones para highlight de marcadores en hover
const highlightMarker = (property) => {
  if (!property || !markerElements.value[property.id]) return;
  
  const markerEl = markerElements.value[property.id];
  markerEl.classList.add('marker-highlighted');
  
  // Agregar efecto de pulso
  const dot = markerEl.querySelector('.marker-dot');
  const bubble = markerEl.querySelector('.price-bubble');
  
  if (dot) {
    dot.style.transform = 'scale(1.3)';
    dot.style.transition = 'transform 0.3s ease';
    dot.style.zIndex = '10';
  }
  
  if (bubble) {
    bubble.style.transform = 'scale(1.1)';
    bubble.style.transition = 'transform 0.3s ease';
    bubble.style.zIndex = '10';
  }
};

const unhighlightMarker = (property) => {
  if (!property || !markerElements.value[property.id]) return;
  
  const markerEl = markerElements.value[property.id];
  markerEl.classList.remove('marker-highlighted');
  
  // Restaurar estado normal
  const dot = markerEl.querySelector('.marker-dot');
  const bubble = markerEl.querySelector('.price-bubble');
  
  if (dot) {
    dot.style.transform = 'scale(1)';
    dot.style.transition = 'transform 0.3s ease';
    dot.style.zIndex = '5';
  }
  
  if (bubble) {
    bubble.style.transform = 'scale(1)';
    bubble.style.transition = 'transform 0.3s ease';
    bubble.style.zIndex = '5';
  }
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

// Variable para almacenar todas las propiedades disponibles
const allProperties = ref([]);

// Variable global para MapLibre
let maplibreglInstance = null;

// --- FUNCIÓN PARA CARGAR PROPIEDADES POR VIEWPORT ---
const fetchViewportProperties = async () => {
  if (!map || !propertiesApiUrl.value) {
    console.log('⏸️ fetchViewportProperties: mapa o URL no disponible');
    return;
  }
  
  // Cancelar request anterior si existe
  if (fetchController) {
    fetchController.abort();
  }
  
  fetchController = new AbortController();
  
  try {
    isLoadingProperties.value = true;
    
    // Obtener bounds del viewport actual
    const bounds = map.getBounds();
    const bbox = [
      bounds.getWest(),
      bounds.getSouth(),
      bounds.getEast(),
      bounds.getNorth()
    ].join(',');
    
    const zoom = Math.round(map.getZoom());
    
    console.log(`📍 Cargando propiedades en viewport (zoom ${zoom}):`, bbox);
    
    // Construir URL con parámetros
    const url = `${propertiesApiUrl.value}?bbox=${bbox}&zoom=${zoom}&limit=1000`;
    
    // Fetch con cancelación
    const response = await fetch(url, { 
      signal: fetchController.signal,
      cache: 'no-store'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const geojson = await response.json();
    
    // Convertir GeoJSON a formato de propiedades
    if (geojson.features && Array.isArray(geojson.features)) {
      const newProperties = geojson.features.map(feature => ({
        ...feature.properties,
        lat: feature.geometry.coordinates[1],
        lng: feature.geometry.coordinates[0]
      }));
      
      console.log(`✅ Cargadas ${newProperties.length} propiedades en viewport`);
      
      // Actualizar propiedades
      properties.value = newProperties;
      filteredProperties.value = newProperties;
      
      // Actualizar marcadores
      if (map.isStyleLoaded()) {
        addMarkersToMap();
      }
    }
    
  } catch (e) {
    if (e.name === 'AbortError') {
      console.log('⏹️ Request cancelado (nuevo movimiento del mapa)');
    } else {
      console.error('❌ Error cargando propiedades:', e);
      error.value = e;
    }
  } finally {
    isLoadingProperties.value = false;
  }
};

// Función con debounce para evitar demasiados requests
const debouncedFetchViewport = () => {
  clearTimeout(fetchTimer);
  fetchTimer = setTimeout(() => {
    fetchViewportProperties();
  }, 300); // 300ms de debounce
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
  
  // Posicionar el card SIN mover el mapa
  positionCard(property);
};

// Función para ajustar el mapa automáticamente para que el card sea visible
const adjustMapForCard = (property) => {
  if (!map) return;
  
  const cardWidth = 320; // Ancho aproximado del card
  const cardHeight = 360; // Alto aproximado del card
  const margin = 20; // Margen de seguridad
  
  // Obtener dimensiones del contenedor del mapa
  const mapContainer = map.getContainer();
  const mapWidth = mapContainer.clientWidth;
  const mapHeight = mapContainer.clientHeight;
  
  // Proyectar la posición de la propiedad en píxeles
  const point = map.project([property.lng, property.lat]);
  
  // Calcular la posición ideal del card (centrado sobre el marker)
  let cardX = point.x - (cardWidth / 2);
  let cardY = point.y - cardHeight - 20; // 20px de separación del marker
  
  // Calcular el offset necesario para centrar la propiedad + card
  let offsetX = 0;
  let offsetY = 0;
  
  // Offset horizontal: mover hacia el centro si el card se sale
  if (cardX < margin) {
    // Card se sale por la izquierda - mover hacia la derecha
    offsetX = (mapWidth / 2) - point.x - (cardWidth / 4);
  } else if (cardX + cardWidth > mapWidth - margin) {
    // Card se sale por la derecha - mover hacia la izquierda
    offsetX = (mapWidth / 2) - point.x + (cardWidth / 4);
  } else {
    // Card está bien horizontalmente - pequeño offset hacia el centro
    offsetX = (mapWidth / 2) - point.x - (cardWidth / 6);
  }
  
  // Offset vertical: mover hacia el centro si el card se sale
  if (cardY < margin) {
    // Card se sale por arriba - mover hacia abajo
    offsetY = (mapHeight / 2) - point.y - (cardHeight / 4);
  } else if (cardY + cardHeight > mapHeight - margin) {
    // Card se sale por abajo - mover hacia arriba
    offsetY = (mapHeight / 2) - point.y + (cardHeight / 4);
  } else {
    // Card está bien verticalmente - pequeño offset hacia el centro
    offsetY = (mapHeight / 2) - point.y - (cardHeight / 6);
  }
  
  // Convertir offset de píxeles a coordenadas del mapa
  const currentCenter = map.getCenter();
  const offsetPoint = map.unproject([offsetX, offsetY]);
  
  // Calcular nuevo centro
  const newCenter = {
    lng: currentCenter.lng + (offsetPoint.lng - currentCenter.lng),
    lat: currentCenter.lat + (offsetPoint.lat - currentCenter.lat)
  };
  
  // Aplicar el ajuste del mapa
  map.easeTo({
    center: newCenter,
    duration: 500, // Animación suave de 500ms
    easing: (t) => t * (2 - t) // Easing suave
  });
  
  // Esperar a que termine la animación antes de posicionar el card
  setTimeout(() => {
    positionCard(property);
  }, 550);
};

// Función para posicionar el card con más espacio en los bordes
const positionCard = (property) => {
  if (!map) return;
  
  const p = map.project([property.lng, property.lat]);
  const cardWidth = 320;
  const cardHeight = 360;
  
  // Aumentar márgenes para mejor visibilidad
  const marginX = 40; // Más espacio en los lados
  const marginY = 50; // Más espacio arriba y abajo
  
  // Calcular posición centrada del card con más espacio
  const x = Math.max(marginX, Math.min(p.x - (cardWidth / 2), windowWidth.value - cardWidth - marginX));
  const y = Math.max(marginY, Math.min(p.y - cardHeight - 20, windowHeight.value - cardHeight - marginY));
  
  cardPosition.value = { x, y };
  cardPlacement.value = p.y < cardHeight + 60 ? 'top' : 'bottom'; // Ajustar threshold también
  
  console.log('Card posicionado con más espacio en:', { x, y, placement: cardPlacement.value, margins: { x: marginX, y: marginY } });
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
  // Inicializar eventos de ventana
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', () => {
      windowWidth.value = window.innerWidth;
      windowHeight.value = window.innerHeight;
    });
    window.addEventListener('mousemove', (e) => {
      mouse.value = { x: e.clientX, y: e.clientY };
    });
  }

  if (mapContainer.value) {
    // Importación dinámica de MapLibre
    const { default: maplibregl } = await import('maplibre-gl');
    await import('maplibre-gl/dist/maplibre-gl.css');
    
    // Guardar la instancia globalmente
    maplibreglInstance = maplibregl;
    
    console.log('🗺️ MapLibre cargado dinámicamente');
    
    // Verificar que el contenedor tiene dimensiones
    const container = mapContainer.value;
    
    // Asegurar que el contenedor tiene dimensiones
    if (container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.warn('Contenedor sin dimensiones, esperando...');
      await nextTick();
      container.style.width = '100%';
      container.style.height = '100%';
    }
    
    // Crear mapa
    map = new maplibregl.Map({
      container: container,
      style: `https://api.maptiler.com/maps/streets/style.json?key=RqptbBn3gxBTDHGJ4a3O`,
      center: [-57.5425, -38.0179], // Mar del Plata centro
      zoom: 13
    });
    
    map.addControl(new maplibreglInstance.NavigationControl(), 'bottom-right');
    
    // Cuando el mapa esté listo
    map.on('load', () => {
      console.log('🗺️ Mapa cargado y listo');
      map.resize();
      
      // Cargar propiedades del viewport inicial
      fetchViewportProperties();
      
      // Eventos del mapa
      map.on('moveend', () => {
        debouncedFetchViewport(); // Cargar propiedades cuando se mueve el mapa
    updateFilteredProperties();
      });
      
      map.on('zoom', updateMarkersVisibility);
      
      // Cerrar card al hacer click en el mapa
      map.on('click', (e) => {
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

// Eventos de ventana movidos al onMounted principal

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
}

/* Estilos específicos para nuestros contenedores */
#mapWrapper, #mapContainer {
  width: 100% !important;
  height: 100vh !important;
  min-height: 100vh !important;
  position: relative !important;
  display: block !important;
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

/* Texto más pequeño para "Consultar Precio" */
.price-bubble-container.consultar-precio {
  font-size: 10px;
  padding: 4px 8px;
  line-height: 1.1;
}

/* Punta blanca removida - ya no es necesaria */

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
/* Referencia a punta removida */

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
/* Referencia a punta removida */

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

/* Estilos para highlight de marcadores en hover */
.marker-highlighted .marker-dot {
  background-color: #fbbf24 !important; /* Amarillo dorado */
  box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.3), 0 0 20px rgba(251, 191, 36, 0.6) !important;
  animation: markerPulse 1.5s infinite;
}

.marker-highlighted .price-bubble-container {
  background-color: #fbbf24 !important; /* Amarillo dorado */
  color: #1f2937 !important; /* Gris oscuro para contraste */
  box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.4), 0 4px 20px rgba(251, 191, 36, 0.5) !important;
  border: 2px solid #f59e0b !important; /* Borde más oscuro */
}

/* Animación de pulso para el marcador destacado */
@keyframes markerPulse {
  0% {
    box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.3), 0 0 20px rgba(251, 191, 36, 0.6);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(251, 191, 36, 0.2), 0 0 30px rgba(251, 191, 36, 0.8);
  }
  100% {
    box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.3), 0 0 20px rgba(251, 191, 36, 0.6);
  }
}
</style>