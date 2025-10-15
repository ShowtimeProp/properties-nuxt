-- =====================================================
-- CORREGIR MISMATCH DE IDs CON TRANSACCIÓN ATOMICA
-- =====================================================

-- PROBLEMA: Los IDs no coinciden entre auth.users y realtors
-- auth.users.id: 2d450e8d-0245-4368-a0aa-a6af8736f793
-- realtors.id:   fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5

-- SOLUCIÓN: Usar una transacción para hacer todo atómicamente

BEGIN;

-- Paso 1: Verificar estado actual
SELECT 'ESTADO INICIAL' as etapa;

SELECT
  'auth.users' as tabla,
  id,
  email
FROM auth.users
WHERE email = 'biancannicolini@gmail.com'

UNION ALL

SELECT
  'realtors' as tabla,
  id,
  email
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- Paso 2: Deshabilitar temporalmente la verificación de foreign keys
SET session_replication_role = replica;

-- Paso 3: Actualizar email_templates primero (sin verificación FK)
UPDATE email_templates
SET realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793'
WHERE realtor_id = 'fa17b2d5-d5b8-4f7f-a243-6e317d2a8ce5';

-- Paso 4: Actualizar realtors
UPDATE realtors
SET id = '2d450e8d-0245-4368-a0aa-a6af8736f793'
WHERE email = 'biancannicolini@gmail.com';

-- Paso 5: Rehabilitar verificación de foreign keys
SET session_replication_role = DEFAULT;

-- Paso 6: Verificar resultado final
SELECT 'ESTADO FINAL' as etapa;

SELECT
  'auth.users' as tabla,
  id,
  email
FROM auth.users
WHERE email = 'biancannicolini@gmail.com'

UNION ALL

SELECT
  'realtors' as tabla,
  id,
  email
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- Confirmar la transacción
COMMIT;

-- Verificación adicional: datos completos del realtor
SELECT 
  id,
  name,
  email,
  phone,
  tenant_id,
  created_at
FROM realtors 
WHERE email = 'biancannicolini@gmail.com';
