import loader

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.routers.tasks.routers import router as task_router
from api.routers.offers.routers import router as offer_router
from api.routers.users.routers import router as users_router
from api.routers.messages.routers import router as message_router
from api.routers.segments.routers import router as segments_router
from api.middlewares import FetchUserMiddleware

app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_tags=loader.FASTAPI_TAGS,
    version="1.0.0",
)

app.add_middleware(FetchUserMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# роутер по заказам
app.include_router(task_router)
# роутер по откликам
app.include_router(offer_router)

app.include_router(users_router)

app.include_router(message_router)

app.include_router(segments_router)

# Лёгкий health-check для zero-downtime деплоя и мониторинга
@app.get("/health")
def healthcheck():
    return {"status": "ok"}