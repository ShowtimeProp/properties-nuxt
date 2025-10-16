import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRuntimeConfig, useSupabaseUser } from '#imports'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref<any[]>([])
  const user = useSupabaseUser()
  const config = useRuntimeConfig()
  const apiBaseUrl: string = (config?.public as any)?.apiBaseUrl || ''

  // Convertido a un método simple para mayor fiabilidad
  function isFavorite(propertyId: string | number): boolean {
    if (!propertyId) return false;
    // Usamos '==' para comparar sin importar el tipo (string vs number)
    return favorites.value.some(p => p.id == propertyId)
  }

  const favoriteIds = computed(() => {
    return favorites.value.map(p => p.id)
  })

  async function loadFavoritesFromBackend() {
    try {
      if (!user.value?.id || !apiBaseUrl) return
      const res = await fetch(`${apiBaseUrl}/favorites/${user.value.id}`)
      if (!res.ok) return
      const data = await res.json()
      const list = Array.isArray(data?.favorites) ? data.favorites : []
      // Normalizamos a objetos { id: property_id }
      const normalized = list.map((f: any) => ({ id: f.property_id }))
      favorites.value = normalized
    } catch (e) {
      console.error('Error cargando favoritos del backend', e)
    }
  }

  async function toggleFavorite(property: any) {
    if (!property || !property.id) return
    
    const index = favorites.value.findIndex(p => p.id == property.id)
    if (index === -1) {
      favorites.value.push(property)
      // Persistir en backend
      try {
        if (user.value?.id && apiBaseUrl) {
          await fetch(`${apiBaseUrl}/favorites/${user.value.id}/${property.id}`, { method: 'POST' })
        }
      } catch (e) {
        // Silenciar error para no afectar UX; el dashboard mostrará lo disponible
        console.error('Error agregando favorito en backend', e)
      }
    } else {
      favorites.value.splice(index, 1)
      // Eliminar en backend
      try {
        if (user.value?.id && apiBaseUrl) {
          await fetch(`${apiBaseUrl}/favorites/${user.value.id}/${property.id}`, { method: 'DELETE' })
        }
      } catch (e) {
        console.error('Error eliminando favorito en backend', e)
      }
    }
  }

  return {
    favorites,
    isFavorite, // Ahora es un método
    favoriteIds,
    toggleFavorite,
    loadFavoritesFromBackend,
  }
}, {
  persist: true
})