from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Request, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select, or_, and_
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
import os
import shutil
import aiofiles
import json
from typing import Optional, List
from pydantic import BaseModel

from database.session import get_session, create_db_and_tables
from models.user import User, UserCreate, UserResponse, UserUpdate
from models.document import Document, DocumentCreate, DocumentUpdate, DocumentResponse
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_admin, get_current_manager,
    get_current_staff_or_above
)
from services.weather import get_weather

# ============================================================
# APPLICATION SETUP
# ============================================================
app = FastAPI(
    title="SendIt Document Management API",
    description="Document management system with weather enrichment for SendIt courier company",
    version="1.0.0",
    contact={
        "name": "Lucy Wambui Kimani",
        "email": "c027-01-0890/2024@student.dkut.ac.ke"
    }
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Database tables created successfully!")

# ============================================================
# CONFIGURATION
# ============================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 5 * 1024 * 1024))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.jpg,.jpeg,.png,.docx").split(",")

# ============================================================
# RATE LIMITING
# ============================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================
@app.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(400, "Username already taken")
    
    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(400, "Email already registered")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@app.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(403, "User account is disabled")
    
    user.last_login = datetime.utcnow()
    session.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.role is not None and current_user.role == "admin":
        current_user.role = user_update.role
    if user_update.is_active is not None and current_user.role == "admin":
        current_user.is_active = user_update.is_active
    
    current_user.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(current_user)
    
    return current_user

# ============================================================
# ADMIN ENDPOINTS
# ============================================================
@app.get("/admin/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    return session.exec(select(User)).all()

@app.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    if role not in ["admin", "manager", "staff"]:
        raise HTTPException(400, "Invalid role")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    user.role = role
    user.updated_at = datetime.utcnow()
    session.commit()
    
    return {"message": f"User role updated to {role}"}

@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot delete yourself")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    session.delete(user)
    session.commit()
    
    return {"message": "User deleted successfully"}

# ============================================================
# FILE UPLOAD ENDPOINTS
# ============================================================
def validate_file_extension(filename: str) -> bool:
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in ALLOWED_EXTENSIONS

@app.post("/documents/upload")
@limiter.limit("10/hour")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    city: str = Form(...),
    description: Optional[str] = Form(None),
    country: str = Form("Kenya"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not validate_file_extension(file.filename):
        raise HTTPException(
            400,
            f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    contents = await file.read()
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            400,
            f"File too large. Max size: {MAX_FILE_SIZE // (1024 * 1024)} MB"
        )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{current_user.id}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(contents)
    
    existing_doc = session.exec(
        select(Document).where(Document.original_filename == file.filename)
    ).first()
    
    version = 1
    if existing_doc:
        version = existing_doc.version + 1
    
    document = Document(
        filename=safe_filename,
        original_filename=file.filename,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream",
        city=city,
        country=country,
        description=description,
        uploader_id=current_user.id,
        file_path=file_path,
        status="processing",
        version=version
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    
    try:
        weather_data = await get_weather(city, country)
        if weather_data and "error" not in weather_data:
            document.weather_data = json.dumps(weather_data)
            document.weather_fetched_at = datetime.utcnow()
            document.status = "enriched"
            session.commit()
        else:
            document.status = "uploaded"
            session.commit()
    except Exception as e:
        print(f"Weather API error: {e}")
        document.status = "uploaded"
        session.commit()
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.original_filename,
        "status": document.status,
        "version": document.version
    }

@app.get("/documents")
@limiter.limit("30/minute")
def list_documents(
    request: Request,
    status: Optional[str] = None,
    city: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Document)
    
    if current_user.role not in ["admin", "manager"]:
        query = query.where(Document.uploader_id == current_user.id)
    
    if status:
        query = query.where(Document.status == status)
    if city:
        query = query.where(Document.city == city)
    
    query = query.order_by(Document.uploaded_at.desc())
    
    return session.exec(query).all()

@app.get("/documents/{document_id}")
@limiter.limit("30/minute")
def get_document(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    if current_user.role not in ["admin", "manager"] and document.uploader_id != current_user.id:
        raise HTTPException(403, "Access denied")
    
    return document

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_manager),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    session.delete(document)
    session.commit()
    
    return {"message": "Document deleted successfully"}

@app.put("/documents/{document_id}")
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_manager),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    if document_update.city is not None:
        document.city = document_update.city
    if document_update.country is not None:
        document.country = document_update.country
    if document_update.description is not None:
        document.description = document_update.description
    if document_update.status is not None:
        document.status = document_update.status
    
    document.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(document)
    
    return document

# ============================================================
# DOCUMENT ENRICHMENT ENDPOINTS
# ============================================================
@app.post("/documents/{document_id}/enrich")
@limiter.limit("5/minute")
async def enrich_document(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_manager),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    if document.status == "enriched":
        return {"message": "Document already enriched"}
    
    weather_data = await get_weather(document.city, document.country)
    
    if weather_data and "error" not in weather_data:
        document.weather_data = json.dumps(weather_data)
        document.weather_fetched_at = datetime.utcnow()
        document.status = "enriched"
        session.commit()
        return {
            "message": "Document enriched successfully",
            "weather": weather_data
        }
    else:
        document.status = "failed"
        session.commit()
        error_msg = weather_data.get("error", "Unknown error") if weather_data else "No response"
        raise HTTPException(500, f"Failed to enrich document: {error_msg}")

@app.get("/documents/{document_id}/weather")
@limiter.limit("10/minute")
def get_document_weather(
    request: Request,
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    if current_user.role not in ["admin", "manager"] and document.uploader_id != current_user.id:
        raise HTTPException(403, "Access denied")
    
    if not document.weather_data:
        raise HTTPException(404, "No weather data available for this document")
    
    return {
        "document_id": document.id,
        "city": document.city,
        "country": document.country,
        "weather": json.loads(document.weather_data)
    }

# ============================================================
# EXERCISE 1: Document Search with Filters
# ============================================================
@app.get("/documents/search")
@limiter.limit("20/minute")
def search_documents(
    request: Request,
    q: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Document)
    
    if current_user.role not in ["admin", "manager"]:
        query = query.where(Document.uploader_id == current_user.id)
    
    if q:
        query = query.where(
            or_(
                Document.original_filename.contains(q),
                Document.description.contains(q)
            )
        )
    
    if city:
        query = query.where(Document.city == city)
    
    if status:
        query = query.where(Document.status == status)
    
    if date_from:
        query = query.where(Document.uploaded_at >= date_from)
    if date_to:
        query = query.where(Document.uploaded_at <= date_to)
    
    query = query.order_by(Document.uploaded_at.desc())
    
    return session.exec(query).all()

# ============================================================
# EXERCISE 2: Document Versioning
# ============================================================
@app.get("/documents/{document_id}/versions")
def get_document_versions(
    document_id: int,
    current_user: User = Depends(get_current_manager),
    session: Session = Depends(get_session)
):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    versions = session.exec(
        select(Document).where(
            Document.original_filename == document.original_filename
        ).order_by(Document.version.desc())
    ).all()
    
    return versions

# ============================================================
# EXERCISE 3: Webhook Notification
# ============================================================
from sqlmodel import SQLModel, Field

class WebhookRegistration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    webhook_url: str
    event_type: str
    user_id: int = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

@app.post("/webhooks/register")
def register_webhook(
    webhook_url: str,
    event_type: str,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    if event_type not in ["document.enriched", "document.uploaded"]:
        raise HTTPException(400, "Invalid event type")
    
    existing = session.exec(
        select(WebhookRegistration).where(
            WebhookRegistration.webhook_url == webhook_url,
            WebhookRegistration.event_type == event_type,
            WebhookRegistration.user_id == current_user.id
        )
    ).first()
    
    if existing:
        existing.is_active = True
        session.commit()
        return {"message": "Webhook re-activated"}
    
    webhook = WebhookRegistration(
        webhook_url=webhook_url,
        event_type=event_type,
        user_id=current_user.id
    )
    session.add(webhook)
    session.commit()
    session.refresh(webhook)
    
    return {"message": "Webhook registered successfully", "id": webhook.id}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SendIt API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)