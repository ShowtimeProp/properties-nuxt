-- Schema para el sistema de favoritos multi-tenant
-- Este archivo debe ejecutarse en Supabase SQL Editor

-- 1. Tabla para almacenar favoritos de clientes por tenant
CREATE TABLE IF NOT EXISTS public.favorites (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    client_id UUID NOT NULL, -- ID del usuario/cliente
    property_id TEXT NOT NULL, -- ID de la propiedad en Qdrant
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_favorites_tenant_client ON public.favorites(tenant_id, client_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property ON public.favorites(property_id);
CREATE INDEX IF NOT EXISTS idx_favorites_created_at ON public.favorites(created_at);

-- 3. Política RLS: Los tenants solo pueden ver sus propios favoritos
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;

-- Política para INSERT: Solo permitir insertar favoritos para el tenant actual
CREATE POLICY "Tenants can insert their own favorites" ON public.favorites
    FOR INSERT 
    WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para SELECT: Solo permitir ver favoritos del tenant actual
CREATE POLICY "Tenants can view their own favorites" ON public.favorites        
    FOR SELECT
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para UPDATE: Solo permitir actualizar favoritos del tenant actual  
CREATE POLICY "Tenants can update their own favorites" ON public.favorites      
    FOR UPDATE
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Política para DELETE: Solo permitir eliminar favoritos del tenant actual    
CREATE POLICY "Tenants can delete their own favorites" ON public.favorites      
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
CREATE TRIGGER update_favorites_updated_at 
    BEFORE UPDATE ON public.favorites 
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- 6. Comentarios para documentación
COMMENT ON TABLE public.favorites IS 'Almacena favoritos de clientes por tenant (realtor)';
COMMENT ON COLUMN public.favorites.tenant_id IS 'ID del tenant (realtor) que captó al cliente';
COMMENT ON COLUMN public.favorites.client_id IS 'ID del cliente/usuario que guardó el favorito';
COMMENT ON COLUMN public.favorites.property_id IS 'ID de la propiedad en Qdrant';
