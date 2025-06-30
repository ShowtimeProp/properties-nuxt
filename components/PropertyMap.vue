<template>
  <div class="relative w-full h-full">
    <div ref="mapContainer" class="absolute inset-0"></div>
    
    <!-- Botón Ver Listado -->
    <button 
      ref="toggleButton"
      @click="togglePropertyList"
      class="absolute top-4 right-24 z-20 flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <span>Ver Listado</span>
    </button>
    
    <!-- Panel de Listado de Propiedades -->
    <div 
      ref="propertyListPanel"
      class="fixed top-0 right-0 h-full w-[750px] bg-white shadow-xl z-30 transform transition-transform duration-300 ease-in-out flex flex-col"
      :class="{ 'translate-x-0': showPropertyList, 'translate-x-full': !showPropertyList }"
      style="box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1)"
    >
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-lg font-semibold">Propiedades encontradas</h3>
        <button @click="togglePropertyList" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <!-- Lista de Propiedades en Grid (sin menú de ordenamiento) -->
      <div ref="scrollContainer" class="flex-1 overflow-y-auto p-4">
        <div v-if="sortedProperties.length > 0" class="grid grid-cols-2 gap-4">
          <PropertySlideCardClean
            v-for="property in sortedProperties"
            :key="property.id"
            :property="property"
            :is-favorite="isFavorite(property)"
            @toggle-favorite="toggleFavorite(property)"
            @click="selectPropertyFromList(property)"
            class="mx-auto"
          />
        </div>
        <div v-else class="h-full flex items-center justify-center p-8 text-gray-500">
          <p>No hay propiedades en esta área</p>
        </div>
      </div>
    </div>

    <!-- Controles de Dibujo -->
    <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex flex-row items-center gap-3">
    <!-- Menú Herramienta de Dibujo -->
    <div v-if="isTridentOpen" class="flex flex-col items-center gap-2">
      <div class="bg-white rounded-lg shadow-lg p-3">
        <div class="flex items-center gap-2 text-sm text-gray-600 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Haz clic en el mapa para dibujar. Haz clic derecho para terminar.</span>
        </div>
        <button @click="startDrawing('polygon')" class="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors w-full justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          <span>Dibujar área</span>
        </button>
      </div>
    </div>

    <!-- Botón de Dibujo Principal -->
    <div class="flex items-center gap-2">
        <button v-if="!shapeDrawn" @click="toggleTrident" class="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          <span>Dibujar área</span>
        </button>
        
        <button v-if="shapeDrawn" @click="deleteShape" class="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Eliminar área</span>
        </button>
      <button class="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors">
        <span>Buscar en esta zona</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h5M4 12a8 8 0 0114.24-5.236M20 20v-5h-5M20 12a8 8 0 01-14.24 5.236" />
        </svg>
      </button>
      <div v-if="isTridentOpen" class="text-xs text-gray-600 bg-white/90 px-3 py-1 rounded-lg shadow">
        <p class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Haz clic derecho para terminar el dibujo
        </p>
      </div>
    </div>
  </div>

  <Transition name="property-card">
    <div v-if="selectedProperty"
      :style="{ position: 'absolute', left: `${cardPosition.x}px`, top: `${cardPosition.y}px`, zIndex: 30, width: '310px' }"
    >
      <!-- Card con flecha -->
      <div style="position: relative;">
        <PropertyCard 
          :property="selectedProperty" 
          :is-favorite="isFavorite(selectedProperty)"
          @toggle-favorite="toggleFavorite(selectedProperty)"
          @close="selectedProperty = null"
          @open-modal="isModalOpen = true"
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
      :property="selectedProperty"
      @close="isModalOpen = false"
    />
    </Transition>
  </div>
</template>

<script setup>
import PropertySlideCardClean from './PropertySlideCardClean.vue';
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import PropertyCard from './PropertyCard.vue';
import PropertyModal from './PropertyModal.vue';

// Asegurarse de que MapboxDraw funcione con MapLibre
if (typeof window !== 'undefined') {
  window.MapboxDraw = MapboxDraw;
}

const mapContainer = ref(null)
let map = null // No reactivo, para evitar problemas con el proxy de Vue
const selectedProperty = ref(null);
const isTridentOpen = ref(false);
const scrollContainer = ref(null);
const propertyListPanel = ref(null);
const toggleButton = ref(null);

