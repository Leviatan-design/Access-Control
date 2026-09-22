# Security Audit Report - Control de Acceso Residencial

**Fecha:** 2026-09-22  
**Auditor:** Automated Security Analysis  
**Versión:** 2.0.0  
**Metodología:** Análisis estático + revisión manual de código

## Metodología

1. **Análisis Estático:**
   - `bandit -r app/` - Escaneo de vulnerabilidades Python
   - `pip-audit` - Análisis de dependencias con vulnerabilidades conocidas
   - Búsqueda de secretos hardcodeados con grep
   - Revisión de patrones inseguros en código

2. **Revisión Manual de Seguridad:**
   - Autenticación JWT (expiración, algoritmo, revocación)
   - Autorización y roles (IDOR, escalada de privilegios)
   - Validación de entrada (SQLi, XSS, CSRF)
   - Configuración de seguridad (CORS, headers, rate limiting)
   - Manejo de errores y fuga de información

3. **Análisis de Dependencias:**
   - Revisión de requirements.txt
   - Verificación de versiones vulnerables

## Hallazgos por Severidad

### 🔴 CRÍTICO

#### 1. Panel de propietario sin autenticación
- **Archivo:** `app/main.py:204-286`
- **Severidad:** CRÍTICO
- **CWE:** CWE-306 (Missing Authentication for Critical Function)
- **Descripción:** El endpoint `GET /owner` no requiere autenticación JWT, exponiendo información sensible de propiedades, habitantes y visitas a cualquier usuario.
- **Evidencia:**
  ```python
  @app.get("/owner", response_class=HTMLResponse)
  def owner_panel(...) -> HTMLResponse:
      # No hay decorador de autenticación
      properties = db.query(Propiedad).all()
      # Expose: property names, units, inhabitants, visits
  ```
- **Impacto:** Acceso no autorizado a información personal de residentes, historial de visitas, y capacidad de gestión sin autenticación.
- **Recomendación:** Agregar `@app.get("/owner", response_class=HTMLResponse)` con autenticación JWT y verificación de rol ADMIN_CASA o COHABITANTE.

#### 2. Panel de garita sin autenticación
- **Archivo:** `app/main.py:198-201`
- **Severidad:** CRÍTICO
- **CWE:** CWE-306 (Missing Authentication for Critical Function)
- **Descripción:** El endpoint `GET /guard` no requiere autenticación, permitiendo acceso a funciones de control de acceso sin verificación de identidad.
- **Evidencia:**
  ```python
  @app.get("/guard", response_class=HTMLResponse)
  def guard_panel(request: Request) -> HTMLResponse:
      # No hay autenticación
      return templates.TemplateResponse("guard.html", {"request": request})
  ```
- **Impacto:** Cualquier persona puede acceder al panel de garita, registrar entradas/salidas, y manipular el sistema de control de acceso.
- **Recomendación:** Implementar autenticación JWT y verificación de rol VIGILANTE para este endpoint.

#### 3. Endpoints de API legacy sin autenticación
- **Archivo:** `app/main.py:324-395`
- **Severidad:** CRÍTICO
- **CWE:** CWE-306 (Missing Authentication for Critical Function)
- **Descripción:** Los endpoints `/api/pases/*` (today, inside, search, entry, exit) no requieren autenticación, permitiendo manipulación del sistema de control de acceso.
- **Evidencia:**
  ```python
  @app.get("/api/pases/today")
  def api_pases_today(db: Session = Depends(get_db)) -> JSONResponse:
      # Sin autenticación
      pases = db.query(Pase).filter(...).all()
  
  @app.post("/api/pases/{pase_id}/entry")
  def api_mark_entry(pase_id: int, db: Session = Depends(get_db)) -> JSONResponse:
      # Sin autenticación - permite registrar entrada
  ```
- **Impacto:** Atacantes pueden ver visitas programadas, registrar entradas/salidas falsas, y comprometer la integridad del sistema de control de acceso.
- **Recomendación:** Migrar todos los endpoints legacy a `/api/v1/pases/*` con autenticación JWT o agregar autenticación a los endpoints existentes.

### 🟠 ALTO

#### 4. 135 vulnerabilidades en dependencias
- **Archivo:** `requirements.txt`
- **Severidad:** ALTO
- **CWE:** CWE-937 (Using Components with Known Vulnerabilities)
- **Descripción:** pip-audit detectó 135 vulnerabilidades conocidas en 25 paquetes, incluyendo PyJWT, python-jose, cryptography, y otras dependencias críticas.
- **Evidencia:**
  ```
  Found 135 known vulnerabilities in 25 packages
  pyjwt 2.10.1 - PYSEC-2026-120, PYSEC-2025-183, etc.
  python-jose 3.3.0 - PYSEC-2024-233, PYSEC-2024-232
  cryptography 46.0.3 - Múltiples CVEs
  ```
