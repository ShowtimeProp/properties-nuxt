export default defineNuxtRouteMiddleware(async (to, from) => {
  // Only run on client side
  if (process.server) return

  const { isRealtor, checkRealtorStatus } = useRealtorAuth()

  // Check if user is authenticated and is a realtor
  const isAuthorized = await checkRealtorStatus()
  
  if (!isAuthorized) {
    return navigateTo('/realtor-login')
  }
})
