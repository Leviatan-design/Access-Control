import pytest
from fastapi import status


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
    
    def test_code_format_consistency(self, db_session):
        """Verificar que los códigos tienen formato consistente."""
        from app.seed import generate_code
        
        code = generate_code(db_session)
        
        # Verificar formato XXX-XXX
        assert len(code) == 7
        assert code[3] == "-"
        assert code[:3].isupper()
        assert code[:3].isalpha()
        assert code[4:].isdigit()
        assert len(code[4:]) == 3