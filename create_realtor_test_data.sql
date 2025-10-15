-- Datos actualizados para Bianca Nicolini
-- Los datos ya existen en la tabla realtors, solo necesitamos crear el usuario en Auth

-- Verificar datos existentes en realtors
SELECT * FROM realtors WHERE tenant_id = '76aa777e-fe6b-4219-b255-349e5356dcdb';

-- Actualizar teléfono si es necesario
UPDATE realtors 
SET phone = '+54 9 223 354-4009' 
WHERE email = 'biancannicolini@gmail.com';

-- Verificar actualización
SELECT * FROM realtors WHERE email = 'biancannicolini@gmail.com';
