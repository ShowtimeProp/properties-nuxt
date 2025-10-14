// Plugin para inicializar el sistema de proxy de imágenes en el cliente
export default defineNuxtPlugin(async () => {
  const { initializeProxies, startHealthCheck } = useImageProxy()
  
  // Inicializar proxies al cargar la aplicación
  await initializeProxies()
  
  // Iniciar verificación periódica de salud
  startHealthCheck()
  
  console.log('Sistema de proxy de imágenes inicializado')
})
