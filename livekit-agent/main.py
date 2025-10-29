#!/usr/bin/env python3
"""
LiveKit Agent para ShowtimeProp - Agente Inmobiliario
Asistente virtual que ayuda a visitantes con búsqueda de propiedades
"""

import asyncio
import os
import logging
import httpx
import json
from typing import Optional
from datetime import datetime

from livekit.agents import (
    JobContext, 
    WorkerOptions, 
    cli, 
    llm, 
    stt, 
    tts,
    voice_assistant
)
from livekit import rtc
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.agents.voice_assistant.llm import LLMStream
from livekit.agents.voice_assistant.llm import LLMContext

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyAgent:
    """Agente inmobiliario especializado en búsqueda de propiedades"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_lead = None
        self.tenant_id = None
        
    async def initialize_agent(self, ctx: JobContext):
        """Inicializar el agente con configuración específica"""
        try:
            # Configurar STT (Speech-to-Text) en español
            stt_provider = stt.StreamAdapter(
                stt.Stream(
                    model="assemblyai/universal-streaming",
                    language="es-ES"  # Español
                )
            )
            
            # Configurar LLM (GPT-4 para análisis de intención)
            llm_provider = llm.LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                system_prompt=self._get_system_prompt()
            )
            
            # Configurar TTS (Text-to-Speech) con Eleven Labs en español
            tts_provider = tts.TTS(
                model="elevenlabs/spanish-pro",
                voice="spanish-pro",
                language="es"
            )
            
            # Crear el asistente de voz
            self.assistant = VoiceAssistant(
                stt=stt_provider,
                llm=llm_provider,
                tts=tts_provider,
                conversation_timeout=300,  # 5 minutos de timeout
                partial_results=True
            )
            
            logger.info("Agente inmobiliario inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agente: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Prompt del sistema para el agente inmobiliario"""
        return """
        Eres Showy, un asistente inmobiliario virtual especializado en ayudar a visitantes 
        a encontrar propiedades en Mar del Plata, Argentina.
        
        Tu personalidad:
        - Amigable, profesional y empático
        - Hablas español argentino natural
        - Eres proactivo y haces preguntas inteligentes
        - Tienes memoria de contexto y recuerdas respuestas anteriores
        
        Flujo de conversación optimizado:
        1. Saludo: "¡Hola! Soy Showy, tu asistente inmobiliario virtual. Veo que estás explorando propiedades en Mar del Plata. ¿Cómo te llamas?"
        2. Propósito: "¿Estás buscando para vivir, invertir, o ambos?"
        3. Tipo: "¿Qué tipo de propiedad te interesa? Casa, departamento, local comercial..."
        4. Transacción: "¿Venta, alquiler o alquiler temporario?"
        5. Mostrar propiedades según criterios
        6. Registro: "¿Quieres crear una cuenta para guardar propiedades en favoritos?"
        7. Refinamiento: Seguir mostrando propiedades si cambia criterios
        8. Urgencia: "¿Para cuándo necesitas encontrar algo? ¿Cuál es tu urgencia?"
        9. Condición: "¿Prefieres propiedades nuevas o usadas?"
        10. Contacto: "¿Podrías darme tu teléfono y email?"
        11. Seguimiento: "¿Desearías que te contacte Bianca personalmente?"
        
        Siempre mantén la conversación fluida y natural. Escucha activamente las necesidades del cliente.
        Si detectas que el usuario habla en otro idioma, responde en ese idioma.
        
        Al final de cada conversación, asegúrate de obtener:
        - Nombre completo del visitante
        - Email o teléfono de contacto
        - Tipo de propiedad buscada
        - Tipo de transacción (venta/alquiler/temporario)
        - Urgencia temporal
        - Propósito (inversión/personal/ambos)
        - Condición preferida (nueva/usada/en construcción)
        - Motivo de búsqueda
        
        Mantén la conversación fluida y natural.
        """
    
    async def process_user_input(self, ctx: JobContext, user_input: str) -> str:
        """Procesar input del usuario y generar respuesta"""
        try:
            # Agregar input del usuario al historial
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analizar intención del usuario
            intent = await self._analyze_intent(user_input)
            
            # Generar respuesta basada en la intención
            response = await self._generate_response(intent, user_input, ctx)
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando input del usuario: {e}")
            return "Disculpa, hubo un problema técnico. ¿Podrías repetir tu consulta?"
    
    async def _analyze_intent(self, user_input: str) -> dict:
        """Analizar la intención del usuario"""
        # Aquí podrías usar el LLM para análisis más sofisticado
        # Por ahora, análisis básico por palabras clave
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['hola', 'buenas', 'saludos']):
            return {"type": "greeting", "confidence": 0.9}
        elif any(word in user_input_lower for word in ['buscar', 'encontrar', 'propiedad', 'casa', 'departamento']):
            return {"type": "property_search", "confidence": 0.8}
        elif any(word in user_input_lower for word in ['precio', 'costo', 'valor']):
            return {"type": "price_inquiry", "confidence": 0.8}
        elif any(word in user_input_lower for word in ['visita', 'ver', 'mostrar']):
            return {"type": "schedule_visit", "confidence": 0.8}
        elif any(word in user_input_lower for word in ['contacto', 'llamar', 'email']):
            return {"type": "contact_request", "confidence": 0.8}
        else:
            return {"type": "general", "confidence": 0.5}
    
    async def _generate_response(self, intent: dict, user_input: str, ctx: JobContext = None) -> str:
        """Generar respuesta basada en la intención"""
        if intent["type"] == "greeting":
            return ("¡Hola! Soy Showy, tu asistente inmobiliario virtual. " 
                   "Estoy aquí para ayudarte a encontrar la propiedad perfecta en Mar del Plata. " 
                   "¿En qué puedo asistirte hoy?")
        
        elif intent["type"] == "property_search":
            # Buscar propiedades usando el FastAPI
            try:
                criteria = {
                    "query": user_input,
                    "top_k": 3
                }
                
                properties = await self.search_properties(criteria)
                
                if properties:
                    # Enviar propiedades encontradas como mensaje de datos
                    if ctx and ctx.room:
                        await self._send_properties_data(ctx, properties)
                    
                    return (f"¡Excelente! Encontré {len(properties)} propiedades que podrían interesarte. " 
                           "Te estoy enviando los detalles para que puedas verlas. " 
                           "¿Te gustaría que te ayude con alguna en particular?")
                else:
                    return ("Estoy buscando propiedades que coincidan con tu consulta. " 
                           "¿Podrías ser más específico sobre el tipo de propiedad o ubicación que buscas?")
                    
            except Exception as e:
                logger.error(f"Error buscando propiedades: {e}")
                return ("Disculpa, estoy teniendo problemas técnicos para buscar propiedades. " 
                       "¿Podrías intentar de nuevo o ser más específico en tu consulta?")
        
        elif intent["type"] == "price_inquiry":
            return ("Entiendo que te interesa conocer los precios. " 
                   "Los valores varían según la ubicación, tamaño y características de la propiedad. " 
                   "¿Podrías contarme tu presupuesto aproximado para poder mostrarte opciones adecuadas?")
        
        elif intent["type"] == "schedule_visit":
            return ("¡Excelente! Me parece genial que quieras programar una visita. " 
                   "Para coordinar esto, necesito algunos datos tuyos. " 
                   "¿Podrías darme tu nombre y un teléfono o email de contacto?")
        
        elif intent["type"] == "contact_request":
            return ("Por supuesto, estaré encantado de conectarte con uno de nuestros agentes. " 
                   "¿Podrías proporcionarme tu nombre completo y tu forma preferida de contacto?")
        
        else:
            return ("Entiendo tu consulta. Para poder ayudarte de la mejor manera, " 
                   "¿podrías ser más específico sobre lo que necesitas? " 
                   "Estoy aquí para asistirte con búsqueda de propiedades, precios, visitas y más.")
    
    async def save_conversation_to_crm(self, ctx: JobContext, conversation_data: dict):
        """Guardar conversación completa en Supabase CRM"""
        try:
            # URL del FastAPI para guardar en Supabase
            fastapi_url = os.getenv("FASTAPI_URL", "https://fapi.showtimeprop.com")
            
            # Preparar datos de la conversación
            crm_data = {
                "session_id": ctx.room.name,
                "realtor_id": self.tenant_id,
                "user_name": conversation_data.get("user_name"),
                "transcript": conversation_data.get("transcript", ""),
                "summary": conversation_data.get("summary", ""),
                "property_preferences": conversation_data.get("preferences", {}),
                "lead_score": conversation_data.get("lead_score", 0),
                "language": conversation_data.get("language", "es"),
                "status": "completed"
            }
            
            # Llamar al endpoint del FastAPI para guardar
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{fastapi_url}/crm/conversations",
                    json=crm_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info("Conversación guardada exitosamente en CRM")
                    return True
                else:
                    logger.error(f"Error guardando conversación: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error guardando conversación en CRM: {e}")
            return False

    async def save_lead_to_crm(self, lead_data: dict):
        """Guardar información del lead en el CRM"""
        try:
            # Aquí implementarías la lógica para guardar en Supabase
            logger.info(f"Guardando lead en CRM: {lead_data}")
            
            # Por ahora, solo log
            return True
            
        except Exception as e:
            logger.error(f"Error guardando lead en CRM: {e}")
            return False
    
    async def search_properties(self, criteria: dict) -> list:
        """Buscar propiedades basado en criterios usando FastAPI"""
        try:
            logger.info(f"Buscando propiedades con criterios: {criteria}")
            
            # URL del FastAPI
            fastapi_url = os.getenv("FASTAPI_URL", "https://fapi.showtimeprop.com")
            
            # Construir query de búsqueda
            query = criteria.get("query", "")
            if not query:
                # Construir query desde criterios individuales
                parts = []
                if criteria.get("property_type"):
                    parts.append(f"tipo {criteria['property_type']}")
                if criteria.get("location"):
                    parts.append(f"en {criteria['location']}")
                if criteria.get("price_range"):
                    parts.append(f"precio {criteria['price_range']}")
                if criteria.get("bedrooms"):
                    parts.append(f"{criteria['bedrooms']} dormitorios")
                
                query = " ".join(parts) if parts else "propiedades en Mar del Plata"
            
            # Llamar al endpoint de búsqueda semántica del FastAPI
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{fastapi_url}/properties/search",
                    json={
                        "query": query,
                        "filters": criteria.get("filters", {}),
                        "top_k": criteria.get("top_k", 5)
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    properties = data.get("properties", [])
                    logger.info(f"Encontradas {len(properties)} propiedades")
                    return properties
                else:
                    logger.error(f"Error en FastAPI: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error buscando propiedades: {e}")
            return []

    async def _send_properties_data(self, ctx: JobContext, properties: list):
        """Enviar propiedades encontradas como mensaje de datos"""
        try:
            # Preparar datos de propiedades para enviar
            properties_data = {
                "type": "properties_found",
                "count": len(properties),
                "properties": []
            }
            
            for prop in properties[:3]:  # Máximo 3 propiedades
                property_info = {
                    "id": prop.get("id", ""),
                    "title": prop.get("title", prop.get("description", "Propiedad")),
                    "price": prop.get("price", "Consultar"),
                    "location": prop.get("location", prop.get("address", "Mar del Plata")),
                    "type": prop.get("property_type", "Propiedad"),
                    "bedrooms": prop.get("bedrooms", ""),
                    "bathrooms": prop.get("bathrooms", ""),
                    "images": prop.get("images", [])[:3]  # Máximo 3 imágenes
                }
                properties_data["properties"].append(property_info)
            
            # Enviar como mensaje de datos
            data_message = json.dumps(properties_data)
            await ctx.room.local_participant.publish_data(
                data_message.encode('utf-8'),
                topic="properties"
            )
            
            logger.info(f"Enviadas {len(properties)} propiedades como datos")
            
        except Exception as e:
            logger.error(f"Error enviando propiedades como datos: {e}")

async def entrypoint(ctx: JobContext):
    """Punto de entrada principal del agente"""
    logger.info("Iniciando agente inmobiliario Showy...")
    
    try:
        # Crear instancia del agente
        agent = PropertyAgent()
        
        # Inicializar el agente
        await agent.initialize_agent(ctx)
        
        # Obtener el participante remoto (usuario)
        if not ctx.room.remote_participants:
            logger.warning("No hay participantes remotos en la sala")
            return
        
        participant = ctx.room.remote_participants[0]
        logger.info(f"Conectado con participante: {participant.identity}")
        
        # Iniciar el asistente de voz
        await agent.assistant.start(ctx.room, participant)
        
        # Mensaje de bienvenida
        await agent.assistant.say(
            "¡Hola! Soy Showy, tu asistente inmobiliario virtual. "
            "Estoy aquí para ayudarte a encontrar la propiedad perfecta en Mar del Plata. "
            "¿En qué puedo asistirte hoy?"
        )
        
        # Mantener el agente activo
        await asyncio.sleep(3600)  # 1 hora de sesión máxima
        
    except Exception as e:
        logger.error(f"Error en el agente: {e}")
        raise
    finally:
        logger.info("Agente inmobiliario finalizado")

if __name__ == "__main__":
    # Configurar opciones del worker
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm=True,
        max_retry_count=3
    )
    
    # Ejecutar el agente
    cli.run_app(worker_options)
