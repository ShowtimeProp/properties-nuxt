<template>
  <div ref="mapWrapper" class="w-full h-full">
    <div ref="mapContainer" class="w-full h-full"></div>
    
    <!-- Tooltip flotante para modo dibujo -->
    <div v-if="isDrawing" :style="{ left: `${Math.min(mouse.x + 18, windowWidth - 220)}px`, top: `${Math.min(mouse.y + 18, windowHeight - 48)}px` }" class="fixed z-50 pointer-events-none px-3 py-1 rounded-lg shadow-lg text-xs font-semibold bg-indigo-600 text-white border border-indigo-300 animate-pulse" style="user-select:none;">
      🖱️ DOBLE CLICK = Terminar Dibujo
    </div>
    
    <!-- Botón Ver Listado -->
    <button 
      ref="toggleButton"
      @click="togglePropertyList"
      class="absolute top-24 right-24 z-20 flex items-center gap-2 px-4 py-2 animated-gradient-bg text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <span>Ver Listado</span>
    </button>
    
    <!-- Panel de Listado de Propiedades -->
    <div 
      ref="propertyListPanel"
      class="fixed top-0 right-0 bg-white shadow-xl z-30 transform transition-transform duration-300 ease-in-out flex flex-col pt-[110px] w-full md:w-[450px] lg:w-[40%] max-w-[750px]"
      style="height: 100vh; box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1)"
      :class="{ 'translate-x-0': showPropertyList, 'translate-x-full': !showPropertyList }"
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

    <!-- Controles de Dibujo -->
    <div class="absolute bottom-20 left-1/2 -translate-x-1/2 z-10 flex flex-row items-center gap-3">
      <!-- Botón de Dibujo Principal -->
      <div class="flex items-center gap-2">
        <button v-if="!isTridentOpen && !shapeDrawn" @click="toggleTrident" class="flex items-center gap-2 px-4 py-2 animated-gradient-bg text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          <span>Dibujar área</span>
        </button>
        <button v-if="shapeDrawn" @click="deleteShape" class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-500 via-cyan-400 to-indigo-500 text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Eliminar área</span>
        </button>
        <button class="flex items-center gap-2 px-4 py-2 animated-gradient-bg text-white font-bold rounded-lg shadow-lg hover:from-indigo-400 hover:to-cyan-300 transition-colors">
          <span>Buscar en esta zona</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h5M4 12a8 8 0 0114.24-5.236M20 20v-5h-5M20 12a8 8 0 01-14.24 5.236" />
          </svg>
        </button>
        <div v-if="isTridentOpen && !shapeDrawn" class="text-xs text-gray-600 bg-white/90 px-3 py-1 rounded-lg shadow">
          <p class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Haz clic en el mapa para dibujar. Haz clic derecho para terminar.
          </p>
        </div>
      </div>
    </div>
  </div>

  <Transition name="property-card">
    <div v-if="selectedProperty && (!isModalOpen || !openedFromSlide)"
      :style="{ position: 'absolute', left: `${cardPosition.x}px`, top: `${cardPosition.y}px`, zIndex: 30, width: '310px' }"
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
      @close="handleCloseModal"
    />
  </Transition>

  <!-- Modal de login -->
  <LoginModal :show="showLoginModal" @close="showLoginModal = false" />

</template>

<script setup>
import PropertyCard from './PropertyCard.vue';
import { onMounted, onUnmounted, ref, watch, nextTick, computed } from 'vue';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import PropertyModal from './PropertyModal.vue';
import LoginModal from './LoginModal.vue';
import { useFavoritesStore } from '~/stores/favorites';
import { useLoginModalStore } from '~/stores/loginModal';
import Toast from 'vue-toastification';
import { useSupabaseUser } from '#imports';
import { useSearchStore } from '~/stores/search';

const { useToast } = Toast;
const searchStore = useSearchStore();
const config = useRuntimeConfig();

// --- API Endpoint Configuration ---
const apiBaseUrl = computed(() => {
  if (process.server) {
    // En el servidor, siempre usamos la URL base configurada (para SSR, etc.)
    return config.public.apiBaseUrl;
  }
  // En el cliente, determinamos la URL dinámicamente.
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Para desarrollo local, usamos la URL del .env
    return config.public.apiBaseUrl;
  }
  // Para producción, construimos la URL a partir del subdominio.
  // Asumimos que la API está en fapi.dominio.com
  const parts = hostname.split('.');
  if (parts.length > 2) {
    // bnicolini.showtimeprop.com -> fapi.showtimeprop.com
    return `https://fapi.${parts.slice(-2).join('.')}`;
  }
  // showtimeprop.com -> fapi.showtimeprop.com
  return `https://fapi.${hostname}`;
});

