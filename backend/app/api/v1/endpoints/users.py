from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.dependencies import get_mysql_db
from app.api.v1.deps import get_current_active_user, get_admin_user
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.response import SuccessResponse
from app.services.user_service import update_user, get_user_by_id
from app.models.mysqlModels import User

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.put("/me", response_model=SuccessResponse[UserResponse])
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """更新当前用户信息"""
    updated_user = await update_user(db, current_user.id, user_update)
    return SuccessResponse(data=UserResponse.model_validate(updated_user))


@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """获取用户信息（管理员或自己）"""
    # 只有管理员或用户自己可以查看
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看该用户信息"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return SuccessResponse(data=UserResponse.model_validate(user))