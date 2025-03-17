from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path
from api.generate_story import story_router
from api.generate_images import image_router
from api.generate_speech import speech_router
from api.config import settings, validate_settings
from api.db_init import init_db
from api.story_api import story_db_router

# 验证所有必要设置
validate_settings()

# 初始化数据库
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="An API for generating children's stories using Google Gemini.",
    version=settings.APP_VERSION
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为特定的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保各种目录存在
# 静态文件目录 - 所有静态文件都放在backend/static下
STATIC_ROOT = "static"
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(os.path.join(STATIC_ROOT, "images"), exist_ok=True)
os.makedirs(os.path.join(STATIC_ROOT, "speech"), exist_ok=True)
os.makedirs(os.path.join(STATIC_ROOT, "subtitles"), exist_ok=True)
os.makedirs(os.path.join(STATIC_ROOT, "audio"), exist_ok=True)
os.makedirs(os.path.join(STATIC_ROOT, "videos"), exist_ok=True)

# 临时文件目录 - 所有临时文件都放在backend/temp下
TEMP_ROOT = "temp"
os.makedirs(TEMP_ROOT, exist_ok=True)
os.makedirs(os.path.join(TEMP_ROOT, "audio"), exist_ok=True)
os.makedirs(os.path.join(TEMP_ROOT, "video"), exist_ok=True)

# 数据库目录
DB_ROOT = "database"
os.makedirs(DB_ROOT, exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")

# 添加路由
app.include_router(story_router, prefix="/story")
app.include_router(image_router, prefix="/image")
app.include_router(speech_router, prefix="/speech")
app.include_router(story_db_router, prefix="/stories")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