// --- BÚSQUEDA SEMÁNTICA ---
// Observa cambios en la consulta de búsqueda del store
watch(() => searchStore.searchQuery, (newQuery) => {
  if (newQuery) {
    performSemanticSearch(newQuery);
  } else {
    // Si la búsqueda se limpia, vuelve a cargar todas las propiedades (opcional)
    // fetchAllProperties(); // Necesitaríamos refactorizar para tener esta función
  }
});

async function performSemanticSearch(query) {
  try {
    const searchUrl = new URL('/search', apiBaseUrl.value).href;
    const results = await $fetch(searchUrl, {
      method: 'POST',
      body: {
        query: query,
        top_k: 50 // Traer hasta 50 resultados
      }
    });

    // Actualiza el store con los resultados
    searchStore.setSearchResults(results);

    // Actualiza los marcadores en el mapa
    // Primero, transformamos los resultados para que tengan el formato correcto
    const formattedResults = results.map(property => ({
      ...property,
      lat: parseFloat(property.latitude),
      lng: parseFloat(property.longitude),
      images: property.images_array || []
    }));
    
    properties.value = formattedResults;

  } catch (err) {
    console.error("Error en la búsqueda semántica:", err);
    toast.error("Hubo un error al realizar la búsqueda.");
    searchStore.clearSearch(); // Limpia el estado de búsqueda en caso de error
  }
}


// --- LLAMADA INICIAL A LA API ---
const propertiesApiUrl = computed(() => {
  if (!apiBaseUrl.value) return '';
  return new URL('/properties/all', apiBaseUrl.value).href;
});

const { data: properties, pending, error } = await useFetch(propertiesApiUrl, {
  lazy: true, // Carga los datos en segundo plano sin bloquear la navegación
  server: false, // Asegura que la llamada se haga solo en el lado del cliente
  transform: (data) => {
    if (!Array.isArray(data)) return []; // Devuelve un array vacío si los datos no son los esperados
    // Mapea los datos para normalizar los campos de coordenadas
    return data
      .filter(p => p && p.latitude && p.longitude) // FILTRA propiedades sin coordenadas
      .map(property => ({
        ...property,
        lat: parseFloat(property.latitude),  // Usa 'latitude' y lo convierte a número
        lng: parseFloat(property.longitude), // Usa 'longitude' y lo convierte a número
        images: property.images_array || [] // AÑADIDO: Mapea images_array a images
      }));
  },
  // Valor por defecto mientras se cargan los datos
  default: () => []
});

watch(error, (newError) => {
  if (newError) {
    console.error('Error fetching properties:', newError);
    // Opcional: mostrar una notificación al usuario
    // toast.error('No se pudieron cargar las propiedades. Intente de nuevo más tarde.');
  }
});
// --- FIN DE LA NUEVA LLAMADA A LA API ---


const supabase = useNuxtApp().$supabase
const user = useSupabaseUser()
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
const mapWrapper = ref(null)
const navHeight = ref(81)

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
  windowWidth = window.innerWidth;
  windowHeight = window.innerHeight;
  nextTick(() => {
    const nav = document.querySelector('nav.fixed');
    if (nav) {
      navHeight.value = nav.offsetHeight;
    }
  });
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
const propertyModalRef = ref(null);
const openedFromSlide = ref(false);
const mouse = ref({ x: 0, y: 0 });
const isDrawing = ref(false);
let windowWidth = 0;
let windowHeight = 0;
const isLoggedIn = computed(() => !!user.value)
const showLoginModal = ref(false)

