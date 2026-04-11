from fastapi import FastAPI
from src.config.settings import settings
from src.routes.health import router as health_router
from src.routes.admin import router as admin_router
from src.routes.exercises import router as exercises_router
from src.routes.content import router as content_router
from src.routes.resources import router as resources_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(admin_router)
app.include_router(exercises_router)
app.include_router(content_router)
app.include_router(resources_router)
