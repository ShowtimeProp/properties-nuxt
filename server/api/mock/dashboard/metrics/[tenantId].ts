export default defineEventHandler(async (event) => {
  const tenantId = getRouterParam(event, 'tenantId')
  
  // Datos mock para el dashboard
  const mockMetrics = {
    total_clientes: 5,
    total_propiedades: 12,
    visitas_programadas: 3,
    ventas_mes: 2
  }
  
  return mockMetrics
})