const favoritesStore = useFavoritesStore();
const loginModal = useLoginModalStore();
const toast = useToast();

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
  // ¡LA SOLUCIÓN! Si no hay precio, no falles, solo devuelve un string vacío.
  if (!priceString) {
    return '';
  }
  // Añadimos String() para más seguridad, por si el precio llega como número.
  const num = parseInt(String(priceString).replace(/\./g, ''), 10);
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
  if (!map || !properties.value) return;
  const currentZoom = map.getZoom();
  const isBubbleView = currentZoom > ZOOM_THRESHOLD;

  for (const prop of properties.value) {
    const markerEl = markerElements.value[prop.id];
    if (!markerEl) continue;

    const dot = markerEl.querySelector('.marker-dot');
    const bubble = markerEl.querySelector('.price-bubble');
    if (!dot || !bubble) continue;

    if (isBubbleView) {
      dot.style.opacity = '0';
      dot.style.pointerEvents = 'none';
      bubble.style.opacity = '1';
      bubble.style.pointerEvents = 'auto';
    } else {
      dot.style.opacity = '1';
      dot.style.pointerEvents = 'auto';
      bubble.style.opacity = '0';
      bubble.style.pointerEvents = 'none';
    }

    const isSelected = selectedProperty.value?.id === prop.id;
    // La clase 'selected' ahora se maneja directamente en el contenedor
    if (isSelected) {
      markerEl.classList.add('selected');
    } else {
      markerEl.classList.remove('selected');
    }

    if (viewedProperties.value.has(prop.id)) {
      markerEl.classList.add('viewed');
    } else {
      markerEl.classList.remove('viewed');
    }
  }
};


