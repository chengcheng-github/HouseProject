from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..deps import get_db, get_admin_user, get_mongo_db
from ...models.user import User
from ...schemas.response import SuccessResponse
from ...services.config_service import set_config, get_all_configs
from ...services.statistic_service import get_weekly_statistics
from ...services.log_service import log_operation

router = APIRouter(prefix="/admin", tags=["运维管理"])


@router.get("/configs", response_model=SuccessResponse[Dict[str, Any]])
async def get_configurations(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有配置"""
    configs = await get_all_configs(db)
    return SuccessResponse(data=configs)


@router.post("/configs", response_model=SuccessResponse)
async def update_configuration(
    key: str = Query(..., description="配置键"),
    value: str = Query(..., description="配置值"),
    description: str = Query(None, description="配置描述"),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """更新配置"""
    await set_config(db, key, value, description)
    
    # 记录操作日志
    if request:
        await log_operation(
            db=request.app.state.mongo_db,
            user_id=current_user.id,
            user_email=current_user.email,
            action="update",
            resource_type="config",
            resource_id=0,
            request_path=request.url.path,
            request_params={"key": key, "value": value},
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent", "")
        )
    
    return SuccessResponse()


@router.get("/statistics", response_model=SuccessResponse)
async def get_statistics(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取统计数据"""
    weekly_stats = await get_weekly_statistics(db)
    
    # 转换为前端需要的格式
    data = {
        "dates": [stat.date.strftime("%Y-%m-%d") for stat in weekly_stats],
        "registrations": [stat.user_registrations for stat in weekly_stats],
        "publications": [stat.house_publications for stat in weekly_stats],
        "page_views": [stat.page_views for stat in weekly_stats],
        "unique_visitors": [stat.unique_visitors for stat in weekly_stats]
    }
    
    return SuccessResponse(data=data)


@router.get("/logs", response_model=SuccessResponse)
async def get_operation_logs(
    start_date: datetime = Query(None, description="开始日期"),
    end_date: datetime = Query(None, description="结束日期"),
    user_id: int = Query(None, description="用户ID"),
    action: str = Query(None, description="操作类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_admin_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """获取操作日志"""
    # 构建查询条件
    query = {}
    
    if start_date:
        query["created_at"] = {"$gte": start_date}
    if end_date:
        query["created_at"] = query.get("created_at", {})
        query["created_at"]["$lte"] = end_date
    if user_id:
        query["user_id"] = user_id
    if action:
        query["action"] = action
    
    # 查询日志
    cursor = mongo_db.operation_logs.find(query).sort("created_at", -1)
    
    # 分页
    skip = (page - 1) * page_size
    logs = await cursor.skip(skip).limit(page_size).to_list(length=page_size)
    
    # 获取总数
    total = await mongo_db.operation_logs.count_documents(query)
    
    return SuccessResponse(data={
        "logs": logs,
        "total": total,
        "page": page,
        "page_size": page_size
    })