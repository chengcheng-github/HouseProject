from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings


# 创建MongoDB连接
def get_mongo_client() -> AsyncIOMotorClient:
    """获取MongoDB客户端"""
    if settings.MONGO_USER and settings.MONGO_PWD:
        uri = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PWD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}?authSource=admin"
    else:
        uri = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}"
    
    client = AsyncIOMotorClient(uri)
    return client


# 获取MongoDB数据库
async def get_mongo_db():
    """获取MongoDB数据库的依赖注入函数"""
    client = get_mongo_client()
    try:
        db = client[settings.MONGO_DB]
        yield db
    finally:
        client.close()


# 操作日志集合结构
# collection: operation_logs
# 文档结构:
# {
#     "_id": ObjectId,
#     "user_id": int,
#     "user_email": str,
#     "action": str,  # create, update, delete, view
#     "resource_type": str,  # house, user, visit, etc.
#     "resource_id": int,
#     "request_path": str,
#     "request_params": dict,
#     "ip_address": str,
#     "user_agent": str,
#     "created_at": datetime
# }