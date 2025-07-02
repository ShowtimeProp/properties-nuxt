# Esquema Técnico y Modelo de Base de Datos para CRM Inmobiliario SaaS (Supabase)

> **Actualización:**
> - Se agregan los campos `email_confirmed`, `whatsapp_confirmed` y `fecha_contacto` a la tabla `users` para validar datos de contacto y registrar el primer contacto real.
> - Se agrega la tabla `showings` para registrar visitas a propiedades (fecha, hora, comentarios, etc.).

## Resumen del Proyecto

- SaaS inmobiliario multi-tenant para realtors (inmobiliarias y agentes).
- Cada realtor tiene su propio portal (subdominio o dominio propio), branding y clientes.
- Los clientes/favoritos solo guardan IDs o endpoints de propiedades externas (Postgres/Qdrant).
- Incluye: gestión de usuarios, favoritos, estadísticas, QR dinámicos, referidos, CRM, automatización y vectorización para IA.
- Preparado para integración con workflows (n8n), Qdrant y despliegue en Docker Swarm.

---

## Esquema de Tablas Sugerido

### 1. `realtors`
| Campo                | Tipo         | Descripción                                  |
|----------------------|-------------|----------------------------------------------|
| id                   | uuid (PK)   | Identificador único del realtor              |
| nombre               | text        | Nombre del realtor o inmobiliaria            |
| email                | text        | Email de contacto                            |
| branding             | jsonb       | Colores, logo, textos, etc.                  |
| subdominio           | text        | Subdominio asignado                          |
| dominio_personal     | text        | Dominio propio (opcional)                    |
| objetivo_mensual     | numeric     | Objetivo de ventas mensual                   |
| objetivo_anual       | numeric     | Objetivo de ventas anual                     |
| total_ganado         | numeric     | Total ganado                                 |
| total_comisiones     | numeric     | Total de comisiones                          |
| porcentaje_comision  | numeric     | % de comisión estándar                       |
| created_at           | timestamp   | Fecha de registro                            |

### 2. `users`
| Campo              | Tipo       | Descripción                                  |
|--------------------|-----------|----------------------------------------------|
| id                 | uuid (PK) | Identificador único del usuario/cliente      |
| email              | text      | Email del cliente                            |
| nombre             | text      | Nombre completo                              |
| whatsapp           | text      | WhatsApp                                     |
| realtor_id         | uuid (FK) | A qué realtor pertenece                      |
| referido_por       | uuid (FK) | Referido por (nullable, puede ser user o referente) |
| email_confirmed    | boolean   | Si el email fue validado                     |
| whatsapp_confirmed | boolean   | Si el WhatsApp fue validado                  |
| fecha_contacto     | timestamp | Fecha de primer contacto real                |
| created_at         | timestamp | Fecha de registro                            |

### 3. `favorites`
| Campo             | Tipo       | Descripción                                 |
|-------------------|-----------|---------------------------------------------|
| id                | uuid (PK) | Identificador único                         |
| user_id           | uuid (FK) | Usuario que marcó favorito                  |
| property_endpoint | text      | Endpoint o ID externo de la propiedad       |
| fecha             | timestamp | Fecha de favorito                           |

### 4. `visit_stats`
| Campo         | Tipo       | Descripción                                  |
|---------------|-----------|----------------------------------------------|
| id            | uuid (PK) | Identificador único                          |
| property_endpoint | text   | Endpoint/ID externo de la propiedad         |
| realtor_id    | uuid (FK) | Realtor dueño del portal                     |
| user_id       | uuid (FK) | Usuario (nullable)                           |
| fecha         | timestamp | Fecha de la visita                           |
| fuente        | text      | utm_source, utm_campaign, etc.               |
| qr_code_id    | uuid (FK) | Si vino de QR                                |
| referer_code  | text      | Código de referido (nullable)                |

