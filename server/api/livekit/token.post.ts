import jwt from 'jsonwebtoken'

export default defineEventHandler(async (event) => {
  try {
    const { roomName, participantName } = await readBody(event)
    const config = useRuntimeConfig()
    
    // Configuración de LiveKit desde variables de entorno
    const LIVEKIT_API_KEY = config.livekitApiKey || process.env.LIVEKIT_API_KEY
    const LIVEKIT_API_SECRET = config.livekitApiSecret || process.env.LIVEKIT_API_SECRET
    const LIVEKIT_URL = config.livekitUrl || process.env.LIVEKIT_URL || 'wss://timbre-ai-uy9i2xcb.livekit.cloud'
    
    if (!LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
      throw createError({
        statusCode: 500,
        statusMessage: 'LiveKit API credentials no configuradas'
      })
    }
    
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
      url: LIVEKIT_URL
    }
    
  } catch (error) {
    console.error('❌ Error generando token:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Error generando token: ' + error.message
    })
  }
})
