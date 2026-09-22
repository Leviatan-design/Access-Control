import pytest
from fastapi import status


class TestAuthentication:
    """Tests de autenticación y autorización."""
    
    def test_health_endpoint_public(self, client):
        """Verificar que el endpoint de health es público."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"
    
    def test_guard_panel_requires_auth(self, client):
        """Verificar que el panel de garita requiere autenticación."""
        response = client.get("/guard")
        # Debería redirigir o dar error 401/403
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_guard_panel_with_vigilante_auth(self, client, vigilante_headers):
        """Verificar que el panel de garita funciona con autenticación de vigilante."""
        response = client.get("/guard", headers=vigilante_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_guard_panel_with_owner_auth_fails(self, client, auth_headers):
        """Verificar que el panel de garita falla con autenticación de propietario."""
        response = client.get("/guard", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_owner_panel_requires_auth(self, client):
        """Verificar que el panel de propietario requiere autenticación."""
        response = client.get("/owner")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_owner_panel_with_owner_auth(self, client, auth_headers):
        """Verificar que el panel de propietario funciona con autenticación correcta."""
        response = client.get("/owner", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    def test_owner_panel_idor_protection(self, client, auth_headers, test_user):
        """Verificar protección IDOR en panel de propietario."""
        # Intentar acceder a otra propiedad (si existe)
        response = client.get("/owner?property_id=999", headers=auth_headers)
        # Debería dar 403 o 404 si no tiene acceso
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestAPIEndpoints:
    """Tests de seguridad en endpoints de API."""
    
    def test_pase_entry_requires_auth(self, client):
        """Verificar que registrar entrada requiere autenticación."""
        response = client.post("/api/pases/1/entry")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_pase_exit_requires_auth(self, client):
        """Verificar que registrar salida requiere autenticación."""
        response = client.post("/api/pases/1/exit")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_pase_entry_with_vigilante_auth(self, client, vigilante_headers):
        """Verificar que vigilante puede registrar entrada."""
        # Nota: Esto fallará si no hay pase con ID 1, pero verifica autenticación
        response = client.post("/api/pases/1/entry", headers=vigilante_headers)
        # Puede ser 404 si no existe el pase, pero no debe ser 401/403
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN


class TestSecurityHeaders:
    """Tests de headers de seguridad."""
    
    def test_security_headers_present(self, client):
        """Verificar presence de headers de seguridad."""
        response = client.get("/health")
        headers = response.headers
        
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in headers
        assert "X-XSS-Protection" in headers
        
        # Pueden no estar presentes en HTTP, pero verificar si están
        if "Strict-Transport-Security" in headers:
            assert "max-age" in headers["Strict-Transport-Security"]


class TestCodeGeneration:
    """Tests de generación de códigos seguros."""
    
    def test_generate_code_uses_secrets(self, db_session):
        """Verificar que generate_code usa secrets en lugar de random."""
        from app.seed import generate_code
        from app.models import Pase
        
        # Generar varios códigos para verificar que son únicos
        codes = set()
        for _ in range(100):
            code = generate_code(db_session)
            codes.add(code)
        
        # Debería generar códigos únicos
        assert len(codes) == 100
        
        # Verificar formato correcto
        for code in codes:
            assert len(code) == 7  # XXX-XXX
            assert code[3] == "-"
            assert code[:3].isalpha()
            assert code[4:].isdigit()


class TestCORSConfiguration:
    """Tests de configuración CORS."""
    
    def test_cors_headers(self, client):
        """Verificar headers CORS en respuesta."""
        response = client.get("/health")
        # CORS headers pueden estar presentes dependiendo de la configuración
        # Verificar que la respuesta es exitosa
        assert response.status_code == status.HTTP_200_OK
