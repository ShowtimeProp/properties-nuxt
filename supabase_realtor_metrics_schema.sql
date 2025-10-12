-- =====================================================
-- ESQUEMA CRM PARA REALTORS - MÉTRICAS Y DASHBOARD
-- =====================================================

-- Tabla de métricas del realtor
CREATE TABLE IF NOT EXISTS realtor_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  date DATE DEFAULT CURRENT_DATE,
  total_leads INTEGER DEFAULT 0,
  active_leads INTEGER DEFAULT 0,
  converted_leads INTEGER DEFAULT 0,
  revenue DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices únicos
  UNIQUE(realtor_id, date)
);

-- Tabla de pipeline simple para leads
CREATE TABLE IF NOT EXISTS lead_pipeline (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES agent_leads(id) ON DELETE CASCADE,
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  stage VARCHAR(50) DEFAULT 'new' CHECK (stage IN ('new', 'contacted', 'qualified', 'proposal', 'closed')),
  probability INTEGER DEFAULT 10 CHECK (probability >= 0 AND probability <= 100),
  estimated_value DECIMAL(10,2),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  INDEX idx_lead_pipeline_realtor (realtor_id),
  INDEX idx_lead_pipeline_stage (stage),
  INDEX idx_lead_pipeline_activity (last_activity)
);

-- Tabla de plantillas de email
CREATE TABLE IF NOT EXISTS email_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  template_type VARCHAR(50) DEFAULT 'general' CHECK (template_type IN ('general', 'follow_up', 'proposal', 'closing')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  INDEX idx_email_templates_realtor (realtor_id),
  INDEX idx_email_templates_type (template_type)
);

-- Tabla de campañas de email
CREATE TABLE IF NOT EXISTS email_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  template_id UUID REFERENCES email_templates(id) ON DELETE SET NULL,
  lead_id UUID REFERENCES agent_leads(id) ON DELETE CASCADE,
  campaign_name VARCHAR(255),
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed')),
  sent_at TIMESTAMP WITH TIME ZONE,
  delivered_at TIMESTAMP WITH TIME ZONE,
  opened_at TIMESTAMP WITH TIME ZONE,
  clicked_at TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  INDEX idx_email_campaigns_realtor (realtor_id),
  INDEX idx_email_campaigns_status (status),
  INDEX idx_email_campaigns_sent (sent_at)
);

-- Tabla de actividades del realtor
CREATE TABLE IF NOT EXISTS realtor_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  lead_id UUID REFERENCES agent_leads(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('call', 'email', 'meeting', 'proposal', 'contract', 'note')),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  activity_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  duration_minutes INTEGER,
  outcome VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Índices
  INDEX idx_realtor_activities_realtor (realtor_id),
  INDEX idx_realtor_activities_lead (lead_id),
  INDEX idx_realtor_activities_type (activity_type),
  INDEX idx_realtor_activities_date (activity_date)
);

-- =====================================================
-- FUNCIONES DE UTILIDAD
-- =====================================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- TRIGGERS PARA UPDATED_AT
-- =====================================================

-- Triggers para realtor_metrics
DROP TRIGGER IF EXISTS update_realtor_metrics_updated_at ON realtor_metrics;
CREATE TRIGGER update_realtor_metrics_updated_at
    BEFORE UPDATE ON realtor_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para lead_pipeline
DROP TRIGGER IF EXISTS update_lead_pipeline_updated_at ON lead_pipeline;
CREATE TRIGGER update_lead_pipeline_updated_at
    BEFORE UPDATE ON lead_pipeline
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para email_templates
DROP TRIGGER IF EXISTS update_email_templates_updated_at ON email_templates;
CREATE TRIGGER update_email_templates_updated_at
    BEFORE UPDATE ON email_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para email_campaigns
DROP TRIGGER IF EXISTS update_email_campaigns_updated_at ON email_campaigns;
CREATE TRIGGER update_email_campaigns_updated_at
    BEFORE UPDATE ON email_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para realtor_activities
DROP TRIGGER IF EXISTS update_realtor_activities_updated_at ON realtor_activities;
CREATE TRIGGER update_realtor_activities_updated_at
    BEFORE UPDATE ON realtor_activities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE realtor_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_pipeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE realtor_activities ENABLE ROW LEVEL SECURITY;

-- Políticas para realtor_metrics
DROP POLICY IF EXISTS "Realtors can view own metrics" ON realtor_metrics;
CREATE POLICY "Realtors can view own metrics" ON realtor_metrics
    FOR SELECT USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

