# Mapa del Sitio - Control de Acceso Residencial

## Árbol de Navegación por Rol

### 🌐 Público (Sin autenticación)
- `/` - Landing page (index.html)
- `/health` - Health check endpoint
- `/sw.js` - Service Worker
- `/auth/login` - Login (POST)

### 👤 Propietario (ADMIN_CASA, COHABITANTE)
- `/owner` - Panel de propietario (owner.html)
  - Gestión de habitantes
  - Generación de pases de visita
  - Historial de visitas
  - Estado de cuenta (solvencia)

### 👮 Garita (VIGILANTE)
- `/guard` - Panel de garita (guard.html)
  - Búsqueda por código
  - Escáner QR
  - Registro de entrada/salida
  - Listas en vivo

### 🔧 Administración (SUPER_ADMIN, ADMIN_CONDOMINIO)
- Gestión de usuarios
- Gestión de condominios
- Gestión de propiedades
- Carga CSV de morosidad
- Gestión de anuncios

## Endpoints REST API

### Autenticación
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/auth/login` | Público | Login con credenciales (OAuth2) |
| POST | `/auth/register/cohabitante` | Público | Registro de cohabitante con token |

### Pases (Control de Acceso)
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| GET | `/api/pases/today` | Público | Visitas esperadas hoy |
| GET | `/api/pases/inside` | Público | Visitantes dentro del conjunto |
| GET | `/api/pases/search` | Público | Buscar pase por código |
| POST | `/api/pases/{id}/entry` | Público | Registrar entrada |
| POST | `/api/pases/{id}/exit` | Público | Registrar salida |
| POST | `/api/pases/crear` | Autenticado | Crear nuevo pase (con validación financiera) |

### API v1 - Pases
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/api/v1/pases/crear` | Autenticado | Crear pase |
| GET | `/api/v1/pases/buscar/{codigo}` | Público | Buscar pase por código (PENDIENTE) |
| PATCH | `/api/v1/pases/{pase_id}/entrada` | Autenticado | Registrar entrada |
| PATCH | `/api/v1/pases/{pase_id}/salida` | Autenticado | Registrar salida |
| POST | `/api/v1/pases/sync-offline` | Autenticado | Sincronización offline |
| GET | `/api/v1/pases/propiedad/{propiedad_id}` | Autenticado | Pases por propiedad |
| GET | `/api/v1/pases/activos` | Autenticado | Pases activos (DENTRO) |
| GET | `/api/v1/pases/{pase_id}` | Autenticado | Obtener pase por ID |
| GET | `/api/v1/pases/codigo/{codigo}` | Autenticado | Obtener pase por código (cualquier estado) |

### API v1 - Usuarios
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/api/v1/usuarios/crear` | SUPER_ADMIN, ADMIN_CONDOMINIO | Crear usuario |
| POST | `/api/v1/usuarios/vivienda/generar-invitacion` | ADMIN_CASA | Generar invitación |
| DELETE | `/api/v1/usuarios/vivienda/habitante/{usuario_id}` | ADMIN_CASA | Eliminar habitante |
| GET | `/api/v1/usuarios/vivienda/{propiedad_id}/habitantes` | Autenticado | Obtener habitantes |
| GET | `/api/v1/usuarios/vivienda/{propiedad_id}/conteo` | Autenticado | Contar habitantes |
| GET | `/api/v1/usuarios/{usuario_id}` | Autenticado | Obtener usuario por ID |
| GET | `/api/v1/usuarios/cedula/{cedula}` | Autenticado | Obtener usuario por cédula |

### API v1 - Condominios
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/api/v1/condominio/morosidad/cargar-csv` | SUPER_ADMIN, ADMIN_CONDOMINIO | Cargar CSV morosidad |
| GET | `/api/v1/condominio/morosidad/propiedades` | SUPER_ADMIN, ADMIN_CONDOMINIO | Estado morosidad propiedades |

### API v1 - Propiedades
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| GET | `/api/v1/propiedades/{propiedad_id}` | Autenticado | Obtener propiedad |
| GET | `/api/v1/propiedades/` | Autenticado | Obtener todas las propiedades |

### API v1 - Anuncios
| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/api/v1/anuncios` | ADMIN_CASA, COHABITANTE | Crear anuncio |
| GET | `/api/v1/anuncios` | Autenticado | Listar anuncios |
| DELETE | `/api/v1/anuncios/{anuncio_id}` | Autenticado (autor o moderador) | Eliminar anuncio |

## Templates Jinja2

| Template | Ruta | Propósito |
|----------|------|-----------|
| `base.html` | - | Plantilla base con layout común |
| `index.html` | `/` | Landing page pública |
| `owner.html` | `/owner` | Panel de propietario |
| `guard.html` | `/guard` | Panel de garita |

## Rutas Públicas vs Privadas

### Públicas (requieren solo conexión)
- `/` - Landing page
- `/health` - Health check
- `/sw.js` - Service Worker
- `/auth/login` - Endpoint de autenticación

### Privadas (requieren autenticación JWT)
- `/owner` - Panel propietario (requiere rol ADMIN_CASA o COHABITANTE)
- `/guard` - Panel garita (requiere rol VIGILANTE)
- `/api/v1/*` - Endpoints de API (varios roles según endpoint)

### Semi-privadas (acceso controlado por lógica de negocio)
- `/api/pases/*` - Endpoints de pases legacy (acceso desde panels sin autenticación directa)
