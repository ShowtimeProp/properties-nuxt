# Guía rápida de comandos Git

## 1. Ver el historial de commits

```bash
git log
```
- Muestra todos los commits con detalles.
- Para salir, presiona `q`.

Compacto:
```bash
git log --oneline
```

---

## 2. Deshacer cambios

### a) Deshacer cambios NO guardados (antes de commit)
```bash
git checkout -- nombre-del-archivo
# O para todos los archivos:
git checkout -- .
```

### b) Deshacer el último commit (mantener cambios en archivos)
```bash
git reset --soft HEAD~1
```

### c) Deshacer el último commit y borrar los cambios
```bash
git reset --hard HEAD~1
```
**¡Cuidado! Esto borra los cambios de forma irreversible.**

---

## 3. Trabajar con ramas

Crear una nueva rama y cambiarte a ella:
```bash
git checkout -b nombre-de-la-rama
```

Cambiar de rama:
```bash
git checkout main
```

Subir una rama nueva al remoto:
```bash
git push -u origin nombre-de-la-rama
```

---

## 4. Ver el estado de tus archivos

```bash
git status
```

---

## 5. Ver diferencias entre archivos

```bash
git diff
```

---

## 6. Clonar un repositorio

```bash
git clone https://github.com/ShowtimeProp/properties-nuxt.git
```

---

## 7. Guardar y subir tus cambios

```bash
git add .
git commit -m "fix: Añade cache busting a la llamada de la API de propiedades"
git push
```

---

## 8. Configurar tu usuario y email

```bash
git config --global user.name "Alex Nicolini"
git config --global user.email "showtimeprop@gmail.com"
```

---

## 9. Ayuda rápida

```bash
git help <comando>
# Ejemplo:
git help log
```

---

**¡Recuerda!**
- Cada commit es un "punto de guardado" de tu proyecto.
- Puedes volver atrás, ver el historial y trabajar en equipo sin miedo a perder nada.
- Si tienes dudas, ¡usa `git status` y `git help`! 😉 