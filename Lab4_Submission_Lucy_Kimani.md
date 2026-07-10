Lab 4: FastAPI with PostgreSQL and SQLModels







Name: Lucy Wambui Kimani 

Admission Number: C027-01-0890/2024 

Date: July 10, 2026 







&#x20;GitHub Repository



URL: https://github.com/lucykimani4948-stack/gighub-api





Screenshots



&#x20;Screenshot 1: Swagger UI

!\[Swagger UI](swagger-screenshot.png)



Figure 1: Swagger UI showing all API endpoints



&#x20;Screenshot 2: PostgreSQL Data

!\[PostgreSQL Data](postgres-screenshot.png)



Figure 2: PostgreSQL showing categories and books tables\*



&#x20;Screenshot 3: GitHub Repository

\[GitHub Repository](github-repo-screenshot.png)



Figure 3: GitHub repository with all project files



&#x20;Exercise 1: Category Model



&#x20;File: models/category.py



&#x20;     python

from sqlmodel import SQLModel, Field, Relationship

from typing import List, Optional



class Category(SQLModel, table=True):

&#x20;   """Category model for book classification"""

&#x20;   id: Optional\[int] = Field(default=None, primary\_key=True)

&#x20;   name: str = Field(unique=True, index=True, min\_length=2, max\_length=50)

&#x20;   

&#x20;   # Relationship to books

&#x20;   books: List\["Book"] = Relationship(back\_populates="category")

