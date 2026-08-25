# Vercel serverless entry point for FastAPI
from mangum import Mangum
from app.main import app

# Load environment variables from .env if present (local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Mangum adapter for ASGI -> AWS Lambda / Vercel
handler = Mangum(app, lifespan="off")