// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // updated to suppress Vite warning
  compatibilityDate: '2025-06-28',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/google-fonts',
    '@nuxtjs/supabase'
  ],

  supabase: {
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_KEY,
    // Options
    redirectOptions: {
      login: '/',
      callback: '/confirm',
      exclude: [],
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
  ]
})