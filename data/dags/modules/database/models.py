from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class ApplicationHistory(Base):
    __tablename__ = "application_histories"
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)
    changed: Mapped[str] = mapped_column(String)
    original: Mapped[str] = mapped_column(Text)
    updated: Mapped[str] = mapped_column(Text)


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)
    url: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_notice: Mapped[Optional[str]] = mapped_column(Text)
    request: Mapped[Optional[str]] = mapped_column(Text)
    proposal: Mapped[Optional[str]] = mapped_column(Text)
    process: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Text)
    documents_submitted_for_evaluation: Mapped[Optional[str]] = Column(Text)
    contact_info: Mapped[Optional[str]] = mapped_column(Text)
    history: Mapped[Optional[List[ApplicationHistory]]] = relationship(
        cascade="all, delete"
    )
