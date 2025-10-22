export default defineEventHandler(async (event) => {
  // Obtener la ruta completa desde la URL
  const url = getRouterParam(event, 'url') || ''
  const query = getQuery(event)
  
  console.log('🔍 Proxy debug:', { url, query })
  
  // Construir la URL del backend
  const backendUrl = `http://212.85.20.219:8000/${url}`
  
  // Agregar query parameters si existen
  const queryString = new URLSearchParams(query as Record<string, string>).toString()
  const fullUrl = queryString ? `${backendUrl}?${queryString}` : backendUrl
  
  console.log('🔗 Proxying to:', fullUrl)
  
  try {
    const response = await $fetch(fullUrl, {
      method: getMethod(event),
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': getHeader(event, 'x-tenant-id') || ''
      },
      body: getMethod(event) !== 'GET' ? await readBody(event) : undefined
    })
    
    console.log('✅ Proxy success')
    return response
  } catch (error) {
    console.error('❌ Proxy error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Proxy error: ' + (error as Error).message
    })
  }
})
