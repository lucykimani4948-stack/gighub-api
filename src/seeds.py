from sqlmodel import Session, select
from database.session import engine, create_tables
from models.user import User
from models.patient import Patient
from auth import hash_password
from datetime import datetime

def seed_database():
    create_tables()
    
    with Session(engine) as session:
        existing_users = session.exec(select(User)).all()
        if existing_users:
            print("Database already has users. Skipping seed.")
            return
        
        print("Seeding database...")
        
        admin = User(
            username="admin",
            email="admin@clinic.com",
            hashed_password=hash_password("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        
        dr_james = User(
            username="dr_james",
            email="james@clinic.com",
            hashed_password=hash_password("doctor123"),
            full_name="Dr. James Mwangi",
            role="doctor",
            is_active=True
        )
        
        dr_sarah = User(
            username="dr_sarah",
            email="sarah@clinic.com",
            hashed_password=hash_password("doctor123"),
            full_name="Dr. Sarah Wanjiru",
            role="doctor",
            is_active=True
        )
        
        receptionist = User(
            username="reception",
            email="reception@clinic.com",
            hashed_password=hash_password("reception123"),
            full_name="Jane Akinyi",
            role="receptionist",
            is_active=True
        )
        
        session.add_all([admin, dr_james, dr_sarah, receptionist])
        session.commit()
        
        session.refresh(admin)
        session.refresh(dr_james)
        session.refresh(dr_sarah)
        session.refresh(receptionist)
        
        patients = [
            Patient(
                first_name="Mary",
                last_name="Ochieng",
                date_of_birth=datetime(1985, 5, 15),
                phone="0712345678",
                email="mary@email.com",
                address="123 Nairobi Street",
                medical_notes="Diabetic, under medication",
                doctor_id=dr_james.id,
                created_by=receptionist.id
            ),
            Patient(
                first_name="Peter",
                last_name="Odhiambo",
                date_of_birth=datetime(1990, 8, 22),
                phone="0723456789",
                email="peter@email.com",
                address="456 Kisumu Road",
                medical_notes="Hypertension",
                doctor_id=dr_sarah.id,
                created_by=receptionist.id
            ),
            Patient(
                first_name="Grace",
                last_name="Njuguna",
                date_of_birth=datetime(1978, 3, 10),
                phone="0734567890",
                email="grace@email.com",
                address="789 Nakuru Ave",
                medical_notes="Asthma, allergy to penicillin",
                doctor_id=dr_james.id,
                created_by=admin.id
            ),
            Patient(
                first_name="John",
                last_name="Kamau",
                date_of_birth=datetime(1995, 11, 30),
                phone="0745678901",
                email="john@email.com",
                address="321 Eldoret Lane",
                medical_notes="Routine checkup",
                doctor_id=None,
                created_by=receptionist.id
            ),
            Patient(
                first_name="Faith",
                last_name="Auma",
                date_of_birth=datetime(1982, 7, 18),
                phone="0756789012",
                email="faith@email.com",
                address="654 Mombasa Road",
                medical_notes="Pregnant, prenatal care",
                doctor_id=None,
                created_by=receptionist.id
            )
        ]
        
        session.add_all(patients)
        session.commit()
        
        print("Database seeded successfully!")
        print("Login Credentials:")
        print("  Admin: admin / admin123")
        print("  Doctor: dr_james / doctor123")
        print("  Doctor: dr_sarah / doctor123")
        print("  Receptionist: reception / reception123")

if __name__ == "__main__":
    seed_database()