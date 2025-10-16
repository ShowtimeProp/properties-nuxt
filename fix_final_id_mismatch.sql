-- =====================================================
-- CORREGIR MISMATCH FINAL DE IDS
-- =====================================================

-- Verificar el estado actual
SELECT 
  'ANTES' as estado,
  au.id as auth_id,
  au.email as auth_email,
  r.id as realtor_id,
  r.email as realtor_email
FROM auth.users au
LEFT JOIN realtors r ON au.email = r.email
WHERE au.email = 'biancannicolini@gmail.com';

-- Corregir el ID en realtors para que coincida con auth.users
UPDATE realtors 
SET id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'  -- ID correcto de auth.users
WHERE email = 'biancannicolini@gmail.com';

-- Verificar el resultado
SELECT 
  'DESPUÉS' as estado,
  au.id as auth_id,
  au.email as auth_email,
  r.id as realtor_id,
  r.email as realtor_email,
  CASE 
    WHEN au.id = r.id THEN '✅ IDs COINCIDEN'
    ELSE '❌ IDs NO COINCIDEN'
  END as status
FROM auth.users au
LEFT JOIN realtors r ON au.email = r.email
WHERE au.email = 'biancannicolini@gmail.com';

-- Verificar que el usuario existe en realtors con el ID correcto
SELECT 
  'VERIFICACION FINAL' as estado,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE id = '2d450e8d-0245-43b8-a0aa-a6af8736f793';
