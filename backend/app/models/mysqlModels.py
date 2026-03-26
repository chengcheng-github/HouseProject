import datetime
from app.core.settings import Base
from sqlalchemy import Boolean, DateTime, Table, Index, VARCHAR
from sqlalchemy import Column, Integer, String, ForeignKey, Text

class Config(Base):
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(200), nullable=True)
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_time = Column(DateTime, nullable=False)


class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True)
    user_registrations = Column(Integer, default=0, nullable=False)
    house_publications = Column(Integer, default=0, nullable=False)
    page_views = Column(Integer, default=0, nullable=False)  # PV
    unique_visitors = Column(Integer, default=0, nullable=False)  # UV
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    # 角色 user: 普通用户 admin: 管理员
    role = Column(String(100), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_time = Column(DateTime, nullable=False)


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
    
    # 状态字段 草稿："0" 已上架："1"  已下架: "2"
    status = Column(String(100), default="草稿", nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="houses")
    
    # 时间字段
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_time = Column(DateTime, nullable=False)


class HouseImage(Base):
    __tablename__ = "house_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    
    # 关联房屋
    house = relationship("House", backref="images")

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
    # 时间：上午或下午
    visit_time_slot = Column(String(100), nullable=False)
    # 状态 待确认/已确认/已取消
    status = Column(String(100), default="待确认", nullable=False)
    remark = Column(Text, nullable=True)
    
    # 创建者信息（可选，如果需要跟踪是谁创建的预约）
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", backref="created_visits")
    
    # 时间字段
    created_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_time = Column(DateTime, nullable=False)