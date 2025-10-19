-- =====================================================
-- VERIFICAR SI EL USUARIO EXISTE EN REALTORS
-- =====================================================

-- 1. Verificar si el usuario existe en realtors
SELECT 
  'VERIFICACION REALTORS' as estado,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 2. Verificar TODOS los usuarios en realtors (para ver si hay duplicados)
SELECT 
  'TODOS LOS REALTORS' as estado,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors;

-- 3. Verificar si existe en auth.users
SELECT 
  'AUTH USERS' as estado,
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';

-- 4. Comparar IDs
SELECT
  'COMPARACION FINAL' AS tabla,
  au.id AS auth_id,
  au.email AS auth_email,
  r.id AS realtor_id,
  r.email AS realtor_email,
  CASE
    WHEN au.id = r.id THEN '✅ IDs COINCIDEN'
    ELSE '❌ IDs NO COINCIDEN'
  END AS status
FROM auth.users au
LEFT JOIN realtors r ON au.email = r.email
WHERE au.email = 'biancannicolini@gmail.com';
