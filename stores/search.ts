import { defineStore } from 'pinia';

export const useSearchStore = defineStore('search', {
  state: () => ({
    // La consulta de búsqueda actual, ej: "casa con piscina"
    searchQuery: null as string | null,
    // Estado para saber si una búsqueda está en curso
    isLoading: false,
    // Array para guardar los resultados de la búsqueda
    searchResults: [] as any[],
  }),
  actions: {
    /**
     * Inicia una nueva búsqueda semántica.
     * @param {string} query - El texto que el usuario quiere buscar.
     */
    setSearchQuery(query: string) {
      this.searchQuery = query;
      this.isLoading = true;
    },
    /**
     * Almacena los resultados obtenidos de la API.
     * @param {any[]} results - El array de propiedades encontradas.
     */
    setSearchResults(results: any[]) {
      this.searchResults = results;
      this.isLoading = false;
    },
    /**
     * Limpia la búsqueda y resetea el estado.
     */
    clearSearch() {
      this.searchQuery = null;
      this.searchResults = [];
      this.isLoading = false;
    },
  },
}); 