# Vercel serverless entry point for FastAPI
from mangum import Mangum
import traceback
import sys

# Load environment variables from .env if present (local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import the app with error handling
try:
    from app.main import app
except Exception as e:
    print(f"Failed to import app: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    # Create a minimal error app
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
handler = Mangum(app, lifespan="off")