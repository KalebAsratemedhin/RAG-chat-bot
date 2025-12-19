from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, documents, health
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import questions
from app.api.routes import debug


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Chat Bot",
        description="A simple RAG (Retrieval-Augmented Generation) chat bot",
        version="1.0.0",
    )

    # CORS middleware (allows frontend to call API)
    cors_origins = (
        settings.CORS_ORIGINS.split(",")
        if settings.CORS_ORIGINS != "*"
        else ["*"]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(documents.router, prefix="/documents", tags=["documents"])
    app.include_router(questions.router, prefix="/questions", tags=["questions"])
    app.include_router(debug.router, prefix="/debug", tags=["debug"])

    @app.on_event("startup")
    async def on_startup() -> None:
        # Create tables if they do not exist yet
        init_db()

    @app.get("/")
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "message": "RAG Chat Bot API",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )







