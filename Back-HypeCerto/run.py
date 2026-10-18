"""
run.py
Ponto de entrada para rodar o servidor diretamente.
Uso: python run.py
"""
import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),  # use HOST=0.0.0.0 só atrás de proxy/contêiner
        port=8000,
        reload=(settings.ENVIRONMENT == "development"),
        log_level="info",
    )
