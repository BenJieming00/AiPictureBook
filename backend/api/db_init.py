from .database import engine, Base
from . import db_models

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！") 