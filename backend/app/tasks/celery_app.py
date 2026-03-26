from celery import Celery
from celery.schedules import crontab
import asyncio
from ..core.config import settings

# 创建Celery应用
celery_app = Celery(
    'house_website',
    broker=f'amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PWD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

# 配置定时任务
celery_app.conf.beat_schedule = {
    # 每日凌晨1点执行统计任务
    'daily-statistics': {
        'task': 'app.tasks.tasks.calculate_daily_statistics',
        'schedule': crontab(hour=1, minute=0),
    },
}

# 导入任务
from . import tasks