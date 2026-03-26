from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .api.v1 import api_router
from .core.config import settings
from .core.database import engine, Base
from .core.mongodb import get_mongo_client

# 创建数据库表
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(api_router)

# 启动事件
@app.on_event("startup")
async def startup_event():
    await create_tables()
    
    # 初始化MongoDB连接
    mongo_client = get_mongo_client()
    app.state.mongo_db = mongo_client[settings.MONGO_DB]
    print("数据库表创建完成")
    print("MongoDB连接初始化完成")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, 'mongo_db'):
        app.state.mongo_db.client.close()

# 根路径
@app.get("/")
async def root():
    return {
        "message": "房屋介绍网站API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}