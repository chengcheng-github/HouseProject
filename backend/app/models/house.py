from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class HouseStatus(str, enum.Enum):
    DRAFT = "0"      # 草稿
    PUBLISHED = "1"  # 已上架
    UNPUBLISHED = "2" # 已下架


class House(Base):
    __tablename__ = "houses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    address = Column(String(500), nullable=False)
    district = Column(String(100), nullable=True, index=True)  # 区域
    max_visits_per_day = Column(Integer, default=3, nullable=False)  # 每天最大预约次数
    
    # 状态字段
    status = Column(Enum(HouseStatus), default=HouseStatus.DRAFT, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="houses")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HouseImage(Base):
    __tablename__ = "house_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联房屋
    house = relationship("House", backref="images")