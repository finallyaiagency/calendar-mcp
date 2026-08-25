# app/schemas/calendar.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.auth import User


class CalendarBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3B82F6"
    calendar_type: Optional[str] = "personal"


class CalendarCreate(CalendarBase):
    pass


class CalendarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    calendar_type: Optional[str] = None


class CalendarResponse(CalendarBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    events: Optional[List["EventResponse"]] = None

    class Config:
        orm_mode = True


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    rrule: Optional[str] = None
    until: Optional[datetime] = None
    calendar_id: int
    cost: Optional[float] = None
    currency: Optional[str] = "USD"
    joy_score: Optional[float] = None
    status: str = "confirmed"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


CalendarResponse.update_forward_refs()