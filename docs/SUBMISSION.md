CLINICGUARD API - COMPLETE SUBMISSION

Student: LUCY WAMBUI KIMANI

Registration: C027-01-0890/2024

date: August 5, 2026



TABLE OF CONTENTS



1\. Student Information

2\. Exercise 1: Audit Log (Questions \& Answers)

3\. Exercise 2: Patient Assignment Workflow (Questions \& Answers)

4\. Exercise 3: Secure Patient Search (Questions \& Answers)

5\. Complete Implementation Summary

6\. All Endpoints List

7\. Rate Limits Applied

8\. Security Features



1\. STUDENT INFORMATION



Name: LUCY WAMBUI KIMANI

Registration Number: C027-01-0890/2024

Course: Programming Assignment

Date: August 5, 2026

Module: Lab 8: Authorization \& Rate Limiting

Project: ClinicGuard Patient Management API



2\. EXERCISE 1: AUDIT LOG



QUESTION 1: What information should be logged?



ANSWER:

The audit log should capture the following information for every patient record access:



| Field | Description | Example |

|-------|-------------|---------|

| user\_id | ID of user who performed action | 1 (admin user) |

| patient\_id | ID of patient record accessed | 5 (Faith Auma) |

| action | HTTP method used | GET, POST, PATCH, DELETE |

| endpoint | API endpoint accessed | /patients/5 |

| ip\_address | Client IP address | 192.168.1.100 |

| timestamp | Date and time of action | 2026-08-05T16:55:16 |



CODE IMPLEMENTATION:



