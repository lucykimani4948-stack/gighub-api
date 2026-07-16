# main.py - Complete BookStore API
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import csv
from fastapi.responses import StreamingResponse
import io

from database.session import get_session, create_db_and_tables
from models import (
    Book, BookCreate, BookUpdate,
    Author, AuthorCreate, AuthorUpdate,
    Publisher, PublisherCreate, PublisherUpdate,
    Review, ReviewCreate
)

# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="BookStore API",
    version="1.0.0",
    description="Complete BookStore management API with authors, publishers, and reviews"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ============================================================
# ADDITIONAL MODELS
# ============================================================

class StockUpdate(BaseModel):
    stock: int = Field(ge=0)
    operation: str = Field(default="set", pattern="^(set|add|subtract)$")

class BulkBookCreate(BaseModel):
    books: List[BookCreate]

class BulkDeleteRequest(BaseModel):
    book_ids: List[int]

# ============================================================
# AUTHOR CRUD OPERATIONS
# ============================================================

@app.post("/authors", response_model=Author, status_code=201)
def create_author(author: AuthorCreate, session: Session = Depends(get_session)):
    """Create a new author"""
    existing = session.exec(select(Author).where(Author.name == author.name)).first()
    if existing:
        raise HTTPException(400, "Author already exists")
    
    db_author = Author(**author.dict())
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author

