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

        <!-- Clientes Section -->
        <div class="bg-white shadow rounded-lg p-6 mb-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">👥 Clientes Activos</h3>
          <div v-if="isLoading" class="text-gray-500">Cargando clientes...</div>
          <div v-else-if="clients.length === 0" class="text-gray-500">No hay clientes registrados aún.</div>
          <div v-else class="space-y-4">
            <div 
              v-for="client in clients" 
              :key="client.client_id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="font-medium text-gray-900">Cliente ID: {{ client.client_id.slice(0, 8) }}...</h4>
                  <p class="text-sm text-gray-500">
                    Primera actividad: {{ new Date(client.first_activity).toLocaleDateString() }}
                  </p>
                </div>
                <div class="text-right">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ client.favorites_count }} favoritos
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Propiedades Favoritas Section -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">🏠 Propiedades Favoritas</h3>
          <div v-if="isLoading" class="text-gray-500">Cargando propiedades favoritas...</div>
          <div v-else-if="favoriteProperties.length === 0" class="text-gray-500">No hay propiedades favoritas aún.</div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="favorite in favoriteProperties" 
              :key="`${favorite.client_id}-${favorite.property_id}`"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="space-y-2">
                <h4 class="font-medium text-gray-900">Propiedad ID: {{ favorite.property_id.slice(0, 8) }}...</h4>
                <p class="text-sm text-gray-500">
                  Cliente: {{ favorite.client_id.slice(0, 8) }}...
                </p>
                <p class="text-sm text-gray-500">
                  Agregado: {{ new Date(favorite.created_at).toLocaleDateString() }}
                </p>
                <div class="flex justify-between items-center">
                  <span class="text-xs text-gray-400">
                    ID: {{ favorite.id.slice(0, 8) }}...
                  </span>
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    ♥ Favorito
                  </span>
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

const clients = ref([])
const favoriteProperties = ref([])
const isLoading = ref(true)

const logout = async () => {
  await logoutRealtor()
}

// Función para obtener métricas del backend
const fetchMetrics = async () => {
  try {
    isLoading.value = true
    
    console.log('🔍 Iniciando fetchMetrics...')
    console.log('realtorProfile.value:', realtorProfile.value)
    
    if (!realtorProfile.value?.id) {
      console.log('❌ No hay realtor profile disponible')
      return
    }

    const realtorId = realtorProfile.value.id
    const tenantId = realtorProfile.value.tenant_id
    const backendUrl = 'https://fapi.showtimeprop.com'
    
    console.log('✅ Datos del realtor:')
    console.log('- realtorId:', realtorId)
    console.log('- tenantId:', tenantId)
    console.log('- backendUrl:', backendUrl)
    
    // Obtener métricas del dashboard
    console.log('📊 Llamando a métricas del dashboard...')
    const metricsResponse = await fetch(`${backendUrl}/dashboard/metrics/${realtorId}`)
    console.log('📊 Respuesta métricas:', metricsResponse.status, metricsResponse.statusText)
    
    if (metricsResponse.ok) {
      const metricsData = await metricsResponse.json()
      console.log('✅ Métricas recibidas:', metricsData)
      
      // Mapear métricas del backend al formato del dashboard
      metrics.value = {
        totalClients: metricsData.metrics?.total_leads || 0,
        totalProperties: 0, // Esto necesitaría un endpoint específico
        scheduledVisits: 0, // Esto necesitaría un endpoint específico  
        monthlySales: metricsData.metrics?.revenue || 0
      }
    } else {
      console.error('❌ Error obteniendo métricas:', metricsResponse.status, metricsResponse.statusText)
      const errorText = await metricsResponse.text()
      console.error('❌ Error details:', errorText)
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
    const backendUrl = 'https://fapi.showtimeprop.com'
    
    // Obtener clientes del tenant
    console.log('👥 Llamando a clientes del tenant...')
    const clientsUrl = `${backendUrl}/favorites/tenant/${realtorProfile.value.tenant_id}/clients`
    console.log('👥 URL clientes:', clientsUrl)
    
    const clientsResponse = await fetch(clientsUrl)
    console.log('👥 Respuesta clientes:', clientsResponse.status, clientsResponse.statusText)
    
    if (clientsResponse.ok) {
      const clientsData = await clientsResponse.json()
      console.log('✅ Datos clientes recibidos:', clientsData)
      
      clients.value = clientsData.clients || []
      metrics.value.totalClients = clients.value.length
      console.log('✅ Clientes encontrados:', metrics.value.totalClients)
      console.log('✅ Lista de clientes:', clients.value)
      
      // Obtener todas las propiedades favoritas
      await fetchAllFavoriteProperties()
    } else {
      console.error('❌ Error obteniendo clientes:', clientsResponse.status, clientsResponse.statusText)
      const errorText = await clientsResponse.text()
      console.error('❌ Error details clientes:', errorText)
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

// Función para obtener todas las propiedades favoritas
const fetchAllFavoriteProperties = async () => {
  try {
    const backendUrl = 'https://fapi.showtimeprop.com'
    const allProperties = []
    
    // Para cada cliente, obtener sus favoritos
    for (const client of clients.value) {
      const favoritesResponse = await fetch(`${backendUrl}/favorites/${client.client_id}`)
      if (favoritesResponse.ok) {
        const favoritesData = await favoritesResponse.json()
        const clientFavorites = favoritesData.favorites || []
        
        // Agregar información del cliente a cada favorito
        const favoritesWithClient = clientFavorites.map(fav => ({
          ...fav,
          client_id: client.client_id,
          client_first_activity: client.first_activity,
          client_favorites_count: client.favorites_count
        }))
        
        allProperties.push(...favoritesWithClient)
      }
    }
    
    favoriteProperties.value = allProperties
    metrics.value.totalProperties = allProperties.length
    console.log('Propiedades favoritas encontradas:', allProperties.length)
    
  } catch (error) {
    console.error('Error fetching favorite properties:', error)
  }
}

// Cargar métricas al montar el componente
onMounted(async () => {
  console.log('🚀 Dashboard montado, iniciando carga de datos...')
  console.log('realtorProfile en onMounted:', realtorProfile.value)
  
  // Esperar un poco para que realtorProfile se cargue
  setTimeout(() => {
    console.log('⏰ Timeout completado, llamando fetchMetrics...')
    fetchMetrics()
  }, 2000) // Aumentar a 2 segundos para dar más tiempo
})

// Meta para evitar indexación
definePageMeta({
  layout: false
})
</script>