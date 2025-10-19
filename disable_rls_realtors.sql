-- =====================================================
-- DESHABILITAR RLS EN TABLA REALTORS
-- =====================================================

-- 1. Verificar estado actual de RLS
SELECT 
  'ESTADO ACTUAL RLS' as debug,
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'realtors';

-- 2. Deshabilitar RLS en la tabla realtors
ALTER TABLE realtors DISABLE ROW LEVEL SECURITY;

-- 3. Verificar que RLS se deshabilitó
SELECT 
  'ESTADO DESPUÉS DE DESHABILITAR' as debug,
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'realtors';

-- 4. Probar que la consulta funciona sin RLS
SELECT 
  'PRUEBA: Consulta sin RLS' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 5. Probar consulta por ID
SELECT 
  'PRUEBA: Consulta por ID' as debug,
  id,
  name,
  email,
  phone,
  tenant_id
FROM realtors
WHERE id = '2d450e8d-0245-43b8-a0aa-a6af8736f793';
