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
              placeholder="Email"
              :disabled="isLoading"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Contraseña</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Contraseña"
              :disabled="isLoading"
            />
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

        <div>
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
  form.value.email = 'bruno@bnicolini.com'
  form.value.password = 'test123456' // Contraseña de prueba
}
</script>
