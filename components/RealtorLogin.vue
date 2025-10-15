<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
          <span class="text-2xl">🏠</span>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Acceso para Realtors
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Ingresa tus credenciales para acceder al dashboard
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              style="min-width: 100%; max-width: 100%; width: 100%;"
              placeholder="Email"
              :disabled="isLoading"
            />
          </div>
          <div class="relative">
            <label for="password" class="sr-only">Contraseña</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              style="min-width: 100%; max-width: 100%; width: 100%;"
              placeholder="Contraseña"
              :disabled="isLoading"
            />
            <button
              type="button"
              @click="togglePasswordVisibility"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              :disabled="isLoading"
            >
              <span v-if="showPassword" class="text-lg">👁️</span>
              <span v-else class="text-lg">👁️‍🗨️</span>
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error de autenticación</h3>
              <div class="mt-2 text-sm text-red-700">
                {{ error }}
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            </span>
            <span v-else class="absolute left-0 inset-y-0 flex items-center pl-3">
              <span class="text-lg">🔑</span>
            </span>
            {{ isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
          </button>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-gray-50 text-gray-500">O continúa con</span>
            </div>
          </div>

          <!-- Google Login Button -->
          <button
            type="button"
            @click="loginWithGoogle"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continuar con Google
          </button>
        </div>

        <div class="text-center space-y-2">
          <button
            type="button"
            @click="goToMainSite"
            class="text-blue-600 hover:text-blue-500 text-sm"
          >
            ← Volver al sitio principal
          </button>
          
          <!-- Debug: Auto-fill test data -->
          <div class="text-xs text-gray-500">
            <button
              type="button"
              @click="fillTestData"
              class="text-gray-400 hover:text-gray-600 underline"
            >
              Usar datos de prueba
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const { loginAsRealtor, isLoading, error } = useRealtorAuth()

const form = ref({
  email: '',
  password: ''
})

const showPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  try {
    console.log('Intentando login con:', form.value.email)
    await loginAsRealtor(form.value.email, form.value.password)
    console.log('Login exitoso, navegando...')
    // Navigation will be handled by the composable
  } catch (err) {
    // Error is handled by the composable
    console.error('Login error en componente:', err)
  }
}

const goToMainSite = () => {
  navigateTo('/')
}

const fillTestData = () => {
  form.value.email = 'biancannicolini@gmail.com'
  form.value.password = 'test123456' // Contraseña de prueba
}

const loginWithGoogle = async () => {
  try {
    console.log('Iniciando login con Google...')
    
    const { loginWithGoogle: googleLogin } = useRealtorAuth()
    await googleLogin()
    
    console.log('Login con Google exitoso')
  } catch (err) {
    console.error('Error en login con Google:', err)
  }
}
</script>

<style scoped>
/* Fix para prevenir deformación de campos en carga inicial */
input[type="email"],
input[type="password"],
input[type="text"] {
  min-width: 100% !important;
  max-width: 100% !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Asegurar que el contenedor mantenga sus dimensiones */
.space-y-6 > div {
  width: 100%;
}

.rounded-md {
  width: 100%;
}
</style>