/*
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
*/

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
    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');

    const addMarkersToMap = () => {
      if (!map || !properties.value) return;

      properties.value.forEach(property => {
        // Este chequeo es crucial
        if (!property || isNaN(property.lat) || isNaN(property.lng)) {
          console.warn('Skipping property with invalid data:', property);
          return;
        }

        const el = document.createElement('div');
        el.className = 'marker-container';

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
          showPropertyCard(property);
        });

        markerElements.value[property.id] = el;

        new maplibregl.Marker({ element: el, anchor: 'bottom' }) // ANCLAJE INFERIOR
          .setLngLat([property.lng, property.lat])
          .addTo(map);
      });
      updateMarkersForZoom();
    };


    map.on('load', () => {
      addMarkersToMap();

      // Observar cambios en 'properties' para volver a añadir los marcadores si llegan tarde
      watch(properties, (newProperties) => {
        if (newProperties && newProperties.length > 0) {
          // Limpiar marcadores existentes antes de añadir nuevos
          Object.values(markerElements.value).forEach(el => el.remove());
          markerElements.value = {};
          addMarkersToMap();
        }
      }, { deep: true });

      // ACTUALIZA LA LISTA CUANDO EL MAPA SE MUEVE
      map.on('moveend', updateFilteredProperties);
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
            'line-color': '#6366f1',
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
            'line-color': '#6366f1',
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
            'circle-color': '#6366f1',
            'circle-stroke-color': '#fff',
            'circle-stroke-width': 2
          }
        }
      ]
    });
    map.addControl(draw, 'bottom-right');

    // Detectar si está en modo dibujo para mostrar el tooltip
    map.on('draw.modechange', (e) => {
      isDrawing.value = e.mode === 'draw_polygon';
    });
    map.on('draw.create', () => {
      isDrawing.value = false;
      shapeDrawn.value = true;
    });
    map.on('draw.delete', () => {
      isDrawing.value = false;
      shapeDrawn.value = false;
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
  if (shapeDrawn.value) return; // No permitir otro dibujo si ya hay uno
  isTridentOpen.value = true;
  nextTick(() => {
    startDrawing();
    isDrawing.value = true;
  });
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
  console.log('Botón "Ver Listado" clickeado. Estado actual de showPropertyList:', showPropertyList.value);
  showPropertyList.value = !showPropertyList.value;
  console.log('Nuevo estado de showPropertyList:', showPropertyList.value);
  if (showPropertyList.value) {
    selectedProperty.value = null;
    // Llama al filtro la primera vez que se abre el panel
    updateFilteredProperties();
  }
};

const handleClickOutside = (event) => {
  if (!showPropertyList.value) return;
  const isClickInsidePanel = propertyListPanel.value && propertyListPanel.value.contains(event.target);
  const isClickOnToggleButton = toggleButton.value && toggleButton.value.contains(event.target);
  const isClickInsideModal = propertyModalRef.value && propertyModalRef.value.contains(event.target);
  if (!isClickInsidePanel && !isClickOnToggleButton && !isClickInsideModal) {
    showPropertyList.value = false;
    // Quitar sonar activo de todos los marcadores
    Object.values(markerElements.value).forEach(el => {
      el.classList.remove('sonar-active');
    });
  }
};

const openModalFromSlide = (property) => {
  // Activa el sonar y centra el mapa para una mejor UX
  activateSonarFromSlide(property);
  
  // Abre el modal de detalles
  selectedProperty.value = property;
  isModalOpen.value = true;
  openedFromSlide.value = true;
};

const activateSonarFromSlide = (property) => {
  // Quitar sonar activo de todos los marcadores
  Object.values(markerElements.value).forEach(el => {
    el.classList.remove('sonar-active');
  });
  // Centrar el mapa en la propiedad
  if (map) {
    map.flyTo({
      center: [property.lng, property.lat],
      zoom: 15
    });
  }
  // Activar el efecto sonar en el marcador correspondiente
  const markerEl = markerElements.value[property.id];
  if (markerEl) {
    markerEl.classList.add('sonar-active');
  }
};

const selectPropertyFromList = (property) => {
  if (isModalOpen.value && openedFromSlide.value) return;
  // Quitar sonar activo de todos los marcadores
  Object.values(markerElements.value).forEach(el => {
    el.classList.remove('sonar-active');
  });
  selectedProperty.value = property;
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
    // Robust price parsing
    const priceA = a.price ? parseInt(String(a.price).replace(/\./g, ''), 10) : 0;
    const priceB = b.price ? parseInt(String(b.price).replace(/\./g, ''), 10) : 0;
    
    // Robust surface data for price/m2 calculation
    const surfaceA = a.total_surface > 0 ? a.total_surface : 1;
    const surfaceB = b.total_surface > 0 ? b.total_surface : 1;

    const priceM2A = priceA / surfaceA;
    const priceM2B = priceB / surfaceB;
    
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
  if (!map || !properties.value) {
    filteredProperties.value = [];
    return;
  }
  
  // Obtiene los límites geográficos de la vista actual del mapa
  const bounds = map.getBounds();
  
  // Filtra solo las propiedades que están dentro de esos límites
  filteredProperties.value = properties.value.filter(p => {
    // Asegurarse de que lat y lng son números válidos antes de comprobar
    if (typeof p.lng === 'number' && typeof p.lat === 'number') {
      return bounds.contains([p.lng, p.lat]);
    }
    return false;
  });
};

const toggleFavorite = (property) => {
  if (!user.value) {
    loginModal.open();
    toast.info("Debes iniciar sesión para guardar favoritos");
    return;
  }
  if (!property || !property.id) {
    toast.error('No se puede agregar a favoritos: propiedad inválida.');
    return;
  }

  const wasFavorite = favoritesStore.isFavorite(property.id);
  
  favoritesStore.toggleFavorite(property);
  
  const message = !wasFavorite
    ? `${property.title || 'Propiedad'} agregada a favoritos!`
    : `${property.title || 'Propiedad'} eliminada de favoritos.`;
  
  toast.success(message, {
    icon: !wasFavorite ? 'fas fa-heart text-red-500' : 'fas fa-trash-alt'
  });
};

const isFavorite = (property) => {
  if (!property || !property.id) return false;
  return favoritesStore.isFavorite(property.id);
};

// Actualizar propiedades filtradas cuando se dibuja un área
watch(shapeDrawn, (newVal) => {
  if (newVal && showPropertyList.value) {
    updateFilteredProperties();
  }
});

function showPropertyCard(property) {
  // Quitar sonar activo de todos los marcadores
  Object.values(markerElements.value).forEach(el => {
    el.classList.remove('sonar-active');
  });
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
  let y = pixel.y - cardHeight + 18; // 18px: la flecha debe apuntar al dot
  let placement = 'top';
  // Offset mínimo para la barra de navegación expandida (120px)
  const minY = 120;
  // Si se sale por arriba, mostrar abajo
  if (y < minY) {
    y = pixel.y + 18; // 18px: la flecha debe apuntar al dot
    placement = 'bottom';
  }
  // Si se sale por la izquierda
  if (x < 0) x = 8;
  // Si se sale por la derecha
  if (x + cardWidth > mapRect.width) x = mapRect.width - cardWidth - 8;
  cardPosition.value = { x, y };
  cardPlacement.value = placement;
}

function handleCloseModal() {
  isModalOpen.value = false;
  if (openedFromSlide.value) {
    selectedProperty.value = null;
  }
  openedFromSlide.value = false;
}

function handleMouseMove(e) {
  mouse.value = { x: e.clientX, y: e.clientY };
}

watch(isDrawing, (val) => {
  if (val) {
    window.addEventListener('mousemove', handleMouseMove);
  } else {
    window.removeEventListener('mousemove', handleMouseMove);
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
