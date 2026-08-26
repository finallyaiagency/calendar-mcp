# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Calendar MCP Server", version="0.1.0")

# CORS middleware - adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-load routers to avoid import-time DB connections
def include_routers():
    from app.routers import auth, calendar, ics
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
    app.include_router(ics.router, prefix="/ics", tags=["ics"])
    
    # MCP server integration - optional (requires 'mcp' package)
    try:
        from app.mcp_server import mount_mcp
        mount_mcp(app)
    except ImportError:
        pass  # MCP not installed, skip MCP integration

# Include routers immediately
include_routers()

@app.get("/")
async def root():
    return {"message": "Calendar MCP Server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "calendar-mcp"}