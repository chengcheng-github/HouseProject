from datetime import datetime, timedelta
from celery import shared_task
import asyncio
from ..core.database import async_session_factory
from ..services.statistic_service import calculate_daily_statistics


@shared_task
def calculate_daily_statistics_task():
    """每日统计任务"""
    async def run():
        async with async_session_factory() as db:
            # 计算前一天的统计数据
            yesterday = datetime.now() - timedelta(days=1)
            yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            
            await calculate_daily_statistics(db, yesterday)
    
    asyncio.run(run())


@shared_task
def send_email_task(email: str, subject: str, content: str):
    """发送邮件任务"""
    # 这里应该实现实际的邮件发送逻辑
    # 由于是示例，这里只打印日志
    print(f"Sending email to {email}: {subject}")
    print(f"Content: {content}")
    
    # 实际应用中应该使用邮件服务，如SMTP
    # import smtplib
    # from email.mime.text import MIMEText
    # from email.header import Header
    # 
    # msg = MIMEText(content, 'html', 'utf-8')
    # msg['From'] = Header('房屋介绍网站', 'utf-8')
    # msg['To'] = Header(email, 'utf-8')
    # msg['Subject'] = Header(subject, 'utf-8')
    # 
    # smtp = smtplib.SMTP('smtp.example.com', 587)
    # smtp.starttls()
    # smtp.login('username', 'password')
    # smtp.sendmail('sender@example.com', [email], msg.as_string())
    # smtp.quit()