if __name__ == '__main__':
    import sys
    sys.path.append('/application/backend')
    from app.core.settings import engine
    from app.models.mysqlModels import Base

    # 初始化mysql数据库
    Base.metadata.create_all(engine)
