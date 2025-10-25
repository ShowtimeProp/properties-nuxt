#!/bin/bash

echo "🔧 Aplicando parche para endpoint /properties/geojson..."

# 1. Ir al directorio del backend
cd ~/fastapi-v3

# 2. Hacer backup
echo "📦 Creando backup..."
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)

# 3. Aplicar el parche
echo "🔨 Aplicando parche..."
python3 fix-geojson-endpoint.py

# 4. Verificar que el endpoint se agregó
echo "✅ Verificando que el endpoint se agregó..."
if grep -q "properties/geojson" main.py; then
    echo "✅ Endpoint /properties/geojson encontrado en main.py"
else
    echo "❌ Error: Endpoint no se agregó correctamente"
    exit 1
fi

# 5. Reconstruir la imagen Docker
echo "🐳 Reconstruyendo imagen Docker..."
docker build -t showtimeprop/fastapi-service:latest .

# 6. Subir a Docker Hub
echo "📤 Subiendo imagen a Docker Hub..."
docker push showtimeprop/fastapi-service:latest

echo "🎉 ¡Parche aplicado exitosamente!"
echo "📋 Próximos pasos:"
echo "   1. Ve a Portainer"
echo "   2. Redeploy el stack fastapi-re"
echo "   3. El endpoint /properties/geojson estará disponible"
echo "   4. El mapa debería cargar propiedades correctamente"
