<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
            <span class="ml-3 px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
              {{ realtorName }}
            </span>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="logout"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex">
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error al cargar el dashboard</h3>
            <div class="mt-2 text-sm text-red-700">
              {{ error }}
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Metrics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            v-for="metric in metrics"
            :key="metric.title"
            :title="metric.title"
            :value="metric.value"
            :change="metric.change"
            :icon="metric.icon"
            :color="metric.color"
          />
        </div>

        <!-- Pipeline and Activities Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <!-- Pipeline Board -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Pipeline de Ventas</h2>
            </div>
            <div class="p-6">
              <PipelineBoard :stages="pipelineStages" :leads="pipelineLeads" />
            </div>
          </div>

          <!-- Recent Activities -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Actividades Recientes</h2>
            </div>
            <div class="p-6">
              <div v-if="recentActivities.length === 0" class="text-center py-8 text-gray-500">
                No hay actividades recientes
              </div>
              <div v-else class="space-y-4">
                <div
                  v-for="activity in recentActivities"
                  :key="activity.id"
                  class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span class="text-blue-600 text-sm font-medium">
                        {{ getActivityIcon(activity.activity_type) }}
                      </span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">{{ activity.title }}</p>
                    <p class="text-sm text-gray-500">{{ activity.description }}</p>
                    <p class="text-xs text-gray-400 mt-1">
                      {{ formatDate(activity.activity_date) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Leads Table -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Leads Activos</h2>
          </div>
          <div class="overflow-x-auto">
            <LeadsTable :leads="activeLeads" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSupabaseClient, useSupabaseUser } from '#imports'
import MetricCard from '~/components/MetricCard.vue'
import PipelineBoard from '~/components/PipelineBoard.vue'
import LeadsTable from '~/components/LeadsTable.vue'

// Apply dashboard authentication middleware
definePageMeta({
  middleware: 'dashboard-auth'
})

// SEO
useHead({
  title: 'Dashboard - BNicolini Properties',
  meta: [
    { name: 'description', content: 'Dashboard CRM para realtores' }
  ]
})

// Realtor Authentication
const { realtorProfile, logoutRealtor } = useRealtorAuth()

// State
const isLoading = ref(true)
const error = ref(null)
const realtorName = computed(() => realtorProfile.value?.name || 'Realtor')
const metrics = ref([])
const pipelineStages = ref([])
const pipelineLeads = ref([])
const recentActivities = ref([])
const activeLeads = ref([])

// API Base URL
const apiBaseUrl = ref('')
if (process.client) {
  const hostname = window.location.hostname
  if (hostname === 'localhost') {
    apiBaseUrl.value = 'http://localhost:8000'
  } else if (hostname.includes('vercel.app')) {
    apiBaseUrl.value = 'https://fapi.showtimeprop.com'
  } else {
    apiBaseUrl.value = 'https://fapi.showtimeprop.com'
  }
}

// Realtor ID from profile
const realtorId = computed(() => realtorProfile.value?.id || 'fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5')

// Methods
const getActivityIcon = (type) => {
  const icons = {
    call: '📞',
    email: '📧',
    meeting: '🤝',
    proposal: '📄',
    contract: '📋',
    note: '📝'
  }
  return icons[type] || '📝'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const logout = async () => {
  await logoutRealtor()
}

const loadDashboardData = async () => {
  try {
    isLoading.value = true
    error.value = null

    // Load metrics
    const metricsResponse = await $fetch(`${apiBaseUrl.value}/dashboard/metrics/${realtorId.value}`)
    metrics.value = [
      {
        title: 'Total Leads',
        value: metricsResponse.metrics.total_leads,
        change: '+12%',
        icon: '👥',
        color: 'blue'
      },
      {
        title: 'Leads Activos',
        value: metricsResponse.metrics.active_leads,
        change: '+8%',
        icon: '🔄',
        color: 'green'
      },
      {
        title: 'Conversiones',
        value: metricsResponse.metrics.converted_leads,
        change: '+15%',
        icon: '💰',
        color: 'purple'
      },
      {
        title: 'Ingresos',
        value: `$${metricsResponse.metrics.revenue.toLocaleString()}`,
        change: '+23%',
        icon: '💵',
        color: 'yellow'
      }
    ]

    // Load pipeline data
    const pipelineResponse = await $fetch(`${apiBaseUrl.value}/dashboard/pipeline/${realtorId.value}`)
    pipelineStages.value = [
      { name: 'Nuevos', count: 0, color: 'bg-gray-500' },
      { name: 'Calificados', count: 0, color: 'bg-blue-500' },
      { name: 'Propuesta', count: 0, color: 'bg-yellow-500' },
      { name: 'Cierre', count: 0, color: 'bg-green-500' }
    ]
    pipelineLeads.value = pipelineResponse.leads || []

    // Load recent activities
    const activitiesResponse = await $fetch(`${apiBaseUrl.value}/dashboard/activities/${realtorId.value}?limit=10`)
    recentActivities.value = activitiesResponse.activities || []

    // Mock active leads for now
    activeLeads.value = [
      {
        id: '1',
        name: 'Juan Pérez',
        email: 'juan@email.com',
        phone: '+54 9 11 1234-5678',
        status: 'Nuevo',
        lastActivity: '2024-01-15T10:30:00Z',
        source: 'Website'
      },
      {
        id: '2',
        name: 'María González',
        email: 'maria@email.com',
        phone: '+54 9 11 8765-4321',
        status: 'Calificado',
        lastActivity: '2024-01-14T15:45:00Z',
        source: 'Referido'
      }
    ]

  } catch (err) {
    console.error('Error loading dashboard data:', err)
    error.value = err.message || 'Error al cargar los datos del dashboard'
  } finally {
    isLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>