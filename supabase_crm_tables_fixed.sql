-- Script SQL CORREGIDO para crear las tablas del sistema CRM con Showy
-- Ejecutar en Supabase SQL Editor

-- 1. Tabla de conversaciones con Showy
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL, -- ID único de la sesión LiveKit
  user_name TEXT, -- Nombre del usuario (si se proporciona)
  transcript TEXT, -- Conversación completa
  summary TEXT, -- Resumen generado por IA
  property_preferences JSONB DEFAULT '{}', -- Preferencias extraídas
  lead_score INTEGER DEFAULT 0, -- Puntuación del lead (1-10)
  status TEXT DEFAULT 'active', -- 'active', 'completed', 'follow_up'
  language TEXT DEFAULT 'es', -- Idioma detectado
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabla de leads generados por conversaciones
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  realtor_id UUID REFERENCES realtors(id) ON DELETE CASCADE,
  contact_info JSONB DEFAULT '{}', -- {name, phone, email}
  property_preferences JSONB DEFAULT '{}', -- Preferencias estructuradas
  urgency TEXT, -- 'urgente', '1-3_meses', '6_meses+', 'sin_prisa'
  purpose TEXT, -- 'inversion', 'personal', 'ambos'
  transaction_type TEXT, -- 'venta', 'alquiler', 'alquiler_temporario'
  condition_preference TEXT, -- 'nueva', 'usada', 'en_construccion'
  lead_score INTEGER DEFAULT 0,
  status TEXT DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted'
  assigned_agent TEXT, -- Nombre del agente asignado
  next_action TEXT, -- Próxima acción recomendada
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabla de propiedades mostradas en conversaciones
CREATE TABLE IF NOT EXISTS conversation_properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  property_endpoint TEXT NOT NULL, -- ID/endpoint de la propiedad
  shown_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Cuándo se mostró
  user_reaction TEXT, -- 'interested', 'not_interested', 'maybe'
  notes TEXT -- Notas adicionales
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_conversations_realtor_id ON conversations(realtor_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_leads_realtor_id ON leads(realtor_id);
CREATE INDEX IF NOT EXISTS idx_leads_conversation_id ON leads(conversation_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_properties_conversation_id ON conversation_properties(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_properties_property_endpoint ON conversation_properties(property_endpoint);

-- RLS (Row Level Security) para multi-tenant
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_properties ENABLE ROW LEVEL SECURITY;

-- Políticas RLS CORREGIDAS para conversations
CREATE POLICY "realtors_can_view_own_conversations" ON conversations
  FOR SELECT USING (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

CREATE POLICY "realtors_can_insert_own_conversations" ON conversations
  FOR INSERT WITH CHECK (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

CREATE POLICY "realtors_can_update_own_conversations" ON conversations
  FOR UPDATE USING (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

-- Políticas RLS CORREGIDAS para leads
CREATE POLICY "realtors_can_view_own_leads" ON leads
  FOR SELECT USING (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

CREATE POLICY "realtors_can_insert_own_leads" ON leads
  FOR INSERT WITH CHECK (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

CREATE POLICY "realtors_can_update_own_leads" ON leads
  FOR UPDATE USING (realtor_id::text = (auth.jwt() ->> 'realtor_id'));

-- Políticas RLS CORREGIDAS para conversation_properties
CREATE POLICY "realtors_can_view_own_conversation_properties" ON conversation_properties
  FOR SELECT USING (
    conversation_id IN (
      SELECT id FROM conversations 
      WHERE realtor_id::text = (auth.jwt() ->> 'realtor_id')
    )
  );

CREATE POLICY "realtors_can_insert_own_conversation_properties" ON conversation_properties
  FOR INSERT WITH CHECK (
    conversation_id IN (
      SELECT id FROM conversations 
      WHERE realtor_id::text = (auth.jwt() ->> 'realtor_id')
    )
  );

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_conversations_updated_at 
  BEFORE UPDATE ON conversations 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at 
  BEFORE UPDATE ON leads 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios para documentación
COMMENT ON TABLE conversations IS 'Conversaciones completas con el agente Showy';
COMMENT ON TABLE leads IS 'Leads generados automáticamente desde conversaciones';
COMMENT ON TABLE conversation_properties IS 'Propiedades mostradas durante conversaciones';

COMMENT ON COLUMN conversations.session_id IS 'ID único de la sesión LiveKit';
COMMENT ON COLUMN conversations.transcript IS 'Conversación completa en texto';
COMMENT ON COLUMN conversations.summary IS 'Resumen generado por IA';
COMMENT ON COLUMN conversations.property_preferences IS 'Preferencias extraídas en formato JSON';
COMMENT ON COLUMN conversations.lead_score IS 'Puntuación del lead de 1 a 10';

COMMENT ON COLUMN leads.contact_info IS 'Información de contacto en formato JSON';
COMMENT ON COLUMN leads.property_preferences IS 'Preferencias estructuradas de propiedades';
COMMENT ON COLUMN leads.urgency IS 'Urgencia temporal del cliente';
COMMENT ON COLUMN leads.purpose IS 'Propósito de la búsqueda';
COMMENT ON COLUMN leads.transaction_type IS 'Tipo de transacción deseada';
COMMENT ON COLUMN leads.condition_preference IS 'Preferencia de condición de propiedad';
COMMENT ON COLUMN leads.next_action IS 'Próxima acción recomendada para el agente';
