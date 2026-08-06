<<<<<<< HEAD
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
=======
# models/user.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
>>>>>>> 383572f8d900134b027b956946a9f34aecffa115

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str = Field(min_length=2, max_length=100)
<<<<<<< HEAD
    role: str = Field(default="staff")
=======
    role: str = Field(default="patient")
>>>>>>> 383572f8d900134b027b956946a9f34aecffa115
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
<<<<<<< HEAD

    documents: List["Document"] = Relationship(back_populates="uploader")
=======
    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: Optional[str] = None
>>>>>>> 383572f8d900134b027b956946a9f34aecffa115

class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
<<<<<<< HEAD
    role: str = Field(default="staff")
=======
    role: str = Field(default="patient")
>>>>>>> 383572f8d900134b027b956946a9f34aecffa115

class UserLogin(SQLModel):
    username: str
    password: str

class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
<<<<<<< HEAD
    is_active: bool
    created_at: datetime

class UserUpdate(SQLModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
=======
    created_at: datetime
    is_active: bool
    two_factor_enabled: bool

class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
>>>>>>> 383572f8d900134b027b956946a9f34aecffa115
