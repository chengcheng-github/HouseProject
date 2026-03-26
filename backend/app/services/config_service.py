from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models.config import Config
from ..core.exceptions import NotFoundException


async def get_config(db: AsyncSession, key: str) -> Optional[Config]:
    """获取配置"""
    stmt = select(Config).where(Config.key == key)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_config_value(db: AsyncSession, key: str, default: Any = None) -> Any:
    """获取配置值"""
    config = await get_config(db, key)
    return config.value if config else default


async def set_config(db: AsyncSession, key: str, value: Any, description: Optional[str] = None) -> Config:
    """设置配置"""
    config = await get_config(db, key)
    
    if config:
        config.value = value
        if description:
            config.description = description
    else:
        config = Config(
            key=key,
            value=str(value),
            description=description
        )
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    return config


async def get_all_configs(db: AsyncSession) -> Dict[str, Any]:
    """获取所有配置"""
    stmt = select(Config)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    
    config_dict = {}
    for config in configs:
        config_dict[config.key] = config.value
    
    return config_dict