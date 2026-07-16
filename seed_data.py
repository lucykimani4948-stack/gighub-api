# seed_data.py - Populate database with sample data
from sqlmodel import Session
from database.session import engine, create_db_and_tables
from models import Author, Publisher, Book
from datetime import datetime

def seed_database():
    create_db_and_tables()
    
    with Session(engine) as session:
        # Create Authors
        authors = [
            Author(name="J.K. Rowling", bio="British author, best known for Harry Potter series", nationality="British", birth_year=1965),
            Author(name="George R.R. Martin", bio="American author of A Song of Ice and Fire", nationality="American", birth_year=1948),
            Author(name="J.R.R. Tolkien", bio="English writer and philologist", nationality="British", birth_year=1892),
            Author(name="Stephen King", bio="American author of horror and supernatural fiction", nationality="American", birth_year=1947),
        ]
        
        for author in authors:
            session.add(author)
        session.commit()
        
        # Create Publishers
        publishers = [
            Publisher(name="Penguin Random House", address="New York, USA", website="penguinrandomhouse.com"),
            Publisher(name="HarperCollins", address="New York, USA", website="harpercollins.com"),
            Publisher(name="Simon & Schuster", address="New York, USA", website="simonandschuster.com"),
        ]
        
        for publisher in publishers:
            session.add(publisher)
        session.commit()
        
        # Create Books
        books = [
            Book(
                title="Harry Potter and the Philosopher's Stone",
                isbn="9780747532699",
                description="First book in the Harry Potter series",
                price=25.99,
                stock=50,
                pages=223,
                genre="Fantasy",
                language="English",
                author_id=1,
                publisher_id=1,
                publication_date=datetime(1997, 6, 26)
            ),
            Book(
                title="A Game of Thrones",
                isbn="9780553103540",
                description="First book in A Song of Ice and Fire series",
                price=29.99,
                stock=30,
                pages=694,
                genre="Fantasy",
                language="English",
                author_id=2,
                publisher_id=2,
                publication_date=datetime(1996, 8, 1)
            ),
            Book(
                title="The Hobbit",
                isbn="9780547928227",
                description="Classic fantasy adventure",
                price=19.99,
                stock=40,
                pages=300,
                genre="Fantasy",
                language="English",
                author_id=3,
                publisher_id=3,
                publication_date=datetime(1937, 9, 21)
            ),
            Book(
                title="The Shining",
                isbn="9780307743657",
                description="Classic horror novel",
                price=18.99,
                stock=25,
                pages=447,
                genre="Horror",
                language="English",
                author_id=4,
                publisher_id=1,
                publication_date=datetime(1977, 1, 28)
            ),
        ]
        
        for book in books:
            session.add(book)
        session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created {len(authors)} authors")
        print(f"Created {len(publishers)} publishers")
        print(f"Created {len(books)} books")

if __name__ == "__main__":
    seed_database()