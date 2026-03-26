from app.core.settings import mysqlSession
from app.core.settings import logger

def get_mysql_db():
    db = mysqlSession()
    try:
        logger.info('connect MySQL!!!')
        yield db
    finally:
        db.close()
        logger.info('disconnect MySQL!!!')