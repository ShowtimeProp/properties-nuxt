-- =====================================================
-- DEBUG DETALLADO: Verificar consulta exacta de checkRealtorStatus
-- =====================================================

-- 1. Verificar que el usuario existe con el ID exacto
SELECT 
  'DEBUG: Usuario por ID exacto' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE id = '2d450e8d-0245-43b8-a0aa-a6af8736f793';

-- 2. Verificar que el usuario existe por email
SELECT 
  'DEBUG: Usuario por email' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 3. Simular la consulta exacta de checkRealtorStatus
SELECT 
  'DEBUG: Consulta checkRealtorStatus' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE id = '2d450e8d-0245-43b8-a0aa-a6af8736f793';

-- 4. Verificar permisos RLS (Row Level Security)
SELECT 
  'DEBUG: Verificar RLS' as debug,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual
FROM pg_policies 
WHERE tablename = 'realtors';

-- 5. Verificar si hay algún problema de conexión o permisos
SELECT 
  'DEBUG: Usuario actual' as debug,
  current_user,
  session_user,
  current_database();

-- 6. Verificar que el usuario existe en auth.users
SELECT 
  'DEBUG: Auth users' as debug,
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';
