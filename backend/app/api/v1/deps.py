from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from ..core.database import get_db
from ..core.config import settings
from ..models.user import User, UserRole
from ..core.exceptions import UnauthorizedException, ForbiddenException
from ..schemas.user import TokenData

# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    credentials_exception = UnauthorizedException("无效的认证凭据")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    
    # 查询用户
    user = await db.get(User, token_data.user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")
    if user.is_deleted:
        raise UnauthorizedException("用户已被删除")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise UnauthorizedException("用户已被禁用")
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("需要管理员权限")
    return current_user


async def get_current_user_or_none(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """获取当前用户，如果没有认证则返回None"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        
        user = await db.get(User, int(user_id))
        if user and user.is_active and not user.is_deleted:
            return user
        return None
    except JWTError:
        return None