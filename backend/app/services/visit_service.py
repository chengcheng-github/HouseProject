from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
import redis.asyncio as redis
from ..models.visit import HouseVisit, VisitStatus, VisitTimeSlot
from ..models.house import House
from ..models.user import User
from ..core.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)
from ..core.config import settings


async def get_redis_client():
    """获取Redis客户端"""
    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


async def check_visit_availability(
    db: AsyncSession,
    house_id: int,
    visit_date: date,
    time_slot: VisitTimeSlot
) -> bool:
    """检查预约是否可用"""
    # 首先检查房屋是否存在且已上架
    house = await db.get(House, house_id)
    if not house or house.is_deleted or house.status != "1":
        raise NotFoundException("房屋不存在或未上架")
    
    # 检查日期是否在未来
    if visit_date < date.today():
        raise BadRequestException("只能预约未来的日期")
    
    # 检查日期是否在30天内
    if visit_date > date.today() + timedelta(days=30):
        raise BadRequestException("只能预约未来30天内的日期")
    
    # 从Redis获取剩余预约次数
    redis_client = await get_redis_client()
    cache_key = f"house:available_dates:{house_id}:{visit_date}"
    
    try:
        remaining_visits = await redis_client.get(cache_key)
        if remaining_visits is None:
            # 如果缓存不存在，从数据库查询
            stmt = select(func.count(HouseVisit.id)).where(
                HouseVisit.house_id == house_id,
                HouseVisit.visit_date == visit_date,
                HouseVisit.status.in_([VisitStatus.PENDING, VisitStatus.CONFIRMED])
            )
            result = await db.execute(stmt)
            current_count = result.scalar() or 0
            remaining_visits = house.max_visits_per_day - current_count
            
            # 更新缓存
            await redis_client.setex(
                cache_key,
                timedelta(days=1),  # 缓存1天
                remaining_visits
            )
        else:
            remaining_visits = int(remaining_visits)
        
        return remaining_visits > 0
    finally:
        await redis_client.close()


async def create_visit(
    db: AsyncSession,
    house_id: int,
    visitor_name: str,
    visitor_phone: str,
    visit_date: date,
    time_slot: VisitTimeSlot,
    remark: Optional[str] = None,
    created_by: Optional[int] = None
) -> HouseVisit:
    """创建预约"""
    # 检查可用性
    available = await check_visit_availability(db, house_id, visit_date, time_slot)
    if not available:
        raise BadRequestException("该时段已约满")
    
    # 创建预约
    visit = HouseVisit(
        house_id=house_id,
        visitor_name=visitor_name,
        visitor_phone=visitor_phone,
        visit_date=visit_date,
        visit_time_slot=time_slot,
        status=VisitStatus.PENDING,
        remark=remark,
        created_by=created_by
    )
    
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    
    # 更新Redis缓存
    redis_client = await get_redis_client()
    cache_key = f"house:available_dates:{house_id}:{visit_date}"
    
    try:
        remaining_visits = await redis_client.get(cache_key)
        if remaining_visits:
            await redis_client.decr(cache_key)
    finally:
        await redis_client.close()
    
    return visit


async def get_visit_by_id(db: AsyncSession, visit_id: int) -> Optional[HouseVisit]:
    """根据ID获取预约"""
    stmt = select(HouseVisit).options(
        selectinload(HouseVisit.house)
    ).where(HouseVisit.id == visit_id)
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_visit_status(
    db: AsyncSession,
    visit_id: int,
    status: VisitStatus,
    user_id: int,
    is_admin: bool = False
) -> HouseVisit:
    """更新预约状态"""
    visit = await get_visit_by_id(db, visit_id)
    if not visit:
        raise NotFoundException("预约不存在")
    
    # 获取房屋信息
    house = await db.get(House, visit.house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查：房主或管理员可以更新状态
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限修改该预约")
    
    # 只有待确认状态才能更新为已确认或已取消
    if visit.status != VisitStatus.PENDING:
        raise BadRequestException("只能修改待确认状态的预约")
    
    # 如果取消预约，更新Redis缓存
    if status == VisitStatus.CANCELLED:
        redis_client = await get_redis_client()
        cache_key = f"house:available_dates:{visit.house_id}:{visit.visit_date}"
        
        try:
            await redis_client.incr(cache_key)
        finally:
            await redis_client.close()
    
    # 更新状态
    visit.status = status
    await db.commit()
    await db.refresh(visit)
    
    return visit


async def get_house_visits(
    db: AsyncSession,
    house_id: int,
    user_id: int,
    is_admin: bool = False
) -> List[HouseVisit]:
    """获取房屋的所有预约"""
    # 获取房屋信息
    house = await db.get(House, house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限查看该房屋的预约")
    
    stmt = select(HouseVisit).where(HouseVisit.house_id == house_id).order_by(HouseVisit.visit_date)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user_visits(db: AsyncSession, user_id: int) -> List[HouseVisit]:
    """获取用户的所有预约"""
    stmt = select(HouseVisit).options(
        selectinload(HouseVisit.house)
    ).where(HouseVisit.created_by == user_id).order_by(HouseVisit.visit_date)
    
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_available_dates(
    db: AsyncSession,
    house_id: int,
    days: int = 30
) -> List[dict]:
    """获取未来N天的可预约日期"""
    house = await db.get(House, house_id)
    if not house or house.is_deleted or house.status != "1":
        raise NotFoundException("房屋不存在或未上架")
    
    available_dates = []
    redis_client = await get_redis_client()
    
    try:
        for i in range(days):
            check_date = date.today() + timedelta(days=i)
            cache_key = f"house:available_dates:{house_id}:{check_date}"
            
            # 获取剩余预约次数
            remaining_visits = await redis_client.get(cache_key)
            if remaining_visits is None:
                # 查询数据库
                stmt = select(func.count(HouseVisit.id)).where(
                    HouseVisit.house_id == house_id,
                    HouseVisit.visit_date == check_date,
                    HouseVisit.status.in_([VisitStatus.PENDING, VisitStatus.CONFIRMED])
                )
                result = await db.execute(stmt)
                current_count = result.scalar() or 0
                remaining_visits = house.max_visits_per_day - current_count
                
                # 更新缓存
                await redis_client.setex(
                    cache_key,
                    timedelta(days=1),
                    remaining_visits
                )
            else:
                remaining_visits = int(remaining_visits)
            
            available_dates.append({
                "date": check_date.isoformat(),
                "available": remaining_visits > 0,
                "remaining": remaining_visits
            })
    finally:
        await redis_client.close()
    
    return available_dates