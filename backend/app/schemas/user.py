from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    role: Optional[str] = None
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    role: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class EmailVerify(BaseModel):
    """邮箱验证模型"""
    email: EmailStr


class EmailVerifyCode(BaseModel):
    """邮箱验证码模型"""
    email: EmailStr
    code: str