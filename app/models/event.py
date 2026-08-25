# app/models/event.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey,
    func, Float, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    """
    Core event model.  Ingested from ICS files or created via API.
    Supports all-day events, recurring events, and rich metadata
    for scanning agents (cost, joy, alternatives).
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    # External ICS UID (stable across systems)
    external_uid = Column(String(255), index=True, nullable=True)
    # Human-readable title
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    all_day = Column(Boolean, default=False)

    # Recurrence: RRULE string from ICS (e.g. "FREQ=WEEKLY;BYDAY=MO,WE,FR")
    rrule = Column(String(1000), nullable=True)
    until = Column(DateTime(timezone=True), nullable=True)

    # Calendar FK
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False, index=True)

    # Cost / value tracking for scanning agents
    cost = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    joy_score = Column(Float, nullable=True)  # User-defined happiness rating

    # Status: confirmed, tentative, cancelled
    status = Column(String(20), default="confirmed")

    # Raw ICS payload (for re-export / debugging)
    raw_ics = Column(Text, nullable=True)

    # Flexible metadata (JSON) for extensions
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    calendar = relationship("Calendar", back_populates="events")