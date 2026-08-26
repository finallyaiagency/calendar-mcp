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
    external_uid = Column(String(255), index=True, nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    all_day = Column(Boolean, default=False)

    rrule = Column(String(1000), nullable=True)
    until = Column(DateTime(timezone=True), nullable=True)

    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False, index=True)

    cost = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    joy_score = Column(Float, nullable=True)

    status = Column(String(20), default="confirmed")

    raw_ics = Column(Text, nullable=True)

    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    calendar = relationship("Calendar", back_populates="events")