# app/routers/ics.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
import icalendar
from datetime import datetime, timezone
from typing import List

router = APIRouter()


def get_db_dep():
    from app.database import get_db
    return get_db

def get_event_model():
    from app.models.event import Event
    return Event

def get_calendar_model():
    from app.models.calendar import Calendar
    return Calendar

def get_current_user_dep():
    from app.routers.auth import get_current_user
    return get_current_user


def parse_ics_content(file_content: bytes, calendar_id: int, db: Session):
    """Parse ICS file content and create events in DB."""
    cal = icalendar.Calendar.from_ical(file_content.decode('utf-8'))
    created_events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            Event = get_event_model()
            event = Event()
            event.calendar_id = calendar_id

            event.title = str(component.get('summary', 'Untitled Event'))

            desc = component.get('description')
            if desc:
                event.description = str(desc)

            loc = component.get('location')
            if loc:
                event.location = str(loc)

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
                event.end_time = event.start_time + __import__('datetime').timedelta(hours=1)

            event.all_day = isinstance(dtstart.dt, datetime) is False

            rrule = component.get('rrule')
            if rrule:
                event.rrule = str(rrule.to_ical())

            uid = component.get('uid')
            if uid:
                event.external_uid = str(uid)

            status_prop = component.get('status')
            if status_prop:
                event.status = str(status_prop).lower()

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
    current_user = Depends(lambda: get_current_user_dep()),
    db = Depends(lambda: get_db_dep())
):
    """Ingest an ICS file for a calendar."""
    Calendar = get_calendar_model()
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


def get_db_dep():
    from app.database import get_db
    return get_db

def get_calendar_model():
    from app.models.calendar import Calendar
    return Calendar

def get_current_user_dep():
    from app.routers.auth import get_current_user
    return get_current_user