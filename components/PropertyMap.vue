<template>
  <div class="absolute top-0 left-0 w-full h-full" ref="mapContainer"></div>
  <Transition name="property-card">
    <PropertyCard 
      v-if="selectedProperty" 
      :property="selectedProperty" 
      @close="selectedProperty = null"
      @open-modal="isModalOpen = true"
      class="absolute left-4 top-1/2 -translate-y-1/2 z-30"
    />
  </Transition>

  <!-- Modal de Detalles -->
  <Transition name="fade">
    <PropertyModal 
      v-if="isModalOpen && selectedProperty"
      :property="selectedProperty"
      @close="isModalOpen = false"
    />
  </Transition>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import PropertyCard from './PropertyCard.vue';
import PropertyModal from './PropertyModal.vue';

const mapContainer = ref(null)
let map = null // No reactivo, para evitar problemas con el proxy de Vue
const selectedProperty = ref(null);
const isModalOpen = ref(false);
const markerElements = ref({});
const ZOOM_THRESHOLD = 14.0;

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

    if (isSelected) {
      markerEl.classList.add('selected');
    }
  }
};
const properties = ref([
  { id: 1, lng: -57.54, lat: -38.01, title: 'Departamento céntrico', price: '150.000', expenses: '12.000', address: 'Corrientes 2345', size: 75, rooms: 3, bathrooms: 2, bedrooms: 2, hasVirtualTour: true, virtualTourUrl: 'https://s3.showtimeprop.com/vt360/remax/bianca_nicolini/santiago/index.htm', description: 'Moderno departamento de 3 ambientes en el corazón de la ciudad. Cuenta con amplios ventanales que ofrecen una excelente iluminación natural y vistas panorámicas. Cocina integrada, dos baños completos y balcón. Ideal para quienes buscan confort y una ubicación privilegiada.', images: ['https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=360&h=180&fit=crop'] },
  { id: 2, lng: -57.555, lat: -38.005, title: 'Casa con vista al mar', price: '320.000', expenses: '25.000', address: 'Bv. Marítimo 1100', size: 120, rooms: 4, bathrooms: 3, bedrooms: 3, hasVirtualTour: false, virtualTourUrl: null, description: 'Espectacular casa frente al mar con 3 dormitorios, amplio jardín y piscina. Diseño moderno y acabados de lujo. Una oportunidad única para vivir con el sonido de las olas.', images: ['https://images.unsplash.com/photo-1580587771525-78b9dba3b914?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1572120360610-d971b9d7767c?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=360&h=180&fit=crop'] },
  { id: 3, lng: -57.53, lat: -37.99, title: 'Chalet en zona residencial', price: '210.000', expenses: '18.000', address: 'Formosa 850', size: 90, rooms: 3, bathrooms: 2, bedrooms: 2, hasVirtualTour: false, images: ['https://images.unsplash.com/photo-1570129477492-45c003edd2be?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1605276374104-5de67d60924f?q=80&w=360&h=180&fit=crop'] },
  { id: 4, lng: -57.56, lat: -38.02, title: 'Loft moderno', price: '185.000', expenses: '15.000', address: 'Alvarado 3120', size: 65, rooms: 2, bathrooms: 1, bedrooms: 1, hasVirtualTour: false, isNew: true, virtualTourUrl: null, description: 'Loft de diseño con concepto abierto, ideal para solteros o parejas. Totalmente reciclado con materiales de primera calidad.', images: ['https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1598228723793-52759bba239c?q=80&w=360&h=180&fit=crop', 'https://images.unsplash.com/photo-1540518614846-7eded433c457?q=80&w=360&h=180&fit=crop'] }
]);

onMounted(async () => {
  // Importar dinámicamente solo en el cliente
  const maplibregl = await import('maplibre-gl');
  await import('maplibre-gl/dist/maplibre-gl.css');

  if (mapContainer.value) {
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: `https://api.maptiler.com/maps/streets/style.json?key=RqptbBn3gxBTDHGJ4a3O`,
      center: [-57.55, -38.00], // Coordenadas de Mar del Plata
      zoom: 13
    });

    map.on('load', () => {
      properties.value.forEach(property => {
        const el = document.createElement('div');
        el.className = 'marker';

        el.addEventListener('click', () => {
          selectedProperty.value = property;
        });

        markerElements.value[property.id] = el;

        new maplibregl.Marker({ element: el })
          .setLngLat([property.lng, property.lat])
          .addTo(map);
      });
    });

    // Evento para cerrar la card al hacer clic en el mapa
    map.on('click', (e) => {
      // Si el clic fue directamente sobre el canvas del mapa (y no sobre un marcador HTML),
      // entonces cerramos la tarjeta de propiedad.
      if (e.originalEvent.target === map.getCanvas()) {
        selectedProperty.value = null;
      }
    });

    updateMarkersForZoom();
    map.on('zoom', updateMarkersForZoom);

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
</script>

<style>
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
</style>
