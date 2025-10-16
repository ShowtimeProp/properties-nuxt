-- =====================================================
-- DEBUG: Verificar exactamente qué está pasando en checkRealtorStatus
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

-- 3. Verificar TODOS los realtors para ver si hay algo raro
SELECT 
  'DEBUG: Todos los realtors' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors;

-- 4. Verificar el usuario en auth.users
SELECT 
  'DEBUG: Auth users' as debug,
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';
