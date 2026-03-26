from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


async def log_operation(
    db: AsyncIOMotorDatabase,
    user_id: int,
    user_email: str,
    action: str,
    resource_type: str,
    resource_id: int,
    request_path: str,
    request_params: Dict[str, Any],
    ip_address: str,
    user_agent: str
) -> None:
    """记录操作日志"""
    log_entry = {
        "user_id": user_id,
        "user_email": user_email,
        "action": action,  # create, update, delete, view
        "resource_type": resource_type,  # house, user, visit, etc.
        "resource_id": resource_id,
        "request_path": request_path,
        "request_params": request_params,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": datetime.utcnow()
    }
    
    await db.operation_logs.insert_one(log_entry)