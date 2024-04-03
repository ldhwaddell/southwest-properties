from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Application(Base):
    __tablename__ = "applications"
    id = Column(String(64), primary_key=True)
    active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    url = Column(String)
    title = Column(Text)
    summary = Column(Text, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    update_notice = Column(Text, nullable=True)
    request = Column(Text, nullable=True)
    proposal = Column(Text, nullable=True)
    process = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    documents_submitted_for_evaluation = Column(Text, nullable=True)
    contact_info = Column(Text, nullable=True)
    history = relationship("ApplicationHistory", cascade="all, delete, delete-orphan")


class ApplicationHistory(Base):
    __tablename__ = "application_histories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"))
    created_at = Column(DateTime, default=datetime.now)
    changed = Column(String)
    original = Column(Text)
    updated = Column(Text)


class ScrapedApplication(Base):
    __tablename__ = "scraped_applications"
    id = Column(String(64), primary_key=True)
    active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    url = Column(String)
    title = Column(Text)
    summary = Column(Text, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    update_notice = Column(Text, nullable=True)
    request = Column(Text, nullable=True)
    proposal = Column(Text, nullable=True)
    process = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    documents_submitted_for_evaluation = Column(Text, nullable=True)
    contact_info = Column(Text, nullable=True)
