import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .data_fetcher import fetch_world_bank_data
from .repository import VaccineRepository
from . import api as api_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="Panamá Sarampión (12–23 meses) – API de solo lectura",
        version="1.0.0",
        description="Cobertura del indicador SH.IMM.MEAS (World Bank) para Panamá.",
    )

    # CORS abierto (ajusta para producción)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def load_data():
        records = await fetch_world_bank_data()
        api_routes.repo = VaccineRepository(records)

    app.include_router(api_routes.router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
