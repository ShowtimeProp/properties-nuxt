# Configurar Supabase MCP en Cursor

## 🚀 Instalación del Servidor MCP de Supabase

### 1. Instalar el servidor MCP
```bash
npm install -g @supabase/mcp-server
```

### 2. Configurar en Cursor

Agrega esto a tu archivo `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "@supabase/mcp-server",
        "--url", "https://tu-proyecto-id.supabase.co",
        "--anon-key", "tu-anon-key-aqui",
        "--service-role-key", "tu-service-role-key-aqui"
      ],
      "env": {
        "SUPABASE_URL": "https://tu-proyecto-id.supabase.co",
        "SUPABASE_ANON_KEY": "tu-anon-key-aqui",
        "SUPABASE_SERVICE_ROLE_KEY": "tu-service-role-key-aqui"
      }
    }
  }
}
```

### 3. Obtener las Claves de Supabase

1. Ve a tu proyecto en [Supabase Dashboard](https://supabase.com/dashboard)
2. Ve a **Settings** → **API**
3. Copia:
   - **Project URL**: `https://tu-proyecto-id.supabase.co`
   - **anon public**: Clave pública
   - **service_role**: Clave de servicio (¡MANTÉNLA SECRETA!)

### 4. Funciones Disponibles con MCP

Una vez configurado, podré:
- ✅ Consultar tablas directamente
- ✅ Verificar datos de usuarios
- ✅ Ejecutar queries SQL
- ✅ Verificar políticas RLS
- ✅ Monitorear logs de autenticación
- ✅ Debuggear problemas en tiempo real

### 5. Ejemplo de Configuración Completa

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "@supabase/mcp-server",
        "--url", "https://tqjvqjvqjvqjvqjvqjv.supabase.co",
        "--anon-key", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "--service-role-key", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      ]
    }
  }
}
```

### 6. Reiniciar Cursor

Después de configurar, reinicia Cursor para que cargue el servidor MCP.

### 7. Verificar Funcionamiento

Una vez configurado, podré hacer consultas como:
- "Verifica si existe el usuario biancannicolini@gmail.com en auth.users"
- "Muestra todos los realtores en la tabla realtors"
- "Verifica las políticas RLS de la tabla realtors"

## 🔒 Seguridad

- **NUNCA** subas el archivo `.cursor/mcp.json` a Git
- Agrega `.cursor/mcp.json` a tu `.gitignore`
- Usa variables de entorno para las claves en producción

## 🎯 Beneficios

- **Debug en tiempo real** de problemas de autenticación
- **Verificación automática** de datos en Supabase
- **Consultas directas** sin necesidad de screenshots
- **Diagnóstico rápido** de problemas de RLS
- **Monitoreo** de logs y errores
