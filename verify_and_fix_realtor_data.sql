-- =====================================================
-- VERIFICAR Y CORREGIR DATOS DE BIANCA NICOLINI
-- =====================================================

-- 1. Verificar si el realtor existe en la tabla realtors
SELECT 
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';

-- 2. Si no existe, insertar el realtor (descomentar si es necesario)
/*
INSERT INTO realtors (
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
) VALUES (
  '65e71111-0000-0000-0000-000000000000',
  'Bianca Nicolini',
  'biancannicolini@gmail.com',
  '+54 9 223 354-4009',
  '76aa777e-fe6b-4219-b255-349e5356dcdb',
  NOW()
) ON CONFLICT (email) DO UPDATE SET
  name = EXCLUDED.name,
  phone = EXCLUDED.phone;
*/

-- 3. Actualizar datos si ya existe pero están incorrectos
UPDATE realtors 
SET 
  name = 'Bianca Nicolini',
  phone = '+54 9 223 354-4009'
WHERE email = 'biancannicolini@gmail.com';

-- 4. Verificar actualización
SELECT 
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';

-- 5. Verificar si el usuario existe en auth.users
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users
WHERE email = 'biancannicolini@gmail.com';

-- NOTA: Si el usuario NO existe en auth.users, debes crear uno:
-- Ve a Supabase Dashboard → Authentication → Users → Add user
-- Email: biancannicolini@gmail.com
-- Password: test123456
-- Confirm email: ✓ (marca el checkbox)

