from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    Integer,
    Float,
)
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


class FourFourFourRentListing(Base):
    __tablename__ = "fourfourfourrent_listings"
    id = Column(String(64), primary_key=True)
    available = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    management = Column(String)
    url = Column(String)
    address = Column(String)
    building = Column(String)
    unit = Column(String, nullable=True)
    location = Column(String, nullable=True)
    square_feet = Column(Float, nullable=True)
    available_date = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    rooms = Column(String, nullable=True)
    leasing_info = Column(Text, nullable=True)
    description_info = Column(Text, nullable=True)
    building_info = Column(Text, nullable=True)
    suite_info = Column(Text, nullable=True)
    history = relationship(
        "FourFourFourRentListingHistory", cascade="all, delete, delete-orphan"
    )


class FourFourFourRentListingHistory(Base):
    __tablename__ = "fourfourfourrent_listings_histories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(String(64), ForeignKey("fourfourfourrent_listings.id"))
    created_at = Column(DateTime, default=datetime.now)
    changed = Column(String)
    original = Column(Text)
    updated = Column(Text)


class ScrapedFourFourFourRentListing(Base):
    __tablename__ = "scraped_fourfourfourrent_listings"
    id = Column(String(64), primary_key=True)
    available = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    management = Column(String)
    url = Column(String)
    address = Column(String)
    building = Column(String)
    unit = Column(String, nullable=True)
    location = Column(String, nullable=True)
    square_feet = Column(Float, nullable=True)
    available_date = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    rooms = Column(String, nullable=True)
    leasing_info = Column(Text, nullable=True)
    description_info = Column(Text, nullable=True)
    building_info = Column(Text, nullable=True)
    suite_info = Column(Text, nullable=True)


class ApartmentsDotComListing(Base):
    __tablename__ = "apartments_dot_com_listings"
    id = Column(String(7), primary_key=True)
    available = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    # management = Column(String)
    url = Column(String)
    address = Column(String)
    building = Column(String)
    monthly_rent = Column(String, nullable=True)
    bedrooms = Column(String, nullable=True)
    bathrooms = Column(String, nullable=True)
    square_feet = Column(String, nullable=True)
    about = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    fees = Column(Text, nullable=True)
    history = relationship(
        "ApartmentsDotComListingHistory", cascade="all, delete, delete-orphan"
    )


class ApartmentsDotComListingHistory(Base):
    __tablename__ = "apartments_dot_com_listings_histories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(String(7), ForeignKey("apartments_dot_com_listings.id"))
    created_at = Column(DateTime, default=datetime.now)
    changed = Column(String)
    original = Column(Text)
    updated = Column(Text)


class ScrapedApartmentsDotComListing(Base):
    __tablename__ = "scraped_apartments_dot_com_listings"
    id = Column(String(7), primary_key=True)
    available = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    # management = Column(String)
    url = Column(String)
    address = Column(String)
    building = Column(String)
    monthly_rent = Column(String, nullable=True)
    bedrooms = Column(String, nullable=True)
    bathrooms = Column(String, nullable=True)
    square_feet = Column(String, nullable=True)
    about = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    fees = Column(Text, nullable=True)
