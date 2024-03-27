from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class Applications(Base):
    __tablename__ = "applications"
    id = Column(String(64), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    url = Column(String)
    title = Column(Text)
    summary = Column(Text)
    last_updated = Column(DateTime)
    update_notice = Column(Text)
    request = Column(Text)
    proposal = Column(Text)
    process = Column(Text)
    status = Column(Text)
    contact_info = Column(Text)
    documents_submitted_for_evaluation = Column(Text)


class ActiveApplication(Base):
    __tablename__ = "active_applications"
    id = Column(String(64), ForeignKey("applications.id"), primary_key=True)
    application = relationship(
        "Application", backref=backref("active_application", uselist=False)
    )


class ArchivedApplication(Base):
    __tablename__ = "archived_applications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"))
    archived_at = Column(DateTime, default=datetime.now)
    application = relationship("Application", backref="archived_applications")


class ApplicationHistory(Base):
    __tablename__ = "application_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(64), ForeignKey("applications.id"))
    changed_data = Column(Text)  # Description of what changed
    change_time = Column(DateTime, default=datetime.now)
    application = relationship("Application", backref="history")
