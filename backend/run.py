#!/usr/bin/env python
"""
启动儿童故事生成API服务器的脚本
"""
import uvicorn
from api.config import settings, validate_settings


def main():
    """启动API服务器"""
    try:
        # 验证设置
        validate_settings()

        print(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"服务器地址: http://{settings.HOST}:{settings.PORT}")
        print(f"API文档地址: http://{settings.HOST}:{settings.PORT}/docs")

        # 启动服务器
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True
        )
    except Exception as e:
        print(f"启动失败: {str(e)}")


if __name__ == "__main__":
    main()
