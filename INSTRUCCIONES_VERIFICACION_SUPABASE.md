# 🔍 Instrucciones para Verificar y Corregir Datos en Supabase

## **Paso 1: Ejecutar Script de Verificación**

1. Ve a **Supabase Dashboard** → [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto **"Showtime Prop"**
3. En el menú lateral, haz click en **"SQL Editor"**
4. Copia y pega el contenido del archivo `verify_and_fix_realtor_data.sql`
5. Haz click en **"Run"** para ejecutar el script

## **Paso 2: Interpretar los Resultados**

### **A. Si el realtor EXISTE en la tabla `realtors`:**
```
✅ Verás un registro con:
- id: 65e71111-0000-0000-0000-000000000000
- name: Bianca Nicolini
- email: biancannicolini@gmail.com
- phone: +54 9 223 354-4009
- tenant_id: 76aa777e-fe6b-4219-b255-349e5356dcdb
```

### **B. Si el realtor NO EXISTE:**
1. Descomenta la sección de `INSERT` en el script SQL
2. Ejecuta el script nuevamente

### **C. Verificar usuario en Auth:**
El script también verifica si existe el usuario en `auth.users`.

**Si NO existe en auth.users:**
1. Ve a **Authentication** → **Users** en el menú lateral
2. Haz click en **"Add user"**
3. Completa:
   - Email: `biancannicolini@gmail.com`
   - Password: `test123456`
   - ✅ Marca "Confirm email" (importante!)
4. Haz click en **"Create user"**

**Si existe pero no está confirmado:**
1. Ve a **Authentication** → **Users**
2. Busca `biancannicolini@gmail.com`
3. Haz click en el usuario
4. Verifica que `email_confirmed_at` tenga un valor (no sea NULL)
5. Si es NULL, haz click en **"Send email confirmation"** o marca manualmente como confirmado

## **Paso 3: Probar el Login**

Una vez que:
- ✅ El realtor exista en `realtors` tabla
- ✅ El usuario exista en `auth.users`
- ✅ El email esté confirmado

Entonces podrás hacer login en:
[https://dash.bnicolini.showtimeprop.com/realtor-login](https://dash.bnicolini.showtimeprop.com/realtor-login)

Usa el botón **"Usar datos de prueba"** para auto-completar el formulario.

## **Paso 4: Troubleshooting**

Si después de todo esto sigue sin funcionar:
1. Abre la consola del navegador (F12)
2. Ve a la pestaña **"Console"**
3. Intenta hacer login
4. Copia todos los mensajes de la consola
5. Comparte los errores para diagnóstico adicional

---

## **Scripts SQL de Referencia:**

### Verificar realtor:
```sql
SELECT * FROM realtors WHERE email = 'biancannicolini@gmail.com';
```

### Verificar usuario auth:
```sql
SELECT id, email, email_confirmed_at FROM auth.users WHERE email = 'biancannicolini@gmail.com';
```

### Actualizar datos:
```sql
UPDATE realtors 
SET name = 'Bianca Nicolini', phone = '+54 9 223 354-4009'
WHERE email = 'biancannicolini@gmail.com';
```


