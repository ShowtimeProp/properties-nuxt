#!/usr/bin/env python3
"""
Script para agregar el endpoint /properties/geojson al backend FastAPI
"""

import os
import re

def add_geojson_endpoint():
    """Agrega el endpoint /properties/geojson al archivo main.py"""
    
    # Leer el archivo actual
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar donde agregar el nuevo endpoint (después de los endpoints existentes)
    # Buscar el patrón de un endpoint existente para insertar después
    pattern = r'(@app\.get\("/properties/\{property_id\}"[^}]+}\s*async def[^}]+}\s*)\n'
    
    # Nuevo endpoint para geojson
    geojson_endpoint = '''
@app.get("/properties/geojson", summary="Get Properties by Viewport (BBOX)")
async def get_properties_geojson(
    bbox: str = Query(..., description="Bounding box as 'minx,miny,maxx,maxy'"),
    zoom: int = Query(13, description="Map zoom level"),
    limit: int = Query(1000, description="Maximum number of properties to return"),
    tenant_id: str = Query(None, description="Optional tenant ID to filter properties")
):
    """
    Get properties in GeoJSON format for a given viewport.
    If tenant_id is provided, filter by tenant. Otherwise, return all properties.
    """
    try:
        # Parse bbox
        bbox_parts = bbox.split(',')
        if len(bbox_parts) != 4:
            raise HTTPException(status_code=400, detail="Invalid bbox format. Use 'minx,miny,maxx,maxy'")
        
        minx, miny, maxx, maxy = map(float, bbox_parts)
        
        print(f"Fetching properties in BBOX: [{minx}, {miny}, {maxx}, {maxy}] at zoom {zoom}")
        if tenant_id:
            print(f"Filtering by tenant: {tenant_id}")
        else:
            print("No tenant filter - returning all properties")
        
        # Query Qdrant for properties in the bounding box
        # If tenant_id is provided, filter by tenant, otherwise get all
        if tenant_id:
            # Filter by tenant_id if provided
            results = qdrant_cli.search(
                collection_name=settings["collection_name"],
                query_vector=[0] * 384,  # Dummy vector for spatial search
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="tenant_id",
                            match=models.MatchValue(value=tenant_id)
                        ),
                        models.FieldCondition(
                            key="latitude",
                            range=models.Range(
                                gte=miny,
                                lte=maxy
                            )
                        ),
                        models.FieldCondition(
                            key="longitude", 
                            range=models.Range(
                                gte=minx,
                                lte=maxx
                            )
                        )
                    ]
                ),
                limit=limit
            )
        else:
            # Get all properties in the bounding box (no tenant filter)
            results = qdrant_cli.search(
                collection_name=settings["collection_name"],
                query_vector=[0] * 384,  # Dummy vector for spatial search
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="latitude",
                            range=models.Range(
                                gte=miny,
                                lte=maxy
                            )
                        ),
                        models.FieldCondition(
                            key="longitude", 
                            range=models.Range(
                                gte=minx,
                                lte=maxx
                            )
                        )
                    ]
                ),
                limit=limit
            )
        
        print(f"Qdrant returned {len(results)} properties")
        
        # Convert to GeoJSON format
        features = []
        for result in results:
            payload = result.payload
            lat = payload.get('latitude')
            lng = payload.get('longitude')
            
            if lat is None or lng is None:
                continue
                
            print(f"Property {payload.get('id')}: lat={lat}, lng={lng}")
            
            feature = {
                "type": "Feature",
                "id": payload.get('id'),
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": {
                    "id": payload.get('id'),
                    "title": payload.get('title', ''),
                    "price": payload.get('price', 0),
                    "address": payload.get('address', ''),
                    "property_type": payload.get('property_type', ''),
                    "tipo_operacion": payload.get('tipo_operacion', ''),
                    "bedrooms": payload.get('bedrooms', 0),
                    "bathrooms": payload.get('bathrooms', 0),
                    "area_m2": payload.get('area_m2', 0),
                    "images": payload.get('images', [])
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        print(f"Returning {len(features)} properties in GeoJSON format")
        return geojson
        
    except Exception as e:
        print(f"Error in get_properties_geojson: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching properties: {str(e)}")

'''
    
    # Insertar el nuevo endpoint después del endpoint de properties/{property_id}
    if re.search(pattern, content):
        new_content = re.sub(pattern, r'\1' + geojson_endpoint + '\n', content)
    else:
        # Si no encuentra el patrón, agregar al final antes del último bloque
        new_content = content + geojson_endpoint
    
    # Escribir el archivo modificado
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Endpoint /properties/geojson agregado exitosamente")
    print("📝 El endpoint ahora soporta:")
    print("   - Sin tenant_id: Devuelve TODAS las propiedades")
    print("   - Con tenant_id: Filtra por tenant específico")
    print("   - Filtrado por bounding box (lat/lng)")
    print("   - Formato GeoJSON para el mapa")

if __name__ == "__main__":
    add_geojson_endpoint()
