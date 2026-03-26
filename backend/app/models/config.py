from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class Config(Base):
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime(timezone=True), nullable=False, unique=True)
    user_registrations = Column(Integer, default=0, nullable=False)
    house_publications = Column(Integer, default=0, nullable=False)
    page_views = Column(Integer, default=0, nullable=False)  # PV
    unique_visitors = Column(Integer, default=0, nullable=False)  # UV
    created_at = Column(DateTime(timezone=True), server_default=func.now())