const loadMoreProperties = () => {
  // Placeholder for infinite scroll logic
  console.log('Loading more properties...');
  // In a real application, you would fetch more data here
  // and append it to the sortedProperties array.
};

onMounted(() => {
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('scroll', () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value;
      if (scrollTop + clientHeight >= scrollHeight - 50) { // 50px from bottom
        loadMoreProperties();
      }
    });
  }
  
  // Agregar listener global para cerrar el panel al hacer click fuera
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  if (scrollContainer.value) {
    scrollContainer.value.removeEventListener('scroll', () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value;
      if (scrollTop + clientHeight >= scrollHeight - 50) {
        loadMoreProperties();
      }
    });
  }
  
  // Remover listener global
  document.removeEventListener('click', handleClickOutside);
});
const shapeDrawn = ref(false);
const showPropertyList = ref(false);
const sortBy = ref('relevance');
const favorites = ref(new Set());
let draw = null;
const isModalOpen = ref(false);
const markerElements = ref({});
const ZOOM_THRESHOLD = 14.0;
const filteredProperties = ref([]);
const showSortMenu = ref(false);
const viewedProperties = ref(new Set());
const cardPosition = ref({ x: 0, y: 0 });
const cardPlacement = ref('top'); // 'top' o 'bottom'

const sortOptions = [
  { value: 'relevance', label: 'Relevancia' },
  { value: 'price-asc', label: 'Menor precio' },
  { value: 'price-desc', label: 'Mayor precio' },
  { value: 'price-m2-asc', label: 'Menor precio/m²' },
  { value: 'price-m2-desc', label: 'Mayor precio/m²' },
  { value: 'size-asc', label: 'Menor tamaño' },
  { value: 'size-desc', label: 'Mayor tamaño' }
];

const formatPriceForBubble = (priceString) => {
  const num = parseInt(priceString.replace(/\./g, ''), 10);
  if (isNaN(num)) return '';
  if (num >= 1000000) {
    const value = num / 1000000;
    return (value % 1 === 0 ? value.toFixed(0) : value.toFixed(1)) + 'M';
  }
  if (num >= 1000) {
    return `${Math.round(num / 1000)}K`;
  }
  return num.toString();
};

const updateMarkersForZoom = () => {
  if (!map) return;
  const currentZoom = map.getZoom();
  const isBubbleView = currentZoom > ZOOM_THRESHOLD;

  for (const prop of properties.value) {
    const markerEl = markerElements.value[prop.id];
    if (!markerEl) continue;

    const isSelected = markerEl.classList.contains('selected');
    const currentView = markerEl.dataset.view;
    const newView = isBubbleView ? 'bubble' : 'dot';

    if (currentView === newView) {
        if (isSelected && !markerEl.classList.contains('selected')) {
            markerEl.classList.add('selected');
        } else if (!isSelected && markerEl.classList.contains('selected')) {
            markerEl.classList.remove('selected');
        }
        // Cambiar color si fue vista
        if (viewedProperties.value.has(prop.id)) {
          markerEl.classList.add('viewed');
        } else {
          markerEl.classList.remove('viewed');
        }
        continue;
    }

    markerEl.dataset.view = newView;

    if (isBubbleView) {
      markerEl.className = 'price-bubble';
      markerEl.innerHTML = `
        <div class="price-bubble-container">
          <span class="price-text">${formatPriceForBubble(prop.price)}</span>
        </div>
        ${prop.hasVirtualTour ? `<div class="bubble-badge-external tour">3D TOUR</div>` : ''}
        ${prop.isNew ? '<div class="bubble-badge-external new">NEW</div>' : ''}
      `;
    } else {
      markerEl.className = 'marker-dot';
      markerEl.innerHTML = '';
    }

    // Cambiar color si fue vista
    if (viewedProperties.value.has(prop.id)) {
      markerEl.classList.add('viewed');
    } else {
      markerEl.classList.remove('viewed');
    }

    if (isSelected) {
      markerEl.classList.add('selected');
    }
  }
};

