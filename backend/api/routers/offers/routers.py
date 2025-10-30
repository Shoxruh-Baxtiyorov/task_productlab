from fastapi import APIRouter

from api.routers.offers.client_offers.routers import router as client_offers_router

router = APIRouter(prefix='/offers')

router.include_router(
    client_offers_router,
    prefix='/client'
)
