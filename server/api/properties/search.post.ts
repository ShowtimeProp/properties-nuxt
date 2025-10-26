import { QdrantClient } from '@qdrant/js-client-rest'

const QDRANT_HOST = 'http://212.85.20.219:6333'
const COLLECTION_NAME = 'propertiesV3'

const qdrantClient = new QdrantClient({ url: QDRANT_HOST })

export default defineEventHandler(async (event) => {
  try {
    const { query } = await readBody(event)
    
    console.log('🔍 Buscando propiedades con query:', query)
    
    if (!query || query.trim() === '') {
      return { properties: [] }
    }
    
    // Buscar propiedades en Qdrant
    // Por ahora, obtener todas las propiedades y filtrar
    const result = await qdrantClient.scroll(COLLECTION_NAME, {
      limit: 100,
      with_payload: true,
      with_vectors: false
    })
    
    console.log(`📦 Encontradas ${result[0].length} propiedades en total`)
    
    // Filtrar propiedades basado en la consulta (simplificado)
    const lowerQuery = query.toLowerCase()
    const filteredProperties = result[0]
      .map(record => ({
        id: record.payload.id,
        title: record.payload.title || '',
        price: record.payload.price,
        address: record.payload.address || '',
        bedrooms: record.payload.bedrooms,
        bathrooms: record.payload.bathrooms,
        area_m2: record.payload.area_m2,
        tipo_operacion: record.payload.tipo_operacion || 'venta',
        images: record.payload.images_array || [],
        lat: record.payload.lat,
        lng: record.payload.lng
      }))
      .filter(prop => 
        prop.title.toLowerCase().includes(lowerQuery) ||
        prop.address?.toLowerCase().includes(lowerQuery) ||
        prop.tipo_operacion?.toLowerCase().includes(lowerQuery) ||
        (lowerQuery.includes('2') && prop.bedrooms === 2) ||
        (lowerQuery.includes('3') && prop.bedrooms === 3) ||
        (lowerQuery.includes('departamento') && prop.title.toLowerCase().includes('departamento')) ||
        (lowerQuery.includes('casa') && prop.title.toLowerCase().includes('casa')) ||
        (lowerQuery.includes('jardín') || lowerQuery.includes('jardin')) ||
        (lowerQuery.includes('mar') || lowerQuery.includes('cerca del'))
      )
      .slice(0, 5) // Limitar a 5 resultados
    
    console.log(`✅ Encontradas ${filteredProperties.length} propiedades filtradas`)
    
    return { properties: filteredProperties }
    
  } catch (error) {
    console.error('❌ Error buscando propiedades:', error)
    return { properties: [] }
  }
})
