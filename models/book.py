# models/book.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Book(SQLModel, table=True):
    """Book model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=2, max_length=200)
    isbn: str = Field(unique=True, index=True, min_length=10, max_length=13)
    description: str = Field(min_length=10, max_length=1000)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    pages: Optional[int] = Field(default=None, ge=1)
    publication_date: Optional[datetime] = Field(default=None)
    genre: str = Field(min_length=2, max_length=50)
    language: str = Field(default="English", min_length=2, max_length=30)
    rating: float = Field(default=0.0, ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    publisher_id: Optional[int] = Field(default=None, foreign_key="publisher.id")
    
    author: Optional["Author"] = Relationship(back_populates="books")
    publisher: Optional["Publisher"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book")

class BookCreate(SQLModel):
    title: str = Field(min_length=2, max_length=200)
    isbn: str = Field(min_length=10, max_length=13)
    description: str = Field(min_length=10, max_length=1000)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    pages: Optional[int] = Field(None, ge=1)
    publication_date: Optional[datetime] = None
    genre: str = Field(min_length=2, max_length=50)
    language: str = Field(default="English", min_length=2, max_length=30)
    author_id: Optional[int] = None
    publisher_id: Optional[int] = None

class BookUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    pages: Optional[int] = Field(None, ge=1)
    publication_date: Optional[datetime] = None
    genre: Optional[str] = Field(None, min_length=2, max_length=50)
    language: Optional[str] = Field(None, min_length=2, max_length=30)
    author_id: Optional[int] = None
    publisher_id: Optional[int] = None

class Review(SQLModel, table=True):
    """Review model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)
    reviewer_name: str = Field(min_length=2, max_length=100)
    reviewer_email: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    book: Optional[Book] = Relationship(back_populates="reviews")

class ReviewCreate(SQLModel):
    book_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
    reviewer_name: str = Field(min_length=2, max_length=100)
    reviewer_email: Optional[str] = Field(None, max_length=100)