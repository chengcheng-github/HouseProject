from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.statistics import Statistics
from ..models.user import User
from ..models.house import House


async def get_daily_statistics(db: AsyncSession, date: datetime) -> Optional[Statistics]:
    """获取指定日期的统计数据"""
    # 查找当天的统计记录
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    stmt = select(Statistics).where(
        Statistics.date >= start_of_day,
        Statistics.date < end_of_day
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def calculate_daily_statistics(db: AsyncSession, date: datetime) -> Statistics:
    """计算每日统计数据"""
    # 查找现有记录
    statistics = await get_daily_statistics(db, date)
    
    if not statistics:
        statistics = Statistics(date=date)
        db.add(statistics)
    
    # 统计注册用户数
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # 统计注册用户数
    user_count_stmt = select(func.count(User.id)).where(
        User.created_at >= start_of_day,
        User.created_at < end_of_day,
        User.is_deleted == False
    )
    user_result = await db.execute(user_count_stmt)
    statistics.user_registrations = user_result.scalar() or 0
    
    # 统计房源发布数
    house_count_stmt = select(func.count(House.id)).where(
        House.created_at >= start_of_day,
        House.created_at < end_of_day,
        House.is_deleted == False
    )
    house_result = await db.execute(house_count_stmt)
    statistics.house_publications = house_result.scalar() or 0
    
    # PV和UV从Redis获取（这里先设为0，实际应该从Redis读取）
    statistics.page_views = 0
    statistics.unique_visitors = 0
    
    await db.commit()
    await db.refresh(statistics)
    
    return statistics


async def get_weekly_statistics(db: AsyncSession) -> list[Statistics]:
    """获取最近7天的统计数据"""
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=6)
    
    stmt = select(Statistics).where(
        Statistics.date >= start_date,
        Statistics.date <= end_date
    ).order_by(Statistics.date)
    
    result = await db.execute(stmt)
    return result.scalars().all()