const properties = ref([
  {
    id: 1,
    lng: -57.54,
    lat: -38.01,
    title: 'Departamento céntrico',
    price: '150.000',
    expenses: '12.000',
    address: 'Corrientes 2345, Mar del Plata',
    zone: 'Centro',
    total_surface: 75,
    ambience: 3,
    bedrooms: 2,
    bathrooms: 2,
    garage_count: 1,
    realty: 'REMAX BIANCA NICOLINI',
    hasVirtualTour: true,
    badge: '3D TOUR',
    isNew: false,
    images: [
      'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=360&h=180&fit=crop'
    ]
  },
  {
    id: 2,
    lng: -57.555,
    lat: -38.005,
    title: 'Casa con vista al mar',
    price: '320.000',
    expenses: '25.000',
    address: 'Bv. Marítimo 1100',
    zone: 'Playa Grande',
    total_surface: 120,
    ambience: 4,
    bedrooms: 3,
    bathrooms: 3,
    garage_count: 2,
    realty: 'INMOBILIARIA COSTA',
    hasVirtualTour: false,
    badge: null,
    isNew: false,
    images: [
      'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1572120360610-d971b9d7767c?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=360&h=180&fit=crop'
    ]
  },
  {
    id: 3,
    lng: -57.53,
    lat: -37.99,
    title: 'Chalet en zona residencial',
    price: '210.000',
    expenses: '18.000',
    address: 'Formosa 850',
    zone: 'Los Troncos',
    total_surface: 90,
    ambience: 3,
    bedrooms: 2,
    bathrooms: 2,
    garage_count: 1,
    realty: 'INMOBILIARIA LOS PINOS',
    hasVirtualTour: false,
    badge: null,
    isNew: false,
    images: [
      'https://images.unsplash.com/photo-1570129477492-45c003edd2be?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1568605114967-8130f3a36994?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1605276374104-5de67d60924f?q=80&w=360&h=180&fit=crop'
    ]
  },
  {
    id: 4,
    lng: -57.56,
    lat: -38.02,
    title: 'Loft moderno',
    price: '185.000',
    expenses: '15.000',
    address: 'Alvarado 3120',
    zone: 'Macrocentro',
    total_surface: 65,
    ambience: 2,
    bedrooms: 1,
    bathrooms: 1,
    garage_count: 0,
    realty: 'INMOBILIARIA URBANA',
    hasVirtualTour: false,
    badge: 'NUEVO',
    isNew: true,
    images: [
      'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1598228723793-52759bba239c?q=80&w=360&h=180&fit=crop',
      'https://images.unsplash.com/photo-1540518614846-7eded433c457?q=80&w=360&h=180&fit=crop'
    ]
  }
]);

