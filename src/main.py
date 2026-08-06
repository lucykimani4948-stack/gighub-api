from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from typing import Optional
from database.session import get_session, create_tables, engine
from models.user import User, UserCreate, UserResponse
from models.patient import Patient, PatientCreate, PatientUpdate
from models.audit import AuditLog
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_active_user,
    get_current_admin, get_current_doctor, get_receptionist_or_above
)

app = FastAPI(title="ClinicGuard API", version="1.0.0")

# ============================================================
# RATE LIMITING
# ============================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================
# AUDIT LOG MIDDLEWARE
# ============================================================
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    """Log all patient endpoint accesses."""
    response = await call_next(request)
    
    # Only log patient endpoints
    if "/patients" in request.url.path and request.method != "OPTIONS":
        try:
            # Get current user if authenticated
            token = request.headers.get("Authorization")
            if token:
                from auth import decode_access_token
                try:
                    payload = decode_access_token(token.replace("Bearer ", ""))
                    username = payload.get("sub")
                    if username:
                        with Session(engine) as session:
                            from models.user import User
                            user = session.exec(select(User).where(User.username == username)).first()
                            if user:
                                # Determine patient_id from path
                                patient_id = None
                                path_parts = request.url.path.split("/")
                                for i, part in enumerate(path_parts):
                                    if part == "patients" and i + 1 < len(path_parts) and path_parts[i+1].isdigit():
                                        patient_id = int(path_parts[i+1])
                                        break
                                
                                audit = AuditLog(
                                    user_id=user.id,
                                    patient_id=patient_id,
                                    action=request.method,
                                    endpoint=request.url.path,
                                    ip_address=request.client.host if request.client else None
                                )
                                session.add(audit)
                                session.commit()
                except:
                    pass
        except:
            pass
    
    return response

@app.on_event("startup")
def on_startup():
    create_tables()

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/register", status_code=201)
@limiter.limit("5/minute")
def register_user(
    request: Request,
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(409, "Username already exists")
    
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(409, "Email already exists")
    
    hashed = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=user_data.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {"message": "User created successfully", "user": db_user}

@app.post("/login")
@limiter.limit("5/minute")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(403, "User is inactive")
    
    user.last_login = datetime.utcnow()
    session.commit()
    
    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "username": user.username,
        "role": user.role
    }

# ============================================================
# PATIENT ENDPOINTS
# ============================================================

