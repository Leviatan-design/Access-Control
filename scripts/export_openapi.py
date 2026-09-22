#!/usr/bin/env python3
"""Script para exportar el esquema OpenAPI de la aplicación FastAPI."""
import json
import os
import sys
from pathlib import Path

# Configurar variables de entorno mínimas para exportar OpenAPI
os.environ.setdefault("DATABASE_URL", "postgresql://dummy:dummy@localhost:5432/dummy")
os.environ.setdefault("JWT_SECRET_KEY", "dummy-secret-for-openapi-export")
os.environ.setdefault("DATA_DIR", "./data")
os.environ.setdefault("PORT", "8080")

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

def export_openapi():
    """Exporta el esquema OpenAPI a un archivo JSON."""
    openapi_schema = app.openapi()
    
    # Crear directorio docs si no existe
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # Escribir el esquema OpenAPI
    output_file = docs_dir / "openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"OpenAPI schema exportado a {output_file}")
    print(f"Total de endpoints: {len(openapi_schema.get('paths', {}))}")
    print(f"Version: {openapi_schema.get('openapi', 'N/A')}")
    print(f"Titulo: {openapi_schema.get('info', {}).get('title', 'N/A')}")

if __name__ == "__main__":
    export_openapi()
