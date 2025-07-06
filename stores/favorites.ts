import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<any[]>([]) // Array de objetos de propiedad completos

  // Getter para comprobar si una propiedad es favorita por su ID
  const isFavorite = computed(() => {
    return (propertyId: string) => favorites.value.some(p => p.id === propertyId)
  })

  // Getter que devuelve el array de IDs de favoritos
  const favoriteIds = computed(() => {
    return favorites.value.map(p => p.id)
  })

  // Acción para añadir/quitar un favorito
  function toggleFavorite(property: any) {
    if (!property || !property.id) return
    
    const index = favorites.value.findIndex(p => p.id === property.id)
    if (index === -1) {
      favorites.value.push(property) // Añadir
    } else {
      favorites.value.splice(index, 1) // Quitar
    }
  }

  return {
    favorites,
    isFavorite,
    favoriteIds,
    toggleFavorite,
  }
}, {
  persist: true
})