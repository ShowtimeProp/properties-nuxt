export default defineEventHandler(async (event) => {
  // Datos mock para que el mapa funcione temporalmente
  const mockGeoJSON = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {
          "id": "mock-1",
          "title": "Casa en Mar del Plata",
          "price": "$150,000",
          "tipo_operacion": "VENTA",
          "estado": "DISPONIBLE"
        },
        "geometry": {
          "type": "Point",
          "coordinates": [-57.5575, -38.0023]
        }
      },
      {
        "type": "Feature", 
        "properties": {
          "id": "mock-2",
          "title": "Departamento Centro",
          "price": "$80,000",
          "tipo_operacion": "VENTA",
          "estado": "DISPONIBLE"
        },
        "geometry": {
          "type": "Point",
          "coordinates": [-57.5500, -38.0000]
        }
      }
    ]
  }
  
  return mockGeoJSON
})
