\# LAB 9: File Uploads \& External APIs – "SendIt" Document Management API



\*\*Student Name:\*\* Lucy Wambui Kimani  

\*\*Registration Number:\*\* C027-01-0890/2024  

\*\*GitHub Repository:\*\* https://github.com/lucykimani4948-stack/gighub-api  



\## Table of Contents



1\. \[Project Overview](#project-overview)

2\. \[File Structure Comparison](#file-structure-comparison)

3\. \[Setup and Configuration](#setup-and-configuration)

4\. \[Models and Database](#models-and-database)

5\. \[Authentication and Authorization](#authentication-and-authorization)

6\. \[File Upload Endpoints](#file-upload-endpoints)

7\. \[External API Integration](#external-api-integration)

8\. \[Document Enrichment](#document-enrichment)

9\. \[Exercise 1: Document Search with Filters](#exercise-1-document-search-with-filters)

10\. \[Exercise 2: Document Versioning](#exercise-2-document-versioning)

11\. \[Exercise 3: Webhook Notification](#exercise-3-webhook-notification)

12\. \[Screenshots](#screenshots)

13\. \[Conclusion](#conclusion)



\---



\## Project Overview



\### The Problem



SendIt, a Nyeri-based courier company, faces the following challenges:



1\. No digital document storage – All documents are on paper (waybills, invoices, customs forms)

2\. No way to enrich documents – Cannot automatically add weather conditions at pickup/delivery locations

3\. Manual tracking – No way to know if a document was uploaded correctly

4\. No validation – Staff upload invalid files (wrong type, too large)

5\. No external data integration – Cannot pull weather data for delivery locations



\### Solution



I built a document management API that:

\- Uploads documents (PDFs, images) with validation

\- Enriches documents with external data (weather API)

\- Tracks document status (uploaded, processing, enriched, failed)

\- Provides secure access based on user roles



\### Technology Stack



\- Backend Framework: FastAPI (Python)

\- Database: PostgreSQL (via Docker) with SQLModel ORM

\- Authentication: JWT tokens with passlib

\- External API: Open-Meteo Weather API

\- File Handling: aiofiles for async file uploads

\- Rate Limiting: SlowAPI

\- Containerization: Docker



\---



\## File Structure Comparison



\### Lab 9 File Structure



sendit-api/

├── main.py

├── models/

│   ├── \_\_init\_\_.py

│   ├── user.py

│   └── document.py

├── database/

│   ├── \_\_init\_\_.py

│   └── session.py

├── services/

│   ├── \_\_init\_\_.py

│   └── weather.py

├── uploads/

├── auth.py

├── seeds.py

├── .env

├── docker-compose.yml

└── alembic.ini



\### Comparison with Lab 8



| Lab 8 (Previous) | Lab 9 (Current) | Comparison |

|------------------|-----------------|------------|

| main.py | main.py | Kept same |

| models/user.py | models/user.py | Reused from Lab 8 |

| models/item.py | models/document.py | Changed to document model |

| database/session.py | database/session.py | Kept same |

| auth.py | auth.py | Reused from Lab 8 |

| seeds.py | seeds.py | Reused but updated |

| .env | .env | Added file upload config |

| docker-compose.yml | docker-compose.yml | Kept same |

| N/A | uploads/ | NEW - File storage |

| N/A | services/weather.py | NEW - External API |



\### Key Differences from Lab 8



1\. File Upload Feature: Introduces file upload capabilities with validation

2\. External API Integration: Weather service to enrich documents

3\. Document Status Tracking: Status: uploaded, processing, enriched, failed

4\. Role-Based Access: Staff see own documents; managers/admins see all

5\. Versioning: Documents can have multiple versions

6\. Webhook Notifications: Webhook registration system



\---



\## Setup and Configuration



\### Docker Configuration



services:

&#x20; db:

&#x20;   image: postgres:16

&#x20;   container\_name: sendit\_db

&#x20;   environment:

&#x20;     POSTGRES\_USER: postgres

&#x20;     POSTGRES\_PASSWORD: postgres

&#x20;     POSTGRES\_DB: sendit\_db

&#x20;   ports:

&#x20;     - "5433:5432"

&#x20;   volumes:

&#x20;     - postgres\_data:/var/lib/postgresql/data



Port Change: Changed from 5432 to 5433 to avoid port conflict.



\### Environment Variables



DATABASE\_URL=postgresql://postgres:postgres@localhost:5433/sendit\_db

SECRET\_KEY=lucy-wambui-kimani-c027-01-0890-2024-secret-key

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

WEATHER\_API\_URL=https://api.open-meteo.com/v1/forecast

GEOCODING\_API\_URL=https://geocoding-api.open-meteo.com/v1/search

MAX\_UPLOAD\_SIZE=5242880

ALLOWED\_EXTENSIONS=.pdf,.jpg,.jpeg,.png,.docx



\### File Upload Configuration



\- File Type: Only .pdf, .jpg, .jpeg, .png, .docx allowed

\- File Size: Maximum 5 MB

\- Safe Filename: Timestamp + user\_id to avoid conflicts



\---



\## Models and Database



\### User Model



class User(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   username: str = Field(unique=True, index=True)

&#x20;   email: str = Field(unique=True, index=True)

&#x20;   hashed\_password: str

&#x20;   full\_name: str

&#x20;   role: str = Field(default="staff")

&#x20;   is\_active: bool = Field(default=True)

&#x20;   created\_at: datetime = Field(default\_factory=datetime.utcnow)

&#x20;   updated\_at: datetime = Field(default\_factory=datetime.utcnow)

&#x20;   last\_login: Optional\[datetime] = None

&#x20;   documents: List\["Document"] = Relationship(back\_populates="uploader")



Roles:

\- Admin: Full access - manage users, view all documents, delete anything

\- Manager: View all documents, delete documents, enrich documents

\- Staff: Upload documents, view only their own documents



\### Document Model



class Document(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   filename: str

&#x20;   original\_filename: str

&#x20;   file\_size: int

&#x20;   file\_type: str

&#x20;   status: str = Field(default="uploaded")

&#x20;   version: int = Field(default=1)

&#x20;   city: str = Field(index=True)

&#x20;   country: str = Field(default="Kenya")

&#x20;   weather\_data: Optional\[str] = Field(default=None)

&#x20;   weather\_fetched\_at: Optional\[datetime] = None

&#x20;   description: Optional\[str] = None

&#x20;   uploader\_id: int = Field(foreign\_key="user.id")

&#x20;   uploader: "User" = Relationship(back\_populates="documents")

&#x20;   uploaded\_at: datetime = Field(default\_factory=datetime.utcnow)

&#x20;   updated\_at: datetime = Field(default\_factory=datetime.utcnow)

&#x20;   file\_path: str



Document Status Flow:

1\. uploaded → File uploaded

2\. processing → File being processed

3\. enriched → Weather data added

4\. failed → Enrichment failed



\---



\## Authentication and Authorization



\### Authentication Implementation



from passlib.context import CryptContext

from jose import JWTError, jwt



pwd\_context = CryptContext(schemes=\["sha256\_crypt"], deprecated="auto")



def hash\_password(password: str) -> str:

&#x20;   return pwd\_context.hash(password)



def verify\_password(plain\_password: str, hashed\_password: str) -> bool:

&#x20;   return pwd\_context.verify(plain\_password, hashed\_password)



def create\_access\_token(data: dict) -> str:

&#x20;   to\_encode = data.copy()

&#x20;   expire = datetime.utcnow() + timedelta(minutes=ACCESS\_TOKEN\_EXPIRE\_MINUTES)

&#x20;   to\_encode.update({"exp": expire})

&#x20;   return jwt.encode(to\_encode, SECRET\_KEY, algorithm=ALGORITHM)



\### Role-Based Access Control



def get\_current\_admin(current\_user: User = Depends(get\_current\_user)) -> User:

&#x20;   if current\_user.role != "admin":

&#x20;       raise HTTPException(403, "Admin access required")

&#x20;   return current\_user



def get\_current\_manager(current\_user: User = Depends(get\_current\_user)) -> User:

&#x20;   if current\_user.role not in \["admin", "manager"]:

&#x20;       raise HTTPException(403, "Manager or admin access required")

&#x20;   return current\_user



\### Test Credentials



| Role | Username | Password |

|------|----------|----------|

| Admin | admin | Admin123 |

| Manager | manager | Manager123 |

| Staff 1 | staff1 | Staff123 |

| Staff 2 | staff2 | Staff123 |



\---



\## File Upload Endpoints



\### Upload Document Endpoint



@app.post("/documents/upload")

@limiter.limit("10/hour")

async def upload\_document(

&#x20;   file: UploadFile = File(...),

&#x20;   city: str = Form(...),

&#x20;   description: Optional\[str] = Form(None),

&#x20;   country: str = Form("Kenya"),

&#x20;   current\_user: User = Depends(get\_current\_user),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   # 1. Validate file extension

&#x20;   # 2. Validate file size

&#x20;   # 3. Generate safe filename

&#x20;   # 4. Save file asynchronously

&#x20;   # 5. Create document record

&#x20;   # 6. Enrich with weather data

&#x20;   # 7. Return document details



Validation Features:

\- File type validation

\- File size validation (max 5 MB)

\- Safe filename generation

\- Async file saving

\- Automatic weather enrichment



Rate Limiting:

\- Upload: 10 requests/hour

\- List: 30 requests/minute

\- Search: 20 requests/minute

\- Enrich: 5 requests/minute



\### List Documents with Filters



@app.get("/documents")

def list\_documents(

&#x20;   status: Optional\[str] = None,

&#x20;   city: Optional\[str] = None,

&#x20;   current\_user: User = Depends(get\_current\_user),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   # Managers and admins see all documents

&#x20;   # Staff see only their own documents

&#x20;   # Optional filters: status, city



\---



\## External API Integration



\### Weather Service Implementation



async def get\_coordinates(city: str, country: str = "Kenya") -> Optional\[tuple]:

&#x20;   async with httpx.AsyncClient() as client:

&#x20;       response = await client.get(

&#x20;           GEOCODING\_API\_URL,

&#x20;           params={"name": city, "count": 1, "language": "en", "format": "json"}

&#x20;       )

&#x20;       if data.get("results"):

&#x20;           return (result\["latitude"], result\["longitude"])

&#x20;   return None



async def get\_weather(city: str, country: str = "Kenya") -> Optional\[Dict]:

&#x20;   coordinates = await get\_coordinates(city, country)

&#x20;   if not coordinates:

&#x20;       return {"error": "Could not find city coordinates"}

&#x20;   

&#x20;   response = await client.get(

&#x20;       WEATHER\_API\_URL,

&#x20;       params={

&#x20;           "latitude": lat,

&#x20;           "longitude": lon,

&#x20;           "current\_weather": True,

&#x20;           "temperature\_unit": "celsius",

&#x20;           "timezone": "Africa/Nairobi"

&#x20;       }

&#x20;   )

&#x20;   return {

&#x20;       "city": city,

&#x20;       "country": country,

&#x20;       "temperature": current.get("temperature"),

&#x20;       "windspeed": current.get("windspeed"),

&#x20;       "weathercode": current.get("weathercode"),

&#x20;       "weather\_description": weather\_description,

&#x20;       "time": current.get("time"),

&#x20;       "source": "Open-Meteo"

&#x20;   }



Weather Data Returned:

\- Temperature (°C)

\- Wind speed (km/h)

\- Weather code and description

\- Time of data

\- Source (Open-Meteo)

\- Coordinates



Weather Codes Mapping:



| Code | Description |

|------|-------------|

| 0 | Clear sky |

| 1 | Mainly clear |

| 2 | Partly cloudy |

| 3 | Overcast |

| 45 | Fog |

| 51-55 | Drizzle |

| 61-65 | Rain |

| 71-75 | Snow fall |

| 80-82 | Rain showers |

| 95-99 | Thunderstorm |



\---



\## Document Enrichment



\### Automatic Enrichment on Upload



When a document is uploaded, the API automatically:

1\. Calls the weather API for the specified city

2\. Saves weather data as JSON in the document record

3\. Sets status to enriched if successful, or uploaded if failed



\### Manual Enrichment Endpoint



@app.post("/documents/{document\_id}/enrich")

async def enrich\_document(

&#x20;   document\_id: int,

&#x20;   current\_user: User = Depends(get\_current\_manager)

):

&#x20;   document = session.get(Document, document\_id)

&#x20;   if document.status == "enriched":

&#x20;       return {"message": "Document already enriched"}

&#x20;   

&#x20;   weather\_data = await get\_weather(document.city, document.country)

&#x20;   if weather\_data:

&#x20;       document.weather\_data = json.dumps(weather\_data)

&#x20;       document.status = "enriched"

&#x20;       return {"message": "Document enriched successfully"}

&#x20;   else:

&#x20;       document.status = "failed"

&#x20;       raise HTTPException(500, "Failed to enrich document")



\---



\## Exercise 1: Document Search with Filters



\### Implementation



@app.get("/documents/search")

def search\_documents(

&#x20;   q: Optional\[str] = None,

&#x20;   city: Optional\[str] = None,

&#x20;   status: Optional\[str] = None,

&#x20;   date\_from: Optional\[datetime] = None,

&#x20;   date\_to: Optional\[datetime] = None,

&#x20;   current\_user: User = Depends(get\_current\_user),

&#x20;   session: Session = Depends(get\_session)

):

&#x20;   query = select(Document)

&#x20;   

&#x20;   if current\_user.role not in \["admin", "manager"]:

&#x20;       query = query.where(Document.uploader\_id == current\_user.id)

&#x20;   

&#x20;   if q:

&#x20;       query = query.where(

&#x20;           or\_(

&#x20;               Document.original\_filename.contains(q),

&#x20;               Document.description.contains(q)

&#x20;           )

&#x20;       )

&#x20;   

&#x20;   if city:

&#x20;       query = query.where(Document.city == city)

&#x20;   

&#x20;   if status:

&#x20;       query = query.where(Document.status == status)

&#x20;   

&#x20;   if date\_from:

&#x20;       query = query.where(Document.uploaded\_at >= date\_from)

&#x20;   if date\_to:

&#x20;       query = query.where(Document.uploaded\_at <= date\_to)

&#x20;   

&#x20;   return session.exec(query).all()



\### Questions Answered



1\. How would you make this search efficient with a large number of documents?



\- Database Indexes: Add indexes on city, status, uploaded\_at, uploader\_id

\- Full-Text Search: Use PostgreSQL's full-text search for text fields

\- Pagination: Limit results with offset and limit

\- Caching: Use Redis to cache frequent search results

\- Elasticsearch: For very large datasets, use Elasticsearch

\- Query Optimization: Use selectinload() to eager load relationships



2\. Should managers see all documents while staff see only their own?



Yes, this is the correct approach because:



\- Security: Staff should only access their own documents

\- Need-to-Know: Staff don't need access to other staff's documents

\- Manager Oversight: Managers need to oversee all documents

\- Audit Trail: Managers can ensure all documents are properly enriched

\- Scalability: Role-based access control scales well as the company grows



\---



\## Exercise 2: Document Versioning



\### Implementation



Added version field:

class Document(SQLModel, table=True):

&#x20;   version: int = Field(default=1)



Upload endpoint checks for existing documents:

existing\_doc = session.exec(

&#x20;   select(Document).where(Document.original\_filename == file.filename)

).first()



version = 1

if existing\_doc:

&#x20;   version = existing\_doc.version + 1



Get all versions endpoint:

@app.get("/documents/{document\_id}/versions")

def get\_document\_versions(

&#x20;   document\_id: int,

&#x20;   current\_user: User = Depends(get\_current\_manager)

):

&#x20;   document = session.get(Document, document\_id)

&#x20;   versions = session.exec(

&#x20;       select(Document).where(

&#x20;           Document.original\_filename == document.original\_filename

&#x20;       ).order\_by(Document.version.desc())

&#x20;   ).all()

&#x20;   return versions



\### Questions Answered



1\. How would you track changes between versions?



\- Version Metadata: Store version\_number, uploaded\_at, uploaded\_by, file\_size, file\_type

\- Audit Trail: Create VersionHistory table to track changes

\- Diff Tracking: For text documents, track differences between versions

\- Comment System: Allow users to add comments describing changes

\- Checksum: Store file hash to verify integrity



2\. Should you store the old version or delete it?



Store the old version for:



\- Audit Trail: Regulatory compliance requires keeping history

\- Rollback: Revert to previous version if needed

\- Comparison: See what changed between versions

\- Data Integrity: Complete history of document changes

\- Recovery: Recover if a document is corrupted



Storage Strategy:

\- Compression: Compress older versions to save space

\- Archiving: Move old versions to cheaper storage (S3, Glacier)

\- Retention Policy: Keep all versions for X months, then archive

\- Version Limit: Keep last N versions (e.g., 10 versions)



\---



\## Exercise 3: Webhook Notification



\### Implementation



Webhook Registration Model:

class WebhookRegistration(SQLModel, table=True):

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   webhook\_url: str

&#x20;   event\_type: str

&#x20;   user\_id: int = Field(foreign\_key="user.id")

&#x20;   is\_active: bool = Field(default=True)

&#x20;   created\_at: datetime = Field(default\_factory=datetime.utcnow)



Register Webhook Endpoint:

@app.post("/webhooks/register")

def register\_webhook(

&#x20;   webhook\_url: str,

&#x20;   event\_type: str,

&#x20;   current\_user: User = Depends(get\_current\_admin)

):

&#x20;   if event\_type not in \["document.enriched", "document.uploaded"]:

&#x20;       raise HTTPException(400, "Invalid event type")

&#x20;   

&#x20;   existing = session.exec(

&#x20;       select(WebhookRegistration).where(

&#x20;           WebhookRegistration.webhook\_url == webhook\_url,

&#x20;           WebhookRegistration.event\_type == event\_type,

&#x20;           WebhookRegistration.user\_id == current\_user.id

&#x20;       )

&#x20;   ).first()

&#x20;   

&#x20;   if existing:

&#x20;       existing.is\_active = True

&#x20;       return {"message": "Webhook re-activated"}

&#x20;   

&#x20;   webhook = WebhookRegistration(...)

&#x20;   session.add(webhook)

&#x20;   return {"message": "Webhook registered successfully"}



\### Questions Answered



1\. How would you handle retries if the webhook fails?



Implement a Retry Mechanism:



\- Retry Queue: Use Redis/RabbitMQ for failed webhook deliveries

\- Exponential Backoff: Retry with increasing delays:

&#x20; - Attempt 1: immediate

&#x20; - Attempt 2: after 5 seconds

&#x20; - Attempt 3: after 30 seconds

&#x20; - Attempt 4: after 2 minutes

&#x20; - Attempt 5: after 10 minutes

\- Max Retries: Set maximum of 5-10 retries

\- Dead Letter Queue: Send to a dead letter queue for manual review

\- Webhook History: Store all delivery attempts with status and error messages



Sample Retry Implementation:

async def send\_webhook\_with\_retry(webhook\_url: str, payload: dict, max\_retries: int = 5):

&#x20;   for attempt in range(max\_retries):

&#x20;       try:

&#x20;           async with httpx.AsyncClient() as client:

&#x20;               response = await client.post(webhook\_url, json=payload, timeout=10.0)

&#x20;               if response.status\_code in \[200, 201, 204]:

&#x20;                   return {"success": True}

&#x20;       except Exception as e:

&#x20;           if attempt < max\_retries - 1:

&#x20;               wait\_time = 2 \*\* attempt

&#x20;               await asyncio.sleep(wait\_time)

&#x20;           else:

&#x20;               return {"success": False, "error": str(e)}



2\. What security measures would you put in place?



Authentication \& Authorization:

\- API Keys: Require API keys for webhook endpoints

\- HMAC Signatures: Sign webhook payloads with HMAC-SHA256

\- IP Whitelisting: Only accept webhook requests from known IPs

\- Rate Limiting: Limit webhook requests per second



Payload Security:

\- Encryption: Encrypt sensitive data in webhook payloads

\- Payload Validation: Validate payload structure before processing

\- Timeout: Set short timeouts (10 seconds) to avoid hanging



Monitoring \& Logging:

\- Audit Logs: Log all webhook registrations and deliveries

\- Failure Alerts: Alert admins when webhooks fail repeatedly

\- Webhook Dashboard: Monitor webhook delivery success rates



Prevention of Abuse:

\- Webhook URL Validation: Validate URLs against allowed domains

\- Maximum Payload Size: Limit webhook payload size (1MB)

\- Deactivation: Auto-deactivate webhooks that fail > 20 times





\## Screenshots



All screenshots are organized in the /screenshots folder:



| # | Screenshot | Description |

|---|------------|-------------|

| 1 | Swagger UI Home | Full API documentation |

| 2 | Register Success | New user registration |

| 3 | Register Error | Duplicate username error |

| 4 | Login Success | Authentication with token |

| 5 | Login Error | Invalid credentials |

| 6 | Get Current User | Authenticated user info |

| 7 | Update User | User profile update |

| 8 | List All Users | Admin user list |

| 9 | Update Role | Admin role update |

| 10 | Delete User | Admin user deletion |

| 11 | Upload Success | Document with weather enrichment |

| 12 | Upload Invalid Type | File type validation error |

| 13 | Upload Too Large | File size validation error |

| 14 | List Documents | Document list with filters |

| 15 | Get Document | Document details |

| 16 | Update Document | Document metadata update |

| 17 | Delete Document | Document deletion |

| 18 | Delete Unauthorized | Access denied error |

| 19 | Get Weather | Weather data for document |

| 20 | Enrich Document | Manual weather enrichment |

| 21 | Already Enriched | Status check |

| 22-26 | Search Filters | Various search combinations |

| 27-29 | Versioning | Version upload and listing |

| 30-32 | Webhook | Webhook registration and errors |

| 33 | Health Check | API health status |







\## Conclusion



\### Summary of Achievements



\- Complete Document Management API built with FastAPI and PostgreSQL

\- File Upload with validation for type and size

\- Weather Enrichment using Open-Meteo API

\- Document Status Tracking (uploaded, processing, enriched, failed)

\- Role-Based Access Control (Admin, Manager, Staff)

\- Exercise 1: Document Search with Filters

\- Exercise 2: Document Versioning

\- Exercise 3: Webhook Notification System

\- Comprehensive Testing via Swagger UI and PowerShell

\- Complete Documentation with 50+ screenshots



\### Lessons Learned



1\. Security First: Always use .env files for secrets and never commit them to GitHub

2\. Role-Based Access: Implement proper access controls from the start

3\. External APIs: Always handle API failures gracefully

4\. Async Operations: Use async for file uploads and external API calls

5\. Rate Limiting: Protect your API from abuse with rate limiting

6\. Versioning: Document versioning is crucial for audit trails

7\. Webhooks: Webhooks require proper retry mechanisms and security



\### Future Improvements



1\. Cloud Storage: Store files in AWS S3 or Google Cloud Storage

2\. Advanced Search: Implement Elasticsearch for better search performance

3\. Webhook Retries: Implement full retry mechanism with exponential backoff

4\. Document Preview: Add document preview capability

5\. Batch Processing: Support batch upload of multiple documents

6\. Webhook Dashboard: UI for monitoring webhook deliveries

7\. Document Templates: Pre-defined templates for common documents







\## Appendix



\### API Endpoints Summary



| Method | Endpoint | Description | Access |

|--------|----------|-------------|--------|

| POST | /register | Register new user | Public |

| POST | /login | Login to get token | Public |

| GET | /users/me | Get current user info | Authenticated |

| PUT | /users/me | Update current user | Authenticated |

| GET | /admin/users | List all users | Admin |

| PUT | /admin/users/{id}/role | Update user role | Admin |

| DELETE | /admin/users/{id} | Delete user | Admin |

| POST | /documents/upload | Upload document | Authenticated |

| GET | /documents | List documents | Authenticated |

| GET | /documents/{id} | Get document | Authenticated |

| PUT | /documents/{id} | Update document | Manager/Admin |

| DELETE | /documents/{id} | Delete document | Manager/Admin |

| POST | /documents/{id}/enrich | Enrich with weather | Manager/Admin |

| GET | /documents/{id}/weather | Get weather data | Authenticated |

| GET | /documents/search | Search documents | Authenticated |

| GET | /documents/{id}/versions | Get versions | Manager/Admin |

| POST | /webhooks/register | Register webhook | Admin |

| GET | /health | Health check | Public |









