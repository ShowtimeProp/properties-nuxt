-- =====================================================
-- CORREGIR MISMATCH DE IDs ENTRE AUTH.USERS Y REALTORS
-- Y RESOLVER VIOLACIÓN DE FOREIGN KEY
-- =====================================================

-- PROBLEMA IDENTIFICADO:
-- auth.users.id: 2d450e8d-0245-4368-a0aa-a6af8736f793
-- realtors.id:   fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5
-- Los IDs no coinciden, por eso falla el login.
-- Además, la actualización del ID en 'realtors' viola la FK 'email_templates_realtor_id_fkey'.

-- SOLUCIÓN:
-- 1. Obtener los IDs.
-- 2. Actualizar 'email_templates.realtor_id' al nuevo ID de auth.users.
-- 3. Actualizar 'realtors.id' al nuevo ID de auth.users.

-- Paso 0: Verificar IDs antes de cualquier cambio
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

-- Paso 1: Actualizar la tabla 'email_templates' para que referencie el nuevo ID
-- Esto debe hacerse ANTES de cambiar el ID en la tabla 'realtors'
UPDATE email_templates
SET realtor_id = (SELECT id FROM auth.users WHERE email = 'biancannicolini@gmail.com')
WHERE realtor_id = (SELECT id FROM realtors WHERE email = 'biancannicolini@gmail.com');

-- Paso 2: Actualizar el ID en la tabla 'realtors'
UPDATE realtors
SET id = (SELECT id FROM auth.users WHERE email = 'biancannicolini@gmail.com')
WHERE email = 'biancannicolini@gmail.com';

-- Paso 3: Verificación final de que los IDs coinciden
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
