from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ActivePlanningApplications(Base):
    __tablename__ = "active_planning_applications"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    last_updated = Column(String)
    update_notice = Column(String)
    request = Column(String)
    proposal = Column(String)
    process = Column(String)
    status = Column(String)
    contact_info = Column(String)
