export default defineNuxtRouteMiddleware((to, from) => {
  const { user } = useSupabaseUser()
  
  // Si no hay usuario autenticado, redirigir a login
  if (!user.value) {
    return navigateTo('/login')
  }
  
  // Verificar si el usuario es un realtor
  // Esto se puede hacer verificando el tenant_id o role en el token JWT
  const tenantId = user.value.user_metadata?.tenant_id
  const userRole = user.value.user_metadata?.role
  
  if (!tenantId || userRole !== 'realtor') {
    // Si no es realtor, redirigir a la página principal
    return navigateTo('/')
  }
})
