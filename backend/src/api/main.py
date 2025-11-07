print("=== STARTING APP ===", flush=True)
import sys
print(f"Python version: {sys.version}", flush=True)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.config.settings import get_settings
from src.api.routes.agent import router as agent_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.tiers import router as tiers_router
from src.api.routes.widget import router as widget_router
from src.api.routes.webhooks import router as webhooks_router
from src.api.routes.product_crawl import router as product_crawl_router
from src.api.routes.scheduled import router as scheduled_router
from src.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

settings = get_settings()

app = FastAPI(title="Local Business AI Agent Platform", debug=settings.debug)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add error handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

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

# Register all routers
app.include_router(agent_router)
app.include_router(analytics_router)
app.include_router(tiers_router)
app.include_router(widget_router)
app.include_router(webhooks_router)
app.include_router(product_crawl_router)
app.include_router(scheduled_router)
