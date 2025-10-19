-- =====================================================
-- DEBUG: Verificar tenant_id y favoritos
-- =====================================================

-- 1. Ver todos los tenants disponibles
SELECT 
    id,
    subdomain,
    name,
    created_at
FROM tenants
ORDER BY created_at;

-- 2. Ver todos los favoritos con sus tenant_id
SELECT 
    f.id,
    f.tenant_id,
    f.client_id,
    f.property_id,
    f.created_at,
    t.subdomain as tenant_subdomain,
    t.name as tenant_name
FROM favorites f
LEFT JOIN tenants t ON f.tenant_id = t.id
ORDER BY f.created_at DESC;

-- 3. Ver usuarios con sus tenant_id
SELECT 
    u.id,
    u.email,
    u.tenant_id,
    u.created_at,
    t.subdomain as tenant_subdomain,
    t.name as tenant_name
FROM users u
LEFT JOIN tenants t ON u.tenant_id = t.id
ORDER BY u.created_at DESC;

-- 4. Verificar si existe un tenant por defecto o sin subdominio
SELECT 
    id,
    subdomain,
    name,
    CASE 
        WHEN subdomain IS NULL THEN 'SIN SUBDOMINIO'
        WHEN subdomain = '' THEN 'SUBDOMINIO VACÍO'
        ELSE subdomain
    END as subdomain_status
FROM tenants
WHERE subdomain IS NULL OR subdomain = '';

-- 5. Contar favoritos por tenant
SELECT 
    t.id as tenant_id,
    t.subdomain,
    t.name as tenant_name,
    COUNT(f.id) as total_favorites,
    COUNT(DISTINCT f.client_id) as unique_clients
FROM tenants t
LEFT JOIN favorites f ON t.id = f.tenant_id
GROUP BY t.id, t.subdomain, t.name
ORDER BY total_favorites DESC;
