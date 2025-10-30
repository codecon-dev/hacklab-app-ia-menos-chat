from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import cities, tourism, auth, roteiros

app = FastAPI(
    title="Turismo Inteligente API",
    description="API para sugestões de pontos turísticos em rotas entre cidades",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(cities.router, prefix="/api/v1/cities", tags=["cities"])
app.include_router(tourism.router, prefix="/api/v1/tourism", tags=["tourism"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roteiros.router, prefix="/api/v1/roteiros", tags=["roteiros"])

@app.get("/")
async def root():
    return {"message": "Turismo Inteligente API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )