from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.api.analytics_api import router as analytics_router
from fastapi.middleware.cors import CORSMiddleware
def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.APP_NAME)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # include routers
    from app.api import health
    from app.api.college import router as college_router
    from app.api.course import router as course_router
    from app.api.candidate import router as candidate_router
    from app.api.vacancy import router as vacancy_router
    from app.api.cutoff import router as cutoff_router
    from app.api import imports

    app.include_router(health.router, prefix="/api")
    app.include_router(college_router, prefix="/api")
    app.include_router(course_router, prefix="/api")
    app.include_router(candidate_router, prefix="/api")
    app.include_router(vacancy_router, prefix="/api")
    app.include_router(cutoff_router, prefix="/api")
    app.include_router(imports.router)
    app.include_router(analytics_router)

    @app.on_event("startup")
    def on_startup():
        # perform any startup checks here (DB, caches, etc.)
        pass

    @app.on_event("shutdown")
    def on_shutdown():
        pass

    return app


app = create_app()