@app.post("/patients", status_code=201)
@limiter.limit("20/hour")
def create_patient(
    request: Request,
    patient_data: PatientCreate,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    if patient_data.doctor_id:
        doctor = session.get(User, patient_data.doctor_id)
        if not doctor:
            raise HTTPException(404, "Doctor not found")
        if doctor.role not in ["admin", "doctor"]:
            raise HTTPException(400, "Assigned user must be a doctor")
    
    db_patient = Patient(
        **patient_data.dict(),
        created_by=current_user.id
    )
    
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient

@app.get("/patients")
@limiter.limit("30/minute")
def list_patients(
    request: Request,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    query = select(Patient)
    
    if current_user.role == "doctor":
        query = query.where(Patient.doctor_id == current_user.id)
    
    return session.exec(query).all()

@app.get("/patients/{patient_id}")
@limiter.limit("30/minute")
def get_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    if current_user.role == "doctor" and patient.doctor_id != current_user.id:
        raise HTTPException(403, "Access denied to this patient record")
    
    return patient

@app.patch("/patients/{patient_id}")
@limiter.limit("20/minute")
def update_patient(
    request: Request,
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    if current_user.role != "admin" and patient.doctor_id != current_user.id:
        raise HTTPException(403, "You can only update your own patients")
    
    for key, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, key, value)
    
    patient.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(patient)
    return patient

@app.delete("/patients/{patient_id}")
@limiter.limit("10/hour")
def delete_patient(
    request: Request,
    patient_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    session.delete(patient)
    session.commit()
    return {"message": "Patient record deleted"}

# ============================================================
# ADMIN USER MANAGEMENT
# ============================================================

@app.get("/users", response_model=list[UserResponse])
@limiter.limit("20/minute")
def list_users(
    request: Request,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    return session.exec(select(User)).all()

@app.get("/users/{user_id}", response_model=UserResponse)
@limiter.limit("20/minute")
def get_user(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.patch("/users/{user_id}/role")
@limiter.limit("10/minute")
def update_user_role(
    request: Request,
    user_id: int,
    new_role: str,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    if new_role not in ["admin", "doctor", "receptionist"]:
        raise HTTPException(400, "Invalid role")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.id == admin.id:
        raise HTTPException(400, "You cannot change your own role")
    
    user.role = new_role
    session.commit()
    return {"message": f"User {user.username} role updated to {new_role}"}

@app.patch("/users/{user_id}/activate")
@limiter.limit("10/minute")
def toggle_user_activation(
    request: Request,
    user_id: int,
    activate: bool,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.id == admin.id:
        raise HTTPException(400, "You cannot deactivate yourself")
    
    user.is_active = activate
    session.commit()
    return {"message": f"User {user.username} activation set to {activate}"}

# ============================================================
# AUDIT LOG ENDPOINTS (Admin Only)
# ============================================================

@app.get("/audit-logs")
@limiter.limit("20/minute")
def get_audit_logs(
    request: Request,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    limit: int = 100,
    skip: int = 0
):
    """Get all audit logs (admin only)."""
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    return session.exec(query).all()

@app.get("/audit-logs/patient/{patient_id}")
@limiter.limit("20/minute")
def get_audit_logs_by_patient(
    request: Request,
    patient_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Get audit logs for a specific patient (admin only)."""
    query = select(AuditLog).where(AuditLog.patient_id == patient_id).order_by(AuditLog.timestamp.desc())
    return session.exec(query).all()

@app.get("/audit-logs/user/{user_id}")
@limiter.limit("20/minute")
def get_audit_logs_by_user(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Get audit logs for a specific user (admin only)."""
    query = select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.timestamp.desc())
    return session.exec(query).all()

# ============================================================
# PATIENT ASSIGNMENT WORKFLOW (Exercise 2)
# ============================================================

@app.get("/patients/unassigned")
@limiter.limit("20/minute")
def get_unassigned_patients(
    request: Request,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    """Get list of unassigned patients (doctors only)."""
    query = select(Patient).where(Patient.doctor_id.is_(None))
    return session.exec(query).all()

@app.patch("/patients/{patient_id}/claim")
@limiter.limit("10/minute")
def claim_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    """Claim a patient (assign to current doctor)."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    if patient.doctor_id:
        raise HTTPException(400, "Patient is already assigned to a doctor")
    
    patient.doctor_id = current_user.id
    patient.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(patient)
    return {"message": f"Patient {patient.first_name} {patient.last_name} assigned to you", "patient": patient}

@app.patch("/patients/{patient_id}/unassign")
@limiter.limit("10/minute")
def unassign_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    """Unassign a patient from current doctor."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    if patient.doctor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "You can only unassign your own patients")
    
    patient.doctor_id = None
    patient.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(patient)
    return {"message": f"Patient {patient.first_name} {patient.last_name} unassigned", "patient": patient}

@app.get("/patients/assigned-to-me")
@limiter.limit("20/minute")
def get_my_patients(
    request: Request,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    """Get all patients assigned to the current doctor."""
    query = select(Patient).where(Patient.doctor_id == current_user.id)
    return session.exec(query).all()

# ============================================================
# SECURE PATIENT SEARCH (Exercise 3)
# ============================================================

@app.get("/patients/search")
@limiter.limit("20/minute")
def search_patients(
    request: Request,
    q: str,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    """
    Search patients by name.
    - Admins and receptionists can search all patients
    - Doctors can only search their own patients
    """
    query = select(Patient).where(
        (Patient.first_name.ilike(f"%{q}%")) |
        (Patient.last_name.ilike(f"%{q}%"))
    )
    
    # Doctors can only see their own patients
    if current_user.role == "doctor":
        query = query.where(Patient.doctor_id == current_user.id)
    
    return session.exec(query).all()

@app.get("/patients/search/advanced")
@limiter.limit("20/minute")
def advanced_search_patients(
    request: Request,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    doctor_id: Optional[int] = None,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    """
    Advanced search with multiple filters.
    - Admins and receptionists can search all patients
    - Doctors can only search their own patients
    """
    query = select(Patient)
    
    # Apply filters
    if first_name:
        query = query.where(Patient.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.where(Patient.last_name.ilike(f"%{last_name}%"))
    if phone:
        query = query.where(Patient.phone.contains(phone))
    if doctor_id:
        query = query.where(Patient.doctor_id == doctor_id)
    
    # Doctors can only see their own patients
    if current_user.role == "doctor":
        query = query.where(Patient.doctor_id == current_user.id)
    
    return session.exec(query).all()