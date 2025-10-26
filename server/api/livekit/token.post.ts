import jwt from 'jsonwebtoken'

export default defineEventHandler(async (event) => {
  try {
    const { roomName, participantName } = await readBody(event)
    
    // Configuración de LiveKit
    const LIVEKIT_API_KEY = 'z7KC/QRN0QxHLAmGKaJl26Cv'
    const LIVEKIT_API_SECRET = 'r4uo2upnbN64dr76bXI8P4ITcdxP8qdK'
    
    // Validar parámetros
    if (!roomName || !participantName) {
      throw createError({
        statusCode: 400,
        statusMessage: 'roomName y participantName son requeridos'
      })
    }
    
    // Generar token JWT para LiveKit
    const token = jwt.sign(
      {
        iss: LIVEKIT_API_KEY,
        sub: participantName,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (60 * 60), // 1 hora
        video: {
          room: roomName,
          roomJoin: true,
          canPublish: true,
          canSubscribe: true,
          canPublishData: true
        }
      },
      LIVEKIT_API_SECRET,
      { algorithm: 'HS256' }
    )
    
    console.log('✅ Token generado para:', { roomName, participantName })
    
    return {
      token,
      roomName,
      participantName,
      url: 'https://lkit.showtimeprop.com'
    }
    
  } catch (error) {
    console.error('❌ Error generando token:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Error generando token: ' + error.message
    })
  }
})
