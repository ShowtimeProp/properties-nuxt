-- Crear datos de prueba para realtores
-- Ejecutar en Supabase SQL Editor

-- 1. Crear usuario de prueba en auth.users (esto se hace automáticamente al registrarse)
-- Pero necesitamos crear el registro en la tabla realtors

-- Insertar realtor de prueba
INSERT INTO realtors (id, tenant_id, name, email, phone) 
VALUES (
  gen_random_uuid(),
  '76aa777e-fe6b-4219-b255-349e5356dcdb', -- Tenant ID de BNicolini
  'Bruno Nicolini',
  'bruno@bnicolini.com',
  '+54 9 223 123-4567'
) ON CONFLICT (email) DO NOTHING;

-- Insertar segundo realtor de prueba
INSERT INTO realtors (id, tenant_id, name, email, phone) 
VALUES (
  gen_random_uuid(),
  '76aa777e-fe6b-4219-b255-349e5356dcdb', -- Tenant ID de BNicolini
  'Bianca Nicolini',
  'biancannicolini@gmail.com',
  '+54 9 223 987-6543'
) ON CONFLICT (email) DO NOTHING;

-- Verificar que se insertaron correctamente
SELECT * FROM realtors WHERE tenant_id = '76aa777e-fe6b-4219-b255-349e5356dcdb';