- **Impacto:** Exposición a ataques conocidos, posible ejecución remota de código, bypass de autenticación, y otros exploits.
- **Recomendación:** Actualizar todas las dependencias a versiones seguras. Priorizar: PyJWT (2.12.0+), python-jose (3.4.0+), cryptography (46.0.5+).

#### 5. Generación de códigos con random inseguro
- **Archivo:** `app/seed.py:34-37`
- **Severidad:** ALTO
- **CWE:** CWE-330 (Use of Insufficiently Random Values)
- **Descripción:** La función `generate_code()` usa `random.choices()` para generar códigos de pase, lo cual es predecible y no criptográficamente seguro.
- **Evidencia:**
  ```python
  def generate_code(db: Session) -> str:
      while True:
          letters = "".join(random.choices(string.ascii_uppercase, k=3))
          digits = "".join(random.choices(string.digits, k=3))
          code = f"{letters}-{digits}"
  ```
- **Impacto:** Atacantes pueden predecir códigos de pase, permitir acceso no autorizado, y comprometer la seguridad del sistema de control de acceso.
- **Recomendación:** Reemplazar `random.choices()` con `secrets.choice()` para generación criptográficamente segura.

#### 6. Sin revocación de tokens JWT
- **Archivo:** `app/security.py:32-57`
- **Severidad:** ALTO
- **CWE:** CWE-613 (Insufficient Session Expiration)
- **Descripción:** No hay mecanismo de revocación de tokens JWT. Una vez emitido, el token es válido hasta su expiración (60 min).
- **Evidencia:**
  ```python
  def create_access_token(user: Usuario) -> str:
      expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
      # No hay blacklist o mecanismo de revocación
  ```
- **Impacto:** Tokens comprometidos siguen siendo válidos por 60 minutos, permitiendo acceso no autorizado incluso después de detectar intrusiones.
- **Recomendación:** Implementar blacklist de tokens en Redis/base de datos, o usar refresh tokens con rotación.

#### 7. Posible IDOR en endpoints de propiedades
- **Archivo:** `app/routes/propiedades.py:11-30`
- **Severidad:** ALTO
- **CWE:** CWE-639 (Authorization Bypass Through User-Controlled Key)
- **Descripción:** Los endpoints de propiedades no verifican que el usuario autenticado tenga permiso para acceder a la propiedad solicitada.
- **Evidencia:**
  ```python
  @router.get("/{propiedad_id}")
  def obtener_propiedad(propiedad_id: int, db: Session = Depends(get_db)):
      # No verifica si el usuario tiene acceso a esta propiedad
      propiedad = db.query(Propiedad).filter(Propiedad.id == propiedad_id).first()
  ```
- **Impacto:** Usuarios pueden acceder a información de propiedades de otros condominios/usuarios mediante enumeración de IDs.
- **Recomendación:** Verificar que `current_user.propiedad_id == propiedad_id` o que el usuario tenga rol de administrador.

### 🟡 MEDIO

#### 8. Binding a todas las interfaces
- **Archivo:** `app/main.py:445`
- **Severidad:** MEDIO
- **CWE:** CWE-605 (Exposure of Sensitive Information Through Public Repository Metadata)
- **Descripción:** La aplicación se bind a `0.0.0.0`, exponiendo el servicio a todas las interfaces de red.
- **Evidencia:**
  ```python
  uvicorn.run("app.main:app", host="0.0.0.0", port=port)
  ```
- **Impacto:** En entornos de desarrollo no controlados, puede exponer servicios a redes públicas accidentalmente.
- **Recomendación:** En producción, usar configuración específica de host o firewall para limitar exposición.

#### 9. Sin headers de seguridad HTTP
- **Archivo:** `app/main.py:31`
- **Severidad:** MEDIO
- **CWE:** CWE-693 (Protection Mechanism Failure)
- **Descripción:** La aplicación FastAPI no configura headers de seguridad como X-Content-Type-Options, X-Frame-Options, CSP, etc.
- **Evidencia:**
  ```python
  app = FastAPI(title="Access Pass - FlowLogic", version="2.0.0")
  # No hay middleware de seguridad
  ```
- **Impacto:** Vulnerable a XSS, clickjacking, y otros ataques basados en headers.
- **Recomendación:** Implementar middleware de seguridad con headers apropiados.

#### 10. Sin rate limiting
- **Archivo:** Global
- **Severidad:** MEDIO
- **CWE:** CWE-770 (Allocation of Resources Without Limits)
- **Descripción:** No hay implementación de rate limiting en ningún endpoint.
- **Impacto:** Vulnerable a ataques de fuerza bruta, DoS, y abuso de API.
- **Recomendación:** Implementar rate limiting con slowapi o similar.

