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

// Echo Agent - Repite lo que escucha
class EchoAgent {
  constructor() {
    this.room = new Room();
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Escuchar cuando se conecta al room
    this.room.on(RoomEvent.Connected, () => {
      console.log('🎯 Echo Agent conectado al room:', this.room.name);
      
      // Esperar un poco para que se inicialice completamente
      setTimeout(() => {
        try {
          console.log('📊 Información del room:', {
            name: this.room.name,
            participants: this.room.participants?.size || 0,
            localParticipant: this.room.localParticipant?.identity || 'N/A'
          });
          
          // Emitir evento personalizado para actualizar la UI
          this.emitRoomUpdate();
        } catch (error) {
          console.error('❌ Error en evento Connected:', error);
        }
      }, 100);
    });

    // Escuchar cuando se desconecta
    this.room.on(RoomEvent.Disconnected, (reason) => {
      console.log('❌ Echo Agent desconectado:', reason);
      this.emitRoomUpdate();
    });

    // Escuchar cuando llega un participante
    this.room.on(RoomEvent.ParticipantConnected, (participant) => {
      console.log('👤 Participante conectado:', participant.identity);
      console.log('📊 Total participantes:', this.room.participants?.size || 0);
      this.setupParticipantListeners(participant);
      this.emitRoomUpdate();
    });

    // Escuchar cuando se va un participante
    this.room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      console.log('👋 Participante desconectado:', participant.identity);
      console.log('📊 Total participantes:', this.room.participants?.size || 0);
      this.emitRoomUpdate();
    });

    // Escuchar cuando llega un track de audio
    this.room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      console.log('🎵 Track de audio recibido de:', participant.identity);
      
      if (track.kind === Track.Kind.Audio) {
        // Reproducir el audio recibido
        const audioElement = track.attach();
        document.body.appendChild(audioElement);
        audioElement.play();
        
        // Simular "echo" - en un agente real aquí procesarías el audio
        console.log('🔄 Echo: Reproduciendo audio de', participant.identity);
      }
    });

    // Escuchar cuando llega un track de video
    this.room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      if (track.kind === Track.Kind.Video) {
        console.log('📹 Track de video recibido de:', participant.identity);
        const videoElement = track.attach();
        document.body.appendChild(videoElement);
        videoElement.play();
      }
    });

    // Escuchar mensajes de datos
    this.room.on(RoomEvent.DataReceived, (payload, participant) => {
      console.log('📨 Mensaje recibido de:', participant.identity, payload);
      
      // Responder con echo
      if (participant && participant !== this.room.localParticipant) {
        const echoMessage = `Echo: ${payload}`;
        this.room.localParticipant.publishData(
          new TextEncoder().encode(echoMessage),
          { reliable: true }
        );
        console.log('🔄 Echo enviado:', echoMessage);
      }
    });
  }

  setupParticipantListeners(participant) {
    // Escuchar cuando el participante publica un track
    participant.on(RemoteParticipant.TrackPublished, (publication) => {
      console.log('📢 Participante publicó track:', publication.trackName);
    });

    // Escuchar cuando el participante deja de publicar
    participant.on(RemoteParticipant.TrackUnpublished, (publication) => {
      console.log('🔇 Participante dejó de publicar:', publication.trackName);
    });
  }

  // Conectar al room
  async connect(roomName = 'echo-room', participantName = 'echo-agent') {
    try {
      console.log('🚀 Conectando Echo Agent...');
      
      // Obtener token real del backend
      const tokenData = await getTokenFromBackend(roomName, participantName);
      
      // Conectar al room
      await this.room.connect(tokenData.url, tokenData.token, {
        participantName: participantName,
        roomName: roomName
      });

      console.log('✅ Echo Agent conectado exitosamente!');
      return true;
    } catch (error) {
      console.error('❌ Error conectando Echo Agent:', error);
      return false;
    }
  }

  // Desconectar del room
  async disconnect() {
    try {
      await this.room.disconnect();
      console.log('👋 Echo Agent desconectado');
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
  async sendTestMessage(message = 'Hola desde Echo Agent!') {
    try {
      if (this.room?.state === 'connected' && this.room?.localParticipant) {
        await this.room.localParticipant.publishData(
          new TextEncoder().encode(message),
          { reliable: true }
        );
        console.log('📤 Mensaje enviado:', message);
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
}

// Exportar para uso en otros archivos
export { EchoAgent };

// Si se ejecuta directamente, crear una instancia de prueba
if (typeof window !== 'undefined') {
  window.EchoAgent = EchoAgent;
  console.log('🎯 Echo Agent cargado. Usa: new EchoAgent()');
}
