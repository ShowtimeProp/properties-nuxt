// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // updated to suppress Vite warning
  compatibilityDate: '2025-06-28',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@pinia-plugin-persistedstate/nuxt',
    '@nuxtjs/google-fonts',
    '@nuxtjs/supabase',
    '@vueuse/nuxt',
  ],

  supabase: {
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_KEY,
    // Options
    redirectOptions: {
      login: '/',
      callback: '/confirm',
      exclude: [],
    },
    redirect: false 
  },
  
  runtimeConfig: {
    // Variables privadas (solo servidor)
    livekitApiKey: process.env.LIVEKIT_API_KEY,
    livekitApiSecret: process.env.LIVEKIT_API_SECRET,
    livekitUrl: process.env.LIVEKIT_URL || 'wss://timbre-ai-uy9i2xcb.livekit.cloud',
    // Variables públicas (cliente)
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || ''
    }
  },

  googleFonts: {
    families: {
      'Open Sans': [400, 700]
    }
  },

  css: [
    'swiper/css',
    'swiper/css/pagination',
    'swiper/css/navigation'
  ],

  build: {
    transpile: ['lucide-vue-next', 'vue-toastification']
  },
  
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            // Separar librerías grandes en chunks independientes
            'maplibre': ['maplibre-gl'],
            'swiper': ['swiper'],
            'supabase': ['@supabase/supabase-js'],
            'vue-vendor': ['vue', '@vue/runtime-core'],
          }
        }
      },
      chunkSizeWarningLimit: 1000 // Aumentar límite a 1MB
    }
  },
  ssr: false
})