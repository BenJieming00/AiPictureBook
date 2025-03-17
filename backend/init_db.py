#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import engine, Base
from api import db_models

def init_db():
    """初始化数据库，创建所有表"""
    # 创建数据库目录
    os.makedirs("database", exist_ok=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_db() 