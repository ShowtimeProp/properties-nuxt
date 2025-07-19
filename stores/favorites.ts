import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<any[]>([])

  // Convertido a un método simple para mayor fiabilidad
  function isFavorite(propertyId: string | number): boolean {
    if (!propertyId) return false;
    // Usamos '==' para comparar sin importar el tipo (string vs number)
    return favorites.value.some(p => p.id == propertyId)
  }

  const favoriteIds = computed(() => {
    return favorites.value.map(p => p.id)
  })

  function toggleFavorite(property: any) {
    if (!property || !property.id) return
    
    const index = favorites.value.findIndex(p => p.id == property.id)
    if (index === -1) {
      favorites.value.push(property)
    } else {
      favorites.value.splice(index, 1)
    }
  }

  return {
    favorites,
    isFavorite, // Ahora es un método
    favoriteIds,
    toggleFavorite,
  }
}, {
  persist: true
})