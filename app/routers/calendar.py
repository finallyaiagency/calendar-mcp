# app/routers/calendar.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter()


def get_db_dep():
    from app.database import get_db
    return get_db

def get_calendar_model():
    from app.models.calendar import Calendar
    return Calendar

def get_user_model():
    from app.models.user import User
    return User

def get_schemas():
    from app.schemas.calendar import CalendarResponse, CalendarCreate, CalendarUpdate
    return CalendarResponse, CalendarCreate, CalendarUpdate


@router.post("/", response_model=lambda: get_schemas()[0])
def create_calendar(
    calendar_data: dict,
    current_user = Depends(lambda: get_current_user_dep()),
    db: Session = Depends(lambda: get_db_dep())
):
    """Create a new calendar for the current user."""
    Calendar = get_calendar_model()
    CalendarResponse, CalendarCreate, CalendarUpdate = get_schemas()
    
    name = calendar_data.get('name') if isinstance(calendar_data, dict) else calendar_data.name
    description = calendar_data.get('description') if isinstance(calendar_data, dict) else calendar_data.description
    color = calendar_data.get('color') if isinstance(calendar_data, dict) else calendar_data.color
    calendar_type = calendar_data.get('calendar_type') if isinstance(calendar_data, dict) else calendar_data.calendar_type
    
    db_calendar = Calendar(
        name=name,
        description=description,
        color=color,
        calendar_type=calendar_type,
        owner_id=current_user.id
    )
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


@router.get("/", response_model=lambda: List[get_schemas()[0]])
def read_calendars(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(lambda: get_current_user_dep()),
    db: Session = Depends(lambda: get_db_dep())
):
    """List calendars for the current user."""
    Calendar = get_calendar_model()
    calendars = db.query(Calendar).filter(
        Calendar.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return calendars


@router.get("/{calendar_id}", response_model=lambda: get_schemas()[0])
def read_calendar(
    calendar_id: int,
    current_user = Depends(lambda: get_current_user_dep()),
    db: Session = Depends(lambda: get_db_dep())
):
    """Get a specific calendar by ID."""
    Calendar = get_calendar_model()
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.owner_id == current_user.id
    ).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )
    return calendar


@router.patch("/{calendar_id}", response_model=lambda: get_schemas()[0])
def update_calendar(
    calendar_id: int,
    calendar_data: dict,
    current_user = Depends(lambda: get_current_user_dep()),
    db: Session = Depends(lambda: get_db_dep())
):
    """Update a calendar."""
    Calendar = get_calendar_model()
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.owner_id == current_user.id
    ).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )
    for key, value in calendar_data.items():
        if value is not None:
            setattr(calendar, key, value)
    db.commit()
    db.refresh(calendar)
    return calendar


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    calendar_id: int,
    current_user = Depends(lambda: get_current_user_dep()),
    db: Session = Depends(lambda: get_db_dep())
):
    """Delete a calendar."""
    Calendar = get_calendar_model()
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.owner_id == current_user.id
    ).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )
    db.delete(calendar)
    db.commit()
    return None


def get_db_dep():
    from app.database import get_db
    return get_db


def get_current_user_dep():
    from app.routers.auth import get_current_user
    return get_current_user