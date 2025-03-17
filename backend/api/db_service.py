from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from . import db_models
from . import models

# Story 相关操作
def create_story(db: Session, story_request: models.StoryRequest) -> db_models.Story:
    """创建故事记录"""
    db_story = db_models.Story(
        theme=story_request.theme,
        story_type=story_request.story_type.value,
        age_range=story_request.age_range,
        language=story_request.language.value,
        word_count=story_request.word_count,
        pages=story_request.pages
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def get_story(db: Session, story_id: str) -> Optional[db_models.Story]:
    """获取故事记录"""
    return db.query(db_models.Story).filter(db_models.Story.id == story_id).first()

def get_stories(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Story]:
    """获取故事列表"""
    return db.query(db_models.Story).order_by(db_models.Story.created_at.desc()).offset(skip).limit(limit).all()

def delete_story(db: Session, story_id: str) -> bool:
    """删除故事记录"""
    db_story = get_story(db, story_id)
    if db_story:
        db.delete(db_story)
        db.commit()
        return True
    return False

# Paragraph 相关操作
def create_paragraphs(db: Session, story_id: str, paragraphs: List[str]) -> List[db_models.Paragraph]:
    """创建段落记录"""
    db_paragraphs = []
    for i, content in enumerate(paragraphs):
        db_paragraph = db_models.Paragraph(
            story_id=story_id,
            content=content,
            page_number=i + 1
        )
        db.add(db_paragraph)
        db_paragraphs.append(db_paragraph)
    
    db.commit()
    for paragraph in db_paragraphs:
        db.refresh(paragraph)
    
    return db_paragraphs

def get_paragraphs(db: Session, story_id: str) -> List[db_models.Paragraph]:
    """获取故事的所有段落"""
    return db.query(db_models.Paragraph).filter(db_models.Paragraph.story_id == story_id).order_by(db_models.Paragraph.page_number).all()

# Character 相关操作
def create_characters(db: Session, story_id: str, characters: List[models.CharacterDescription]) -> List[db_models.Character]:
    """创建人物记录"""
    db_characters = []
    for character in characters:
        db_character = db_models.Character(
            story_id=story_id,
            name=character.name,
            role=character.role,
            appearance=character.appearance,
            traits=character.traits,
            age=character.age
        )
        db.add(db_character)
        db_characters.append(db_character)
    
    db.commit()
    for character in db_characters:
        db.refresh(character)
    
    return db_characters

def get_characters(db: Session, story_id: str) -> List[db_models.Character]:
    """获取故事的所有人物"""
    return db.query(db_models.Character).filter(db_models.Character.story_id == story_id).all()

# ImageDescription 相关操作
def create_image_descriptions(
    db: Session, 
    story_id: str, 
    descriptions: List[str], 
    cover_description: str,
    style: str,
    paragraphs: List[db_models.Paragraph] = None
) -> List[db_models.ImageDescription]:
    """创建图片描述记录"""
    db_image_descriptions = []
    
    # 创建封面图片描述
    cover_desc = db_models.ImageDescription(
        story_id=story_id,
        description=cover_description,
        is_cover=True,
        style=style
    )
    db.add(cover_desc)
    db_image_descriptions.append(cover_desc)
    
    # 创建段落图片描述
    if paragraphs is None:
        paragraphs = get_paragraphs(db, story_id)
    
    for i, (desc, paragraph) in enumerate(zip(descriptions, paragraphs)):
        db_image_description = db_models.ImageDescription(
            story_id=story_id,
            paragraph_id=paragraph.id,
            description=desc,
            is_cover=False,
            style=style
        )
        db.add(db_image_description)
        db_image_descriptions.append(db_image_description)
    
    db.commit()
    for image_description in db_image_descriptions:
        db.refresh(image_description)
    
    return db_image_descriptions

def get_image_descriptions(db: Session, story_id: str) -> List[db_models.ImageDescription]:
    """获取故事的所有图片描述"""
    return db.query(db_models.ImageDescription).filter(db_models.ImageDescription.story_id == story_id).all()

# Image 相关操作
def create_image(
    db: Session,
    story_id: str,
    image_description_id: str,
    file_path: str,
    is_cover: bool,
    aspect_ratio: str,
    model: str = None,
    seed: int = None,
    paragraph_id: str = None
) -> db_models.Image:
    """创建图片记录"""
    db_image = db_models.Image(
        story_id=story_id,
        image_description_id=image_description_id,
        paragraph_id=paragraph_id,
        file_path=file_path,
        is_cover=is_cover,
        aspect_ratio=aspect_ratio,
        model=model,
        seed=seed
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_images(db: Session, story_id: str) -> List[db_models.Image]:
    """获取故事的所有图片"""
    return db.query(db_models.Image).filter(db_models.Image.story_id == story_id).all()

# Speech 相关操作
def create_speech(
    db: Session,
    story_id: str,
    paragraph_id: str,
    file_path: str,
    emotion: str = None,
    duration: float = None
) -> db_models.Speech:
    """创建语音记录"""
    db_speech = db_models.Speech(
        story_id=story_id,
        paragraph_id=paragraph_id,
        file_path=file_path,
        emotion=emotion,
        duration=duration
    )
    db.add(db_speech)
    db.commit()
    db.refresh(db_speech)
    return db_speech

def get_speeches(db: Session, story_id: str) -> List[db_models.Speech]:
    """获取故事的所有语音"""
    return db.query(db_models.Speech).filter(db_models.Speech.story_id == story_id).all()

# Video 相关操作
def create_video(
    db: Session,
    story_id: str,
    file_path: str,
    duration: float = None,
    resolution: str = None
) -> db_models.Video:
    """创建视频记录"""
    db_video = db_models.Video(
        story_id=story_id,
        file_path=file_path,
        duration=duration,
        resolution=resolution
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_videos(db: Session, story_id: str) -> List[db_models.Video]:
    """获取故事的所有视频"""
    return db.query(db_models.Video).filter(db_models.Video.story_id == story_id).all()

# 转换函数
def story_to_response(story: db_models.Story) -> Dict[str, Any]:
    """将数据库故事对象转换为响应格式"""
    paragraphs = [{"id": p.id, "content": p.content, "page_number": p.page_number} for p in story.paragraphs]
    characters = [
        models.CharacterDescription(
            name=c.name,
            role=c.role,
            appearance=c.appearance,
            traits=c.traits,
            age=c.age
        ) for c in story.characters
    ]
    
    # 获取图片描述
    image_descriptions = {}
    for desc in story.image_descriptions:
        if desc.is_cover:
            image_descriptions["cover"] = desc.description
        elif desc.paragraph_id:
            image_descriptions[desc.paragraph_id] = desc.description
    
    # 获取图片
    images = {}
    for img in story.images:
        if img.is_cover:
            if "cover" not in images:
                images["cover"] = []
            images["cover"].append(img.file_path)
        elif img.paragraph_id:
            if img.paragraph_id not in images:
                images[img.paragraph_id] = []
            images[img.paragraph_id].append(img.file_path)
    
    # 获取语音
    speeches = {}
    for speech in story.speeches:
        speeches[speech.paragraph_id] = speech.file_path
    
    # 获取视频
    videos = [video.file_path for video in story.videos]
    
    return {
        "id": story.id,
        "theme": story.theme,
        "story_type": story.story_type,
        "age_range": story.age_range,
        "language": story.language,
        "word_count": story.word_count,
        "pages": story.pages,
        "created_at": story.created_at.isoformat(),
        "updated_at": story.updated_at.isoformat(),
        "paragraphs": paragraphs,
        "characters": [c.dict() for c in characters],
        "image_descriptions": image_descriptions,
        "images": images,
        "speeches": speeches,
        "videos": videos
    } 