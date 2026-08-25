# app/routers/ics.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
import icalendar
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.event import Event
from app.models.calendar import Calendar
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter()


def parse_ics_content(file_content: bytes, calendar_id: int, db: Session):
    """Parse ICS file content and create events in DB."""
    cal = icalendar.Calendar.from_ical(file_content.decode('utf-8'))
    created_events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            event = Event()
            event.calendar_id = calendar_id

            # Title / Summary
            event.title = str(component.get('summary', 'Untitled Event'))

            # Description
            desc = component.get('description')
            if desc:
                event.description = str(desc)

            # Location
            loc = component.get('location')
            if loc:
                event.location = str(loc)

            # Start / End
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')
            if dtstart and dtstart.dt:
                event.start_time = dtstart.dt
                if event.start_time.tzinfo is None:
                    event.start_time = event.start_time.replace(tzinfo=timezone.utc)
            if dtend and dtend.dt:
                event.end_time = dtend.dt
                if event.end_time.tzinfo is None:
                    event.end_time = event.end_time.replace(tzinfo=timezone.utc)
            else:
                # Default 1-hour event if no end specified
                event.end_time = event.start_time + __import__('datetime').timedelta(hours=1)

            # All-day check
            event.all_day = isinstance(dtstart.dt, datetime) is False

            # Recurrence
            rrule = component.get('rrule')
            if rrule:
                event.rrule = str(rrule.to_ical())

            # UID for stable reference
            uid = component.get('uid')
            if uid:
                event.external_uid = str(uid)

            # Status
            status_prop = component.get('status')
            if status_prop:
                event.status = str(status_prop).lower()

            # Store raw ICS snippet
            event.raw_ics = component.to_ical()

            db.add(event)
            created_events.append(event)

    db.commit()
    for ev in created_events:
        db.refresh(ev)
    return created_events


@router.post("/upload/{calendar_id}")
def upload_ics(
    calendar_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest an ICS file for a calendar."""
    # Verify calendar ownership
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.owner_id == current_user.id
    ).first()
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found or access denied"
        )

    file_content = file.file.read()
    events = parse_ics_content(file_content, calendar_id, db)
    return {
        "calendar_id": calendar_id,
        "events_ingested": len(events),
        "event_ids": [e.id for e in events]
    }