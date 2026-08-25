# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, calendar, ics

app = FastAPI(title="Calendar MCP Server", version="0.1.0")

# MCP server integration - optional
try:
    from app.mcp_server import mount_mcp
    mount_mcp(app)
except ImportError:
    pass  # MCP not installed, skip MCP integration

# CORS middleware - adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(ics.router, prefix="/ics", tags=["ics"])

# Mount MCP server
mount_mcp(app)

@app.get("/")
async def root():
    return {"message": "Calendar MCP Server is running"}