from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ..deps import get_db, get_current_active_user
from ...core.config import settings
from ...core.security import create_access_token
from ...schemas.user import UserCreate, UserResponse, Token, UserLogin
from ...schemas.response import SuccessResponse
from ...services.user_service import create_user, authenticate_user
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=SuccessResponse[UserResponse])
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    user = await create_user(db, user_create)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.post("/login", response_model=SuccessResponse[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return SuccessResponse(data=Token(access_token=access_token))


@router.post("/login/json", response_model=SuccessResponse[Token])
async def login_json(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录（JSON格式）"""
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return SuccessResponse(data=Token(access_token=access_token))


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return SuccessResponse(data=UserResponse.model_validate(current_user))