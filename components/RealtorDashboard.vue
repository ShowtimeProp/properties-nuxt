<template>
  <div class="realtor-dashboard p-6 bg-gray-50 min-h-screen">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard Realtor</h1>
      <p class="text-gray-600 mt-2">Bienvenido, {{ realtorName }}</p>
    </div>

    <!-- Métricas Principales -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <MetricCard 
        title="Total Leads"
        :value="metrics.totalLeads"
        :change="metrics.leadsChange"
        icon="users"
        color="blue"
      />
      <MetricCard 
        title="Leads Activos"
        :value="metrics.activeLeads"
        :change="metrics.activeChange"
        icon="user-check"
        color="green"
      />
      <MetricCard 
        title="Conversiones"
        :value="metrics.conversions"
        :change="metrics.conversionChange"
        icon="target"
        color="purple"
      />
      <MetricCard 
        title="Revenue"
        :value="metrics.revenue"
        :change="metrics.revenueChange"
        icon="dollar-sign"
        color="green"
      />
    </div>

    <!-- Pipeline de Ventas -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-8">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">Pipeline de Ventas</h3>
      <PipelineBoard :stages="pipelineStages" :leads="pipelineLeads" />
    </div>

    <!-- Leads Recientes -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">Leads Recientes</h3>
      <LeadsTable :leads="recentLeads" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MetricCard from './MetricCard.vue'
import PipelineBoard from './PipelineBoard.vue'
import LeadsTable from './LeadsTable.vue'

// Estado del componente
const realtorName = ref('Realtor')
const metrics = ref({
  totalLeads: 0,
  leadsChange: 0,
  activeLeads: 0,
  activeChange: 0,
  conversions: 0,
  conversionChange: 0,
  revenue: 0,
  revenueChange: 0
})

const pipelineStages = ref([
  { id: 'new', name: 'Nuevos', color: 'bg-blue-500' },
  { id: 'contacted', name: 'Contactados', color: 'bg-yellow-500' },
  { id: 'qualified', name: 'Calificados', color: 'bg-orange-500' },
  { id: 'proposal', name: 'Propuesta', color: 'bg-purple-500' },
  { id: 'closed', name: 'Cerrados', color: 'bg-green-500' }
])

const pipelineLeads = ref([])
const recentLeads = ref([])

// Composable para dashboard
const { 
  metrics: dashboardMetrics, 
  pipelineData, 
  recentActivities, 
  isLoading, 
  error,
  loadDashboardData: loadDashboardFromAPI
} = useDashboard()

// Cargar datos del dashboard
const loadDashboardData = async () => {
  try {
    // ID del realtor (por ahora hardcodeado, después vendrá del auth)
    const realtorId = 'fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5'
    
    await loadDashboardFromAPI(realtorId)
    
    // Actualizar métricas locales
    metrics.value = {
      totalLeads: dashboardMetrics.value.totalLeads || 0,
      leadsChange: dashboardMetrics.value.leadsChange || 0,
      activeLeads: dashboardMetrics.value.activeLeads || 0,
      activeChange: dashboardMetrics.value.activeChange || 0,
      conversions: dashboardMetrics.value.conversions || 0,
      conversionChange: dashboardMetrics.value.conversionChange || 0,
      revenue: dashboardMetrics.value.revenue || 0,
      revenueChange: dashboardMetrics.value.revenueChange || 0
    }

    // Actualizar pipeline leads
    pipelineLeads.value = pipelineData.value.map(lead => ({
      id: lead.id,
      name: lead.agent_leads?.name || 'Sin nombre',
      stage: lead.stage,
      value: lead.estimated_value || 0,
      lastActivity: lead.last_activity
    }))

    // Actualizar leads recientes (por ahora datos de ejemplo)
    recentLeads.value = [
      { id: 1, name: 'Juan Pérez', email: 'juan@email.com', phone: '+54 9 11 1234-5678', source: 'Website', status: 'new', createdAt: '2024-01-15' },
      { id: 2, name: 'María García', email: 'maria@email.com', phone: '+54 9 11 2345-6789', source: 'Referral', status: 'contacted', createdAt: '2024-01-14' },
      { id: 3, name: 'Carlos López', email: 'carlos@email.com', phone: '+54 9 11 3456-7890', source: 'Facebook', status: 'qualified', createdAt: '2024-01-13' }
    ]
  } catch (error) {
    console.error('Error cargando datos del dashboard:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.realtor-dashboard {
  font-family: 'Inter', sans-serif;
}
</style>
