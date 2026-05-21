"""
API v1 routes
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, accounts, transactions, copilot, recommendations, documents, simulations, workflows, document_parser

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(accounts.router, tags=["Accounts"])
api_router.include_router(transactions.router, tags=["Transactions"])
api_router.include_router(copilot.router, tags=["AI Copilot"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(document_parser.router, prefix="/parse-document", tags=["Document Parser"])
api_router.include_router(simulations.router, tags=["Simulations"])
api_router.include_router(workflows.router, tags=["Workflows"])

# Made with Bob
