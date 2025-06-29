import { defineStore } from 'pinia'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favorites: [] as string[], // Array de IDs de propiedades favoritas
  }),
  actions: {
    toggleFavorite(propertyId: string) {
      const index = this.favorites.indexOf(propertyId)
      if (index === -1) {
        this.favorites.push(propertyId)
      } else {
        this.favorites.splice(index, 1)
      }
    },
    isFavorite(propertyId: string) {
      return this.favorites.includes(propertyId)
    }
  },
  persist: true // Guarda automáticamente en localStorage
})