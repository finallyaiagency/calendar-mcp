# Vercel serverless entry point for FastAPI
import traceback
import sys
import os

print(f"Python version: {sys.version}", file=sys.stderr)
print(f"DATABASE_URL set: {'DATABASE_URL' in os.environ}", file=sys.stderr)
print(f"SECRET_KEY set: {'SECRET_KEY' in os.environ}", file=sys.stderr)

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    print("FastAPI imported successfully", file=sys.stderr)
except Exception as e:
    print(f"Failed to import FastAPI: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

# Create the app
app = FastAPI(title="Calendar MCP Server", version="0.1.0")

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defer router inclusion until first request
_routers_included = False

def include_routers():
    global _routers_included
    if not _routers_included:
        try:
            from app.routers import auth, calendar, ics
            app.include_router(auth.router, prefix="/auth", tags=["auth"])
            app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
            app.include_router(ics.router, prefix="/ics", tags=["ics"])
            try:
                from app.mcp_server import mount_mcp
                mount_mcp(app)
            except ImportError:
                pass
            _routers_included = True
            print("Routers included successfully", file=sys.stderr)
        except Exception as e:
            print(f"Failed to include routers: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

# Middleware to include routers on first request
@app.middleware("http")
async def lazy_include_routers(request, call_next):
    if not hasattr(app.state, '_routers_included') or not app.state._routers_included:
        include_routers()
        app.state._routers_included = True
    return await call_next(request)

# Root and health endpoints (always available)
@app.get("/")
async def root():
    return {"message": "Calendar MCP Server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "calendar-mcp"}

# Try Mangum
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    print("Mangum handler created successfully", file=sys.stderr)
except Exception as e:
    print(f"Mangum failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    handler = app

# Export handler explicitly for Vercel
__all__ = ["handler", "app"]