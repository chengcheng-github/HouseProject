from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import verify_password, get_password_hash
from ..core.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """创建用户"""
    # 检查邮箱是否已存在
    stmt = select(User).where(User.email == user_create.email, User.is_deleted == False)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise BadRequestException("该邮箱已被注册")
    
    # 创建新用户
    db_user = User(
        email=user_create.email,
        password_hash=get_password_hash(user_create.password),
        nickname=user_create.nickname,
        avatar=user_create.avatar,
        role=UserRole.USER,  # 默认是普通用户
        is_active=True,
        is_deleted=False,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """验证用户"""
    stmt = select(User).where(User.email == email, User.is_deleted == False)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")
    
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    user = await db.get(User, user_id)
    if not user or user.is_deleted:
        return None
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    stmt = select(User).where(User.email == email, User.is_deleted == False)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User:
    """更新用户信息"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("用户不存在")
    
    # 如果更新邮箱，检查是否已被使用
    if user_update.email and user_update.email != user.email:
        stmt = select(User).where(
            User.email == user_update.email,
            User.id != user_id,
            User.is_deleted == False
        )
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise BadRequestException("该邮箱已被使用")
    
    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user