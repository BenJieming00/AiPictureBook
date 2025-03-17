from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

from .database import get_db
from . import db_models, db_service, models
from .config import settings

story_db_router = APIRouter(tags=["故事数据库API"])

# 获取所有故事
@story_db_router.get("/", response_model=List[Dict[str, Any]])
def get_all_stories(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="返回的最大记录数"),
    db: Session = Depends(get_db)
):
    """获取所有故事列表"""
    stories = db_service.get_stories(db, skip=skip, limit=limit)
    return [db_service.story_to_response(story) for story in stories]

# 获取单个故事
@story_db_router.get("/{story_id}", response_model=Dict[str, Any])
def get_story(story_id: str, db: Session = Depends(get_db)):
    """获取单个故事详情"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return db_service.story_to_response(story)

# 创建故事
@story_db_router.post("/", response_model=Dict[str, Any])
def create_story(story_request: models.StoryRequest, db: Session = Depends(get_db)):
    """创建新故事"""
    # 创建故事记录
    story = db_service.create_story(db, story_request)
    return {"id": story.id, "message": "故事创建成功"}

# 删除故事
@story_db_router.delete("/{story_id}")
def delete_story(story_id: str, db: Session = Depends(get_db)):
    """删除故事"""
    success = db_service.delete_story(db, story_id)
    if not success:
        raise HTTPException(status_code=404, detail="故事不存在")
    return {"message": "故事删除成功"}

# 添加故事段落
@story_db_router.post("/{story_id}/paragraphs", response_model=Dict[str, Any])
def add_paragraphs(
    story_id: str, 
    paragraphs: List[str], 
    db: Session = Depends(get_db)
):
    """添加故事段落"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 创建段落记录
    db_paragraphs = db_service.create_paragraphs(db, story_id, paragraphs)
    return {"message": "段落添加成功", "count": len(db_paragraphs)}

# 添加故事人物
@story_db_router.post("/{story_id}/characters", response_model=Dict[str, Any])
def add_characters(
    story_id: str, 
    characters: List[models.CharacterDescription], 
    db: Session = Depends(get_db)
):
    """添加故事人物"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 创建人物记录
    db_characters = db_service.create_characters(db, story_id, characters)
    return {"message": "人物添加成功", "count": len(db_characters)}

# 添加图片描述
@story_db_router.post("/{story_id}/image-descriptions", response_model=Dict[str, Any])
def add_image_descriptions(
    story_id: str,
    cover_description: str = Form(...),
    descriptions: str = Form(...),
    style: str = Form(...),
    db: Session = Depends(get_db)
):
    """添加图片描述"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 解析描述列表
    descriptions_list = json.loads(descriptions)
    
    # 获取段落
    paragraphs = db_service.get_paragraphs(db, story_id)
    if len(descriptions_list) != len(paragraphs):
        raise HTTPException(status_code=400, detail="描述数量与段落数量不匹配")
    
    # 创建图片描述记录
    db_image_descriptions = db_service.create_image_descriptions(
        db, story_id, descriptions_list, cover_description, style, paragraphs
    )
    
    return {"message": "图片描述添加成功", "count": len(db_image_descriptions)}

# 添加图片
@story_db_router.post("/{story_id}/images", response_model=Dict[str, Any])
def add_image(
    story_id: str,
    image: UploadFile = File(...),
    image_description_id: str = Form(...),
    is_cover: bool = Form(False),
    aspect_ratio: str = Form("16:9"),
    model: Optional[str] = Form(None),
    seed: Optional[int] = Form(None),
    paragraph_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """添加图片"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 保存图片文件
    image_dir = Path("static/images")
    image_dir.mkdir(exist_ok=True, parents=True)
    
    # 生成文件名
    file_ext = os.path.splitext(image.filename)[1]
    image_filename = f"{story_id}_{image_description_id}{file_ext}"
    image_path = image_dir / image_filename
    
    # 写入文件
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    
    # 创建图片记录
    db_image = db_service.create_image(
        db,
        story_id,
        image_description_id,
        f"/static/images/{image_filename}",
        is_cover,
        aspect_ratio,
        model,
        seed,
        paragraph_id
    )
    
    return {
        "message": "图片添加成功",
        "image_id": db_image.id,
        "file_path": db_image.file_path
    }

# 添加语音
@story_db_router.post("/{story_id}/speeches", response_model=Dict[str, Any])
def add_speech(
    story_id: str,
    speech: UploadFile = File(...),
    paragraph_id: str = Form(...),
    emotion: Optional[str] = Form(None),
    duration: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """添加语音"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 保存语音文件
    speech_dir = Path("static/speech")
    speech_dir.mkdir(exist_ok=True, parents=True)
    
    # 生成文件名
    file_ext = os.path.splitext(speech.filename)[1]
    speech_filename = f"{story_id}_{paragraph_id}{file_ext}"
    speech_path = speech_dir / speech_filename
    
    # 写入文件
    with open(speech_path, "wb") as f:
        f.write(speech.file.read())
    
    # 创建语音记录
    db_speech = db_service.create_speech(
        db,
        story_id,
        paragraph_id,
        f"/static/speech/{speech_filename}",
        emotion,
        duration
    )
    
    return {
        "message": "语音添加成功",
        "speech_id": db_speech.id,
        "file_path": db_speech.file_path
    }

# 添加视频
@story_db_router.post("/{story_id}/videos", response_model=Dict[str, Any])
def add_video(
    story_id: str,
    video: UploadFile = File(...),
    duration: Optional[float] = Form(None),
    resolution: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """添加视频"""
    story = db_service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    # 保存视频文件
    video_dir = Path("static/videos")
    video_dir.mkdir(exist_ok=True, parents=True)
    
    # 生成文件名
    file_ext = os.path.splitext(video.filename)[1]
    video_filename = f"{story_id}{file_ext}"
    video_path = video_dir / video_filename
    
    # 写入文件
    with open(video_path, "wb") as f:
        f.write(video.file.read())
    
    # 创建视频记录
    db_video = db_service.create_video(
        db,
        story_id,
        f"/static/videos/{video_filename}",
        duration,
        resolution
    )
    
    return {
        "message": "视频添加成功",
        "video_id": db_video.id,
        "file_path": db_video.file_path
    } 