-- =====================================================
-- DEBUG: Verificar JWT y tenant_id del usuario autenticado
-- =====================================================

-- 1. Verificar el JWT actual del usuario autenticado
SELECT 
  'DEBUG: JWT actual' as debug,
  auth.jwt() as jwt_data;

-- 2. Verificar el tenant_id del usuario autenticado
SELECT 
  'DEBUG: Tenant ID del JWT' as debug,
  (auth.jwt() ->> 'tenant_id')::text as tenant_id_from_jwt;

-- 3. Verificar el tenant_id en la tabla realtors para Bianca
SELECT 
  'DEBUG: Tenant ID en realtors' as debug,
  tenant_id,
  name,
  email
FROM realtors
WHERE email = 'biancannicolini@gmail.com';

-- 4. Comparar tenant_ids
SELECT 
  'DEBUG: Comparación tenant_ids' as debug,
  (auth.jwt() ->> 'tenant_id')::text as jwt_tenant_id,
  r.tenant_id::text as realtor_tenant_id,
  CASE 
    WHEN (auth.jwt() ->> 'tenant_id')::text = r.tenant_id::text THEN '✅ COINCIDEN'
    ELSE '❌ NO COINCIDEN'
  END as status
FROM realtors r
WHERE r.email = 'biancannicolini@gmail.com';

-- 5. Verificar si RLS está habilitado en la tabla realtors
SELECT 
  'DEBUG: RLS habilitado' as debug,
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'realtors';
