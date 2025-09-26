from fastapi import APIRouter
from .endpoints import auth, users, customers, loyalty, affiliates, whatsapp, analytics
from .endpoints import rewards, tiers, erp

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["loyalty"])
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])
api_router.include_router(tiers.router, prefix="/tiers", tags=["tiers"])
api_router.include_router(affiliates.router, prefix="/affiliates", tags=["affiliates"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
api_router.include_router(erp.router, prefix="/erp", tags=["erp"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])