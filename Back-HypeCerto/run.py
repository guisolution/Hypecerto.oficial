"""
run.py
Ponto de entrada para rodar o servidor diretamente.
Uso: python run.py
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=(settings.ENVIRONMENT == "development"),
        log_level="info",
    )
