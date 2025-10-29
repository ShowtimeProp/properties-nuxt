# REGLAS CRÍTICAS DE PRODUCCIÓN - NO MODIFICAR SIN PERMISO

## 🚫 REGLAS ABSOLUTAS:

### 1. **FASTAPI STACK - PROHIBIDO TOCAR**
- ❌ **NUNCA** modificar `fastapi-stack.yml` sin permiso explícito del usuario
- ❌ **NUNCA** sugerir cambios automáticos al stack
- ✅ **SOLO** sugerir cambios pero NO implementarlos
- ✅ El usuario maneja el stack directamente en Portainer
- ✅ Si hay problemas con API keys, SOLO sugerir qué cambiar, NO hacerlo

### 2. **AMBIENTE DE PRODUCCIÓN**
- ✅ **SIEMPRE** trabajar en producción (Vercel) NO en local
- ✅ **SIEMPRE** recordar que estamos en `bnicolini.showtimeprop.com`
- ✅ **SIEMPRE** hacer deploy a Vercel, NO usar `npm run dev`
- ✅ **SIEMPRE** probar en producción, NO en localhost

### 3. **API KEYS Y SECRETOS**
- ✅ **SIEMPRE** usar placeholders en código para GitHub
- ✅ **SIEMPRE** configurar keys reales en Vercel Environment Variables
- ✅ **SIEMPRE** recordar que el usuario maneja las keys del servidor

### 4. **COMUNICACIÓN**
- ✅ **SIEMPRE** preguntar antes de modificar archivos críticos
- ✅ **SIEMPRE** explicar qué va a pasar antes de hacer cambios
- ✅ **SIEMPRE** respetar las decisiones del usuario sobre infraestructura

## 📋 CHECKLIST ANTES DE CUALQUIER CAMBIO:
- [ ] ¿Es necesario modificar el stack de FastAPI? → **PREGUNTAR PRIMERO**
- [ ] ¿Estoy trabajando en producción o local? → **PRODUCCIÓN SIEMPRE**
- [ ] ¿Tengo permiso explícito del usuario? → **OBLIGATORIO**
- [ ] ¿Estoy respetando las reglas de seguridad? → **VERIFICAR**

---
**Fecha de creación:** $(date)
**Usuario:** Anico
**Estado:** ACTIVO - NO MODIFICAR SIN PERMISO
