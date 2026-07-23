from typing import Optional
from datetime import datetime
import re
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    contact_person: str
    email: str = Field(unique=True, index=True)
    phone: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SupplierCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    contact_person: str = Field(min_length=2, max_length=100)
    email: str
    phone: str
    is_active: bool = True

    @field_validator("email")
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format. Expected: name@domain.com")
        return v.lower()

    @field_validator("phone")
    def validate_phone(cls, v):
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        pattern = r'^(\+254|0)[17]\d{8}$'
        if not re.match(pattern, cleaned):
            raise ValueError("Invalid phone format. Expected: 07XXXXXXXX, 01XXXXXXXX, or +2547XXXXXXXX")
        return v

class SupplierUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    contact_person: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None