DROP POLICY IF EXISTS "Realtors can insert own metrics" ON realtor_metrics;
CREATE POLICY "Realtors can insert own metrics" ON realtor_metrics
    FOR INSERT WITH CHECK (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

DROP POLICY IF EXISTS "Realtors can update own metrics" ON realtor_metrics;
CREATE POLICY "Realtors can update own metrics" ON realtor_metrics
    FOR UPDATE USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

-- Políticas para lead_pipeline
DROP POLICY IF EXISTS "Realtors can manage own pipeline" ON lead_pipeline;
CREATE POLICY "Realtors can manage own pipeline" ON lead_pipeline
    FOR ALL USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

-- Políticas para email_templates
DROP POLICY IF EXISTS "Realtors can manage own email templates" ON email_templates;
CREATE POLICY "Realtors can manage own email templates" ON email_templates
    FOR ALL USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

-- Políticas para email_campaigns
DROP POLICY IF EXISTS "Realtors can manage own email campaigns" ON email_campaigns;
CREATE POLICY "Realtors can manage own email campaigns" ON email_campaigns
    FOR ALL USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

-- Políticas para realtor_activities
DROP POLICY IF EXISTS "Realtors can manage own activities" ON realtor_activities;
CREATE POLICY "Realtors can manage own activities" ON realtor_activities
    FOR ALL USING (
        realtor_id = (auth.jwt() ->> 'tenant_id')::uuid
    );

-- =====================================================
-- FUNCIONES DE DASHBOARD
-- =====================================================

-- Función para obtener métricas del realtor
CREATE OR REPLACE FUNCTION get_realtor_metrics(p_realtor_id UUID, p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    total_leads BIGINT,
    active_leads BIGINT,
    converted_leads BIGINT,
    revenue DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT lp.lead_id) as total_leads,
        COUNT(DISTINCT CASE WHEN lp.stage NOT IN ('closed') THEN lp.lead_id END) as active_leads,
        COUNT(DISTINCT CASE WHEN lp.stage = 'closed' THEN lp.lead_id END) as converted_leads,
        COALESCE(SUM(CASE WHEN lp.stage = 'closed' THEN lp.estimated_value ELSE 0 END), 0) as revenue
    FROM lead_pipeline lp
    WHERE lp.realtor_id = p_realtor_id
    AND DATE(lp.created_at) <= p_date;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener leads por stage
CREATE OR REPLACE FUNCTION get_leads_by_stage(p_realtor_id UUID)
RETURNS TABLE (
    stage VARCHAR(50),
    lead_count BIGINT,
    total_value DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lp.stage,
        COUNT(lp.id) as lead_count,
        COALESCE(SUM(lp.estimated_value), 0) as total_value
    FROM lead_pipeline lp
    WHERE lp.realtor_id = p_realtor_id
    GROUP BY lp.stage
    ORDER BY 
        CASE lp.stage
            WHEN 'new' THEN 1
            WHEN 'contacted' THEN 2
            WHEN 'qualified' THEN 3
            WHEN 'proposal' THEN 4
            WHEN 'closed' THEN 5
        END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener actividades recientes
CREATE OR REPLACE FUNCTION get_recent_activities(p_realtor_id UUID, p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    id UUID,
    lead_name VARCHAR(255),
    activity_type VARCHAR(50),
    title VARCHAR(255),
    activity_date TIMESTAMP WITH TIME ZONE,
    outcome VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ra.id,
        al.name as lead_name,
        ra.activity_type,
        ra.title,
        ra.activity_date,
        ra.outcome
    FROM realtor_activities ra
    JOIN agent_leads al ON ra.lead_id = al.id
    WHERE ra.realtor_id = p_realtor_id
    ORDER BY ra.activity_date DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- COMENTARIOS EN TABLAS
-- =====================================================

COMMENT ON TABLE realtor_metrics IS 'Métricas diarias de performance del realtor';
COMMENT ON TABLE lead_pipeline IS 'Pipeline de leads con stages y probabilidades';
COMMENT ON TABLE email_templates IS 'Plantillas de email personalizables por realtor';
COMMENT ON TABLE email_campaigns IS 'Campañas de email enviadas a leads';
COMMENT ON TABLE realtor_activities IS 'Actividades y notas del realtor con leads';

COMMENT ON COLUMN lead_pipeline.stage IS 'Etapa del lead: new, contacted, qualified, proposal, closed';
COMMENT ON COLUMN lead_pipeline.probability IS 'Probabilidad de cierre (0-100%)';
COMMENT ON COLUMN email_campaigns.status IS 'Estado del email: pending, sent, delivered, opened, clicked, bounced, failed';
COMMENT ON COLUMN realtor_activities.activity_type IS 'Tipo de actividad: call, email, meeting, proposal, contract, note';
