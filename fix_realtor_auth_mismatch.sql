-- =====================================================
-- CORREGIR MISMATCH DE IDs ENTRE AUTH.USERS Y REALTORS
-- =====================================================

-- PROBLEMA IDENTIFICADO:
-- auth.users.id: 2d450e8d-0245-4368-a0aa-a6af8736f793
-- realtors.id:   fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5
-- 
-- Los IDs no coinciden, por eso falla el login.

-- SOLUCIÓN: Actualizar el ID en realtors para que coincida con auth.users

-- 1. Verificar datos actuales
SELECT 
  'auth.users' as tabla,
  id,
  email,
  created_at
FROM auth.users 
WHERE email = 'biancannicolini@gmail.com'

UNION ALL

SELECT 
  'realtors' as tabla,
  id,
  email,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';

-- 2. ACTUALIZAR el ID en realtors para que coincida con auth.users
UPDATE realtors 
SET id = '2d450e8d-0245-4368-a0aa-a6af8736f793'
WHERE email = 'biancannicolini@gmail.com';

-- 3. Verificar que la actualización fue exitosa
SELECT 
  'auth.users' as tabla,
  id,
  email,
  created_at
FROM auth.users 
WHERE email = 'biancannicolini@gmail.com'

UNION ALL

SELECT 
  'realtors' as tabla,
  id,
  email,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';

-- 4. Verificar datos completos del realtor actualizado
SELECT 
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';
