# SendIt - Document Management & Enrichment API

**Student:** Lucy Wambui Kimani  
**Reg. No:** C027-01-0890/2024  
**Course:** Lab 9: File Uploads & External APIs

## Project Overview
Document management API for SendIt courier company with weather enrichment.

## Features
- User Authentication with JWT
- Role-Based Access Control (Admin, Manager, Staff)
- File Upload with Validation
- Weather Enrichment via Open-Meteo API
- Document Status Tracking
- Search with Filters
- Document Versioning
- Webhook Notifications

## How to Run
1. Create virtual environment: python -m venv venv
2. Activate: .\venv\Scripts\activate
3. Install: pip install -r requirements.txt
4. Start Docker: docker compose up -d
5. Seed database: python seeds.py
6. Run: uvicorn main:app --reload --port 8000
7. Open: http://localhost:8000/docs

## Test Credentials
- Admin: admin / Admin123
- Manager: manager / Manager123
- Staff: staff1 / Staff123

## Screenshots
All endpoint screenshots are in the /screenshots folder.
