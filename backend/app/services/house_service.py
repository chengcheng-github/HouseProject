from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload
from ..models.house import House, HouseImage, HouseStatus
from ..models.user import User
from ..schemas.house import HouseCreate, HouseUpdate, HouseStatusUpdate, HouseImageCreate
from ..schemas.response import PaginationParams
from ..core.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)


async def create_house(db: AsyncSession, house_create: HouseCreate, user_id: int) -> House:
    """创建房屋"""
    db_house = House(
        **house_create.model_dump(),
        user_id=user_id,
        status=HouseStatus.DRAFT,
        is_deleted=False,
    )
    
    db.add(db_house)
    await db.commit()
    await db.refresh(db_house)
    
    return db_house


async def get_house_list(
    db: AsyncSession,
    pagination: PaginationParams,
    title: Optional[str] = None,
    district: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    user_id: Optional[int] = None,
    only_published: bool = True,
) -> tuple[List[House], int]:
    """获取房屋列表"""
    stmt = select(House).options(
        selectinload(House.user),
        selectinload(House.images),
    ).where(
        House.is_deleted == False
    )
    
    # 筛选条件
    if only_published:
        stmt = stmt.where(House.status == HouseStatus.PUBLISHED)
    
    if title:
        stmt = stmt.where(House.title.contains(title))
    
    if district:
        stmt = stmt.where(House.district == district)
    
    if min_price is not None:
        stmt = stmt.where(House.price >= min_price)
    
    if max_price is not None:
        stmt = stmt.where(House.price <= max_price)
    
    if user_id:
        stmt = stmt.where(House.user_id == user_id)
    
    # 统计总数
    count_stmt = select(func.count(House.id)).where(stmt.whereclause)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # 分页
    stmt = stmt.order_by(House.created_at.desc()).offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(stmt)
    houses = result.scalars().all()
    
    return houses, total


async def get_house_by_id(db: AsyncSession, house_id: int) -> Optional[House]:
    """根据ID获取房屋"""
    stmt = select(House).options(
        selectinload(House.user),
        selectinload(House.images),
    ).where(
        House.id == house_id,
        House.is_deleted == False
    )
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_house(
    db: AsyncSession,
    house_id: int,
    house_update: HouseUpdate,
    user_id: int,
    is_admin: bool = False,
) -> House:
    """更新房屋信息"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限修改该房屋")
    
    # 更新房屋信息
    update_data = house_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(house, field, value)
    
    await db.commit()
    await db.refresh(house)
    
    return house


async def update_house_status(
    db: AsyncSession,
    house_id: int,
    status_update: HouseStatusUpdate,
    user_id: int,
    is_admin: bool = False,
) -> House:
    """更新房屋状态"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限修改该房屋状态")
    
    # 更新状态
    house.status = status_update.status
    
    await db.commit()
    await db.refresh(house)
    
    return house


async def delete_house(
    db: AsyncSession,
    house_id: int,
    user_id: int,
    is_admin: bool = False,
) -> House:
    """软删除房屋"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限删除该房屋")
    
    # 软删除
    house.is_deleted = True
    
    await db.commit()
    await db.refresh(house)
    
    return house


async def add_house_image(
    db: AsyncSession,
    house_id: int,
    image_create: HouseImageCreate,
    user_id: int,
    is_admin: bool = False,
) -> HouseImage:
    """添加房屋图片"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限添加图片")
    
    # 如果是主图，先将其他图片设为非主图
    if image_create.is_primary:
        await db.execute(
            update(HouseImage)
            .where(HouseImage.house_id == house_id)
            .values(is_primary=False)
        )
    
    # 创建图片
    db_image = HouseImage(
        house_id=house_id,
        image_url=image_create.image_url,
        is_primary=image_create.is_primary,
    )
    
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    
    return db_image


async def delete_house_image(
    db: AsyncSession,
    image_id: int,
    user_id: int,
    is_admin: bool = False,
) -> None:
    """删除房屋图片"""
    image = await db.get(HouseImage, image_id)
    if not image:
        raise NotFoundException("图片不存在")
    
    # 获取房屋信息
    house = await get_house_by_id(db, image.house_id)
    if not house:
        raise NotFoundException("房屋不存在")
    
    # 权限检查
    if not is_admin and house.user_id != user_id:
        raise ForbiddenException("没有权限删除该图片")
    
    # 删除图片
    await db.delete(image)
    await db.commit()