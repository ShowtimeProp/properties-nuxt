-- =====================================================
-- VERIFICAR USUARIO DESPUÉS DE GOOGLE AUTH
-- =====================================================

-- 1. Verificar si el usuario existe en auth.users después del Google Auth
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at,
  raw_user_meta_data
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';

-- 2. Verificar si existe en la tabla realtors
SELECT 
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 3. Si el usuario existe en auth.users pero NO en realtors, insertarlo
-- (Descomenta si es necesario)
/*
INSERT INTO realtors (
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
)
SELECT 
  au.id,
  COALESCE(au.raw_user_meta_data->>'full_name', 'Bianca Nicolini'),
  au.email,
  '+54 9 223 354-4009',
  '76aa777e-fe6b-4219-b255-349e5356dcdb',
  NOW()
FROM auth.users au
WHERE au.email = 'biancannicolini@gmail.com'
  AND NOT EXISTS (
    SELECT 1 FROM realtors r WHERE r.email = au.email
  );
*/

-- 4. Verificar resultado final
SELECT
  'auth.users' AS tabla,
  id,
  email,
  email_confirmed_at::text,
  last_sign_in_at::text
FROM auth.users
WHERE email = 'biancannicolini@gmail.com'

UNION ALL

SELECT
  'realtors' AS tabla,
  id,
  email,
  created_at::text,
  phone::text
FROM realtors
WHERE email = 'biancannicolini@gmail.com';