onMounted(async () => {
  // Importar dinámicamente solo en el cliente
  const maplibregl = await import('maplibre-gl');
  await import('maplibre-gl/dist/maplibre-gl.css');

  if (mapContainer.value) {
    // Configuración del mapa con MapTiler
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: `https://api.maptiler.com/maps/streets/style.json?key=RqptbBn3gxBTDHGJ4a3O`,
      center: [-57.5425, -38.0179],
      zoom: 13
    });

    // Agregar controles de navegación
    map.addControl(new maplibregl.NavigationControl(), 'top-right');

    map.on('load', () => {
      properties.value.forEach(property => {
        const el = document.createElement('div');
        el.className = 'marker';

        el.addEventListener('click', (e) => {
          e.stopPropagation();
          showPropertyCard(property);
        });

        markerElements.value[property.id] = el;

        new maplibregl.Marker({ element: el })
          .setLngLat([property.lng, property.lat])
          .addTo(map);
      });
    });

    // Ocultar el card al arrastrar el mapa
    map.on('dragstart', () => {
      selectedProperty.value = null;
    });

    // Ocultar el card al hacer click en el mapa (fuera de una burbuja)
    map.on('click', (e) => {
      if (e.originalEvent.target === map.getCanvas()) {
        selectedProperty.value = null;
      }
    });

    updateMarkersForZoom();
    map.on('zoom', updateMarkersForZoom);

    // Inicializar MapboxDraw con estilos compatibles
    draw = new MapboxDraw({
      displayControlsDefault: false, // Usaremos nuestros propios controles
      controls: {
        polygon: true,
        trash: false // Usaremos un botón de eliminar personalizado
      },
      styles: [
        // Estilo para el polígono activo (cuando se está dibujando)
        {
          id: 'gl-draw-polygon-fill-active',
          type: 'fill',
          filter: ['all',
            ['==', 'active', 'true'],
            ['==', '$type', 'Polygon']
          ],
          paint: {
            'fill-color': '#3bb2d0',
            'fill-outline-color': '#3bb2d0',
            'fill-opacity': 0.1
          }
        },
        // Estilo para el polígono inactivo
        {
          id: 'gl-draw-polygon-fill-inactive',
          type: 'fill',
          filter: ['all',
            ['==', 'active', 'false'],
            ['==', '$type', 'Polygon']
          ],
          paint: {
            'fill-color': '#3bb2d0',
            'fill-outline-color': '#3bb2d0',
            'fill-opacity': 0.1
          }
        },
        // Estilo para el borde del polígono activo
        {
          id: 'gl-draw-polygon-stroke-active',
          type: 'line',
          filter: ['all',
            ['==', 'active', 'true'],
            ['==', '$type', 'Polygon']
          ],
          layout: {},
          paint: {
            'line-color': '#3bb2d0',
            'line-width': 2,
            'line-dasharray': [2, 2]
          }
        },
        // Estilo para el borde del polígono inactivo
        {
          id: 'gl-draw-polygon-stroke-inactive',
          type: 'line',
          filter: ['all',
            ['==', 'active', 'false'],
            ['==', '$type', 'Polygon']
          ],
          layout: {},
          paint: {
            'line-color': '#3bb2d0',
            'line-width': 2
          }
        },
        // Estilo para los puntos de control
        {
          id: 'gl-draw-polygon-and-line-vertex-active',
          type: 'circle',
          filter: ['all',
            ['==', 'meta', 'vertex'],
            ['==', '$type', 'Point']
          ],
          paint: {
            'circle-radius': 4,
            'circle-color': '#fbb03b'
          }
        }
      ]
    });
    map.addControl(draw, 'top-right');

    map.on('draw.create', () => {
      shapeDrawn.value = true;
      isTridentOpen.value = false;
      // Aquí irá la lógica para filtrar propiedades
    });

    map.on('draw.delete', () => {
      shapeDrawn.value = false;
      // Lógica para resetear el filtro
    });

    map.on('style.load', () => {
      console.log('El estilo del mapa se ha cargado completamente.');
    });

    watch(selectedProperty, (newVal, oldVal) => {
      // Quitar clase del marcador antiguo
      if (oldVal && markerElements.value[oldVal.id]) {
        markerElements.value[oldVal.id].classList.remove('active-marker');
      }
      // Añadir clase al nuevo marcador
      if (newVal && markerElements.value[newVal.id]) {
        markerElements.value[newVal.id].classList.add('active-marker');
      }
    });
  }
});

onUnmounted(() => {
  if (map) {
    map.remove();
  }
});

const toggleTrident = () => {
  isTridentOpen.value = !isTridentOpen.value;
};

const startDrawing = () => {
  isTridentOpen.value = false;
  if (draw) {
    draw.changeMode('draw_polygon');
  }
};

const deleteShape = () => {
  if (draw) {
    draw.deleteAll();
    shapeDrawn.value = false;
    filteredProperties.value = [];
  }
};

const togglePropertyList = () => {
  showPropertyList.value = !showPropertyList.value;
  if (showPropertyList.value) {
    selectedProperty.value = null;
    updateFilteredProperties();
  }
};

const handleClickOutside = (event) => {
  // Solo cerrar si el panel está abierto
  if (!showPropertyList.value) return;
  
  // Verificar si el click fue fuera del panel y fuera del botón toggle
  const isClickInsidePanel = propertyListPanel.value && propertyListPanel.value.contains(event.target);
  const isClickOnToggleButton = toggleButton.value && toggleButton.value.contains(event.target);
  
  // Si el click fue fuera del panel y no fue en el botón toggle, cerrar el panel
  if (!isClickInsidePanel && !isClickOnToggleButton) {
    showPropertyList.value = false;
  }
};

