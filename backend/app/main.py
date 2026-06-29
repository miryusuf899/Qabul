from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, businesses, clients, services, staff, working_hours


def create_app() -> FastAPI:
    app = FastAPI(
        title="Qabul API",
        description="Backend API for Qabul digital administrator MVP.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(businesses.router, prefix="/api/v1")
    app.include_router(services.router, prefix="/api/v1")
    app.include_router(staff.router, prefix="/api/v1")
    app.include_router(working_hours.router, prefix="/api/v1")
    app.include_router(clients.router, prefix="/api/v1")

    return app


app = create_app()
