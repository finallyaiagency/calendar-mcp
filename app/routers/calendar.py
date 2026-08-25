# app/routers/calendar.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.calendar import Calendar
from app.models.user import User
from app.schemas.calendar import (
    CalendarResponse, CalendarCreate, CalendarUpdate
)
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=CalendarResponse)
def create_calendar(
    calendar_data: CalendarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar for the current user."""
    db_calendar = Calendar(
        name=calendar_data.name,
        description=calendar_data.description,
        color=calendar_data.color,
        calendar_type=calendar_data.calendar_type,
        owner_id=current_user.id
    )
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar


@router.get("/", response_model=List[CalendarResponse])
def read_calendars(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List calendars for the current user."""
    calendars = db.query(Calendar).filter(
        Calendar.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return calendars


@router.get("/{calendar_id}", response_model=CalendarResponse)
def read_calendar(
    calendar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific calendar by ID."""
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


@router.patch("/{calendar_id}", response_model=CalendarResponse)
def update_calendar(
    calendar_id: int,
    calendar_data: CalendarUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a calendar."""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.owner_id == current_user.id
    ).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )
    for key, value in calendar_data.dict(exclude_unset=True).items():
        setattr(calendar, key, value)
    db.commit()
    db.refresh(calendar)
    return calendar


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    calendar_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar."""
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