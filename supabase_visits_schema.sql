-- Schema para visitas y calificaciones de propiedades
-- Este archivo debe ejecutarse en Supabase SQL Editor

-- 1. Tabla para visitas programadas y realizadas
CREATE TABLE IF NOT EXISTS public.visits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    property_id TEXT NOT NULL, -- ID de la propiedad en Qdrant
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL,
    visit_status TEXT NOT NULL DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no_show'
    realtor_notes TEXT, -- Notas del realtor sobre la visita
    client_notes TEXT, -- Notas del cliente sobre la visita
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- Calificación del cliente 1-5
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabla para seguimiento de favoritos (mejorada)
-- Esta tabla rastrea cuando un cliente marca/desmarca favoritos
CREATE TABLE IF NOT EXISTS public.favorite_activity (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    property_id TEXT NOT NULL,
    action TEXT NOT NULL, -- 'added', 'removed', 'viewed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_visits_tenant_client ON public.visits(tenant_id, client_id);
CREATE INDEX IF NOT EXISTS idx_visits_property ON public.visits(property_id);
CREATE INDEX IF NOT EXISTS idx_visits_date ON public.visits(visit_date);
CREATE INDEX IF NOT EXISTS idx_visits_status ON public.visits(visit_status);
CREATE INDEX IF NOT EXISTS idx_favorite_activity_tenant_client ON public.favorite_activity(tenant_id, client_id);
CREATE INDEX IF NOT EXISTS idx_favorite_activity_property ON public.favorite_activity(property_id);
CREATE INDEX IF NOT EXISTS idx_favorite_activity_created_at ON public.favorite_activity(created_at);

-- 4. Políticas RLS para visits
ALTER TABLE public.visits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenants can manage their own visits" ON public.visits
    FOR ALL 
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- 5. Políticas RLS para favorite_activity
ALTER TABLE public.favorite_activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenants can view their own favorite activity" ON public.favorite_activity
    FOR ALL 
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- 6. Función para crear visita automáticamente
CREATE OR REPLACE FUNCTION public.create_visit(
    p_client_id UUID,
    p_property_id TEXT,
    p_visit_date TIMESTAMP WITH TIME ZONE,
    p_realtor_notes TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    visit_id UUID;
    p_tenant_id UUID;
BEGIN
    -- Obtener tenant_id del cliente
    SELECT tenant_id INTO p_tenant_id 
    FROM public.users 
    WHERE id = p_client_id;
    
    IF p_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Client not found or not assigned to a tenant';
    END IF;
    
    -- Crear visita
    INSERT INTO public.visits (tenant_id, client_id, property_id, visit_date, realtor_notes)
    VALUES (p_tenant_id, p_client_id, p_property_id, p_visit_date, p_realtor_notes)
    RETURNING id INTO visit_id;
    
    RETURN visit_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Función para completar visita con calificación
CREATE OR REPLACE FUNCTION public.complete_visit(
    p_visit_id UUID,
    p_rating INTEGER,
    p_client_notes TEXT DEFAULT NULL
) RETURNS UUID AS $$
BEGIN
    -- Validar rating
    IF p_rating < 1 OR p_rating > 5 THEN
        RAISE EXCEPTION 'Rating must be between 1 and 5';
    END IF;
    
    -- Actualizar visita
    UPDATE public.visits 
    SET 
        visit_status = 'completed',
        rating = p_rating,
        client_notes = p_client_notes,
        updated_at = NOW()
    WHERE id = p_visit_id;
    
    RETURN p_visit_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Función para obtener historial completo del cliente
CREATE OR REPLACE FUNCTION public.get_client_history(
    p_client_id UUID,
    p_tenant_id UUID DEFAULT NULL
) RETURNS TABLE (
    activity_type TEXT,
    property_id TEXT,
    activity_date TIMESTAMP WITH TIME ZONE,
    rating INTEGER,
    notes TEXT,
    visit_status TEXT
) AS $$
BEGIN
    -- Si no se proporciona tenant_id, usar el del JWT
    IF p_tenant_id IS NULL THEN
        p_tenant_id := (auth.jwt() ->> 'tenant_id')::UUID;
    END IF;
    
    -- Combinar favoritos y visitas
    RETURN QUERY
    SELECT 
        'favorite'::TEXT as activity_type,
        fa.property_id,
        fa.created_at as activity_date,
        NULL::INTEGER as rating,
        fa.action as notes,
        NULL::TEXT as visit_status
    FROM public.favorite_activity fa
    WHERE fa.client_id = p_client_id AND fa.tenant_id = p_tenant_id
    
    UNION ALL
    
    SELECT 
        'visit'::TEXT as activity_type,
        v.property_id,
        v.visit_date as activity_date,
        v.rating,
        COALESCE(v.client_notes, v.realtor_notes) as notes,
        v.visit_status
    FROM public.visits v
    WHERE v.client_id = p_client_id AND v.tenant_id = p_tenant_id
    
    ORDER BY activity_date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Función para actualizar updated_at automáticamente (si no existe)
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 10. Triggers para actualizar updated_at
CREATE TRIGGER update_visits_updated_at 
    BEFORE UPDATE ON public.visits 
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- 11. Comentarios para documentación
COMMENT ON TABLE public.visits IS 'Visitas programadas y realizadas a propiedades';
COMMENT ON TABLE public.favorite_activity IS 'Actividad de favoritos de clientes (agregar, quitar, ver)';
COMMENT ON COLUMN public.visits.visit_status IS 'Estado de la visita: scheduled, completed, cancelled, no_show';
COMMENT ON COLUMN public.visits.rating IS 'Calificación del cliente (1-5) después de la visita';
COMMENT ON COLUMN public.favorite_activity.action IS 'Acción realizada: added, removed, viewed';
