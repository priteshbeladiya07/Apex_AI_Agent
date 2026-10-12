from fastapi import APIRouter

from apex_ai.api.routes import chat, conversations, expenses, health, mcp

router = APIRouter(prefix="/api")

router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)

router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["Conversations"],
)

router.include_router(
    expenses.router,
    prefix="/expenses",
    tags=["Expenses"],
)

router.include_router(
    mcp.router,
    prefix="/mcp",
    tags=["MCP"],
)