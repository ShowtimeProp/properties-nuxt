# GitHub Actions Workflows

Este directorio contiene los workflows de GitHub Actions para automatizar el despliegue.

## Build FastAPI Docker Image

El workflow `build-fastapi.yml` construye y publica automáticamente la imagen Docker de FastAPI cuando hay cambios en el directorio `fastapi-service/`.

### Configuración Requerida

Para que el workflow funcione, necesitas configurar los siguientes **Secrets** en GitHub:

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Haz clic en "New repository secret"
4. Agrega estos dos secrets:

#### `DOCKERHUB_USERNAME`
- **Valor:** Tu nombre de usuario de Docker Hub (ej: `showtimeprop`)

#### `DOCKERHUB_TOKEN`
- **Valor:** Tu token de acceso de Docker Hub
  - Ve a Docker Hub → Account Settings → Security → New Access Token
  - Crea un token con permisos de "Read & Write"
  - Copia el token y guárdalo como secret

### Tags Generados

El workflow genera los siguientes tags automáticamente:
- `main-<sha>` - Tag basado en el commit SHA
- `debug-v<YYYYMMDD>-<sha>` - Tag con fecha y SHA (ej: `debug-v20250102-abc123`)
- `latest` - Solo en la rama `main`

### Ejecución Manual

Puedes ejecutar el workflow manualmente desde:
- GitHub → Actions → Build and Push FastAPI Docker Image → Run workflow

### Ejemplo de Uso

Después de hacer push a `main` con cambios en `fastapi-service/`:
1. El workflow se ejecuta automáticamente
2. Construye la imagen Docker
3. La publica en Docker Hub con los tags correspondientes
4. Puedes actualizar el stack en Portainer con el nuevo tag

