#!/bin/bash

# Script para levantar FastAPI con todas las variables de entorno
# Copiar y pegar TODO esto en el servidor

# Limpiar contenedor viejo
docker rm -f fastapi-service 2>/dev/null || true
docker compose -f fastapi-stack.yml down 2>/dev/null || true

# Crear nuevo contenedor con TODAS las variables
docker run -d \
  --name fastapi-service \
  --restart unless-stopped \
  -p 8000:80 \
  -e QDRANT_HOST=http://212.85.20.219:6333 \
  -e QDRANT_API_KEY=be1414ca9972e6bd0c429aba3e379cd9 \
  -e OPENAI_API_KEY='PLACEHOLDER_OPENAI_KEY' \
  -e SUPABASE_URL=https://ugqqlnlmubedxpsepvgz.supabase.co \
  -e SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVncXFsbmxtdWJlZHhwc2Vwdmd6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTM0MjA0NiwiZXhwIjoyMDY2OTE4MDQ2fQ.k5j51MVgY0b16e2NznD5KRSQ0Fg4P5KcmOTpymZqbY' \
  -e COLLECTION_NAME=propertiesV3 \
  showtimeprop/fastapi-service:debug-v3

# Esperar 3 segundos
sleep 3

# Ver logs
echo "Verificando logs..."
docker logs fastapi-service

# Probar que funciona
echo -e "\n=== Probando endpoint ==="
curl http://localhost:8000/docs 2>/dev/null | head -20 || echo "No responde"

