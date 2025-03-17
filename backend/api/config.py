import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from enum import Enum
from pathlib import Path

# 加载环境变量
load_dotenv()


# 语言枚举
class Language(str, Enum):
    CHINESE = "中文"
    ENGLISH = "英文"


# 艺术风格枚举
class ArtStyle(str, Enum):
    WATERCOLOR = "水彩风格"
    FLAT = "扁平风格"
    CARTOON = "卡通风格"
    INK = "水墨画风格"
    ANIME = "动漫风格"
    PIXAR = "皮克斯风格"
    MIYAZAKI = "宫崎骏风格"
    PIXEL = "像素风格"
    COLORED_PENCIL = "手绘彩铅风格"
    CRAYON = "蜡笔画风格"
    PICTURE_BOOK = "童书插画风格"
    FANTASY = "梦幻插画风格"
    CHILD_DOODLE = "童趣涂鸦风格"
    SKETCH = "简笔画风格"
    RETRO_ANIME = "80日漫风格"
    CHINESE_TRADITIONAL = "国风工笔画风格"
    BLACK_WHITE = "黑白线稿风格"
    FELT_ART = "毛毡艺术风格"
    HEALING_SKETCH = "简笔治愈风格"
    BLIND_BOX = "3D盲盒风格"
    DREAMY_WATERCOLOR = "梦幻水彩风格"
    DOPAMINE = "多巴胺插画风格"
    HAZY_PENCIL = "朦胧彩铅风格"
    THICK_LINE = "粗线条风格"


# 故事类型枚举
class StoryType(str, Enum):
    ADVENTURE = "冒险"
    FANTASY = "奇幻"
    EDUCATIONAL = "教育"
    FABLE = "寓言"
    SCIFI = "科幻"
    MYSTERY = "悬疑"
    FRIENDSHIP = "友谊"
    NATURE = "自然"


# 年龄范围枚举
class AgeRange(str, Enum):
    TODDLER = "0-3岁"
    CHILD = "3-8岁"
    TEEN = "8-14岁"


# 定义图片尺寸映射
IMAGE_SIZES = {
    "1:1": (1024, 1024),      # 正方形
    "4:3": (1024, 768),       # 标准照片
    "3:2": (1024, 683),       # 经典摄影
    "16:9": (1024, 576),      # 宽屏
    "9:16": (576, 1024),      # 竖屏
    "5:4": (1024, 819),       # 小幅宽屏
    "2:3": (683, 1024),       # 竖版照片
    "21:9": (1024, 439),      # 超宽屏
    "3:4": (768, 1024),       # 竖版标准
}


class Settings(BaseSettings):
    """应用配置类"""

    # 应用设置
    APP_NAME: str = "儿童故事生成API"
    APP_VERSION: str = "1.0.0"

    # Gemini API设置
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    # DeepInfra API设置
    DEEPINFRA_API_KEY: str = os.environ.get("DEEPINFRA_API_KEY", "")
    DEFAULT_SEED: int = int(os.environ.get("DEFAULT_SEED", 1))
    # 可用的图片生成模型
    IMAGE_MODELS: list = [
        {"name": "black-forest-labs/FLUX-1-schnell",
            "display_name": "FLUX Schnell", "default": "true"},
        {"name": "black-forest-labs/FLUX-1-dev",
            "display_name": "FLUX Dev", "default": "false"}
    ]

    # 文件目录设置
    STATIC_ROOT: Path = Path(os.environ.get("STATIC_ROOT", "static"))
    TEMP_ROOT: Path = Path(os.environ.get("TEMP_ROOT", "temp"))

    # 图片目录
    UPLOAD_DIR: Path = STATIC_ROOT / "images"

    # 语音和音频目录
    SPEECH_DIR: Path = STATIC_ROOT / "speech"
    AUDIO_DIR: Path = STATIC_ROOT / "audio"
    SUBTITLE_DIR: Path = STATIC_ROOT / "subtitles"

    # 临时文件目录
    TEMP_AUDIO_DIR: Path = TEMP_ROOT / "audio"

    # 语音API设置
    SILICONFLOW_API_KEY: str = os.environ.get("SILICONFLOW_API_KEY", "")
    SILICONFLOW_URL: str = os.environ.get(
        "SILICONFLOW_URL", "https://api.siliconflow.cn/v1")
    SILICONFLOW_MODEL: str = os.environ.get(
        "SILICONFLOW_MODEL", "FunAudioLLM/CosyVoice2-0.5B")
    SILICONFLOW_VOICE: str = os.environ.get(
        "SILICONFLOW_VOICE", "fishaudio/fish-speech-1.5:claire")

    # 服务器设置
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8001"))

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 允许额外的字段，忽略未在类中定义的环境变量


# 创建全局设置实例
settings = Settings()

# 验证必要设置


def validate_settings():
    """验证所有必要的设置"""
    if not settings.GEMINI_API_KEY:
        raise ValueError("未设置GEMINI_API_KEY环境变量，请在.env文件中添加")

    if not settings.SILICONFLOW_API_KEY:
        raise ValueError("未设置SILICONFLOW_API_KEY环境变量，请在.env文件中添加")

    if not settings.DEEPINFRA_API_KEY:
        raise ValueError("未设置DEEPINFRA_API_KEY环境变量，请在.env文件中添加")

    # 可以添加更多验证
