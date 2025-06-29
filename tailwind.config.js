module.exports = {
    content: [
      './components/**/*.{vue,js,ts}',
      './layouts/**/*.vue',
      './pages/**/*.vue',
      './app.vue',
    ],
    theme: {
      extend: {
        fontFamily: {
          sans: ['"Open Sans"', 'sans-serif'],
        }
      },
    },
    plugins: [require('daisyui')],
    daisyui: {
      themes: [
        "light",      // Claro
        "dark",       // Oscuro
        "cupcake",    // Colorido pastel
        "bumblebee",  // Amarillo
        "emerald",    // Verde
        "corporate",  // Empresarial
        "synthwave",  // Neon
        "retro",      // Vintage
        "cyberpunk",  // Futurista
        "valentine",  // Rosado
        "halloween",  // Naranja/oscuro
        "garden",     // Verde floral
        "forest",     // Bosque
        "aqua",       // Azul agua
        "lofi",       // Minimalista
        "pastel",     // Pastel
        "fantasy",    // Fantasía
        "wireframe",  // Esquemático
        "black",      // Negro puro
        "luxury",     // Dorado/negro
        "dracula"     // Inspirado en Dracula Theme
      ],
      darkTheme: "dark", // Tema oscuro por defecto
    }
  }