const selectPropertyFromList = (property) => {
  selectedProperty.value = property;
  // Opcional: Centrar el mapa en la propiedad seleccionada
  if (map) {
    map.flyTo({
      center: [property.lng, property.lat],
      zoom: 15
    });
  }
};

const sortedProperties = computed(() => {
  const properties = [...filteredProperties.value];
  
  return properties.sort((a, b) => {
    const priceA = parseInt(a.price.replace(/\./g, ''));
    const priceB = parseInt(b.price.replace(/\./g, ''));
    const priceM2A = priceA / a.total_surface;
    const priceM2B = priceB / b.total_surface;
    
    switch (sortBy.value) {
      case 'price-asc':
        return priceA - priceB;
      case 'price-desc':
        return priceB - priceA;
      case 'price-m2-asc':
        return priceM2A - priceM2B;
      case 'price-m2-desc':
        return priceM2B - priceM2A;
      case 'size-asc':
        return a.total_surface - b.total_surface;
      case 'size-desc':
        return b.total_surface - a.total_surface;
      default:
        return 0; // Relevancia (sin ordenar o orden original)
    }
  });
});

const updateFilteredProperties = () => {
  // Por ahora, mostramos todas las propiedades
  // En una implementación real, aquí filtrarías las propiedades basadas en el área dibujada
  filteredProperties.value = [...properties.value];
};

const toggleFavorite = (property) => {
  const id = property.id.toString();
  if (favorites.value.has(id)) {
    favorites.value.delete(id);
  } else {
    favorites.value.add(id);
  }
  // Aquí podrías guardar los favoritos en localStorage
  // localStorage.setItem('favorites', JSON.stringify(Array.from(favorites.value)));
};

const isFavorite = (property) => {
  return favorites.value.has(property.id.toString());
};

// Actualizar propiedades filtradas cuando se dibuja un área
watch(shapeDrawn, (newVal) => {
  if (newVal && showPropertyList.value) {
    updateFilteredProperties();
  }
});

function showPropertyCard(property) {
  selectedProperty.value = property;
  viewedProperties.value.add(property.id);
  // Calcular posición del card
  const pixel = map.project([property.lng, property.lat]);
  // Obtener dimensiones del mapa y del card
  const mapRect = mapContainer.value.getBoundingClientRect();
  const cardWidth = 310;
  const cardHeight = 282 + 18; // 18px de la flecha
  // Por defecto, arriba de la burbuja
  let x = pixel.x - cardWidth / 2;
  let y = pixel.y - cardHeight;
  let placement = 'top';
  // Si se sale por arriba, mostrar abajo
  if (y < 0) {
    y = pixel.y + 24; // 24px para dejar espacio a la burbuja
    placement = 'bottom';
  }
  // Si se sale por la izquierda
  if (x < 0) x = 8;
  // Si se sale por la derecha
  if (x + cardWidth > mapRect.width) x = mapRect.width - cardWidth - 8;
  cardPosition.value = { x, y };
  cardPlacement.value = placement;
}
</script>

<style>
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
  position: relative;
  background-color: #EF4444;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  cursor: pointer;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
}

.price-bubble {
  position: relative;
  cursor: pointer;
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
  top: -18px; /* Aún más arriba */
  left: 50%;
  transform: translateX(-45px);
}

.bubble-badge-external.tour {
  top: -18px; /* Misma altura que NEW para consistencia */
  left: 50%;
  transform: translateX(5px); /* Desplazamiento reducido para centrarla más */
}

.price-bubble.selected .price-bubble-container {
  background-color: #333;
}
.price-bubble.selected .price-bubble-container::after {
  border-top-color: #333;
}

.price-bubble.selected::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 12px;
  transform: translateX(-50%);
  width: 90%;
  padding-bottom: 45%;
  height: 0;
  border-radius: 16px;
  background-color: #333;
  animation: sonar-wave 1.5s infinite ease-out;
  z-index: -1;
}

@keyframes sonar-wave {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}

.marker-dot.viewed, .price-bubble.viewed .price-bubble-container {
  background-color: #38e8ff !important; /* Turquesa claro */
  border-color: #fff !important; /* Borde blanco */
  border-width: 2px !important;
}
.price-bubble.viewed .price-bubble-container {
  color: #222 !important;
}
</style>