@app.get("/authors", response_model=List[Author])
def list_authors(
    skip: int = 0,
    limit: int = 10,
    nationality: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List all authors with optional filters"""
    query = select(Author)
    if nationality:
        query = query.where(Author.nationality == nationality)
    return session.exec(query.offset(skip).limit(limit)).all()

@app.get("/authors/{author_id}", response_model=Author)
def get_author(author_id: int, session: Session = Depends(get_session)):
    """Get author by ID"""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    return author

@app.put("/authors/{author_id}", response_model=Author)
def update_author(
    author_id: int,
    author_update: AuthorUpdate,
    session: Session = Depends(get_session)
):
    """Update an author"""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    
    update_data = author_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(author, key, value)
    
    author.updated_at = datetime.utcnow()
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: int, session: Session = Depends(get_session)):
    """Delete an author"""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    
    # Check if author has books
    books = session.exec(select(Book).where(Book.author_id == author_id)).all()
    if books:
        raise HTTPException(400, f"Cannot delete author with {len(books)} books")
    
    session.delete(author)
    session.commit()
    return None

# ============================================================
# PUBLISHER CRUD OPERATIONS
# ============================================================

@app.post("/publishers", response_model=Publisher, status_code=201)
def create_publisher(publisher: PublisherCreate, session: Session = Depends(get_session)):
    """Create a new publisher"""
    existing = session.exec(select(Publisher).where(Publisher.name == publisher.name)).first()
    if existing:
        raise HTTPException(400, "Publisher already exists")
    
    db_publisher = Publisher(**publisher.dict())
    session.add(db_publisher)
    session.commit()
    session.refresh(db_publisher)
    return db_publisher

@app.get("/publishers", response_model=List[Publisher])
def list_publishers(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """List all publishers"""
    return session.exec(select(Publisher).offset(skip).limit(limit)).all()

@app.get("/publishers/{publisher_id}", response_model=Publisher)
def get_publisher(publisher_id: int, session: Session = Depends(get_session)):
    """Get publisher by ID"""
    publisher = session.get(Publisher, publisher_id)
    if not publisher:
        raise HTTPException(404, "Publisher not found")
    return publisher

@app.put("/publishers/{publisher_id}", response_model=Publisher)
def update_publisher(
    publisher_id: int,
    publisher_update: PublisherUpdate,
    session: Session = Depends(get_session)
):
    """Update a publisher"""
    publisher = session.get(Publisher, publisher_id)
    if not publisher:
        raise HTTPException(404, "Publisher not found")
    
    update_data = publisher_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(publisher, key, value)
    
    publisher.updated_at = datetime.utcnow()
    session.add(publisher)
    session.commit()
    session.refresh(publisher)
    return publisher

@app.delete("/publishers/{publisher_id}", status_code=204)
def delete_publisher(publisher_id: int, session: Session = Depends(get_session)):
    """Delete a publisher"""
    publisher = session.get(Publisher, publisher_id)
    if not publisher:
        raise HTTPException(404, "Publisher not found")
    
    books = session.exec(select(Book).where(Book.publisher_id == publisher_id)).all()
    if books:
        raise HTTPException(400, f"Cannot delete publisher with {len(books)} books")
    
    session.delete(publisher)
    session.commit()
    return None

# ============================================================
# BOOK CRUD OPERATIONS
# ============================================================

@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    # Validate ISBN uniqueness
    existing = session.exec(select(Book).where(Book.isbn == book.isbn)).first()
    if existing:
        raise HTTPException(400, "Book with this ISBN already exists")
    
    # Validate author exists
    if book.author_id:
        author = session.get(Author, book.author_id)
        if not author:
            raise HTTPException(404, "Author not found")
    
    # Validate publisher exists
    if book.publisher_id:
        publisher = session.get(Publisher, book.publisher_id)
        if not publisher:
            raise HTTPException(404, "Publisher not found")
    
    db_book = Book(**book.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    title: Optional[str] = None,
    author_id: Optional[int] = None,
    publisher_id: Optional[int] = None,
    genre: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    min_rating: Optional[float] = None,
    language: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """List books with comprehensive filters"""
    query = select(Book)
    
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author_id:
        query = query.where(Book.author_id == author_id)
    if publisher_id:
        query = query.where(Book.publisher_id == publisher_id)
    if genre:
        query = query.where(Book.genre.ilike(f"%{genre}%"))
    if min_price is not None:
        query = query.where(Book.price >= min_price)
    if max_price is not None:
        query = query.where(Book.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.where(Book.stock > 0)
        else:
            query = query.where(Book.stock == 0)
    if min_rating is not None:
        query = query.where(Book.rating >= min_rating)
    if language:
        query = query.where(Book.language == language)
    
    return session.exec(query.offset(skip).limit(limit)).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get book by ID"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    """Update a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    
    # Validate ISBN uniqueness if updating
    if book_update.isbn:
        existing = session.exec(
            select(Book).where(
                Book.isbn == book_update.isbn,
                Book.id != book_id
            )
        ).first()
        if existing:
            raise HTTPException(400, "Book with this ISBN already exists")
    
    # Validate relationships
    if book_update.author_id is not None:
        author = session.get(Author, book_update.author_id)
        if not author:
            raise HTTPException(404, "Author not found")
    
    if book_update.publisher_id is not None:
        publisher = session.get(Publisher, book_update.publisher_id)
        if not publisher:
            raise HTTPException(404, "Publisher not found")
    
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    
    book.updated_at = datetime.utcnow()
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.patch("/books/{book_id}", response_model=Book)
def patch_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    """Partially update a book"""
    return update_book(book_id, book_update, session)

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    """Delete a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    
    # Delete associated reviews first
    reviews = session.exec(select(Review).where(Review.book_id == book_id)).all()
    for review in reviews:
        session.delete(review)
    
    session.delete(book)
    session.commit()
    return None

# ============================================================
# REVIEW OPERATIONS
# ============================================================

@app.post("/reviews", response_model=Review, status_code=201)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    """Create a new review for a book"""
    book = session.get(Book, review.book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    
    db_review = Review(**review.dict())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    
    # Update book rating
    update_book_rating(book.id, session)
    
    return db_review

@app.get("/books/{book_id}/reviews", response_model=List[Review])
def get_book_reviews(book_id: int, session: Session = Depends(get_session)):
    """Get all reviews for a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    
    return session.exec(select(Review).where(Review.book_id == book_id)).all()

@app.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: int, session: Session = Depends(get_session)):
    """Delete a review"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    
    book_id = review.book_id
    session.delete(review)
    session.commit()
    
    # Update book rating
    update_book_rating(book_id, session)
    return None

def update_book_rating(book_id: int, session: Session):
    """Helper function to update book rating"""
    reviews = session.exec(select(Review).where(Review.book_id == book_id)).all()
    book = session.get(Book, book_id)
    
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        book.rating = round(avg_rating, 1)
        book.reviews_count = len(reviews)
    else:
        book.rating = 0.0
        book.reviews_count = 0
    
    session.add(book)
    session.commit()

# ============================================================
# SEARCH FUNCTIONALITY
# ============================================================

@app.get("/books/search/")
def search_books(
    query: str,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Search books by title, description, or genre"""
    if not query or len(query) < 2:
        raise HTTPException(400, "Search query must be at least 2 characters")
    
    search_term = f"%{query}%"
    statement = select(Book).where(
        or_(
            Book.title.ilike(search_term),
            Book.description.ilike(search_term),
            Book.genre.ilike(search_term)
        )
    ).offset(skip).limit(limit)
    
    results = session.exec(statement).all()
    return {
        "query": query,
        "count": len(results),
        "results": results
    }

