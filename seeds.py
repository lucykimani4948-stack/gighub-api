from sqlmodel import Session, select
from database.session import engine, create_db_and_tables
from models.user import User
from models.document import Document
from auth import hash_password
from datetime import datetime, timedelta
import json
import os

def seed_database():
    create_db_and_tables()
    
    with Session(engine) as session:
        existing_users = session.exec(select(User)).all()
        if existing_users:
            print("Database already seeded. Skipping...")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@sendit.co.ke",
            hashed_password=hash_password("Admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        session.add(admin)
        
        manager = User(
            username="manager",
            email="manager@sendit.co.ke",
            hashed_password=hash_password("Manager123"),
            full_name="Lucy Wambui Kimani",
            role="manager",
            is_active=True
        )
        session.add(manager)
        
        staff1 = User(
            username="staff1",
            email="staff1@sendit.co.ke",
            hashed_password=hash_password("Staff123"),
            full_name="John Mwangi",
            role="staff",
            is_active=True
        )
        session.add(staff1)
        
        staff2 = User(
            username="staff2",
            email="staff2@sendit.co.ke",
            hashed_password=hash_password("Staff123"),
            full_name="Mary Wanjiru",
            role="staff",
            is_active=True
        )
        session.add(staff2)
        
        session.commit()
        
        session.refresh(admin)
        session.refresh(manager)
        session.refresh(staff1)
        session.refresh(staff2)
        
        sample_weather = {
            "city": "Nairobi",
            "country": "Kenya",
            "temperature": 24.5,
            "windspeed": 12.3,
            "weathercode": 1,
            "weather_description": "Mainly clear",
            "time": datetime.now().isoformat(),
            "source": "Open-Meteo"
        }
        
        documents = [
            Document(
                filename="waybill_001.pdf",
                original_filename="waybill_001.pdf",
                file_size=245760,
                file_type="application/pdf",
                status="enriched",
                city="Nairobi",
                country="Kenya",
                weather_data=json.dumps(sample_weather),
                weather_fetched_at=datetime.now(),
                description="Waybill for shipment to Nairobi",
                uploader_id=staff1.id,
                file_path="uploads/waybill_001.pdf",
                uploaded_at=datetime.now() - timedelta(days=2),
                updated_at=datetime.now() - timedelta(days=2)
            ),
            Document(
                filename="invoice_002.pdf",
                original_filename="invoice_002.pdf",
                file_size=156672,
                file_type="application/pdf",
                status="uploaded",
                city="Mombasa",
                country="Kenya",
                weather_data=None,
                weather_fetched_at=None,
                description="Invoice for Mombasa delivery",
                uploader_id=staff2.id,
                file_path="uploads/invoice_002.pdf",
                uploaded_at=datetime.now() - timedelta(days=1),
                updated_at=datetime.now() - timedelta(days=1)
            ),
            Document(
                filename="customs_form_003.jpg",
                original_filename="customs_form_003.jpg",
                file_size=312576,
                file_type="image/jpeg",
                status="processing",
                city="Kisumu",
                country="Kenya",
                weather_data=None,
                weather_fetched_at=None,
                description="Customs declaration for Kisumu",
                uploader_id=staff1.id,
                file_path="uploads/customs_form_003.jpg",
                uploaded_at=datetime.now() - timedelta(hours=6),
                updated_at=datetime.now() - timedelta(hours=6)
            )
        ]
        
        for doc in documents:
            session.add(doc)
        
        session.commit()
        print("Database seeded successfully!")
        print("\n=== Test Credentials ===")
        print("Admin:   admin / Admin123")
        print("Manager: manager / Manager123")
        print("Staff1:  staff1 / Staff123")
        print("Staff2:  staff2 / Staff123")
        print("========================")

if __name__ == "__main__":
    seed_database()