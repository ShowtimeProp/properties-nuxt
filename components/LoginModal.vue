<template>
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
      <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-lg flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-1 text-indigo-700">Inicia Sesión o Regístrate Gratis!</h2>
            <!-- Google -->
        <button
          class="btn w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-lg shadow transition mb-6"
          @click="loginWithGoogle"
        >
        <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" class="w-5 h-5" />
          Iniciar sesión con Google
        </button>
        <!-- Acordeón exclusivo para login y registro -->
        <div class="w-full max-w-md mx-auto">
          <!-- Inicia Sesión -->
          <div class="border rounded-xl mb-2 overflow-hidden shadow-sm">
            <button
              class="w-full flex items-center justify-between gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-lg shadow transition text-base focus:outline-none mb-2"
              @click="activePanel = (activePanel === 'login' ? null : 'login')"
              type="button"
            >
              <span class="flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                Inicia Sesión
              </span>
              <svg :class="[activePanel === 'login' ? 'rotate-180' : '', 'w-5 h-5 transition-transform']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <transition name="accordion">
              <form v-show="activePanel === 'login'" class="px-4 pb-4 pt-2 flex flex-col gap-3 bg-white" @submit.prevent="loginWithUser">
                <input v-model="loginUser" type="text" placeholder="Usuario" class="input input-bordered w-full transition-all duration-200 placeholder-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:shadow-lg focus:-translate-y-0.5" />
                <input v-model="loginPassword" type="password" placeholder="Contraseña" class="input input-bordered w-full transition-all duration-200 placeholder-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:shadow-lg focus:-translate-y-0.5" />
                <button type="submit" class="btn btn-primary w-full">Iniciar Sesión</button>
              </form>
            </transition>
          </div>
          <!-- Regístrate con WhatsApp -->
          <div class="border rounded-xl overflow-hidden shadow-sm">
            <button
              class="w-full flex items-center justify-between gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-lg shadow transition text-base focus:outline-none mb-2"
              @click="activePanel = (activePanel === 'register' ? null : 'register')"
              type="button"
            >
              <span class="flex items-center gap-2">
                <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' class='w-5 h-5 fill-green-500'><path d='M16 3C9.373 3 4 8.373 4 15c0 2.65.867 5.1 2.35 7.1L4 29l7.15-2.3C13.1 27.133 14.533 27.5 16 27.5c6.627 0 12-5.373 12-12S22.627 3 16 3zm0 22c-1.367 0-2.7-.267-3.933-.8l-.283-.117-4.25 1.367 1.4-4.1-.183-.3C6.9 18.1 6 16.6 6 15c0-5.523 4.477-10 10-10s10 4.477 10 10-4.477 10-10 10zm5.267-7.267c-.283-.15-1.667-.817-1.933-.917-.267-.1-.467-.15-.667.15-.2.283-.767.917-.933 1.1-.167.183-.35.2-.633.067-.283-.15-1.2-.433-2.283-1.383-.85-.75-1.417-1.667-1.583-1.95-.167-.283-.017-.433.133-.583.133-.133.283-.35.417-.533.133-.183.183-.317.283-.533.1-.217.05-.4-.017-.567-.067-.183-.667-1.6-.917-2.2-.242-.583-.487-.5-.667-.5-.167-.017-.367-.017-.567-.017-.2 0-.533.067-.817.317-.283.25-1.083 1.05-1.083 2.567 0 1.517 1.108 2.983 1.267 3.183.15.2 2.183 3.333 5.283 4.533.733.317 1.3.5 1.75.633.733.233 1.4.2 1.933.117.583-.083 1.667-.683 1.9-1.35.233-.667.233-1.233.167-1.35-.067-.117-.25-.183-.533-.317z'/></svg>
                Regístrate con tu WhatsApp
              </span>
              <svg :class="[activePanel === 'register' ? 'rotate-180' : '', 'w-5 h-5 transition-transform']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <transition name="accordion">
              <div v-show="activePanel === 'register'" class="px-4 pb-4 pt-2 bg-white">
                <form class="flex flex-col gap-3" @submit.prevent="registerWithForm">
                  <p class="text-xs text-gray-500 text-center mt-3">
                    ¿Querés guardar tus propiedades favoritas, usar búsquedas con inteligencia artificial y tener el control total para encontrar tu casa ideal o próxima inversión?
                    <span class="font-bold text-indigo-600">¡Registrate gratis!</span>
                    <br>Si ya tenés cuenta, simplemente
                    <a href="#" class="text-indigo-600 underline hover:text-indigo-800 font-semibold cursor-pointer" @click.prevent="activePanel = 'login'">iniciá sesión</a>.
                  </p>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de usuario</label>
                    <input v-model="username" type="text" placeholder="Ej: juanperez" class="input input-bordered w-full transition-all duration-200 placeholder-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:shadow-lg focus:-translate-y-0.5" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">WhatsApp <span class="text-red-500">*</span></label>
                    <input v-model="whatsapp" type="tel" placeholder="Ej: 5492233534444" class="input input-bordered w-full transition-all duration-200 placeholder-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:shadow-lg focus:-translate-y-0.5" />
                    <span v-if="whatsappError" class="text-xs text-red-500">{{ whatsappError }}</span>
                  </div>
                  <button type="submit" class="btn btn-primary w-full mt-2">Registrarse</button>
                </form>
              </div>
            </transition>
          </div>
        </div>
        <!-- Botón de cerrar (cruz) abajo centrado -->
        <div class="w-full flex justify-center mt-4">
          <button
            class="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-indigo-500 transition text-xl shadow"
            @click="$emit('close')"
            aria-label="Cerrar"
          >
            <!-- SVG de cruz -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  const supabase = useNuxtApp().$supabase
  const props = defineProps({ show: Boolean })
  const emit = defineEmits(['close'])
  
  // Modelos de datos
  const email = ref('')
  const username = ref('')
  const whatsapp = ref('')
  
  // Errores
  const whatsappError = ref('')
  const emailError = ref('')
  
  const showForm = ref(false)
  
  const loginUser = ref("")
  const loginPassword = ref("")
  
  const activePanel = ref(null)
  
  async function loginWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({ provider: 'google' })
    if (error) alert('Error al iniciar sesión: ' + error.message)
  }
  
  function validateWhatsapp(number) {
    const regex = /^\d{11,15}$/;
    if (!number) return 'El número de WhatsApp es obligatorio.';
    if (!regex.test(number)) return 'Debe ingresar un número válido, solo dígitos, entre 11 y 15 caracteres.';
    if (number.startsWith('549') && number.length !== 13) return 'Para Argentina debe tener 13 dígitos (ej: 5492233544057).';
    return '';
  }
  
  function validateEmail(mail) {
    if (!mail) return '';
    if (!mail.includes('@')) return 'El email debe contener @';
    return '';
  }
  
  async function registerWithForm() {
    whatsappError.value = validateWhatsapp(whatsapp.value)
    emailError.value = validateEmail(email.value)
    if (whatsappError.value || emailError.value) return;
  
    // Aquí puedes enviar los datos a tu backend o a Supabase
    // Ejemplo: solo registro por email si se completó
    if (email.value) {
      const { error } = await supabase.auth.signUp({ email: email.value, password: Math.random().toString(36).slice(-10) }, {
        data: { username: username.value, whatsapp: whatsapp.value }
      })
      if (error) alert('Error al registrarse: ' + error.message)
      else alert('¡Registro exitoso! Revisa tu correo para confirmar tu cuenta.')
    } else {
      alert('¡Registro exitoso! (Simulado, sin email)')
    }
    // Limpiar campos
    username.value = ''
    whatsapp.value = ''
    email.value = ''
    emit('close')
  }
  
  function loginWithUser() {
    // Aquí puedes implementar la lógica de login
    alert(`Login de usuario: ${loginUser.value}`)
  }
  </script>
  
  <style scoped>
  .accordion-enter-active, .accordion-leave-active {
    transition: max-height 0.4s cubic-bezier(0.4,0,0.2,1), opacity 0.4s cubic-bezier(0.4,0,0.2,1);
  }
  .accordion-enter-from, .accordion-leave-to {
    max-height: 0;
    opacity: 0;
  }
  .accordion-enter-to, .accordion-leave-from {
    max-height: 600px;
    opacity: 1;
  }
  </style>