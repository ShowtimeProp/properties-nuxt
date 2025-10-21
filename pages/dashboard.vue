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
        <div class="bg-white shadow rounded-lg p-6 mb-8">
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

        <!-- Clientes Section con desplegables -->
        <div class="bg-white shadow rounded-lg p-6 mb-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">👥 Clientes Activos</h3>
          <div v-if="isLoading" class="text-gray-500">Cargando clientes...</div>
          <div v-else-if="clients.length === 0" class="text-gray-500">No hay clientes registrados aún.</div>
          <div v-else class="space-y-4">
            <div 
              v-for="client in clients" 
              :key="client.client_id"
              class="border border-gray-200 rounded-lg"
            >
              <!-- Header del cliente -->
              <div 
                class="p-4 cursor-pointer hover:bg-gray-50 transition-colors duration-200"
                @click="toggleClientExpansion(client.client_id)"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <h4 class="font-medium text-gray-900">
                        {{ client.full_name || client.email || `Cliente ${client.client_id.slice(0, 8)}...` }}
                      </h4>
                      <button
                        v-if="!client.isEditing"
                        @click.stop="startEditClient(client)"
                        class="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        ✏️ Editar
                      </button>
                    </div>
                    <p class="text-sm text-gray-500">
                      Email: {{ client.email || 'No disponible' }}
                    </p>
                    <p class="text-sm text-gray-500">
                      Primera actividad: {{ new Date(client.first_activity).toLocaleDateString() }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {{ client.favorites_count }} favoritos
                    </span>
                    <svg 
                      :class="['w-5 h-5 text-gray-400 transition-transform duration-200', 
                              client.isExpanded ? 'rotate-180' : '']"
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <!-- Formulario de edición -->
              <div v-if="client.isEditing" class="p-4 bg-gray-50 border-t border-gray-200">
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
                    <input
                      v-model="client.editData.full_name"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Nombre completo del cliente"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      v-model="client.editData.email"
                      type="email"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Email del cliente"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                    <input
                      v-model="client.editData.phone"
                      type="tel"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Teléfono del cliente"
                    />
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="saveClientEdit(client)"
                      class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                    >
                      Guardar
                    </button>
                    <button
                      @click="cancelClientEdit(client)"
                      class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- Favoritos del cliente (desplegable) -->
              <div v-if="client.isExpanded" class="border-t border-gray-200 bg-gray-50">
                <div class="p-4">
                  <h5 class="text-sm font-medium text-gray-700 mb-3">Propiedades Favoritas</h5>
                  <div v-if="client.favorites && client.favorites.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <DashboardPropertyCard
                      v-for="favorite in client.favorites"
                      :key="favorite.property_id"
                      :property="favorite"
                      :client-email="client.email"
                      @open-property="openPropertyModal"
                    />
                  </div>
                  <div v-else class="text-gray-500 text-sm">
                    Este cliente no tiene propiedades favoritas aún.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- Property Details Modal -->
    <PropertyDetailsModal
      :is-open="showPropertyModal"
      :property-id="selectedPropertyId"
      @close="closePropertyModal"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import DashboardPropertyCard from '~/components/DashboardPropertyCard.vue'
import PropertyDetailsModal from '~/components/PropertyDetailsModal.vue'

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

// Estado del modal de detalles de propiedad
const showPropertyModal = ref(false)
const selectedPropertyId = ref('')

const logout = async () => {
  await logoutRealtor()
}

// Funciones para manejar el modal de detalles de propiedad
const openPropertyModal = (property) => {
  selectedPropertyId.value = property.property_id
  showPropertyModal.value = true
}

const closePropertyModal = () => {
  showPropertyModal.value = false
  selectedPropertyId.value = ''
}

// Funciones para manejar desplegables de clientes
const toggleClientExpansion = (clientId) => {
  const client = clients.value.find(c => c.client_id === clientId)
  if (client) {
    client.isExpanded = !client.isExpanded
    
    // Si se está expandiendo, cargar los favoritos del cliente
    if (client.isExpanded && !client.favorites) {
      loadClientFavorites(client)
    }
  }
}