#### 11. Sin protección CSRF
- **Archivo:** Global
- **Severidad:** MEDIO
- **CWE:** CWE-352 (Cross-Site Request Forgery)
- **Descripción:** No hay implementación de tokens CSRF en formularios POST.
- **Impacto:** Atacantes pueden ejecutar acciones no autorizadas en nombre de usuarios autenticados.
- **Recomendación:** Implementar protección CSRF con tokens o same-site cookies.

#### 12. Contraseñas hardcodeadas en seed
- **Archivo:** `app/seed.py:86,94,102,116,124`
- **Severidad:** MEDIO
- **CWE:** CWE-798 (Use of Hard-coded Credentials)
- **Descripción:** Las contraseñas de demo están hardcodeadas en el código fuente.
- **Evidencia:**
  ```python
  password_hash=hash_password("Demo-FlowLogic-2026!"),
  ```
- **Impacto:** Credenciales conocidas que pueden ser usadas si el código es accesible.
- **Recomendación:** Usar variables de entorno o generar contraseñas aleatorias en entorno de producción.

### 🟢 BAJO

#### 13. Uso de random en seed (bandit B311)
- **Archivo:** `app/seed.py:35-36`
- **Severidad:** BAJO
- **CWE:** CWE-330 (Use of Insufficiently Random Values)
- **Descripción:** Uso de `random.choices()` en generación de datos de prueba.
- **Impacto:** Bajo - solo afecta datos de demostración.
- **Recomendación:** Cambiar a `secrets` si se usa en producción.

#### 14. "bearer" hardcoded (bandit B106)
- **Archivo:** `app/routes/auth.py:25`
- **Severidad:** BAJO
- **CWE:** CWE-259 (Use of Hard-coded Password)
- **Descripción:** String "bearer" en response de token (falso positivo).
- **Impacto:** Nulo - es el tipo de token estándar OAuth2.
- **Recomendación:** Ignorar este hallazgo (falso positivo).

## Checklist OWASP Top 10

| # | Categoría | Estado | Observaciones |
|---|-----------|--------|---------------|
| A01 | Broken Access Control | ❌ CRÍTICO | Panels sin auth, IDOR posible |
| A02 | Cryptographic Failures | ❌ ALTO | Random inseguro, JWT sin revocación |
| A03 | Injection | ⚠️ PARCIAL | SQLAlchemy ORM mitiga SQLi, pero validar inputs |
| A04 | Insecure Design | ❌ ALTO | Sin rate limiting, sin CSRF protection |
| A05 | Security Misconfiguration | ❌ ALTO | Sin headers seguridad, CORS no configurado |
| A06 | Vulnerable Components | ❌ CRÍTICO | 135 vulnerabilidades en dependencias |
| A07 | Auth Failures | ❌ CRÍTICO | Panels sin auth, sin token revocation |
| A08 | Software/Data Integrity | ⚠️ PARCIAL | No hay verificación de integridad de paquetes |
| A09 | Logging/Monitoring | ❌ MEDIO | Logging básico, sin alertas de seguridad |
| A10 | SSRF | ✅ OK | No hay endpoints que hagan requests externos |

## Recomendaciones Prioritarias

### Inmediato (1-2 días)
1. **Agregar autenticación a panels críticos** (`/owner`, `/guard`)
2. **Actualizar dependencias críticas** (PyJWT, python-jose, cryptography)
3. **Reemplazar random con secrets** en generación de códigos

### Corto plazo (1 semana)
4. **Implementar headers de seguridad** HTTP
5. **Agregar rate limiting** en endpoints sensibles
6. **Corregir IDOR** en endpoints de propiedades/usuarios
7. **Implementar blacklist de tokens** JWT

### Medio plazo (2-4 semanas)
8. **Implementar protección CSRF**
9. **Configurar CORS** apropiadamente
10. **Mejorar logging** de eventos de seguridad
11. **Implementar monitoreo** y alertas

## Conclusión

La aplicación presenta **vulnerabilidades críticas** principalmente relacionadas con:
- Falta de autenticación en endpoints críticos
- Dependencias con vulnerabilidades conocidas
- Falta de controles de seguridad básicos (headers, rate limiting, CSRF)

**Riesgo general:** ALTO - Se recomienda no desplegar en producción sin corregir las vulnerabilidades críticas y altas identificadas.

---

**Generado por:** Automated Security Analysis  
**Versión del reporte:** 1.0  
**Próxima revisión recomendada:** Después de corregir vulnerabilidades críticas
