
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apex_ai.agents.graph import graph
from apex_ai.agents.nodes import configure_tools
from apex_ai.core.logging import configure_logging, get_logger
from apex_ai.database.session import close_db, init_db
from apex_ai.mcp.client_manager import MCPClientManager
from apex_ai.api.router import router

configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Apex AI")

    try:
        await init_db()

        mcp_manager = MCPClientManager()
        tools = await mcp_manager.get_tools()

        configure_tools(tools)
        app.state.agent = graph
        app.state.mcp_manager = mcp_manager

        logger.info("Apex AI initialized with %s MCP tools", len(tools))
        yield

    except Exception:
        logger.exception("Failed to initialize Apex AI")
        raise

    finally:
        app.state.agent = None
        await close_db()
        logger.info("Apex AI stopped")


app = FastAPI(title="Apex AI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
