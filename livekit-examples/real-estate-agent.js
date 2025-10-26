import { Room, RoomEvent, RemoteParticipant, RemoteTrack, Track } from 'livekit-client';

// Configuración de LiveKit
const LIVEKIT_URL = 'https://lkit.showtimeprop.com';
const LIVEKIT_API_KEY = 'z7KC/QRN0QxHLAmGKaJl26Cv';
const LIVEKIT_API_SECRET = 'r4uo2upnbN64dr76bXI8P4ITcdxP8qdK';

// Función para obtener token real del backend
async function getTokenFromBackend(roomName, participantName) {
  try {
    const response = await fetch('/api/livekit/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        roomName: roomName,
        participantName: participantName
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('✅ Token obtenido del backend');
    return data;
  } catch (error) {
    console.error('❌ Error obteniendo token:', error);
    throw error;
  }
}

// Función para buscar propiedades en Qdrant usando búsqueda semántica
async function searchProperties(query) {
  try {
    console.log('🔍 Buscando propiedades en Qdrant con búsqueda semántica:', query);
    
    // Llamar al endpoint real de FastAPI que usa OpenAI embeddings
    const response = await fetch('https://fapi.showtimeprop.com/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        filters: {},
        top_k: 5
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Encontradas ${data?.length || 0} propiedades con búsqueda semántica`);
    
    return data || [];
  } catch (error) {
    console.error('❌ Error buscando propiedades:', error);
    return [];
  }
}

// Agente Inmobiliario Inteligente
class RealEstateAgent {
  constructor() {
    this.room = new Room();
    this.setupEventListeners();
    this.conversationHistory = [];
  }

  setupEventListeners() {
    // Escuchar cuando se conecta al room
    this.room.on(RoomEvent.Connected, () => {
      console.log('🏠 Agente Inmobiliario conectado al room:', this.room.name);
      
      // Esperar un poco para que se inicialice completamente
      setTimeout(() => {
        try {
          console.log('📊 Información del room:', {
            name: this.room.name,
            participants: this.room.participants?.size || 0,
            localParticipant: this.room.localParticipant?.identity || 'N/A'
          });
          
          // Enviar mensaje de bienvenida
          this.sendWelcomeMessage();
          
          // Emitir evento personalizado para actualizar la UI
          this.emitRoomUpdate();
        } catch (error) {
          console.error('❌ Error en evento Connected:', error);
        }
      }, 100);
    });

    // Escuchar cuando se desconecta
    this.room.on(RoomEvent.Disconnected, (reason) => {
      console.log('❌ Agente Inmobiliario desconectado:', reason);
      this.emitRoomUpdate();
    });

    // Escuchar cuando llega un participante
    this.room.on(RoomEvent.ParticipantConnected, (participant) => {
      console.log('👤 Cliente conectado:', participant.identity);
      console.log('📊 Total participantes:', this.room.participants?.size || 0);
      this.setupParticipantListeners(participant);
      this.emitRoomUpdate();
    });

    // Escuchar cuando se va un participante
    this.room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      console.log('👋 Cliente desconectado:', participant.identity);
      console.log('📊 Total participantes:', this.room.participants?.size || 0);
      this.emitRoomUpdate();
    });

    // Escuchar mensajes de datos del cliente
    this.room.on(RoomEvent.DataReceived, async (payload, participant) => {
      try {
        const message = new TextDecoder().decode(payload);
        console.log('💬 Mensaje del cliente:', participant.identity, message);
        
        // Agregar a historial de conversación
        this.conversationHistory.push({
          sender: participant.identity,
          message: message,
          timestamp: new Date()
        });
        
        // Procesar mensaje y responder
        await this.processMessage(message, participant);
        
      } catch (error) {
        console.error('❌ Error procesando mensaje:', error);
      }
    });
  }

  setupParticipantListeners(participant) {
    // Escuchar cuando el participante publica un track
    participant.on(RemoteParticipant.TrackPublished, (publication) => {
      console.log('📢 Cliente publicó track:', publication.trackName);
    });

    // Escuchar cuando el participante deja de publicar
    participant.on(RemoteParticipant.TrackUnpublished, (publication) => {
      console.log('🔇 Cliente dejó de publicar:', publication.trackName);
    });
  }

  // Enviar mensaje de bienvenida
  async sendWelcomeMessage() {
    const welcomeMessage = `¡Hola! 👋 Soy tu agente inmobiliario inteligente. 

🏠 Puedo ayudarte a encontrar la propiedad perfecta en Mar del Plata.

¿Qué estás buscando? Por ejemplo:
• "Busco un departamento de 2 ambientes cerca del mar"
• "Quiero una casa con jardín para alquilar"
• "Necesito algo económico en el centro"

¡Cuéntame qué necesitas! 🏡`;
    
    await this.sendMessage(welcomeMessage);
  }

  // Procesar mensaje del cliente y generar respuesta
  async processMessage(message, participant) {
    try {
      console.log('🧠 Procesando mensaje:', message);
      
      // Analizar la intención del mensaje
      const intent = this.analyzeIntent(message);
      console.log('🎯 Intención detectada:', intent);
      
      let response = '';
      
      switch (intent.type) {
        case 'search_properties':
          response = await this.handlePropertySearch(intent.query);
          break;
        case 'greeting':
          response = this.handleGreeting();
          break;
        case 'help':
          response = this.handleHelp();
          break;
        default:
          response = this.handleGeneralQuery(message);
      }
      
      // Enviar respuesta
      await this.sendMessage(response);
      
    } catch (error) {
      console.error('❌ Error procesando mensaje:', error);
      await this.sendMessage('Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?');
    }
  }

  // Analizar la intención del mensaje
  analyzeIntent(message) {
    const lowerMessage = message.toLowerCase();
    
    // Detectar búsqueda de propiedades
    const searchKeywords = ['busco', 'buscar', 'necesito', 'quiero', 'departamento', 'casa', 'alquiler', 'venta', 'ambientes'];
    const hasSearchIntent = searchKeywords.some(keyword => lowerMessage.includes(keyword));
    
    if (hasSearchIntent) {
      return {
        type: 'search_properties',
        query: message
      };
    }
    
    // Detectar saludo
    const greetingKeywords = ['hola', 'buenos', 'buenas', 'saludos', 'hi', 'hello'];
    const hasGreeting = greetingKeywords.some(keyword => lowerMessage.includes(keyword));
    
    if (hasGreeting) {
      return {
        type: 'greeting',
        query: message
      };
    }
    
    // Detectar ayuda
    const helpKeywords = ['ayuda', 'help', 'qué puedes', 'cómo funciona'];
    const hasHelp = helpKeywords.some(keyword => lowerMessage.includes(keyword));
    
    if (hasHelp) {
      return {
        type: 'help',
        query: message
      };
    }
    
    return {
      type: 'general',
      query: message
    };
  }

  // Manejar búsqueda de propiedades
  async handlePropertySearch(query) {
    try {
      const properties = await searchProperties(query);
      
      if (properties.length === 0) {
        return `🔍 No encontré propiedades que coincidan con tu búsqueda: "${query}"

¿Podrías ser más específico? Por ejemplo:
• "Departamento 2 ambientes cerca del mar"
• "Casa con jardín para alquilar"
• "Algo económico en el centro"

¡Estoy aquí para ayudarte! 🏠`;
      }
      
      let response = `🎯 Encontré ${properties.length} propiedades que podrían interesarte:\n\n`;
      
      properties.forEach((prop, index) => {
        response += `${index + 1}. **${prop.title}**\n`;
        response += `   💰 Precio: $${prop.price.toLocaleString()}\n`;
        response += `   📍 Dirección: ${prop.address}\n`;
        response += `   🛏️ Ambientes: ${prop.bedrooms}\n`;
        response += `   🚿 Baños: ${prop.bathrooms}\n`;
        response += `   📐 Área: ${prop.area_m2}m²\n`;
        response += `   📋 Tipo: ${prop.tipo_operacion}\n\n`;
      });
      
      response += `¿Te interesa alguna de estas propiedades? Puedo darte más detalles o buscar otras opciones. 🏡`;
      
      return response;
      
    } catch (error) {
      console.error('❌ Error en búsqueda de propiedades:', error);
      return 'Lo siento, hubo un error buscando propiedades. ¿Podrías intentar de nuevo?';
    }
  }

  // Manejar saludo
  handleGreeting() {
    return `¡Hola! 👋 

Soy tu agente inmobiliario inteligente y estoy aquí para ayudarte a encontrar la propiedad perfecta en Mar del Plata.

🏠 ¿Qué estás buscando hoy?`;
  }

  // Manejar solicitud de ayuda
  handleHelp() {
    return `¡Por supuesto! Te puedo ayudar con:

🔍 **Búsqueda de propiedades**
• Departamentos y casas
• Alquiler y venta
• Por ubicación, precio, ambientes

💬 **Conversación natural**
• "Busco un departamento de 2 ambientes cerca del mar"
• "Quiero algo económico en el centro"
• "Necesito una casa con jardín"

📊 **Información detallada**
• Precios, ubicaciones, características
• Comparaciones entre propiedades

¿Qué te gustaría hacer? 🏡`;
  }

  // Manejar consultas generales
  handleGeneralQuery(message) {
    return `Entiendo que dices: "${message}"

Para ayudarte mejor, puedes preguntarme sobre:

🏠 **Propiedades disponibles**
• Departamentos y casas
• Alquiler y venta
• Por ubicación o características

🔍 **Búsquedas específicas**
• "Busco un departamento de 2 ambientes"
• "Quiero algo cerca del mar"
• "Necesito algo económico"

¿Qué estás buscando exactamente? 🏡`;
  }

  // Enviar mensaje al cliente
  async sendMessage(message) {
    try {
      if (this.room?.state === 'connected' && this.room?.localParticipant) {
        await this.room.localParticipant.publishData(
          new TextEncoder().encode(message),
          { reliable: true }
        );
        console.log('📤 Mensaje enviado:', message.substring(0, 50) + '...');
        return true;
      } else {
        console.log('❌ No conectado o sin participante local, no se puede enviar mensaje');
        return false;
      }
    } catch (error) {
      console.error('❌ Error enviando mensaje:', error);
      return false;
    }
  }

  // Conectar al room
  async connect(roomName = 'real-estate-room', participantName = 'real-estate-agent') {
    try {
      console.log('🚀 Conectando Agente Inmobiliario...');
      
      // Obtener token real del backend
      const tokenData = await getTokenFromBackend(roomName, participantName);
      
      // Conectar al room
      await this.room.connect(tokenData.url, tokenData.token, {
        participantName: participantName,
        roomName: roomName
      });

      console.log('✅ Agente Inmobiliario conectado exitosamente!');
      return true;
    } catch (error) {
      console.error('❌ Error conectando Agente Inmobiliario:', error);
      return false;
    }
  }

  // Desconectar del room
  async disconnect() {
    try {
      await this.room.disconnect();
      console.log('👋 Agente Inmobiliario desconectado');
    } catch (error) {
      console.error('❌ Error desconectando:', error);
    }
  }

  // Emitir actualización del room para la UI
  emitRoomUpdate() {
    try {
      const roomInfo = this.getRoomInfo();
      
      // Emitir evento personalizado
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('livekit-room-update', {
          detail: roomInfo
        }));
      }
    } catch (error) {
      console.error('❌ Error emitiendo actualización del room:', error);
    }
  }

  // Obtener información del room
  getRoomInfo() {
    try {
      return {
        name: this.room?.name || 'N/A',
        participants: this.room?.participants?.size || 0,
        isConnected: this.room?.state === 'connected',
        localParticipant: this.room?.localParticipant?.identity || 'N/A'
      };
    } catch (error) {
      console.error('❌ Error obteniendo información del room:', error);
      return {
        name: 'N/A',
        participants: 0,
        isConnected: false,
        localParticipant: 'N/A'
      };
    }
  }

  // Enviar mensaje de prueba
  async sendTestMessage(message = '¡Hola! Soy tu agente inmobiliario inteligente 🏠') {
    return await this.sendMessage(message);
  }
}

// Exportar para uso en otros archivos
export { RealEstateAgent };

// Si se ejecuta directamente, crear una instancia de prueba
if (typeof window !== 'undefined') {
  window.RealEstateAgent = RealEstateAgent;
  console.log('🏠 Agente Inmobiliario cargado. Usa: new RealEstateAgent()');
}
