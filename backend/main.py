from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.APP_NAME)

    # include routers
    from app.api import health

    app.include_router(health.router, prefix="/api")

    @app.on_event("startup")
    def on_startup():
        # perform any startup checks here (DB, caches, etc.)
        pass

    @app.on_event("shutdown")
    def on_shutdown():
        pass

    return app


app = create_app()
