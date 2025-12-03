# Modificar Agente para Manejar Alternativas

## Cambios Realizados en FastAPI

El endpoint `/search` ahora retorna información sobre alternativas cuando no hay resultados exactos pero sí hay propiedades similares disponibles.

### Formato de Respuesta

**Cuando hay resultados exactos** (comportamiento normal):
```json
[
  {
    "id": "...",
    "title": "...",
    ...
  }
]
```

**Cuando NO hay resultados exactos pero SÍ hay alternativas**:
```json
{
  "properties": [],
  "alternatives": [
    {
      "id": "...",
      "title": "...",
      ...
    }
  ],
  "message": "No encontré propiedades con exactamente 1 ambiente en La Perla, pero encontré 4 propiedades con 2 o 3 ambientes en la misma zona."
}
```

## Modificaciones Necesarias en el Agente

El archivo del agente está en: `Showy-Agent/showy-agent/src/agent.py`

### Función `search_properties`

Modificar la función para detectar cuando la respuesta es un objeto con `alternatives`:

```python
async def search_properties(self, context: RunContext, query: str) -> str:
    try:
        fastapi_url = os.getenv("FASTAPI_URL", "https://fapi.showtimeprop.com")
        logger.info(f"🔍 [HERRAMIENTA] Buscando propiedades con query: {query}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            top_k = 12
            response = await client.post(
                f"{fastapi_url}/search",
                json={"query": query, "top_k": top_k, "filters": {}},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                # ... manejo de errores existente ...
                return f"Disculpa, hubo un problema técnico..."
            
            data = response.json()
            
            # NUEVO: Detectar si hay alternativas disponibles
            if isinstance(data, dict) and "alternatives" in data:
                alternatives = data.get("alternatives", [])
                message = data.get("message", "No encontré propiedades exactas, pero tengo algunas alternativas.")
                
                if alternatives:
                    # Enviar alternativas al frontend
                    await self._send_properties_to_frontend(context, alternatives, query)
                    
                    # Generar respuesta sugerente
                    result_text = (
                        f"{message}\n\n"
                        f"Encontré {len(alternatives)} propiedades con 2 o 3 ambientes en la misma zona. "
                        f"¿Te gustaría que te muestre estas opciones o prefieres buscar en otra zona?"
                    )
                    
                    logger.info(f"✅ [HERRAMIENTA] Alternativas encontradas: {len(alternatives)} propiedades")
                    return result_text
                else:
                    return "Disculpa, no encontré propiedades que coincidan con tu búsqueda. ¿Podrías ser más específico?"
            
            # Comportamiento normal: lista de propiedades
            if isinstance(data, list):
                properties = data
            elif isinstance(data, dict) and "properties" in data:
                properties = data.get("properties", [])
            else:
                properties = []
            
            # ... resto del código existente ...
            
    except Exception as e:
        logger.error(f"❌ [HERRAMIENTA] Error inesperado: {e}")
        return "Disculpa, tuve un problema técnico buscando propiedades. ¿Podrías intentar de nuevo?"
```

### Instrucciones para Aplicar

1. Abrir `Showy-Agent/showy-agent/src/agent.py`
2. Buscar la función `search_properties`
3. Agregar la detección de alternativas después de `response.json()`
4. Probar con una búsqueda de "1 ambiente en La Perla" para verificar que sugiere alternativas

## Ejemplo de Interacción Esperada

**Usuario:** "Busco departamentos de 1 ambiente en La Perla"

**Agente:** "No encontré propiedades con exactamente 1 ambiente en La Perla, pero encontré 4 propiedades con 2 o 3 ambientes en la misma zona. ¿Te gustaría que te muestre estas opciones o prefieres buscar en otra zona?"

**Usuario:** "Sí, muéstrame las de 2 ambientes"

**Agente:** [Muestra las propiedades de 2 ambientes]

