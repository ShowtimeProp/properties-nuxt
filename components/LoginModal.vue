<template>
  <div v-if="isOpen" class="fixed inset-0 z-50" @click.self="resetAndClose">
    <!-- Contenedor Intermedio para Centrado Robusto -->
    <div class="flex items-center justify-center min-h-screen w-full bg-black/40 px-4 py-8">
      
      <!-- Contenedor del Modal -->
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full h-fit p-6 sm:p-8 relative transition-all duration-300" @click.stop>
        
        <!-- Botón de Cerrar -->
        <button
          class="absolute top-3 right-3 flex items-center justify-center w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-indigo-500 transition-colors"
          @click="resetAndClose"
          aria-label="Cerrar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Video -->
        <div class="w-full mb-4">
          <iframe
            class="rounded-lg shadow-md w-full aspect-video"
            src="https://www.youtube.com/embed/dQw4w9WgXcQ"
            title="Video de bienvenida"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>

        <!-- Títulos dinámicos -->
        <h1 class="text-2xl font-bold text-gray-800 text-center mb-1">
          {{ formStep === 'email' ? 'Inicie sesión o regístrese' : 'Cree su contraseña' }}
        </h1>
        <p class="text-gray-500 text-center mb-6">
          {{ formStep === 'email' ? 'Ingrese su email para continuar' : `Para la cuenta: ${email}` }}
        </p>

        <!-- Paso 1: Email -->
        <div v-if="formStep === 'email'" class="w-full">
          <div class="w-full flex items-center bg-gray-50 rounded-lg border border-gray-300 px-2 py-1 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition">
            <input
              v-model="email"
              type="email"
              placeholder="Su dirección de email..."
              class="flex-1 border-none outline-none bg-transparent text-base px-2 py-2"
              @input="validateEmail"
              @keyup.enter="isEmailValid && goToPasswordStep()"
            />
            <button
              v-if="isEmailValid"
              class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg px-4 py-2 ml-2 flex-shrink-0 flex items-center transition-transform transform hover:scale-105"
              @click="goToPasswordStep"
            >
              Siguiente
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Paso 2: Contraseña -->
        <div v-if="formStep === 'password'" class="w-full">
          <div class="w-full flex items-center bg-gray-50 rounded-lg border border-gray-300 px-2 py-1 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition">
            <input
              v-model="password"
              type="password"
              placeholder="Elija una contraseña (mín. 6 caracteres)"
              class="flex-1 border-none outline-none bg-transparent text-base px-2 py-2"
              @input="validatePassword"
              @keyup.enter="isPasswordValid && handleRegister()"
            />
            <button
              v-if="isPasswordValid"
              class="bg-green-500 hover:bg-green-600 text-white font-bold rounded-lg px-4 py-2 ml-2 flex-shrink-0 flex items-center transition-transform transform hover:scale-105"
              @click="handleRegister"
              :disabled="loading"
            >
              <span v-if="!loading">Enviar</span>
              <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>
          </div>
          <p v-if="authError" class="text-red-500 text-sm text-center mt-2">{{ authError }}</p>
        </div>
        
        <!-- Separador y Login con Google -->
        <div class="w-full">
          <div class="flex items-center my-4">
            <div class="flex-grow border-t border-gray-300"></div>
            <span class="flex-shrink mx-4 text-gray-500 text-sm">o utilice</span>
            <div class="flex-grow border-t border-gray-300"></div>
          </div>
          <button
            class="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-lg shadow-sm transition-all"
            @click="loginWithGoogle"
          >
            <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" class="w-5 h-5" />
            Registrarse con Google
          </button>
        </div>

      </div>

      </div>
    </div>
  </template>
  
  <script setup>
import { ref } from 'vue';
import { useLoginModalStore } from '~/stores/loginModal';
import { storeToRefs } from 'pinia';


const supabase = useSupabaseClient();
const loginModalStore = useLoginModalStore();
const { isOpen } = storeToRefs(loginModalStore);

// Estado del formulario
const formStep = ref('email'); // 'email' | 'password'
const email = ref('');
const password = ref('');
const loading = ref(false);

// Estado de validación
const isEmailValid = ref(false);
const isPasswordValid = ref(false);
const authError = ref('');

// --- Funciones de Validación ---
function validateEmail() {
  authError.value = '';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  isEmailValid.value = emailRegex.test(email.value);
}

function validatePassword() {
  authError.value = '';
  isPasswordValid.value = password.value.length >= 6;
}

// --- Flujo del Formulario ---
function goToPasswordStep() {
  if (isEmailValid.value) {
    formStep.value = 'password';
  }
}

function resetForm() {
  email.value = '';
  password.value = '';
  formStep.value = 'email';
  isEmailValid.value = false;
  isPasswordValid.value = false;
  authError.value = '';
  loading.value = false;
}

function resetAndClose() {
  resetForm();
  loginModalStore.close();
}

// --- Autenticación con Supabase ---
async function handleRegister() {
  if (!isPasswordValid.value || loading.value) return;

  loading.value = true;
  authError.value = '';

  try {
    // Primero, intenta iniciar sesión
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });

    if (signInError) {
      // Si el error es "Invalid login credentials", significa que el usuario no existe.
      // Procedemos a registrarlo.
      if (signInError.message.includes('Invalid login credentials')) {
        const { error: signUpError } = await supabase.auth.signUp({
          email: email.value,
          password: password.value,
        });

        if (signUpError) {
          // Si el registro también falla (p. ej., la contraseña es débil), muestra el error.
          throw signUpError;
        }
        // Si el registro es exitoso, Supabase maneja el estado del usuario.
        // El middleware se encargará de la redirección.
        // No necesitamos hacer nada más aquí, solo cerrar el modal.
    } else {
        // Si es otro tipo de error de inicio de sesión, muéstralo.
        throw signInError;
      }
    }
    // Si el signIn fue exitoso, el middleware se encargará de todo.
    // Simplemente cerramos el modal.
    resetAndClose();

  } catch (error) {
    authError.value = 'Error: ' + error.message;
  } finally {
    // Esto se ejecutará SIEMPRE, sin importar si hubo éxito o error.
    loading.value = false;
  }
}

async function loginWithGoogle() {
  if (loading.value) return;
  loading.value = true;
  authError.value = '';
  try {
    const { error } = await supabase.auth.signInWithOAuth({ 
      provider: 'google',
      options: {
        redirectTo: window.location.origin // Asegura la redirección correcta tras el login de Google
      }
    });
    if (error) {
      throw error;
    }
    // No es necesario cerrar el modal aquí, Google redirigirá la página completa.
  } catch (error) {
    authError.value = 'Error con Google: ' + error.message;
    loading.value = false; // Desactivar el spinner si hay un error antes de redirigir.
  }
  }
  </script>
  
  <style scoped>
/* Opcional: añade una transición suave a la altura del modal si cambia */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
  }
  </style>