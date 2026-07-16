# models/publisher.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Publisher(SQLModel, table=True):
    """Publisher model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=2, max_length=100)
    address: Optional[str] = Field(default=None, max_length=200)
    website: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    founded_year: Optional[int] = Field(default=None, ge=1400, le=datetime.now().year)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    books: List["Book"] = Relationship(back_populates="publisher")

class PublisherCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1400, le=datetime.now().year)

class PublisherUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1400, le=datetime.now().year)