from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from ..deps import get_db, get_current_active_user, get_admin_user
from ...schemas.house import (
    HouseCreate,
    HouseUpdate,
    HouseStatusUpdate,
    HouseImageCreate,
    HouseResponse,
    HouseListResponse,
)
from ...schemas.response import SuccessResponse, PaginationParams, PaginatedResponse, PaginatedData
from ...services.house_service import (
    create_house,
    get_house_list,
    get_house_by_id,
    update_house,
    update_house_status,
    delete_house,
    add_house_image,
    delete_house_image,
)
from ...models.user import User
from ...core.config import settings

router = APIRouter(prefix="/houses", tags=["房屋管理"])


@router.post("", response_model=SuccessResponse[HouseResponse])
async def create_new_house(
    house_create: HouseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建房屋"""
    house = await create_house(db, house_create, current_user.id)
    return SuccessResponse(data=HouseResponse.model_validate(house))


@router.get("", response_model=PaginatedResponse[HouseListResponse])
async def get_houses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    district: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取房屋列表"""
    pagination = PaginationParams(page=page, page_size=page_size)
    
    # 如果是管理员，可以看到所有房屋；普通用户只能看到已上架的房屋
    only_published = current_user.role != "admin" if current_user else True
    
    houses, total = await get_house_list(
        db=db,
        pagination=pagination,
        title=title,
        district=district,
        min_price=min_price,
        max_price=max_price,
        user_id=None,  # 获取所有房屋
        only_published=only_published,
    )
    
    # 转换为列表响应格式
    items = []
    for house in houses:
        primary_image = None
        for image in house.images:
            if image.is_primary:
                primary_image = image.image_url
                break
        
        item = HouseListResponse(
            id=house.id,
            title=house.title,
            price=house.price,
            area=house.area,
            rooms=house.rooms,
            address=house.address,
            district=house.district,
            status=house.status,
            user_id=house.user_id,
            user_nickname=house.user.nickname if house.user else None,
            primary_image=primary_image,
            created_at=house.created_at,
        )
        items.append(item)
    
    total_pages = (total + page_size - 1) // page_size
    
    paginated_data = PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    
    return PaginatedResponse(data=paginated_data.model_dump())


@router.get("/my", response_model=PaginatedResponse[HouseListResponse])
async def get_my_houses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的房屋列表"""
    pagination = PaginationParams(page=page, page_size=page_size)
    
    houses, total = await get_house_list(
        db=db,
        pagination=pagination,
        user_id=current_user.id,
        only_published=False,  # 查看所有状态的房屋
    )
    
    # 转换为列表响应格式
    items = []
    for house in houses:
        primary_image = None
        for image in house.images:
            if image.is_primary:
                primary_image = image.image_url
                break
        
        item = HouseListResponse(
            id=house.id,
            title=house.title,
            price=house.price,
            area=house.area,
            rooms=house.rooms,
            address=house.address,
            district=house.district,
            status=house.status,
            user_id=house.user_id,
            user_nickname=house.user.nickname if house.user else None,
            primary_image=primary_image,
            created_at=house.created_at,
        )
        items.append(item)
    
    total_pages = (total + page_size - 1) // page_size
    
    paginated_data = PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    
    return PaginatedResponse(data=paginated_data.model_dump())


@router.get("/{house_id}", response_model=SuccessResponse[HouseResponse])
async def get_house(
    house_id: int,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取房屋详情"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="房屋不存在"
        )
    
    # 如果是草稿状态，只有房主或管理员可以查看
    if house.status == "0":
        if not current_user or (current_user.id != house.user_id and current_user.role != "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看该房屋"
            )
    
    return SuccessResponse(data=HouseResponse.model_validate(house))


@router.put("/{house_id}", response_model=SuccessResponse[HouseResponse])
async def update_house_info(
    house_id: int,
    house_update: HouseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新房屋信息"""
    house = await update_house(
        db=db,
        house_id=house_id,
        house_update=house_update,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
    )
    return SuccessResponse(data=HouseResponse.model_validate(house))


@router.patch("/{house_id}/status", response_model=SuccessResponse[HouseResponse])
async def update_house_status_info(
    house_id: int,
    status_update: HouseStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新房屋状态"""
    house = await update_house_status(
        db=db,
        house_id=house_id,
        status_update=status_update,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
    )
    return SuccessResponse(data=HouseResponse.model_validate(house))


@router.delete("/{house_id}", response_model=SuccessResponse)
async def delete_house_info(
    house_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除房屋"""
    await delete_house(
        db=db,
        house_id=house_id,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
    )
    return SuccessResponse()


@router.post("/{house_id}/images", response_model=SuccessResponse)
async def upload_house_image(
    house_id: int,
    file: UploadFile = File(...),
    is_primary: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """上传房屋图片"""
    # 检查文件类型
    if not file.filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持jpg、jpeg、png、gif格式的图片"
        )
    
    # 检查文件大小
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小不能超过 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, f"houses/{house_id}")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 构建相对URL
    image_url = f"/uploads/houses/{house_id}/{file.filename}"
    
    # 添加到数据库
    image_create = HouseImageCreate(image_url=image_url, is_primary=is_primary)
    await add_house_image(
        db=db,
        house_id=house_id,
        image_create=image_create,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
    )
    
    return SuccessResponse()


@router.delete("/{house_id}/images/{image_id}", response_model=SuccessResponse)
async def remove_house_image(
    house_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除房屋图片"""
    await delete_house_image(
        db=db,
        image_id=image_id,
        user_id=current_user.id,
        is_admin=current_user.role == "admin",
    )
    return SuccessResponse()