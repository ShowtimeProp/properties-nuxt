-- Schema para usuarios/clientes con asignación automática por tenant
-- Este archivo debe ejecutarse en Supabase SQL Editor

-- 1. Tabla para usuarios/clientes con asignación automática por tenant
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- 2. Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON public.users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at);

-- 3. Política RLS: Los usuarios solo pueden ver sus propios datos
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Política para INSERT: Solo permitir insertar usuarios para el tenant actual
CREATE POLICY "Users can insert their own profile" ON public.users
    FOR INSERT 
    WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para SELECT: Solo permitir ver usuarios del tenant actual
CREATE POLICY "Tenants can view their own users" ON public.users
    FOR SELECT 
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para UPDATE: Solo permitir actualizar usuarios del tenant actual
CREATE POLICY "Users can update their own profile" ON public.users
    FOR UPDATE 
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para DELETE: Solo permitir eliminar usuarios del tenant actual
CREATE POLICY "Tenants can delete their own users" ON public.users
    FOR DELETE 
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- 4. Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Trigger para actualizar updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- 6. Comentarios para documentación
COMMENT ON TABLE public.users IS 'Usuarios/clientes asignados automáticamente por tenant (realtor)';
COMMENT ON COLUMN public.users.tenant_id IS 'ID del tenant (realtor) que captó al cliente';
COMMENT ON COLUMN public.users.email IS 'Email único del cliente';
COMMENT ON COLUMN public.users.full_name IS 'Nombre completo del cliente';
COMMENT ON COLUMN public.users.phone IS 'Teléfono del cliente';
COMMENT ON COLUMN public.users.last_login IS 'Último acceso del cliente';

-- 7. Función para crear usuario automáticamente con tenant_id
CREATE OR REPLACE FUNCTION public.create_user_with_tenant(
    p_email TEXT,
    p_full_name TEXT DEFAULT NULL,
    p_phone TEXT DEFAULT NULL,
    p_tenant_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    user_id UUID;
BEGIN
    -- Si no se proporciona tenant_id, usar el del JWT
    IF p_tenant_id IS NULL THEN
        p_tenant_id := (auth.jwt() ->> 'tenant_id')::UUID;
    END IF;
    
    -- Crear usuario
    INSERT INTO public.users (email, full_name, phone, tenant_id)
    VALUES (p_email, p_full_name, p_phone, p_tenant_id)
    RETURNING id INTO user_id;
    
    RETURN user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Función para obtener usuario por email y tenant
CREATE OR REPLACE FUNCTION public.get_user_by_email_and_tenant(
    p_email TEXT,
    p_tenant_id UUID DEFAULT NULL
) RETURNS TABLE (
    id UUID,
    email TEXT,
    full_name TEXT,
    phone TEXT,
    tenant_id UUID,
    created_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    -- Si no se proporciona tenant_id, usar el del JWT
    IF p_tenant_id IS NULL THEN
        p_tenant_id := (auth.jwt() ->> 'tenant_id')::UUID;
    END IF;
    
    RETURN QUERY
    SELECT u.id, u.email, u.full_name, u.phone, u.tenant_id, u.created_at, u.last_login
    FROM public.users u
    WHERE u.email = p_email AND u.tenant_id = p_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
