-- =====================================================
-- DEBUG: VERIFICAR CONSULTA DE REALTOR
-- =====================================================

-- 1. Verificar el usuario en auth.users
SELECT 
  'auth.users' as tabla,
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';

-- 2. Verificar TODOS los usuarios en realtors
SELECT 
  'realtors - TODOS' as tabla,
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors
ORDER BY created_at DESC;

-- 3. Buscar específicamente por el ID del usuario autenticado
SELECT 
  'realtors - POR ID' as tabla,
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors
WHERE id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

-- 4. Buscar por email en realtors
SELECT 
  'realtors - POR EMAIL' as tabla,
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 5. Verificar si hay algún problema con el ID
SELECT 
  'COMPARACION' as tabla,
  au.id as auth_id,
  au.email as auth_email,
  r.id as realtor_id,
  r.email as realtor_email,
  CASE 
    WHEN au.id = r.id THEN 'IDs COINCIDEN'
    ELSE 'IDs NO COINCIDEN'
  END as status
FROM auth.users au
LEFT JOIN realtors r ON au.email = r.email
WHERE au.email = 'biancannicolini@gmail.com';
