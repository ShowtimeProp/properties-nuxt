# Supabase Database Schema Documentation

Este documento proporciona una descripción detallada del esquema de la base de datos en Supabase para el proyecto de propiedades. Sirve como una fuente de verdad única para la estructura de las tablas, sus columnas y la lógica de automatización (triggers).

## 1. Tablas Principales

### 1.1. Tabla `public.tenants`

Almacena la información de cada "inquilino" (ej. inmobiliaria) en nuestro sistema multi-tenant. Cada tenant tiene su propia marca, dominio y conjunto de usuarios y propiedades asociados.

| column_name   | data_type                | is_nullable | column_default    | Descripción                                           |
|---------------|--------------------------|-------------|-------------------|-------------------------------------------------------|
| id            | uuid                     | NO          | gen_random_uuid() | Identificador único para el tenant.                   |
| name          | text                     | NO          | null              | Nombre de la inmobiliaria o tenant.                   |
| branding      | jsonb                    | YES         | null              | Almacena configuraciones de marca como colores, logos. |
| subdomain     | text                     | YES         | null              | Subdominio asignado para el portal (ej. `remax.propertysaas.com`). |
| custom_domain | text                     | YES         | null              | Dominio personalizado si el tenant lo configura (ej. `www.remax.com`). |
| created_at    | timestamp with time zone | YES         | now()             | Fecha y hora de creación del tenant.                  |

---

### 1.2. Tabla `public.profiles`

Extiende la tabla `auth.users` de Supabase con información pública y específica de nuestra aplicación para cada usuario.

| column_name        | data_type                | is_nullable | column_default      | Descripción                                                |
|--------------------|--------------------------|-------------|---------------------|------------------------------------------------------------|
| id                 | uuid                     | NO          | null                | FK a `auth.users.id`. Mantiene la sincronía entre tablas.   |
| tenant_id          | uuid                     | YES         | null                | FK a `public.tenants.id`. Asocia al usuario con una inmobiliaria. |
| full_name          | text                     | YES         | null                | Nombre completo del usuario.                               |
| role               | USER-DEFINED (`user_role`) | NO          | `'client'::user_role` | Rol del usuario (`client`, `agent`, `admin`).              |
| whatsapp           | text                     | YES         | null                | Número de WhatsApp del usuario.                            |
| email_confirmed    | boolean                  | YES         | `false`             | Estado de confirmación del email.                          |
| whatsapp_confirmed | boolean                  | YES         | `false`             | Estado de confirmación del WhatsApp.                       |
| updated_at         | timestamp with time zone | YES         | null                | Fecha y hora de la última actualización del perfil.          |

**Relaciones Clave:**
- `profiles.id` está vinculado directamente a `auth.users.id`.
- `profiles.tenant_id` vincula a un usuario con una fila en la tabla `tenants`. Puede ser nulo si un usuario no pertenece a ninguna inmobiliaria.

---

## 2. Triggers y Funciones

### 2.1. Función `handle_new_user()`

Esta función se ejecuta automáticamente cada vez que un nuevo usuario se registra. Su propósito es crear una entrada correspondiente en la tabla `public.profiles`, duplicando el `id` y el `email` desde la tabla `auth.users`.

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Inserta una nueva fila en public.profiles
  INSERT INTO public.profiles (id, full_name, role)
  VALUES (
    new.id,
    -- Usa el nombre de los metadatos si está disponible, si no, el email
    new.raw_user_meta_data->>'full_name',
    -- Asigna el rol desde los metadatos si está disponible, si no, 'client' por defecto
    (new.raw_user_meta_data->>'role')::user_role
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 2.2. Trigger `on_auth_user_created`

Este es el trigger que invoca a la función `handle_new_user` después de que un nuevo usuario es insertado en la tabla `auth.users`. Es el mecanismo que conecta el sistema de autenticación de Supabase con nuestra tabla de perfiles.

```sql
-- Creación del trigger que se dispara después de crear un usuario en auth.users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```