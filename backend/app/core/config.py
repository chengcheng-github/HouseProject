from pydantic_settings import BaseSettings
from typing import Optional


class EnvConf(BaseSettings):
    # 应用配置
    APP_NAME: str = "房屋介绍网站"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    MYSQL_ENGINE: str = "mysql+aiomysql"
    MYSQL_HOST: str = "192.168.1.236"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PWD: str = "123456"
    MYSQL_DB: str = "house"
    
    # MongoDB配置
    MONGO_HOST: str = "192.168.1.236"
    MONGO_PORT: int = 27017
    MONGO_USER: Optional[str] = None
    MONGO_PWD: Optional[str] = None
    MONGO_DB: str = "house"
    
    # Redis配置
    REDIS_HOST: str = "192.168.1.236"
    REDIS_PORT: int = 6379
    
    # RabbitMQ配置
    RABBITMQ_HOST: str = "192.168.1.236"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PWD: str = "123456"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True