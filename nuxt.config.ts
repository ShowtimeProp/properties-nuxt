// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // updated to suppress Vite warning
  compatibilityDate: '2025-06-28',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/google-fonts'
  ],

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