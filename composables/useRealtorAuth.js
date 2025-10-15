export const useRealtorAuth = () => {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()

  const isRealtor = ref(false)
  const realtorProfile = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const checkRealtorStatus = async () => {
    if (!user.value) {
      isRealtor.value = false
      return false
    }

    try {
      isLoading.value = true
      error.value = null

      // Check if user exists in realtors table using the user ID
      const { data: realtor, error: realtorError } = await supabase
        .from('realtors')
        .select(`
          id,
          name,
          email,
          phone,
          tenant_id
        `)
        .eq('id', user.value.id)
        .maybeSingle()

      if (realtorError) {
        console.error('Error checking realtor status:', realtorError)
        isRealtor.value = false
        return false
      }

      if (realtor) {
        isRealtor.value = true
        realtorProfile.value = realtor
        return true
      } else {
        isRealtor.value = false
        return false
      }

    } catch (err) {
      console.error('Error in checkRealtorStatus:', err)
      error.value = err.message
      isRealtor.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  const loginAsRealtor = async (email, password) => {
    try {
      isLoading.value = true
      error.value = null

      console.log('Iniciando login para:', email)

      // Sign in with Supabase
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (authError) {
        console.error('Error de autenticación:', authError)
        throw authError
      }

      console.log('Usuario autenticado:', data.user?.email)

      // Check if user is a realtor
      const isRealtorUser = await checkRealtorStatus()
      
      if (!isRealtorUser) {
        console.log('Usuario no es realtor, cerrando sesión')
        // Sign out if not a realtor
        await supabase.auth.signOut()
        throw new Error('Acceso denegado. Solo realtores pueden acceder al dashboard.')
      }

      console.log('Login exitoso, redirigiendo al dashboard')
      
      // Redirect to dashboard after successful login
      await navigateTo('/dashboard')

      return data

    } catch (err) {
      console.error('Error in loginAsRealtor:', err)
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logoutRealtor = async () => {
    try {
      await supabase.auth.signOut()
      isRealtor.value = false
      realtorProfile.value = null
      await navigateTo('/')
    } catch (err) {
      console.error('Error in logoutRealtor:', err)
      error.value = err.message
    }
  }

  // Check status on composable creation
  if (user.value) {
    checkRealtorStatus()
  }

  return {
    isRealtor: readonly(isRealtor),
    realtorProfile: readonly(realtorProfile),
    isLoading: readonly(isLoading),
    error: readonly(error),
    checkRealtorStatus,
    loginAsRealtor,
    logoutRealtor
  }
}
