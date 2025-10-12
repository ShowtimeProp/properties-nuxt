export const useDashboard = () => {
  const { $fetch } = useNuxtApp()
  const config = useRuntimeConfig()
  
  // Estado del dashboard
  const metrics = ref({
    totalLeads: 0,
    activeLeads: 0,
    conversions: 0,
    revenue: 0,
    leadsChange: 0,
    activeChange: 0,
    conversionChange: 0,
    revenueChange: 0
  })
  
  const pipelineData = ref([])
  const recentActivities = ref([])
  const emailTemplates = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Función para obtener métricas del realtor
  const fetchMetrics = async (realtorId) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/metrics/${realtorId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.metrics) {
        metrics.value = {
          totalLeads: response.metrics.total_leads || 0,
          activeLeads: response.metrics.active_leads || 0,
          conversions: response.metrics.converted_leads || 0,
          revenue: response.metrics.revenue || 0,
          // Por ahora valores estáticos para los cambios
          leadsChange: 12,
          activeChange: 5,
          conversionChange: 2,
          revenueChange: 15000
        }
      }
      
      return response
    } catch (err) {
      error.value = err.message || 'Error al cargar métricas'
      console.error('Error fetching metrics:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para obtener datos del pipeline
  const fetchPipelineData = async (realtorId) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/pipeline/${realtorId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      pipelineData.value = response.leads || []
      return response
    } catch (err) {
      error.value = err.message || 'Error al cargar datos del pipeline'
      console.error('Error fetching pipeline data:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para obtener actividades recientes
  const fetchRecentActivities = async (realtorId, limit = 10) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/activities/${realtorId}?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      recentActivities.value = response.activities || []
      return response
    } catch (err) {
      error.value = err.message || 'Error al cargar actividades recientes'
      console.error('Error fetching recent activities:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para crear una nueva actividad
  const createActivity = async (activityData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/activities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: activityData
      })
      
      // Recargar actividades después de crear una nueva
      if (activityData.realtor_id) {
        await fetchRecentActivities(activityData.realtor_id)
      }
      
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear actividad'
      console.error('Error creating activity:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para actualizar el stage de un lead
  const updateLeadStage = async (leadId, stageData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/pipeline/${leadId}/stage`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: stageData
      })
      
      return response
    } catch (err) {
      error.value = err.message || 'Error al actualizar stage del lead'
      console.error('Error updating lead stage:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para obtener plantillas de email
  const fetchEmailTemplates = async (realtorId) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/email-templates/${realtorId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      emailTemplates.value = response.templates || []
      return response
    } catch (err) {
      error.value = err.message || 'Error al cargar plantillas de email'
      console.error('Error fetching email templates:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para crear una plantilla de email
  const createEmailTemplate = async (templateData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await $fetch(`${config.public.apiBaseUrl}/dashboard/email-templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: templateData
      })
      
      // Recargar plantillas después de crear una nueva
      if (templateData.realtor_id) {
        await fetchEmailTemplates(templateData.realtor_id)
      }
      
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear plantilla de email'
      console.error('Error creating email template:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para cargar todos los datos del dashboard
  const loadDashboardData = async (realtorId) => {
    try {
      isLoading.value = true
      error.value = null
      
      // Cargar todos los datos en paralelo
      await Promise.all([
        fetchMetrics(realtorId),
        fetchPipelineData(realtorId),
        fetchRecentActivities(realtorId),
        fetchEmailTemplates(realtorId)
      ])
      
    } catch (err) {
      error.value = err.message || 'Error al cargar datos del dashboard'
      console.error('Error loading dashboard data:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Función para limpiar el estado
  const clearDashboard = () => {
    metrics.value = {
      totalLeads: 0,
      activeLeads: 0,
      conversions: 0,
      revenue: 0,
      leadsChange: 0,
      activeChange: 0,
      conversionChange: 0,
      revenueChange: 0
    }
    pipelineData.value = []
    recentActivities.value = []
    emailTemplates.value = []
    error.value = null
  }

  return {
    // Estado
    metrics: readonly(metrics),
    pipelineData: readonly(pipelineData),
    recentActivities: readonly(recentActivities),
    emailTemplates: readonly(emailTemplates),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Acciones
    fetchMetrics,
    fetchPipelineData,
    fetchRecentActivities,
    createActivity,
    updateLeadStage,
    fetchEmailTemplates,
    createEmailTemplate,
    loadDashboardData,
    clearDashboard
  }
}
