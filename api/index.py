# Vercel serverless entry point for FastAPI
import traceback
import sys
import os

# Load environment variables from .env if present (local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Print debug info
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"DATABASE_URL set: {'DATABASE_URL' in os.environ}", file=sys.stderr)
print(f"SECRET_KEY set: {'SECRET_KEY' in os.environ}", file=sys.stderr)

# Import mangum
try:
    from mangum import Mangum
    print("Mangum imported successfully", file=sys.stderr)
except Exception as e:
    print(f"Failed to import Mangum: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return JSONResponse(
            status_code=500,
            content={"error": "Mangum import failed", "detail": str(e)}
        )
    # Don't create Mangum handler - just use the ASGI app directly
    handler = app
    print("Created fallback handler (no Mangum)", file=sys.stderr)

# Import the app with error handling
try:
    from app.main import app
    print("Successfully imported app.main", file=sys.stderr)
except Exception as e:
    print(f"Failed to import app: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return JSONResponse(
            status_code=500,
            content={"error": "App import failed", "detail": str(e)}
        )

# Mangum adapter for ASGI -> AWS Lambda / Vercel
try:
    handler = Mangum(app, lifespan="off")
    print("Mangum handler created successfully", file=sys.stderr)
except NameError:
    # Mangum wasn't imported, handler is already set to app
    print("Using app directly as handler (no Mangum)", file=sys.stderr)
except Exception as e:
    print(f"Failed to create Mangum handler: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    handler = app