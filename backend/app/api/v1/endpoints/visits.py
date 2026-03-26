from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.dependencies import get_mysql_db
from app.api.v1.deps import get_admin_user, get_current_active_user
from app.models.mysqlModels import User
from app.models.visit import VisitStatus, VisitTimeSlot
from app.schemas.response import SuccessResponse
from app.services.visit_service import (
    create_visit,
    update_visit_status,
    get_house_visits,
    get_user_visits,
    get_available_dates,
)

router = APIRouter(prefix="/visits", tags=["预约管理"])


@router.post("", response_model=SuccessResponse)
async def create_house_visit(
    house_id: int = Query(..., description="房屋ID"),
    visitor_name: str = Query(..., description="访客姓名"),
    visitor_phone: str = Query(..., description="访客手机号"),
    visit_date: date = Query(..., description="预约日期"),
    time_slot: VisitTimeSlot = Query(..., description="时间段"),
    remark: str = Query(None, description="备注"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """创建预约"""
    visit = await create_visit(
        db=db,
        house_id=house_id,
        visitor_name=visitor_name,
        visitor_phone=visitor_phone,
        visit_date=visit_date,
        time_slot=time_slot,
        remark=remark,
        created_by=current_user.id
    )
    
    return SuccessResponse(data=visit)


@router.get("/house/{house_id}", response_model=SuccessResponse)
async def get_house_visit_list(
    house_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """获取房屋的预约列表"""
    visits = await get_house_visits(
        db=db,
        house_id=house_id,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )
    
    return SuccessResponse(data=visits)


@router.get("/my", response_model=SuccessResponse)
async def get_my_visits(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """获取我的预约列表"""
    visits = await get_user_visits(db=db, user_id=current_user.id)
    return SuccessResponse(data=visits)


@router.patch("/{visit_id}/status", response_model=SuccessResponse)
async def update_visit_status_info(
    visit_id: int,
    status: VisitStatus = Query(..., description="预约状态"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_mysql_db)
):
    """更新预约状态"""
    visit = await update_visit_status(
        db=db,
        visit_id=visit_id,
        status=status,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )
    
    return SuccessResponse(data=visit)


@router.get("/house/{house_id}/available-dates", response_model=SuccessResponse)
async def get_house_available_dates(
    house_id: int,
    days: int = Query(30, ge=1, le=90, description="查询天数"),
    db: AsyncSession = Depends(get_mysql_db)
):
    """获取房屋的可预约日期"""
    dates = await get_available_dates(db=db, house_id=house_id, days=days)
    return SuccessResponse(data=dates)