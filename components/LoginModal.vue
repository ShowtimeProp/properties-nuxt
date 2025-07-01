<template>
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
      <div class="bg-white rounded-xl shadow-xl p-8 w-full max-w-lg flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-2 text-indigo-700">Iniciar sesión o registrarse</h2>
        <p class="mb-4 text-gray-500 text-center text-sm">
          Para guardar propiedades en tus favoritos y tener control total sobre la búsqueda de tu casa soñada o tu próxima inversión, regístrate o inicia sesión.
        </p>
        <!-- Google -->
        <button
          class="btn w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-lg shadow transition mb-6"
          @click="loginWithGoogle"
        >
        <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" class="w-5 h-5" />
          Iniciar sesión con Google
        </button>
        <!-- Divider -->
        <div class="mb-4 text-gray-400 text-xs flex items-center w-full">
          <span class="flex-1 border-t"></span>
          <span class="px-2">o completa el formulario</span>
          <span class="flex-1 border-t"></span>
        </div>
        <!-- Formulario de registro -->
        <form class="w-full flex flex-col gap-3" @submit.prevent="registerWithForm">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de usuario</label>
            <input v-model="username" type="text" placeholder="Ej: juanperez" class="input input-bordered w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">WhatsApp <span class="text-red-500">*</span></label>
            <input v-model="whatsapp" type="tel" placeholder="Ej: 5492234440000" class="input input-bordered w-full" />
            <span v-if="whatsappError" class="text-xs text-red-500">{{ whatsappError }}</span>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="email" type="email" placeholder="Ej: correo@ejemplo.com" class="input input-bordered w-full" />
            <span v-if="emailError" class="text-xs text-red-500">{{ emailError }}</span>
          </div>
          <button type="submit" class="btn btn-primary w-full mt-2">Registrarse</button>
        </form>
        <button class="mt-4 text-sm text-gray-400 hover:text-indigo-500" @click="$emit('close')">Cancelar</button>
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
  </script>