class AuditLog(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   user\_id: int = Field(foreign\_key="user.id")

&#x20;   patient\_id: Optional\[int] = Field(default=None, foreign\_key="patient.id")

&#x20;   action: str  # CREATE, READ, UPDATE, DELETE

&#x20;   endpoint: str

&#x20;   ip\_address: Optional\[str] = None

&#x20;   timestamp: datetime = Field(default\_factory=datetime.utcnow)







QUESTION 2: Should audit logs be accessible to all users or only admins?



ANSWER:

Audit logs should ONLY be accessible to admin users for the following reasons:



1\. SECURITY: Patient records contain sensitive medical information

2\. PRIVACY: Regular users shouldn't know who accessed what

3\. COMPLIANCE: Medical data regulations (HIPAA) require restricted access

4\. ACCOUNTABILITY: Only admins should monitor and audit system usage



ACCESS CONTROL MATRIX:

| User Role | Can View Audit Logs |

|-----------|---------------------|

| Admin | YES |

| Doctor | NO |

| Receptionist | NO |



CODE IMPLEMENTATION:



@app.get("/audit-logs")

def get\_audit\_logs(

&#x20;   admin: User = Depends(get\_current\_admin),  # Only admin can access

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   return session.exec(select(AuditLog)).all()





QUESTION 3: How would you implement this without slowing down the main API?



ANSWER:

Multiple approaches can be used to implement audit logging without affecting API performance:



APPROACH 1: Asynchronous Middleware

\-----------------------------------

@app.middleware("http")

async def audit\_log\_middleware(request: Request, call\_next):

&#x20;   response = await call\_next(request)  # Process request first

&#x20;   # Log asynchronously after response

&#x20;   return response



APPROACH 2: Background Tasks

\----------------------------

from fastapi import BackgroundTasks



@app.post("/patients")

def create\_patient(

&#x20;   background\_tasks: BackgroundTasks,

&#x20;   patient\_data: PatientCreate,

&#x20;   current\_user: User = Depends(get\_current\_user)

):

&#x20;   # Create patient first

&#x20;   db\_patient = Patient(...)

&#x20;   session.add(db\_patient)

&#x20;   session.commit()

&#x20;   

&#x20;   # Log in background

&#x20;   background\_tasks.add\_task(log\_audit, current\_user.id, db\_patient.id, "CREATE")

&#x20;   return db\_patient



APPROACH 3: Separate Database/Queue

\-----------------------------------

\- Write logs to a separate database

\- Use a message queue (RabbitMQ, Redis)

\- Process logs in batches



APPROACH 4: Separate Thread

\---------------------------

import threading



def log\_audit\_async(user\_id, patient\_id, action):

&#x20;   # Log in separate thread

&#x20;   pass



\# Call without waiting

threading.Thread(target=log\_audit\_async, args=(user\_id, patient\_id, "READ")).start()



PERFORMANCE COMPARISON:

| Method | Performance Impact | Implementation Complexity |

|--------|-------------------|---------------------------|

| Async Middleware | Very Low | Easy |

| Background Tasks | Low | Easy |

| Separate DB | Low | Medium |

| Message Queue | Very Low | Hard |



3\. EXERCISE 2: PATIENT ASSIGNMENT WORKFLOW



QUESTION 1: What endpoint would you need to claim a patient?



ANSWER:

The endpoint to claim a patient is:



PATCH /patients/{patient\_id}/claim



CODE IMPLEMENTATION:



@app.patch("/patients/{patient\_id}/claim")

def claim\_patient(

&#x20;   patient\_id: int,

&#x20;   current\_user: User = Depends(get\_current\_doctor),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   patient = session.get(Patient, patient\_id)

&#x20;   if not patient:

&#x20;       raise HTTPException(404, "Patient not found")

&#x20;   

&#x20;   if patient.doctor\_id:

&#x20;       raise HTTPException(400, "Patient is already assigned")

&#x20;   

&#x20;   # Assign patient to current doctor

&#x20;   patient.doctor\_id = current\_user.id

&#x20;   patient.updated\_at = datetime.utcnow()

&#x20;   session.commit()

&#x20;   

&#x20;   return {"message": "Patient assigned to you", "patient": patient}



EXAMPLE REQUEST:

PATCH /patients/4/claim

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...



EXAMPLE RESPONSE:

{

&#x20; "message": "Patient John Kamau assigned to you",

&#x20; "patient": {

&#x20;   "id": 4,

&#x20;   "first\_name": "John",

&#x20;   "last\_name": "Kamau",

&#x20;   "doctor\_id": 2

&#x20; }

}





QUESTION 2: Should a doctor be able to unassign a patient?



ANSWER:

YES, doctors should be able to unassign their own patients.



UNASSIGN RULES:

| User | Can Unassign |

|------|--------------|

| Doctor | YES - Only their own patients |

| Admin | YES - ANY patient |

| Doctor | NO - Cannot unassign other doctors' patients |



CODE IMPLEMENTATION:



@app.patch("/patients/{patient\_id}/unassign")

def unassign\_patient(

&#x20;   patient\_id: int,

&#x20;   current\_user: User = Depends(get\_current\_doctor),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   patient = session.get(Patient, patient\_id)

&#x20;   if not patient:

&#x20;       raise HTTPException(404, "Patient not found")

&#x20;   

&#x20;   # Check if doctor owns this patient

&#x20;   if patient.doctor\_id != current\_user.id and current\_user.role != "admin":

&#x20;       raise HTTPException(403, "You can only unassign your own patients")

&#x20;   

&#x20;   patient.doctor\_id = None

&#x20;   patient.updated\_at = datetime.utcnow()

&#x20;   session.commit()

&#x20;   

&#x20;   return {"message": "Patient unassigned", "patient": patient}



USE CASES FOR UNASSIGNING:

1\. Patient transfers to another doctor

2\. Patient is discharged

3\. Doctor is leaving the clinic

4\. Patient requests a different doctor





QUESTION 3: How would you handle a patient assigned to an inactive doctor?



ANSWER:

Multiple approaches can be used:



APPROACH 1: Prevent Deactivation with Patients

\----------------------------------------------

@app.patch("/users/{user\_id}/activate")

def toggle\_user\_activation(

&#x20;   user\_id: int,

&#x20;   activate: bool,

&#x20;   admin: User = Depends(get\_current\_admin),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   user = session.get(User, user\_id)

&#x20;   if not user:

&#x20;       raise HTTPException(404, "User not found")

&#x20;   

&#x20;   # Check if doctor has patients before deactivating

&#x20;   if user.role == "doctor" and activate == False:

&#x20;       patients = session.exec(select(Patient).where(Patient.doctor\_id == user\_id)).all()

&#x20;       if patients:

&#x20;           raise HTTPException(400, "Cannot deactivate doctor with assigned patients")

&#x20;   

&#x20;   user.is\_active = activate

&#x20;   session.commit()

&#x20;   return {"message": f"User activation set to {activate}"}



APPROACH 2: Auto-Reassign Patients

\----------------------------------

@app.patch("/users/{user\_id}/activate")

def toggle\_user\_activation(

&#x20;   user\_id: int,

&#x20;   activate: bool,

&#x20;   admin: User = Depends(get\_current\_admin),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   user = session.get(User, user\_id)

&#x20;   if not user:

&#x20;       raise HTTPException(404, "User not found")

&#x20;   

&#x20;   if user.role == "doctor" and activate == False:

&#x20;       # Reassign patients to admin

&#x20;       patients = session.exec(select(Patient).where(Patient.doctor\_id == user\_id)).all()

&#x20;       for patient in patients:

&#x20;           patient.doctor\_id = None  # Or assign to another doctor

&#x20;   

&#x20;   user.is\_active = activate

&#x20;   session.commit()

&#x20;   return {"message": f"User activation set to {activate}"}



APPROACH 3: Admin Manual Reassignment

\-------------------------------------

@app.patch("/patients/bulk-reassign")

def bulk\_reassign\_patients(

&#x20;   from\_doctor\_id: int,

&#x20;   to\_doctor\_id: int,

&#x20;   admin: User = Depends(get\_current\_admin),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   patients = session.exec(select(Patient).where(Patient.doctor\_id == from\_doctor\_id)).all()

&#x20;   

&#x20;   for patient in patients:

&#x20;       patient.doctor\_id = to\_doctor\_id

&#x20;       patient.updated\_at = datetime.utcnow()

&#x20;   

&#x20;   session.commit()

&#x20;   return {"message": f"{len(patients)} patients reassigned"}



APPROACH 4: Warning System

\--------------------------

@app.get("/patients/inactive-doctors")

def get\_patients\_with\_inactive\_doctors(

&#x20;   admin: User = Depends(get\_current\_admin),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   # Get all patients assigned to inactive doctors

&#x20;   inactive\_doctors = session.exec(select(User).where(

&#x20;       User.role == "doctor",

&#x20;       User.is\_active == False

&#x20;   )).all()

&#x20;   

&#x20;   inactive\_doctor\_ids = \[doc.id for doc in inactive\_doctors]

&#x20;   

&#x20;   patients = session.exec(select(Patient).where(

&#x20;       Patient.doctor\_id.in\_(inactive\_doctor\_ids)

&#x20;   )).all()

&#x20;   

&#x20;   return {

&#x20;       "patients": patients,

&#x20;       "warning": "These patients are assigned to inactive doctors"

&#x20;   }



BEST PRACTICE RECOMMENDATION:

1\. Prevent deactivation - Warn admin about assigned patients

2\. Auto-reassign - Move patients to admin or another doctor

3\. Manual override - Allow admin to decide



4\. EXERCISE 3: SECURE PATIENT SEARCH



QUESTION 1: How would you prevent a doctor from searching patients assigned to 

another doctor?



ANSWER:

Add a WHERE clause filter to the search query.



CODE IMPLEMENTATION:



@app.get("/patients/search")

def search\_patients(

&#x20;   q: str,

&#x20;   current\_user: User = Depends(get\_current\_doctor),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   query = select(Patient).where(

&#x20;       (Patient.first\_name.ilike(f"%{q}%")) |

&#x20;       (Patient.last\_name.ilike(f"%{q}%"))

&#x20;   )

&#x20;   

&#x20;   # SECURITY FILTER: Only show doctor's own patients

&#x20;   if current\_user.role == "doctor":

&#x20;       query = query.where(Patient.doctor\_id == current\_user.id)

&#x20;   

&#x20;   return session.exec(query).all()



SECURITY CHECKS:

| User Role | Can Search | Search Scope |

|-----------|-----------|--------------|

| Admin | YES | All patients |

| Doctor | YES | Own patients only |

| Receptionist | YES | All patients |



EXAMPLE SCENARIO:

\- dr\_james searches for "Mary"

\- Query becomes: WHERE (first\_name LIKE '%Mary%' AND doctor\_id = 2)

\- Only returns patients assigned to dr\_james



SQL COMPARISON:

\-- Without filter (insecure)

SELECT \* FROM patients WHERE first\_name LIKE '%Mary%'

\-- Returns ALL patients named Mary



\-- With filter (secure)

SELECT \* FROM patients 

WHERE first\_name LIKE '%Mary%' 

AND doctor\_id = 2

\-- Returns ONLY Mary Ochieng (assigned to dr\_james)



API RESPONSE EXAMPLE:

GET /patients/search?q=John



// Returns only John Kamau (assigned to dr\_james)

{

&#x20; "patients": \[

&#x20;   {

&#x20;     "id": 4,

&#x20;     "first\_name": "John",

&#x20;     "last\_name": "Kamau",

&#x20;     "doctor\_id": 2

&#x20;   }

&#x20; ]

}





QUESTION 2: What if two doctors share a patient (e.g., a patient has both a 

primary care doctor and a specialist)?



ANSWER:

This requires a MANY-TO-MANY relationship between Patients and Doctors.



CURRENT DESIGN (One-to-Many):

Patient --→ Doctor (One doctor per patient)

Problem: A patient can only have ONE doctor



SOLUTION 1: Junction Table Approach

\-----------------------------------

class PatientDoctor(SQLModel, table=True):

&#x20;   patient\_id: int = Field(foreign\_key="patient.id", primary\_key=True)

&#x20;   doctor\_id: int = Field(foreign\_key="user.id", primary\_key=True)

&#x20;   role: str  # "primary", "specialist"

&#x20;   assigned\_date: datetime = Field(default\_factory=datetime.utcnow)

&#x20;   is\_active: bool = Field(default=True)



\# Updated Patient model

class Patient(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   first\_name: str

&#x20;   last\_name: str

&#x20;   # Remove doctor\_id field

&#x20;   doctors: List\["User"] = Relationship(link\_model=PatientDoctor)



SOLUTION 2: Array of Doctor IDs

\-------------------------------

from sqlalchemy.dialects.postgresql import ARRAY



class Patient(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   first\_name: str

&#x20;   last\_name: str

&#x20;   doctor\_ids: Optional\[List\[int]] = Field(default=\[], sa\_type=ARRAY(Integer))

&#x20;   primary\_doctor\_id: Optional\[int] = Field(default=None, foreign\_key="user.id")



SOLUTION 3: Separate Specialist Table

\-------------------------------------

class SpecialistReferral(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   patient\_id: int = Field(foreign\_key="patient.id")

&#x20;   specialist\_id: int = Field(foreign\_key="user.id")

&#x20;   referred\_by: int = Field(foreign\_key="user.id")

&#x20;   referral\_date: datetime

&#x20;   specialty: str

&#x20;   status: str  # "active", "completed", "cancelled"



BENEFITS OF MANY-TO-MANY DESIGN:

| Feature | Before (One-to-One) | After (Many-to-Many) |

|---------|---------------------|---------------------|

| Primary Care | YES | YES |

| Specialist | NO | YES |

| Multiple Doctors | NO | YES |

| Doctor Rotation | NO | YES |

| Team Care | NO | YES |



USE CASES:

1\. Patient sees both a Primary Care Doctor and Cardiologist

2\. Patient transfers between doctors

3\. Doctor on vacation - other doctor covers

4\. Specialist consultation



5\. COMPLETE IMPLEMENTATION SUMMARY



ALL ENDPOINTS IMPLEMENTED:

| Category | Endpoint | Method | Access |

|----------|----------|--------|--------|

| Auth | /register | POST | Public |

| Auth | /login | POST | Public |

| Patients | /patients | GET | All logged-in |

| Patients | /patients | POST | Receptionist+ |

| Patients | /patients/{id} | GET | All logged-in |

| Patients | /patients/{id} | PATCH | Doctor/Admin |

| Patients | /patients/{id} | DELETE | Admin only |

| Patients | /patients/search | GET | All logged-in |

| Patients | /patients/search/advanced | GET | All logged-in |

| Patients | /patients/unassigned | GET | Doctor only |

| Patients | /patients/{id}/claim | PATCH | Doctor only |

| Patients | /patients/{id}/unassign | PATCH | Doctor/Admin |

| Patients | /patients/assigned-to-me | GET | Doctor only |

| Users | /users | GET | Admin only |

| Users | /users/{id} | GET | Admin only |

| Users | /users/{id}/role | PATCH | Admin only |

| Users | /users/{id}/activate | PATCH | Admin only |

| Audit | /audit-logs | GET | Admin only |

| Audit | /audit-logs/patient/{id} | GET | Admin only |

| Audit | /audit-logs/user/{id} | GET | Admin only |



6\. RATE LIMITS APPLIED



| Endpoint | Rate Limit | Purpose |

|----------|-----------|---------|

| /register | 5/minute | Prevent spam |

| /login | 5/minute | Prevent brute force |

| /patients (GET) | 30/minute | Normal usage |

| /patients (POST) | 20/hour | Prevent spam |

| /patients/{id} (PATCH) | 20/minute | Normal usage |

| /patients/{id} (DELETE) | 10/hour | Prevent mistakes |

| /patients/search | 20/minute | Normal usage |

| /patients/search/advanced | 20/minute | Normal usage |

| /audit-logs | 20/minute | Admin usage |

| /users | 20/minute | Admin usage |

| /users/{id}/role | 10/minute | Admin usage |

| /users/{id}/activate | 10/minute | Admin usage |

| /patients/unassigned | 20/minute | Doctor usage |

| /patients/{id}/claim | 10/minute | Doctor usage |



7\. SECURITY FEATURES IMPLEMENTED



1\. JWT Token Authentication

2\. Password Hashing (bcrypt with 72-byte truncation)

3\. Role-Based Access Control (Admin, Doctor, Receptionist)

4\. Rate Limiting (prevent brute force and spam)

5\. Audit Logging (track all actions)

6\. Secure Patient Search (doctors see only their patients)

7\. Patient Assignment Workflow (claim/unassign)

8\. Password Protection (minimum 8 characters)

9\. User Activation/Deactivation

10\. IP Address Tracking for Audit



