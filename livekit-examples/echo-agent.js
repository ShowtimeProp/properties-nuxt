import { Room, RoomEvent, RemoteParticipant, RemoteTrack, Track } from 'livekit-client';

// Configuración de LiveKit
const LIVEKIT_URL = 'https://lkit.showtimeprop.com';
const LIVEKIT_API_KEY = 'z7KC/QRN0QxHLAmGKaJl26Cv';
const LIVEKIT_API_SECRET = 'r4uo2upnbN64dr76bXI8P4ITcdxP8qdK';

// Función para generar token (simplificada para testing)
function generateToken(roomName, participantName) {
  // En producción, esto debería hacerse en el backend
  // Por ahora usamos un token básico para testing
  return {
    token: 'test-token', // Token temporal para testing
    roomName: roomName,
    participantName: participantName
  };
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
    });

    // Escuchar cuando se desconecta
    this.room.on(RoomEvent.Disconnected, (reason) => {
      console.log('❌ Echo Agent desconectado:', reason);
    });

    // Escuchar cuando llega un participante
    this.room.on(RoomEvent.ParticipantConnected, (participant) => {
      console.log('👤 Participante conectado:', participant.identity);
      this.setupParticipantListeners(participant);
    });

    // Escuchar cuando se va un participante
    this.room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      console.log('👋 Participante desconectado:', participant.identity);
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
      
      // Generar token (en producción esto se hace en el backend)
      const tokenData = generateToken(roomName, participantName);
      
      // Conectar al room
      await this.room.connect(LIVEKIT_URL, tokenData.token, {
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

  // Obtener información del room
  getRoomInfo() {
    return {
      name: this.room.name,
      participants: this.room.participants.size,
      isConnected: this.room.state === 'connected'
    };
  }
}

// Exportar para uso en otros archivos
export { EchoAgent };

// Si se ejecuta directamente, crear una instancia de prueba
if (typeof window !== 'undefined') {
  window.EchoAgent = EchoAgent;
  console.log('🎯 Echo Agent cargado. Usa: new EchoAgent()');
}
