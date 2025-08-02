from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database.models import Guest
from app.core.config import settings
import redis

router = APIRouter()
templates = Jinja2Templates(directory="templates")

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    name: str | None = None,
    security_code: str | None = None,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    
    if security_code != settings.default_security_code:
        # logic for calculating failed trials
        failed_attempts_key = f"failed_attempts:{client_ip}"
        # Increment count, set expiry 30 minutes
        r.incr(failed_attempts_key)
        r.expire(failed_attempts_key, 1800) # 1800 seconds = 30 minutes
        # If attempts fail > 5, block IP for 30 minutes
        if int(r.get(failed_attempts_key) or 0) >= 5:
            r.set(f"blocked_ip:{client_ip}", "true", ex=1800)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied after multiple failed attempts.")
            
        return templates.TemplateResponse("error.html", {"request": request, "message": "Kode akses tidak valid."})

    guest = db.query(Guest).filter(Guest.name == name).first()
    if not guest:
        guest = Guest(name=name)
        db.add(guest)
        db.commit()
        db.refresh(guest)
    
    # Clear failed attempt count if login is successful
    r.delete(f"failed_attempts:{client_ip}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "guest": guest,
            "bride_name": settings.bride_name,
            "groom_name": settings.groom_name
        }
    )

@router.get("/l5FaD1Lcmieu6U121K6Zy6jgQrYEjfoV8aVIMYrXoqVIj7FhHLrTFBfMICQljjGAMAFmZ0dcW69ricQh", response_class=HTMLResponse)
async def rsvp_form(request: Request):
    return templates.TemplateResponse("rsvp.html", {"request": request})

@router.post("/l5FaD1Lcmieu6U121K6Zy6jgQrYEjfoV8aVIMYrXoqVIj7FhHLrTFBfMICQljjGAMAFmZ0dcW69ricQh", response_class=RedirectResponse)
async def submit_rsvp(
    name: str = Form(...),
    is_attending: bool = Form(False),
    message: str = Form(None),
    db: Session = Depends(get_db)
):
    guest = db.query(Guest).filter(Guest.name == name).first()
    if guest:
        guest.is_attending = is_attending
        guest.message = message
    else:
        guest = Guest(name=name, is_attending=is_attending, message=message)
        db.add(guest)

    db.commit()
    db.refresh(guest)
    return RedirectResponse(url=f"/?name={guest.name}&security_code={settings.default_security_code}", status_code=303)