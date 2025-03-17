from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .services import generate_images
from .models import (
    ImageGenerationRequest, ImageGenerationResponse
)
from .config import IMAGE_SIZES
from pydantic import BaseModel, Field
from .database import get_db
from . import db_service

image_router = APIRouter(tags=["图片生成"])


# 添加新的请求模型
class PromptImageGenerationRequest(BaseModel):
    title: str = Field(..., description="图片标题", example="图片标题")
    cover_description: str = Field(..., description="封面图片描述",
                                   example="封面图片描述")
    descriptions: List[str] = Field(..., description="内容图片描述列表", min_items=1)
    aspect_ratio: str = Field("16:9", description="图片比例", example="16:9")
    image_model: str = Field(None, description="图片生成模型名称",
                             example="black-forest-labs/FLUX-1-schnell")
    seed: int = Field(None, description="随机种子值，用于固定生成结果", example=1)
    story_id: Optional[str] = Field(None, description="故事ID，用于关联到数据库")

    class Config:
        protected_namespaces = ()


@image_router.post("/generate-images-from-prompts", response_model=ImageGenerationResponse)
async def create_images_from_prompts(request: PromptImageGenerationRequest, db: Session = Depends(get_db)):
    """
    直接根据提示词生成图片API

    - **title**: 图片标题，用于命名生成的图片文件
    - **cover_description**: 封面图片描述
    - **descriptions**: 内容图片描述列表
    - **aspect_ratio**: 图片比例 (默认 16:9)
    - **num**: 每个描述生成的图片数量 (默认 1)
    - **image_model**: 图片生成模型名称 (可选)
    - **seed**: 随机种子值，用于固定生成结果 (可选)
    - **story_id**: 故事ID，用于关联到数据库 (可选)

    返回生成图片的路径列表
    """
    try:
        # 合并封面描述和内容描述
        all_descriptions = [request.cover_description] + request.descriptions

        # 使用现有的generate_images函数
        image_paths = await generate_images(
            title=request.title,
            descriptions=all_descriptions,
            aspect_ratio=request.aspect_ratio,
            image_model=request.image_model,
            seed=request.seed
        )

        # 如果提供了故事ID，保存到数据库
        if request.story_id:
            story = db_service.get_story(db, request.story_id)
            if story:
                # 获取图片描述
                image_descriptions = db_service.get_image_descriptions(db, request.story_id)
                
                # 保存封面图片
                if image_paths and len(image_paths) > 0:
                    cover_desc = next((desc for desc in image_descriptions if desc.is_cover), None)
                    if cover_desc:
                        db_service.create_image(
                            db,
                            request.story_id,
                            cover_desc.id,
                            image_paths[0],
                            True,
                            request.aspect_ratio,
                            request.image_model,
                            request.seed
                        )
                
                # 保存内容图片
                paragraphs = db_service.get_paragraphs(db, request.story_id)
                for i, path in enumerate(image_paths[1:], 0):
                    if i < len(paragraphs):
                        desc = next((desc for desc in image_descriptions if desc.paragraph_id == paragraphs[i].id), None)
                        if desc:
                            db_service.create_image(
                                db,
                                request.story_id,
                                desc.id,
                                path,
                                False,
                                request.aspect_ratio,
                                request.image_model,
                                request.seed,
                                paragraphs[i].id
                            )

        return ImageGenerationResponse(
            status="success",
            image_paths=image_paths
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@image_router.get("/aspect-ratios", response_model=List[Dict[str, str]])
async def get_aspect_ratios():
    """
    获取支持的图片比例列表
    """
    ratios = []
    for ratio, size in IMAGE_SIZES.items():
        ratios.append({
            "value": ratio,
            "label": f"{ratio} ({size[0]}x{size[1]})"
        })
    return ratios


@image_router.get("/image-models", response_model=List[Dict[str, str]])
async def get_image_models():
    """
    获取支持的图片生成模型列表
    """
    models = [
        {"value": "black-forest-labs/FLUX-1-schnell", "label": "FLUX-1-schnell (快速)"},
        {"value": "black-forest-labs/FLUX-1", "label": "FLUX-1 (高质量)"},
        {"value": "stabilityai/stable-diffusion-xl-base-1.0", "label": "Stable Diffusion XL"},
        {"value": "runwayml/stable-diffusion-v1-5", "label": "Stable Diffusion v1.5"}
    ]
    return models
