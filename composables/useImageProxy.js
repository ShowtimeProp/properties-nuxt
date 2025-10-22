// Composable para manejo inteligente de proxy de imágenes
export const useImageProxy = () => {
  const { $config } = useNuxtApp()
  
  // Lista de proxies disponibles (solo el principal por ahora)
  const proxyServers = ref([
    {
      id: 'primary',
      url: 'https://fapi.showtimeprop.com/properties/images',
      status: 'active', // active, blocked, error
      lastCheck: null,
      errorCount: 0
    }
    // Proxies de respaldo deshabilitados temporalmente
    // {
    //   id: 'backup1',
    //   url: 'https://backup-proxy1.showtimeprop.com/properties/images',
    //   status: 'inactive',
    //   lastCheck: null,
    //   errorCount: 0
    // },
    // {
    //   id: 'backup2', 
    //   url: 'https://backup-proxy2.showtimeprop.com/properties/images',
    //   status: 'inactive',
    //   lastCheck: null,
    //   errorCount: 0
    // }
  ])

  // Proxy actual activo
  const activeProxy = ref(proxyServers.value[0])

  // Función para obtener URL de imagen del proxy activo
  const getImageUrl = (propertyId, imageIndex) => {
    return `${activeProxy.value.url}/${propertyId}/${imageIndex}`
  }

  // Función para verificar si un proxy está funcionando
  const checkProxyHealth = async (proxy) => {
    try {
      // Para el proxy principal, asumir que está funcionando
      if (proxy.id === 'primary') {
        proxy.status = 'active'
        proxy.lastCheck = new Date()
        proxy.errorCount = 0
        return true
      }
      
      // Para otros proxies, hacer verificación real
      const testUrl = `${proxy.url}/test-property/0`
      const response = await fetch(testUrl, { 
        method: 'HEAD',
        timeout: 5000 // 5 segundos timeout
      })
      
      proxy.status = response.ok ? 'active' : 'error'
      proxy.lastCheck = new Date()
      
      if (!response.ok) {
        proxy.errorCount++
      } else {
        proxy.errorCount = 0
      }
      
      return response.ok
    } catch (error) {
      console.warn(`Error verificando proxy ${proxy.id}:`, error)
      proxy.status = 'error'
      proxy.lastCheck = new Date()
      proxy.errorCount++
      return false
    }
  }

  // Función para cambiar al siguiente proxy disponible
  const switchToNextProxy = () => {
    const availableProxies = proxyServers.value.filter(p => 
      p.status === 'active' || p.status === 'inactive'
    )
    
    const currentIndex = availableProxies.findIndex(p => p.id === activeProxy.value.id)
    const nextIndex = (currentIndex + 1) % availableProxies.length
    
    activeProxy.value = availableProxies[nextIndex]
    console.log(`Cambiado a proxy: ${activeProxy.value.id}`)
    
    return activeProxy.value
  }

  // Función para manejar errores de imagen y cambiar proxy si es necesario
  const handleImageError = async (propertyId, imageIndex) => {
    console.warn(`Error cargando imagen ${imageIndex} para propiedad ${propertyId}`)
    
    // Incrementar contador de errores del proxy actual
    activeProxy.value.errorCount++
    
    // Si hay muchos errores, verificar salud del proxy
    if (activeProxy.value.errorCount >= 3) {
      console.log('Demasiados errores, verificando salud del proxy...')
      
      const isHealthy = await checkProxyHealth(activeProxy.value)
      
      if (!isHealthy) {
        console.log('Proxy actual no está funcionando, cambiando...')
        activeProxy.value.status = 'blocked'
        
        // Intentar cambiar al siguiente proxy
        const newProxy = switchToNextProxy()
        
        // Verificar que el nuevo proxy funcione
        const newProxyHealthy = await checkProxyHealth(newProxy)
        
        if (!newProxyHealthy) {
          console.error('Ningún proxy disponible')
          return false
        }
      }
    }
    
    return true
  }

  // Función para verificar todos los proxies al inicio
  const initializeProxies = async () => {
    console.log('Inicializando verificación de proxies...')
    
    for (const proxy of proxyServers.value) {
      await checkProxyHealth(proxy)
    }
    
    // Seleccionar el primer proxy activo
    const activeProxyFound = proxyServers.value.find(p => p.status === 'active')
    if (activeProxyFound) {
      activeProxy.value = activeProxyFound
      console.log(`Proxy activo: ${activeProxy.value.id}`)
    } else {
      console.error('Ningún proxy disponible')
    }
  }

  // Función para obtener estadísticas de proxies
  const getProxyStats = () => {
    return {
      active: proxyServers.value.filter(p => p.status === 'active').length,
      blocked: proxyServers.value.filter(p => p.status === 'blocked').length,
      error: proxyServers.value.filter(p => p.status === 'error').length,
      current: activeProxy.value.id
    }
  }

  // Verificación periódica de salud (cada 5 minutos)
  const startHealthCheck = () => {
    setInterval(async () => {
      console.log('Verificación periódica de proxies...')
      
      for (const proxy of proxyServers.value) {
        await checkProxyHealth(proxy)
      }
      
      // Si el proxy actual no está funcionando, cambiar
      if (activeProxy.value.status !== 'active') {
        switchToNextProxy()
      }
    }, 5 * 60 * 1000) // 5 minutos
  }

  return {
    getImageUrl,
    handleImageError,
    initializeProxies,
    getProxyStats,
    startHealthCheck,
    switchToNextProxy,
    checkProxyHealth
  }
}
