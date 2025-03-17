from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from .services import generate_story, generate_image_descriptions, generate_images, split_text
from .models import (
    StoryRequest, StoryResponse,
    ImageDescriptionRequest, ImageDescriptionResponse,
    ImageGenerationRequest, ImageGenerationResponse,
    CharacterDescription
)
from .config import ArtStyle, AgeRange, IMAGE_SIZES
from pydantic import BaseModel, Field
from .database import get_db
from . import db_service

# 创建路由
story_router = APIRouter(tags=["Story generation"])


@story_router.post("/generate-story", response_model=StoryResponse)
async def create_story(request: StoryRequest, db: Session = Depends(get_db)):
    """
    生成儿童故事API

    - **theme**: 故事主题
    - **story_type**: 故事类型 (冒险, 奇幻, 教育, 寓言, 科幻, 悬疑, 友谊, 自然)
    - **age_range**: 适合的年龄范围
    - **language**: 故事语言 (中文 or 英文)
    - **word_count**: 故事总字数
    - **pages**: 绘本页数

    返回分段的故事，每段对应一个绘本页，以及故事中的人物设定
    """
    try:
        paragraphs, characters = await generate_story(
            theme=request.theme,
            story_type=request.story_type.value,
            age_range=request.age_range,
            language=request.language.value,
            word_count=request.word_count,
            pages=request.pages
        )

        # 转换CharacterDetail到CharacterDescription
        character_descriptions = [
            CharacterDescription(
                name=char.name,
                role=char.role,
                appearance=char.appearance,
                traits=char.traits,
                age=char.age
            ) for char in characters
        ]

        # 保存到数据库
        db_story = db_service.create_story(db, request)
        db_service.create_paragraphs(db, db_story.id, paragraphs)
        db_service.create_characters(db, db_story.id, character_descriptions)

        return StoryResponse(
            paragraphs=paragraphs,
            characters=character_descriptions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@story_router.post("/generate-image-descriptions", response_model=ImageDescriptionResponse)
async def create_image_descriptions(request: ImageDescriptionRequest, db: Session = Depends(get_db)):
    """
    生成图片描述API

    - **theme**: 故事主题
    - **paragraphs**: 故事段落，每段对应一个场景
    - **style**: 图片风格
    - **age_range**: 适合的年龄范围
    - **characters**: 故事中的主要人物描述，用于保持图片中人物形象的一致性

    返回封面图片描述和每个段落对应的图片描述
    """
    try:
        # 获取故事ID（如果有）
        story_id = request.story_id if hasattr(request, 'story_id') else None

        cover_description, descriptions = await generate_image_descriptions(
            theme=request.theme,
            paragraphs=request.paragraphs,
            style=request.style.value,
            age_range=request.age_range.value,
            characters=request.characters
        )

        # 如果有故事ID，保存到数据库
        if story_id:
            story = db_service.get_story(db, story_id)
            if story:
                db_service.create_image_descriptions(
                    db, story_id, descriptions, cover_description, request.style.value
                )

        return ImageDescriptionResponse(
            cover_description=cover_description,
            descriptions=descriptions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@story_router.get("/art-styles", response_model=List[Dict[str, str]])
async def get_art_styles():
    """
    获取支持的图片风格列表
    """
    styles = []
    for style in ArtStyle:
        styles.append({
            "value": style.value,
            "label": style.value
        })
    return styles


@story_router.get("/age-ranges", response_model=List[Dict[str, str]])
async def get_age_ranges():
    """
    获取支持的年龄范围列表
    """
    ranges = []
    for age_range in AgeRange:
        ranges.append({
            "value": age_range.value,
            "label": age_range.value
        })
    return ranges


class TextSplitRequest(BaseModel):
    text: str = Field(..., min_length=1, description="需要拆分的文本内容")
    use_newline: bool = Field(True, description="是否使用换行符拆分")
    use_punctuation: bool = Field(True, description="是否使用标点符号拆分")


class TextSplitResponse(BaseModel):
    sentences: List[str] = Field(..., description="拆分后的句子列表")


@story_router.post("/split-text", response_model=TextSplitResponse)
async def split_text_api(request: TextSplitRequest):
    """
    将文本拆分为句子
    """
    try:
        sentences = split_text(
            text=request.text,
            use_newline=request.use_newline,
            use_punctuation=request.use_punctuation
        )
        return TextSplitResponse(sentences=sentences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
