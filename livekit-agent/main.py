#!/usr/bin/env python3
"""
LiveKit Agent para ShowtimeProp - Agente Inmobiliario
Asistente virtual que ayuda a visitantes con búsqueda de propiedades
"""

import asyncio
import os
import logging
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
        
        Tu objetivo es:
        1. Saludar cordialmente al visitante
        2. Entender sus necesidades inmobiliarias
        3. Hacer preguntas relevantes sobre tipo de propiedad, ubicación, presupuesto
        4. Buscar propiedades que coincidan con sus criterios
        5. Programar visitas si es necesario
        6. Registrar la información del lead en el CRM
        
        Siempre sé amable, profesional y útil. Habla en español argentino natural.
        Si no entiendes algo, pide aclaración.
        
        Al final de cada conversación, asegúrate de obtener:
        - Nombre completo del visitante
        - Email o teléfono de contacto
        - Tipo de propiedad buscada
        - Ubicación preferida
        - Presupuesto aproximado
        
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
            response = await self._generate_response(intent, user_input)
            
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
    
    async def _generate_response(self, intent: dict, user_input: str) -> str:
        """Generar respuesta basada en la intención"""
        if intent["type"] == "greeting":
            return ("¡Hola! Soy Showy, tu asistente inmobiliario virtual. "
                   "Estoy aquí para ayudarte a encontrar la propiedad perfecta en Mar del Plata. "
                   "¿En qué puedo asistirte hoy?")
        
        elif intent["type"] == "property_search":
            return ("¡Perfecto! Me encanta ayudarte a encontrar tu próxima propiedad. "
                   "Para poder asistirte mejor, ¿podrías contarme qué tipo de propiedad estás buscando? "
                   "Por ejemplo: casa, departamento, local comercial, etc.")
        
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
        """Buscar propiedades basado en criterios"""
        try:
            # Aquí implementarías la búsqueda en Qdrant
            logger.info(f"Buscando propiedades con criterios: {criteria}")
            
            # Por ahora, retornar lista vacía
            return []
            
        except Exception as e:
            logger.error(f"Error buscando propiedades: {e}")
            return []

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
