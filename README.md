# Rentiva Backend

API REST para gestión de rentas inmobiliarias, construida con Django y Django REST Framework.

## Requisitos

- Python 3.11+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/Back-Rentiva.git
cd Back-Rentiva

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y ajusta los valores:

```bash
cp .env.example .env
```

Edita `.env` con tu clave secreta y configuración de base de datos. En desarrollo, SQLite se usa por defecto si no defines `DATABASE_URL`.

## Migraciones y servidor

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario para el admin de Django
python manage.py createsuperuser

# Levantar el servidor
python manage.py runserver
```

El servidor corre en `http://localhost:8000`. El panel de administración está en `/admin/`.

## Endpoints principales

Todos los endpoints viven bajo `/api/v1/`. Los que requieren autenticación esperan un header `Authorization: Bearer <token>`.

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/registro/` | Crear cuenta |
| POST | `/auth/login/` | Iniciar sesión |
| POST | `/auth/token/refresh/` | Refrescar token |
| GET/PATCH | `/auth/me/` | Ver/editar perfil |
| POST | `/auth/cambio-password/` | Cambiar contraseña |
| POST | `/auth/logout/` | Cerrar sesión |

### Recursos (CRUD completo)
| Ruta base | Descripción |
|-----------|-------------|
| `/propiedades/` | Inmuebles |
| `/propiedad-detalles/` | Detalles clave-valor de propiedades |
| `/fotos-propiedad/` | Galería de fotos |
| `/mobiliario/` | Catálogo de mobiliario |
| `/propiedad-mobiliario/` | Mobiliario asignado a propiedades |
| `/arrendatarios/` | Inquilinos |
| `/contratos/` | Contratos de arrendamiento |
| `/historial-contratos/` | Auditoría de cambios de contrato (solo lectura) |
| `/pagos/` | Pagos de renta |
| `/fichas-pago/` | Fichas de pago bancario |
| `/facturas/` | Facturas CFDI |
| `/notificaciones/` | Notificaciones y recordatorios |
| `/notificacion-logs/` | Logs de envío (solo lectura) |
| `/reportes-mantenimiento/` | Reportes de mantenimiento |
| `/especialistas/` | Catálogo de especialistas |
| `/resenas-especialistas/` | Reseñas de especialistas |
| `/documentos/` | Documentos adjuntos (polimórfico) |
| `/datos-fiscales/` | Datos fiscales RFC/CFDI |
| `/dashboard/` | Resumen y métricas del propietario |

### Endpoint especial
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/notificaciones/marcar_leidas/` | Marcar todas las notificaciones como leídas |
| PATCH | `/admin/propietarios/<id>/rol/` | Cambiar rol (solo admin) |

## Estructura del proyecto

```
Back-Rentiva/
├── autenticacion/     # Modelo Propietario, JWT custom, permisos
├── propiedades/       # Inmuebles, detalles, mobiliario, fotos
├── arrendatarios/     # Inquilinos
├── contratos/         # Contratos y auditoría de estados
├── pagos/             # Pagos, fichas de pago, facturas
├── notificaciones/    # Notificaciones y logs de envío
├── mantenimiento/     # Reportes, especialistas, reseñas
├── documentos/        # Documentos adjuntos polimórficos
├── fiscal/            # Datos fiscales RFC/CFDI
├── dashboard/         # Métricas y resumen
└── rentiva_backend/   # Settings, URLs raíz
```

## Tecnologías

- Django 5.x
- Django REST Framework
- Simple JWT (autenticación)
- django-filter (filtros en querysets)
- SQLite (desarrollo) / PostgreSQL (producción)
