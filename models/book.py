from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from models.category import Category

class Book(SQLModel, table=True):
    """Book model for the library database"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    author: str = Field(index=True, min_length=1, max_length=100)
    isbn: str = Field(unique=True, index=True)
    published_year: int = Field(ge=1000, le=datetime.now().year)
    available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign key to Category
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="books")