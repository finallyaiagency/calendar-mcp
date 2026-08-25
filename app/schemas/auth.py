# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    scopes: Optional[list] = None


class User(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    scopes: Optional[list] = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: str  # ISO datetime string
    end_time: str     # ISO datetime string
    all_day: Optional[bool] = False
    rrule: Optional[str] = None
    until: Optional[str] = None
    cost: Optional[float] = None
    currency: Optional[str] = "USD"
    joy_score: Optional[float] = None
    status: Optional[str] = "confirmed"
    calendar_id: int