# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional
import secrets
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

from models.user import User, UserCreate, UserResponse, UserUpdate
from models.patient import Patient
from models.blacklist import TokenBlacklist
from models.password_reset import PasswordResetToken

from database.session import get_session, create_db_and_tables
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_active_user,
    get_current_doctor, get_current_admin,
    decode_access_token, oauth2_scheme
)

app = FastAPI(title="HealthTrack API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Server is alive!"}

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/register", response_model=UserResponse, status_code=201)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == user_data.username)).first():
        raise HTTPException(status_code=409, detail="Username already registered")
    
    if session.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/login")
def login_user(
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    if user.two_factor_enabled:
        temp_token = create_access_token(
            data={"sub": user.username, "2fa_required": True},
            expires_delta=timedelta(minutes=5)
        )
        return {
            "message": "2FA required",
            "temp_token": temp_token,
            "requires_2fa": True
        }
    
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    payload = decode_access_token(token)
    exp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp) if exp else datetime.utcnow() + timedelta(days=1)
    
    blacklisted_token = TokenBlacklist(
        token=token,
        expires_at=expires_at
    )
    session.add(blacklisted_token)
    session.commit()
    
    return {"message": "Successfully logged out"}

# ============================================================
# PASSWORD RESET
# ============================================================

@app.post("/forgot-password")
def forgot_password(email: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return {"message": "If your email is registered, you will receive a reset link"}
    
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    session.add(reset_entry)
    session.commit()
    
    return {
        "message": "Reset token generated",
        "reset_token": reset_token,
        "expires_in_minutes": 60
    }

@app.post("/reset-password")
def reset_password(
    token: str,
    new_password: str,
    session: Session = Depends(get_session)
):
    reset_entry = session.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False
        )
    ).first()
    
    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    user = session.exec(select(User).where(User.id == reset_entry.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = hash_password(new_password)
    reset_entry.is_used = True
    
    session.add(user)
    session.add(reset_entry)
    session.commit()
    
    return {"message": "Password reset successfully"}

# ============================================================
# PROTECTED ENDPOINTS
# ============================================================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.put("/users/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.email is not None:
        if session.exec(
            select(User).where(User.email == user_update.email, User.id != current_user.id)
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    if user_update.username is not None:
        if session.exec(
            select(User).where(User.username == user_update.username, User.id != current_user.id)
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@app.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    statement = select(User)
    if role:
        statement = statement.where(User.role == role)
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

# ============================================================
# 2FA ENDPOINTS
# ============================================================

@app.post("/users/enable-2fa")
def enable_2fa(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    secret = pyotp.random_base32()
    current_user.two_factor_secret = secret
    session.add(current_user)
    session.commit()
    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="HealthTrack"
    )
    
    return {
        "message": "2FA setup initiated",
        "secret": secret,
        "provisioning_uri": provisioning_uri
    }

@app.post("/users/verify-2fa")
def verify_2fa(
    code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not initiated"
        )
    
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    current_user.two_factor_enabled = True
    session.add(current_user)
    session.commit()
    
    return {"message": "2FA enabled successfully"}

@app.post("/users/disable-2fa")
def disable_2fa(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    session.add(current_user)
    session.commit()
    return {"message": "2FA disabled successfully"}

@app.post("/login-2fa")
def login_with_2fa(
    temp_token: str,
    code: str,
    session: Session = Depends(get_session)
):
    payload = decode_access_token(temp_token)
    username = payload.get("sub")
    requires_2fa = payload.get("2fa_required")
    
    if not username or not requires_2fa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA token"
        )
    
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not enabled"
        )
    
    totp = pyotp.TOTP(user.two_factor_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# ============================================================
# PATIENT MANAGEMENT ENDPOINTS
# ============================================================

@app.post("/patients", response_model=Patient)
def create_patient(
    patient_data: Patient,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.id == patient_data.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a patient"
        )
    
    if session.exec(select(Patient).where(Patient.user_id == patient_data.user_id)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already exists"
        )
    
    patient_data.doctor_id = current_user.id
    patient_data.created_at = datetime.utcnow()
    
    session.add(patient_data)
    session.commit()
    session.refresh(patient_data)
    return patient_data

@app.get("/patients", response_model=list[Patient])
def list_patients(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    statement = select(Patient)
    
    if current_user.role == "doctor":
        statement = statement.where(Patient.doctor_id == current_user.id)
    
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    patient = session.exec(select(Patient).where(Patient.id == patient_id)).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if current_user.role == "patient" and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own record"
        )
    
    if current_user.role == "doctor" and current_user.id != patient.doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your patients"
        )
    
    return patient