import os
from core.config import EnvConf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.getenv("BASE_DIR", "/application")

# MONGO 配置
if os.getenv("MONGO_LOCAL", "True") == "True":
    conn = connect(EnvConf.MONGO_DB,
                   host=EnvConf.MONGO_HOST,
                   port=int(EnvConf.MONGO_PORT))
    mongo_db = conn.get_database(EnvConf.MONGO_DB)
else:
    conn = connect(EnvConf.MONGO_DB,
                   host=EnvConf.MONGO_HOST
                   )
    mongo_db = conn.get_database(EnvConf.MONGO_DB)
if EnvConf.MONGO_USER and EnvConf.MONGO_PWD:
    mongo_db.authenticate(EnvConf.MONGO_USER, EnvConf.MONGO_PWD)


# MySQL配置
url = f"{EnvConf.MYSQL_ENGINE}://{EnvConf.MYSQL_USER}:{EnvConf.MYSQL_PWD}@{EnvConf.MYSQL_HOST}:{EnvConf.MYSQL_PORT}/{EnvConf.MYSQL_DB}?charset=utf8mb4"

engine = create_engine(
    url=url,
    echo=True,
    pool_size=1000,
    max_overflow=1000,
    pool_timeout=30,
    pool_recycle=7200,
    pool_pre_ping=True,
    # pool_reset_on_return="rollback",
)
mysqlSession = sessionmaker()
mysqlSession.configure(bind=engine)

Base = declarative_base()

REDIS_CACHE = redis.Redis(connection_pool=redis.ConnectionPool(
    host=EnvConf.REDIS_HOST,
    port=EnvConf.REDIS_PORT,
    db=EnvConf.REDIS_CACHE_DB,
    decode_responses=True,  # 取出二进制默认decode
))

# 配置 loguru
logger.configure(
    handlers=[
        {
            "sink": sys.stderr,
            "level": 'DEBUG' if DEBUG else 'INFO',
            "format": "[{level}] {time:YYYY-MM-DD HH:mm:ss} {file}:{line} - {message}",
            "enqueue": True
        },  # 输出到标准错误流
        {
            "sink": log_filename,
            "rotation": "500 MB",
            "retention": "10 days",
            "level": "ERROR",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {file}:{line} - {message}",
            "enqueue": True
        },  # 输出到文件，并设置文件大小和保留期限
    ],
)