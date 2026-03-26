from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.house import HouseStatus
from .user import UserResponse


class HouseImageBase(BaseModel):
    """房屋图片基础模型"""
    image_url: str
    is_primary: bool = False


class HouseImageCreate(HouseImageBase):
    """房屋图片创建模型"""
    pass


class HouseImageResponse(HouseImageBase):
    """房屋图片响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HouseBase(BaseModel):
    """房屋基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    area: float = Field(..., gt=0)
    rooms: int = Field(..., gt=0)
    address: str = Field(..., min_length=1, max_length=500)
    district: Optional[str] = None
    max_visits_per_day: int = Field(default=3, ge=1)


class HouseCreate(HouseBase):
    """房屋创建模型"""
    pass


class HouseUpdate(BaseModel):
    """房屋更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    area: Optional[float] = Field(None, gt=0)
    rooms: Optional[int] = Field(None, gt=0)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    district: Optional[str] = None
    max_visits_per_day: Optional[int] = Field(None, ge=1)


class HouseStatusUpdate(BaseModel):
    """房屋状态更新模型"""
    status: HouseStatus


class HouseInDB(HouseBase):
    """数据库中的房屋模型"""
    id: int
    status: HouseStatus
    is_deleted: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HouseResponse(HouseBase):
    """房屋响应模型"""
    id: int
    status: HouseStatus
    user_id: int
    user: Optional[UserResponse] = None
    images: List[HouseImageResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HouseListResponse(BaseModel):
    """房屋列表响应模型"""
    id: int
    title: str
    price: float
    area: float
    rooms: int
    address: str
    district: Optional[str] = None
    status: HouseStatus
    user_id: int
    user_nickname: Optional[str] = None
    primary_image: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True