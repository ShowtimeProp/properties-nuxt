# 🔧 Configuración de Google Auth en Supabase

## **Problema Identificado:**
Google Auth redirige a `bnicolini.showtimeprop.com` (mapa principal) en lugar de `dash.bnicolini.showtimeprop.com` (dashboard).

## **Solución - Configurar Supabase:**

### **Paso 1: Ir a Supabase Dashboard**
1. Ve a [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto **"Showtime Prop"**

### **Paso 2: Configurar Authentication**
1. En el menú lateral, haz click en **"Authentication"**
2. Haz click en **"Settings"** (configuraciones)
3. Ve a la sección **"URL Configuration"**

### **Paso 3: Configurar URLs de Redirección**

**Site URL:**
```
https://dash.bnicolini.showtimeprop.com
```

**Additional redirect URLs (agregar estas URLs):**
```
https://dash.bnicolini.showtimeprop.com/dashboard
https://dash.bnicolini.showtimeprop.com/auth/callback
https://bnicolini.showtimeprop.com/auth/callback
```

### **Paso 4: Configurar Google OAuth**
1. En **Authentication** → **Providers**
2. Haz click en **"Google"**
3. Verifica que esté **habilitado**
4. En **"Redirect URLs"**, asegúrate de que esté configurado para:
   ```
   https://dash.bnicolini.showtimeprop.com/auth/callback
   ```

### **Paso 5: Configurar Google Cloud Console**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Ve a **APIs & Services** → **Credentials**
3. Encuentra tu **OAuth 2.0 Client ID**
4. En **"Authorized redirect URIs"**, agrega:
   ```
   https://ugqqlnlmubedxpsepvgz.supabase.co/auth/v1/callback
   ```

## **Verificación:**
Después de estos cambios:
1. **Google Auth** debería redirigir a `dash.bnicolini.showtimeprop.com/dashboard`
2. **El usuario debería estar autenticado** en el dashboard
3. **No debería aparecer el formulario de login** nuevamente

## **Si el problema persiste:**
El campo de email "deformado" indica un problema de CSS. Podemos agregar un fix temporal:
