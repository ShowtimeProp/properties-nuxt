<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">
            Dashboard CRM
          </h1>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500">
              Bienvenida, {{ realtorProfile?.name || 'Realtor' }}
            </span>
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">👥</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Total Clientes
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ isLoading ? '...' : metrics.totalClients }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">🏠</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Propiedades
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ isLoading ? '...' : metrics.totalProperties }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">📅</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Visitas Programadas
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ isLoading ? '...' : metrics.scheduledVisits }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">💰</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Ventas del Mes
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ isLoading ? '...' : metrics.monthlySales }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Welcome Message -->
        <div class="bg-white shadow rounded-lg p-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">
            ¡Bienvenida al Dashboard CRM!
          </h2>
          <p class="text-gray-600 mb-4">
            Hola {{ realtorProfile?.name || 'Bianca' }}, has iniciado sesión exitosamente.
          </p>
          <div class="bg-green-50 border border-green-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <span class="text-green-400 text-xl">✅</span>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-green-800">
                  Autenticación Exitosa
                </h3>
                <div class="mt-2 text-sm text-green-700">
                  <p>Usuario: {{ realtorProfile?.email || 'biancannicolini@gmail.com' }}</p>
                  <p>Tenant ID: {{ realtorProfile?.tenant_id || 'N/A' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const { realtorProfile, logoutRealtor } = useRealtorAuth()

// Estado reactivo para las métricas
const metrics = ref({
  totalClients: 0,
  totalProperties: 0,
  scheduledVisits: 0,
  monthlySales: 0
})

const isLoading = ref(true)

const logout = async () => {
  await logoutRealtor()
}

// Función para obtener métricas del backend
const fetchMetrics = async () => {
  try {
    isLoading.value = true
    
    if (!realtorProfile.value?.id) {
      console.log('No hay realtor profile disponible')
      return
    }

    const realtorId = realtorProfile.value.id
    const backendUrl = 'https://api.bnicolini.showtimeprop.com'
    
    console.log('Obteniendo métricas para realtor:', realtorId)
    
    // Obtener métricas del dashboard
    const metricsResponse = await fetch(`${backendUrl}/dashboard/metrics/${realtorId}`)
    if (metricsResponse.ok) {
      const metricsData = await metricsResponse.json()
      console.log('Métricas recibidas:', metricsData)
      
      // Mapear métricas del backend al formato del dashboard
      metrics.value = {
        totalClients: metricsData.metrics?.total_leads || 0,
        totalProperties: 0, // Esto necesitaría un endpoint específico
        scheduledVisits: 0, // Esto necesitaría un endpoint específico  
        monthlySales: metricsData.metrics?.revenue || 0
      }
    } else {
      console.error('Error obteniendo métricas:', metricsResponse.status)
    }
    
    // Obtener datos adicionales
    await fetchAdditionalData(realtorId)
    
  } catch (error) {
    console.error('Error fetching metrics:', error)
  } finally {
    isLoading.value = false
  }
}

// Función para obtener datos adicionales
const fetchAdditionalData = async (realtorId) => {
  try {
    const backendUrl = 'https://api.bnicolini.showtimeprop.com'
    
    // Obtener clientes del tenant
    const clientsResponse = await fetch(`${backendUrl}/favorites/tenant/${realtorProfile.value.tenant_id}/clients`)
    if (clientsResponse.ok) {
      const clientsData = await clientsResponse.json()
      metrics.value.totalClients = clientsData.clients?.length || 0
      console.log('Clientes encontrados:', metrics.value.totalClients)
    }
    
    // Obtener visitas programadas
    const visitsResponse = await fetch(`${backendUrl}/visits/tenant/${realtorProfile.value.tenant_id}/upcoming`)
    if (visitsResponse.ok) {
      const visitsData = await visitsResponse.json()
      metrics.value.scheduledVisits = visitsData.visits?.length || 0
      console.log('Visitas programadas:', metrics.value.scheduledVisits)
    }
    
  } catch (error) {
    console.error('Error fetching additional data:', error)
  }
}

// Cargar métricas al montar el componente
onMounted(async () => {
  // Esperar un poco para que realtorProfile se cargue
  setTimeout(() => {
    fetchMetrics()
  }, 1000)
})

// Meta para evitar indexación
definePageMeta({
  layout: false
})
</script>