### 5. `qr_codes`
| Campo         | Tipo       | Descripción                                  |
|---------------|-----------|----------------------------------------------|
| id            | uuid (PK) | Identificador único                          |
| realtor_id    | uuid (FK) | Realtor dueño del QR                         |
| tipo          | text      | cartel, referido, etc.                       |
| codigo        | text      | Código único del QR                          |
| url_actual    | text      | Endpoint actual asignado                     |
| historial     | jsonb     | Array de endpoints usados                    |
| activo        | boolean   | Si está activo                               |
| notas         | text      | Notas internas                               |

### 6. `referidos`
| Campo               | Tipo       | Descripción                                 |
|---------------------|-----------|---------------------------------------------|
| id                  | uuid (PK) | Identificador único                         |
| realtor_id          | uuid (FK) | Realtor dueño del referido                  |
| nombre_referente    | text      | Nombre del referente                        |
| codigo              | text      | Código único del referente                  |
| porcentaje_comision | numeric   | % de comisión para el referente             |
| total_referidos     | integer   | Total de referidos                          |
| total_ventas        | integer   | Total de ventas                             |

### 7. `crm_interactions`
| Campo         | Tipo       | Descripción                                  |
|---------------|-----------|----------------------------------------------|
| id            | uuid (PK) | Identificador único                          |
| user_id       | uuid (FK) | Cliente                                      |
| realtor_id    | uuid (FK) | Realtor                                      |
| tipo          | text      | nota, tarea, llamada, visita, doc, etc.      |
| descripcion   | text      | Descripción                                  |
| fecha         | timestamp | Fecha de la interacción                      |
| estado        | text      | to do, done, pendiente, etc.                 |
| checkpoint    | text      | Ej: "visitó propiedad", "oferta enviada"     |

### 8. `property_comments`
| Campo             | Tipo       | Descripción                                 |
|-------------------|-----------|---------------------------------------------|
| id                | uuid (PK) | Identificador único                         |
| user_id           | uuid (FK) | Cliente                                     |
| property_endpoint | text      | Endpoint/ID externo de la propiedad         |
| comentario        | text      | Comentario                                  |
| fecha             | timestamp | Fecha                                       |

### 9. `transactions`
| Campo             | Tipo       | Descripción                                 |
|-------------------|-----------|---------------------------------------------|
| id                | uuid (PK) | Identificador único                         |
| realtor_id        | uuid (FK) | Realtor                                     |
| user_id           | uuid (FK) | Cliente                                     |
| property_endpoint | text      | Propiedad vendida                           |
| monto             | numeric   | Monto de la operación                       |
| fecha             | timestamp | Fecha de la transacción                     |
| estado            | text      | cerrada, en curso, cancelada                |
| comision          | numeric   | Comisión ganada                             |
| notas             | text      | Notas internas                              |

### 10. `showings`
| Campo             | Tipo       | Descripción                                 |
|-------------------|-----------|---------------------------------------------|
| id                | uuid (PK) | Identificador único                         |
| user_id           | uuid (FK) | Cliente que visitó                          |
| realtor_id        | uuid (FK) | Realtor responsable                         |
| property_endpoint | text      | Propiedad visitada                          |
| fecha             | date      | Fecha de la visita                          |
| hora              | time      | Hora de la visita                           |
| comentarios       | text      | Comentarios de la visita (opcional)         |

---

## Sugerencias de Escalabilidad y Automatización
- **Multi-tenant:** Todas las tablas tienen `realtor_id` para aislar datos por realtor. Usa RLS en Supabase.
- **Vectorización:** Guarda textos libres (notas, comentarios, emails, docs) para vectorizar en Qdrant y usar IA personalizada por realtor.
- **Automatización:** Usa triggers/webhooks para notificar a n8n y automatizar tareas, generación de contratos, alertas, etc.
- **Analítica:** Guarda parámetros UTM, QR y referidos para medir campañas y performance de marketing.
- **Personalización:** Branding y configuración dinámica por realtor.
- **Roles:** Considera roles (admin, realtor, cliente, referente) para permisos y vistas.

---

## Notas Finales
- Este esquema es flexible y preparado para crecer.
- Puedes agregar más tablas/campos según necesidades futuras.
- El frontend y la IA pueden consultar y actualizar todo de forma eficiente y segura. 