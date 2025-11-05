print("=== STARTING APP ===", flush=True)
import sys
print(f"Python version: {sys.version}", flush=True)
print("About to import modules...", flush=True)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_settings
from src.api.routes.crawl import router as crawl_router
from src.api.routes.agent import router as agent_router
from src.api.routes.widget import router as widget_router

print("APP STARTING - THIS SHOULD APPEAR IN LOGS", flush=True)
settings = get_settings()

app = FastAPI(title="Local Business AI Agent Platform", debug=settings.debug)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/config")
async def config_preview():
    # Do not return secrets
    return {
        "debug": settings.debug,
        "database_url": settings.database_url.split("@")[0] if "@" in settings.database_url else settings.database_url,
        "redis_url": settings.redis_url,
    }


app.include_router(crawl_router)
app.include_router(agent_router)
app.include_router(widget_router)
