# Control de Acceso Residencial

Sistema de control de acceso residencial full-stack para gestionar visitas en conjuntos residenciales. Incluye panel de propietario (agendar visitas y generar pases con QR) y panel de garita (búsqueda, escaneo QR, entradas/salidas).

## Stack Tecnológico

- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Frontend:** Jinja2 + TailwindCSS (CDN) + JavaScript nativo
- **Base de datos:** PostgreSQL + SQLAlchemy 2.0.36 + Alembic
- **Autenticación:** JWT Bearer + bcrypt + roles jerárquicos
- **Infraestructura:** Docker + docker-compose + Render.com

## Roles de Usuario

- `SUPER_ADMIN`: Administrador general del sistema
- `ADMIN_CONDOMINIO`: Administrador de condominio
- `ADMIN_CASA`: Administrador de propiedad
- `COHABITANTE`: Habitante de la propiedad
- `VIGILANTE`: Personal de seguridad

## Modelos de Datos

- **Condominio**: Información del conjunto residencial
- **Propiedad**: Unidades habitacionales con estado de solvencia
- **Usuario**: Usuarios con roles jerárquicos
- **Pase**: Pases de acceso para visitantes
- **InvitacionVivienda**: Sistema de invitaciones para cohabitantes
- **Anuncio**: Clasificados internos del condominio

## Requisitos

- Python 3.12+
- PostgreSQL 12+
- Docker Desktop (opcional)

## Instalación Local

### 1. Clonar el repositorio y configurar entorno

```bash
# Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# DATABASE_URL, JWT_SECRET_KEY, etc.
```

### 3. Ejecutar migraciones

```bash
# Ejecutar migraciones de base de datos
alembic upgrade head

# Sembrar datos de prueba
python -c "from app.seed import seed_database; from app.database import SessionLocal; seed_database(SessionLocal())"
```

### 4. Iniciar servidor

```bash
# Windows
set PORT=8080
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Linux / macOS
export PORT=8080
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Abre en el navegador: **http://localhost:8080**

## Ejecución con Docker

### Docker Compose (recomendado para desarrollo)

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Docker Build Manual

```bash
# Construir imagen
docker build -t access-control .

# Ejecutar contenedor
docker run --rm -p 8080:8080 -e PORT=8080 access-control
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión PostgreSQL | - |
| `JWT_SECRET_KEY` | Secreto para firmar tokens JWT | - |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración token (min) | 60 |
| `SUPER_ADMIN_EMAIL` | Email del super admin | `dev@flowlogic.com` |
| `SUPER_ADMIN_PASSWORD` | Contraseña del super admin | - |
| `DATA_DIR` | Directorio de datos | `./data` |
| `PORT` | Puerto del servidor | `8080` |

## Usuario de Prueba

El sistema crea automáticamente un usuario SUPER_ADMIN:

| Email | Contraseña | Rol |
|--------|------------|-----|
| `dev@flowlogic.com` | `ChangeThis-FlowLogic-2026!` | `SUPER_ADMIN` |

⚠️ **Importante:** Cambia estas credenciales en producción.

## Estructura del Proyecto

```
.
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── database.py          # Configuración PostgreSQL
│   ├── models.py            # Modelos SQLAlchemy
│   ├── seed.py              # Datos de prueba
│   ├── controller.py        # Lógica de negocio
│   ├── security.py          # Autenticación y autorización
│   ├── schemas.py           # Pydantic schemas
│   ├── static/              # Archivos estáticos
│   ├── templates/           # Plantillas Jinja2
│   └── routes/              # API routers organizados
├── alembic/                 # Migraciones de base de datos
├── docs/                    # Documentación técnica
├── scripts/                 # Scripts utilitarios
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Orquestación local
├── render.yaml              # Configuración Render.com
├── requirements.txt         # Dependencias Python
└── README.md                # Este archivo
```

## Documentación

- **[Mapa del Sitio](docs/site-map.md)** - Estructura de navegación y endpoints API
- **[OpenAPI Schema](docs/openapi.json)** - Especificación completa de la API
- **Health Check:** `GET /health` → `{"status":"ok","service":"access-control"}`

## API REST Principales

### Autenticación
- `POST /auth/login` - Login con credenciales
- `POST /auth/register/cohabitante` - Registro con token de invitación

### Pases
- `GET /api/pases/today` - Visitas esperadas hoy
- `GET /api/pases/inside` - Visitantes dentro del conjunto
- `GET /api/pases/search?code=XXX` - Buscar por código
- `POST /api/pases/{id}/entry` - Registrar entrada
- `POST /api/pases/{id}/exit` - Registrar salida

### API v1
- `/api/v1/pases/*` - Gestión completa de pases
- `/api/v1/usuarios/*` - Gestión de usuarios y habitantes
- `/api/v1/condominio/*` - Gestión de condominios y morosidad
- `/api/v1/propiedades/*` - Gestión de propiedades
- `/api/v1/anuncios/*` - Clasificados internos

## Despliegue en Render.com

El proyecto incluye configuración para despliegue automático en Render.com:

1. Sube el repositorio a GitHub
2. En Render Dashboard: **New → Blueprint**
3. Conecta el repositorio (detecta `render.yaml` automáticamente)
4. Confirma el despliegue

Render configurará automáticamente:
- Base de datos PostgreSQL
- Variables de entorno generadas
- Health checks
- HTTPS automático

## Estado Actual

### Funcionalidades Implementadas
- ✅ Sistema de autenticación JWT con roles jerárquicos
- ✅ Panel de propietario con gestión de visitas
- ✅ Panel de garita con escaneo QR
- ✅ Generación de códigos únicos para pases
- ✅ Validación de solvencia financiera
- ✅ Sistema de invitaciones para cohabitantes
- ✅ Límite de 4 habitantes por propiedad
- ✅ Anuncios clasificados
- ✅ API REST completa
- ✅ Sincronización offline para garita
- ✅ Migraciones Alembic
- ✅ Dockerización completa

### Próximos Pasos
- 🔄 Migración a framework frontend moderno (React/Vue)
- 🔄 Suite de pruebas unitarias y de integración
- 🔄 Pipeline CI/CD
- 🔄 Monitoreo y logging estructurado
- 🔄 Optimización de base de datos
- 🔄 Documentación API completa (Swagger)

## Licencia

Proyecto demo para uso en pruebas y demostraciones.

---

**Documentación técnica:** [docs/site-map.md](docs/site-map.md) | [docs/openapi.json](docs/openapi.json)
