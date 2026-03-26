from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class VisitTimeSlot(str, enum.Enum):
    MORNING = "morning"    # 上午
    AFTERNOON = "afternoon"  # 下午


class VisitStatus(str, enum.Enum):
    PENDING = "0"    # 待确认
    CONFIRMED = "1"  # 已确认
    CANCELLED = "2"  # 已取消


class HouseVisit(Base):
    __tablename__ = "house_visits"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 房屋信息
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    house = relationship("House", backref="visits")
    
    # 访客信息
    visitor_name = Column(String(100), nullable=False)
    visitor_phone = Column(String(20), nullable=False)
    
    # 预约信息
    visit_date = Column(Date, nullable=False, index=True)
    visit_time_slot = Column(Enum(VisitTimeSlot), nullable=False)
    status = Column(Enum(VisitStatus), default=VisitStatus.PENDING, nullable=False)
    remark = Column(Text, nullable=True)
    
    # 创建者信息（可选，如果需要跟踪是谁创建的预约）
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", backref="created_visits")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())