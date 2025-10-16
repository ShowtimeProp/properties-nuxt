-- =====================================================
-- CORREGIR MISMATCH FINAL DE IDS CON TRANSACCIÓN SEGURA
-- =====================================================

-- 1. Verificar el estado actual
SELECT 
  'ANTES' as estado,
  au.id as auth_id,
  au.email as auth_email,
  r.id as realtor_id,
  r.email as realtor_email
FROM auth.users au
LEFT JOIN realtors r ON au.email = r.email
WHERE au.email = 'biancannicolini@gmail.com';

-- 2. Verificar qué tablas referencian al realtor actual
SELECT 'email_templates' AS tabla, COUNT(*) as registros
FROM email_templates 
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793'

UNION ALL

SELECT 'realtor_metrics' AS tabla, COUNT(*) as registros
FROM realtor_metrics 
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793'

UNION ALL

SELECT 'lead_pipeline' AS tabla, COUNT(*) as registros
FROM lead_pipeline 
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793'

UNION ALL

SELECT 'email_campaigns' AS tabla, COUNT(*) as registros
FROM email_campaigns 
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793'

UNION ALL

SELECT 'realtor_activities' AS tabla, COUNT(*) as registros
FROM realtor_activities 
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

-- 3. TRANSACCIÓN SEGURA: Deshabilitar temporalmente foreign key checks
BEGIN;

-- Deshabilitar temporalmente la verificación de foreign keys
SET session_replication_role = replica;

-- Actualizar todas las tablas hijas para que apunten al nuevo ID
UPDATE email_templates 
SET realtor_id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'  -- ID correcto
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';  -- ID actual incorrecto

UPDATE realtor_metrics 
SET realtor_id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

UPDATE lead_pipeline 
SET realtor_id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

UPDATE email_campaigns 
SET realtor_id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

UPDATE realtor_activities 
SET realtor_id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'
WHERE realtor_id = '2d450e8d-0245-4368-a0aa-a6af8736f793';

-- Actualizar el ID del realtor
UPDATE realtors 
SET id = '2d450e8d-0245-43b8-a0aa-a6af8736f793'  -- ID correcto de auth.users
WHERE id = '2d450e8d-0245-4368-a0aa-a6af8736f793';  -- ID actual incorrecto

-- Re-habilitar la verificación de foreign keys
SET session_replication_role = DEFAULT;

COMMIT;

-- 4. Verificar el resultado
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

-- 5. Verificar que el usuario existe en realtors con el ID correcto
SELECT 
  'VERIFICACION FINAL' as estado,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE id = '2d450e8d-0245-43b8-a0aa-a6af8736f793';