# ============================================================
# STOCK MANAGEMENT
# ============================================================

@app.patch("/books/{book_id}/stock")
def update_book_stock(
    book_id: int,
    stock_update: StockUpdate,
    session: Session = Depends(get_session)
):
    """Update book stock"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    
    if stock_update.operation == "set":
        book.stock = stock_update.stock
    elif stock_update.operation == "add":
        book.stock += stock_update.stock
    elif stock_update.operation == "subtract":
        if book.stock < stock_update.stock:
            raise HTTPException(400, f"Insufficient stock. Current stock: {book.stock}")
        book.stock -= stock_update.stock
    
    book.updated_at = datetime.utcnow()
    session.add(book)
    session.commit()
    session.refresh(book)
    
    return {
        "book_id": book_id,
        "title": book.title,
        "new_stock": book.stock,
        "operation": stock_update.operation,
        "message": f"Stock {stock_update.operation} successfully"
    }

@app.get("/books/low-stock/")
def get_low_stock_books(
    threshold: int = 10,
    session: Session = Depends(get_session)
):
    """Get books with stock below threshold"""
    statement = select(Book).where(Book.stock < threshold).where(Book.stock > 0)
    results = session.exec(statement).all()
    return {
        "threshold": threshold,
        "count": len(results),
        "books": results
    }

@app.get("/books/out-of-stock/")
def get_out_of_stock_books(session: Session = Depends(get_session)):
    """Get all books with zero stock"""
    statement = select(Book).where(Book.stock == 0)
    results = session.exec(statement).all()
    return {
        "count": len(results),
        "books": results
    }

# ============================================================
# BULK OPERATIONS
# ============================================================

@app.post("/books/bulk/", response_model=List[Book], status_code=201)
def create_books_bulk(
    bulk_data: BulkBookCreate,
    session: Session = Depends(get_session)
):
    """Create multiple books at once"""
    created_books = []
    
    for book_data in bulk_data.books:
        # Validate ISBN uniqueness
        existing = session.exec(select(Book).where(Book.isbn == book_data.isbn)).first()
        if existing:
            raise HTTPException(400, f"Book with ISBN {book_data.isbn} already exists")
        
        # Validate author
        if book_data.author_id:
            author = session.get(Author, book_data.author_id)
            if not author:
                raise HTTPException(404, f"Author {book_data.author_id} not found")
        
        # Validate publisher
        if book_data.publisher_id:
            publisher = session.get(Publisher, book_data.publisher_id)
            if not publisher:
                raise HTTPException(404, f"Publisher {book_data.publisher_id} not found")
        
        db_book = Book(**book_data.dict())
        session.add(db_book)
        created_books.append(db_book)
    
    session.commit()
    for book in created_books:
        session.refresh(book)
    
    return {
        "message": f"Successfully created {len(created_books)} books",
        "books": created_books
    }

@app.delete("/books/bulk/")
def delete_books_bulk(
    bulk_data: BulkDeleteRequest,
    session: Session = Depends(get_session)
):
    """Delete multiple books at once"""
    deleted_count = 0
    not_found_ids = []
    
    for book_id in bulk_data.book_ids:
        book = session.get(Book, book_id)
        if book:
            # Delete reviews first
            reviews = session.exec(select(Review).where(Review.book_id == book_id)).all()
            for review in reviews:
                session.delete(review)
            
            session.delete(book)
            deleted_count += 1
        else:
            not_found_ids.append(book_id)
    
    session.commit()
    
    return {
        "deleted_count": deleted_count,
        "not_found_ids": not_found_ids,
        "message": f"Successfully deleted {deleted_count} books"
    }

# ============================================================
# STATISTICS
# ============================================================

@app.get("/books/stats/")
def get_book_stats(session: Session = Depends(get_session)):
    """Get comprehensive book statistics"""
    all_books = session.exec(select(Book)).all()
    
    if not all_books:
        return {
            "total_books": 0,
            "in_stock_count": 0,
            "out_of_stock_count": 0,
            "total_inventory_value": 0,
            "average_price": 0,
            "average_rating": 0,
            "genre_distribution": {},
            "language_distribution": {},
            "price_range_distribution": {}
        }
    
    total_count = len(all_books)
    total_value = sum(b.price * b.stock for b in all_books)
    avg_price = sum(b.price for b in all_books) / total_count
    avg_rating = sum(b.rating for b in all_books) / total_count
    
    in_stock = [b for b in all_books if b.stock > 0]
    out_of_stock = [b for b in all_books if b.stock == 0]
    
    # Genre distribution
    genre_stats = {}
    for book in all_books:
        genre_stats[book.genre] = genre_stats.get(book.genre, 0) + 1
    
    # Language distribution
    language_stats = {}
    for book in all_books:
        language_stats[book.language] = language_stats.get(book.language, 0) + 1
    
    # Price range distribution
    price_ranges = {
        "0-20": len([b for b in all_books if b.price < 20]),
        "20-50": len([b for b in all_books if 20 <= b.price < 50]),
        "50-100": len([b for b in all_books if 50 <= b.price < 100]),
        "100+": len([b for b in all_books if b.price >= 100])
    }
    
    return {
        "total_books": total_count,
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_of_stock),
        "total_inventory_value": round(total_value, 2),
        "average_price": round(avg_price, 2),
        "average_rating": round(avg_rating, 2),
        "genre_distribution": genre_stats,
        "language_distribution": language_stats,
        "price_range_distribution": price_ranges
    }

# ============================================================
# EXPORT FUNCTIONALITY
# ============================================================

@app.get("/books/export/csv")
def export_books_csv(session: Session = Depends(get_session)):
    """Export all books as CSV"""
    books = session.exec(select(Book)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Title', 'ISBN', 'Description', 'Price', 'Stock',
        'Pages', 'Genre', 'Language', 'Rating', 'Reviews Count',
        'Author ID', 'Author Name', 'Publisher ID', 'Publisher Name',
        'Publication Date', 'Created At', 'Updated At'
    ])
    
    for book in books:
        writer.writerow([
            book.id,
            book.title,
            book.isbn,
            book.description[:100] + '...' if len(book.description) > 100 else book.description,
            book.price,
            book.stock,
            book.pages,
            book.genre,
            book.language,
            book.rating,
            book.reviews_count,
            book.author_id,
            book.author.name if book.author else "Unknown",
            book.publisher_id,
            book.publisher.name if book.publisher else "Unknown",
            book.publication_date,
            book.created_at,
            book.updated_at
        ])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_export.csv"}
    )

# ============================================================
# HEALTH CHECK & ROOT
# ============================================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BookStore API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to BookStore API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "authors": "/authors",
            "publishers": "/publishers",
            "books": "/books",
            "reviews": "/reviews",
            "search": "/books/search/",
            "stats": "/books/stats/",
            "export": "/books/export/csv"
        }
    }

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)