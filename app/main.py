from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from app.database.db import engine, Base
from app.routers import home
from app.core.config import settings
import redis


load_dotenv()

# Create database table
Base.metadata.create_all(bind=engine)

# redis connection
r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

app = FastAPI(title="Undangan Pernikahan")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middleware for IP blocking
@app.middleware("http")
async def ip_blocking_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    # Check if IP is on block list
    if r.get(f"blocked_ip:{client_ip}"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    
    response = await call_next(request)
    return response

# Include Routes
app.include_router(home.router)