// Función para cargar favoritos de un cliente específico
const loadClientFavorites = async (client) => {
  try {
    console.log('🔍 Cargando favoritos para cliente:', client.client_id)
    const backendUrl = '/api/proxy'
    const favoritesUrl = `${backendUrl}/favorites/${client.client_id}`
    console.log('🔍 URL favoritos:', favoritesUrl)
    
    const favoritesResponse = await fetch(favoritesUrl)
    console.log('🔍 Respuesta favoritos:', favoritesResponse.status, favoritesResponse.statusText)
    
    if (favoritesResponse.ok) {
      const favoritesData = await favoritesResponse.json()
      console.log('✅ Datos favoritos recibidos:', favoritesData)
      const clientFavorites = favoritesData.favorites || []
      console.log('✅ Favoritos encontrados:', clientFavorites.length)
      
      // Obtener detalles de cada propiedad favorita
      const detailedFavorites = []
      for (const favorite of clientFavorites) {
        try {
          console.log('🔍 Cargando detalles de propiedad:', favorite.property_id)
          const propertyResponse = await fetch(`${backendUrl}/properties/${favorite.property_id}`)
          if (propertyResponse.ok) {
            const propertyData = await propertyResponse.json()
            console.log('✅ Detalles de propiedad cargados:', propertyData.property.id)
            detailedFavorites.push({
              ...favorite,
              ...propertyData.property
            })
          } else {
            console.error('❌ Error cargando detalles de propiedad:', propertyResponse.status, propertyResponse.statusText)
          }
        } catch (error) {
          console.error(`Error cargando detalles de propiedad ${favorite.property_id}:`, error)
        }
      }
      
      client.favorites = detailedFavorites
      console.log('✅ Favoritos finales asignados:', client.favorites.length)
    } else {
      console.error('❌ Error obteniendo favoritos:', favoritesResponse.status, favoritesResponse.statusText)
      const errorText = await favoritesResponse.text()
      console.error('❌ Error details:', errorText)
      client.favorites = []
    }
  } catch (error) {
    console.error('Error cargando favoritos del cliente:', error)
    client.favorites = []
  }
}

// Funciones para editar clientes
const startEditClient = (client) => {
  client.isEditing = true
  client.editData = {
    full_name: client.full_name || '',
    email: client.email || '',
    phone: client.phone || ''
  }
}

const cancelClientEdit = (client) => {
  client.isEditing = false
  client.editData = null
}

const saveClientEdit = async (client) => {
  try {
    console.log('💾 Guardando cambios del cliente:', client.client_id)
    console.log('💾 Datos a guardar:', client.editData)
    
    const backendUrl = '/api/proxy'
    const updateUrl = `${backendUrl}/users/${client.client_id}`
    console.log('💾 URL actualización:', updateUrl)
    
    // Actualizar datos del cliente en el backend
    const response = await fetch(updateUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': realtorProfile.value.tenant_id
      },
      body: JSON.stringify(client.editData)
    })
    
    console.log('💾 Respuesta actualización:', response.status, response.statusText)
    
    if (response.ok) {
      const responseData = await response.json()
      console.log('✅ Cliente actualizado exitosamente:', responseData)
      
      // Actualizar datos locales
      client.full_name = client.editData.full_name
      client.email = client.editData.email
      client.phone = client.editData.phone
      client.isEditing = false
      client.editData = null
      
      console.log('✅ Datos locales actualizados')
    } else {
      const errorText = await response.text()
      console.error('❌ Error actualizando cliente:', response.status, response.statusText)
      console.error('❌ Error details:', errorText)
      alert(`Error actualizando cliente: ${response.status} - ${errorText}`)
    }
  } catch (error) {
    console.error('❌ Error guardando cambios del cliente:', error)
    alert(`Error guardando cambios: ${error.message}`)
  }
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
    const backendUrl = '/api/proxy'
    
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
        totalProperties: 0, // Se calculará en fetchAdditionalData
        scheduledVisits: 0, // Se calculará en fetchAdditionalData  
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
    const backendUrl = '/api/proxy'
    
    // Obtener clientes del tenant
    console.log('👥 Llamando a clientes del tenant...')
    const clientsUrl = `${backendUrl}/favorites/tenant/${realtorProfile.value.tenant_id}/clients`
    console.log('👥 URL clientes:', clientsUrl)
    
    const clientsResponse = await fetch(clientsUrl)
    console.log('👥 Respuesta clientes:', clientsResponse.status, clientsResponse.statusText)
    
    if (clientsResponse.ok) {
      const clientsData = await clientsResponse.json()
      console.log('✅ Datos clientes recibidos:', clientsData)
      
      // Obtener detalles de usuarios para cada cliente
      const detailedClients = []
      for (const client of clientsData.clients || []) {
        try {
          // Intentar obtener datos del usuario por email o ID
          let userData = null
          
          // Buscar por ID del cliente
          const userResponse = await fetch(`${backendUrl}/users/${client.client_id}`, {
            headers: {
              'X-Tenant-ID': realtorProfile.value.tenant_id
            }
          })
          if (userResponse.ok) {
            const userResult = await userResponse.json()
            userData = userResult.user
          }
          
          detailedClients.push({
            ...client,
            full_name: userData?.full_name || null,
            email: userData?.email || null,
            phone: userData?.phone || null,
            isExpanded: false,
            isEditing: false,
            editData: null,
            favorites: null
          })
        } catch (error) {
          console.error(`Error obteniendo datos del usuario ${client.client_id}:`, error)
          detailedClients.push({
            ...client,
            full_name: null,
            email: null,
            phone: null,
            isExpanded: false,
            isEditing: false,
            editData: null,
            favorites: null
          })
        }
      }
      
      clients.value = detailedClients
      metrics.value.totalClients = clients.value.length
      console.log('✅ Clientes encontrados:', metrics.value.totalClients)
      console.log('✅ Lista de clientes:', clients.value)
      
      // Calcular total de propiedades favoritas
      let totalFavorites = 0
      for (const client of clients.value) {
        totalFavorites += client.favorites_count || 0
      }
      metrics.value.totalProperties = totalFavorites
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