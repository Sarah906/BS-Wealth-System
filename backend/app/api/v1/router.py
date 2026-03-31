from fastapi import APIRouter
from app.api.v1 import auth, platforms, accounts, assets, deals, transactions, cashflows, imports, analytics

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(platforms.router)
api_router.include_router(accounts.router)
api_router.include_router(assets.router)
api_router.include_router(deals.router)
api_router.include_router(transactions.router)
api_router.include_router(cashflows.router)
api_router.include_router(imports.router)
api_router.include_router(analytics.router)
