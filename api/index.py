# Ultra-minimal Vercel test - no app imports
import traceback
import sys
import os

print(f"Python version: {sys.version}", file=sys.stderr)
print(f"DATABASE_URL set: {'DATABASE_URL' in os.environ}", file=sys.stderr)
print(f"SECRET_KEY set: {'SECRET_KEY' in os.environ}", file=sys.stderr)

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    print("FastAPI imported successfully", file=sys.stderr)
except Exception as e:
    print(f"Failed to import FastAPI: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Minimal test works!", "service": "calendar-mcp"}

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