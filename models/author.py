# models/author.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Author(SQLModel, table=True):
    """Author model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    birth_year: Optional[int] = Field(default=None, ge=1800, le=datetime.now().year)
    nationality: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    books: List["Book"] = Relationship(back_populates="author")

class AuthorCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    birth_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    nationality: Optional[str] = Field(None, max_length=50)

class AuthorUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    birth_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    nationality: Optional[str] = Field(None, max_length=50)