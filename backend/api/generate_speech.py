import os
import time
from pathlib import Path
from openai import OpenAI
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Union, Optional
from sqlalchemy.orm import Session
from .services import generate_speech, split_text, generate_paragraph_audio, create_paragraph_video
from .models import (
    SpeechGenerationRequest, SpeechGenerationResponse,
    TextSplitRequest, TextSplitResponse
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .database import get_db
from . import db_service

# 创建路由
speech_router = APIRouter(tags=["语音生成"])

# 段落语音生成请求模型
class ParagraphAudioRequest(BaseModel):
    title: str = Field(..., description="标题")
    paragraphs: List[str] = Field(..., description="段落文本列表", min_items=1)
    emotion: str = Field("happy", description="语音情感类型", example="happy")
    story_id: Optional[str] = Field(None, description="故事ID，用于关联到数据库")
    paragraph_ids: Optional[List[str]] = Field(None, description="段落ID列表，用于关联到数据库")

# 段落语音生成响应模型
class ParagraphAudioResponse(BaseModel):
    status: str = Field(..., description="响应状态", example="success")
    audio_paths: List[str] = Field(..., description="音频文件路径列表")
    subtitle_paths: List[str] = Field(..., description="字幕文件路径列表")
    paragraph_ids: List[str] = Field(..., description="段落ID列表")

# 段落视频生成请求模型
class ParagraphVideoRequest(BaseModel):
    image_paths: List[str] = Field(...,
                                   description="图片文件路径列表，第一张作为封面", min_items=2)
    audio_paths: List[str] = Field(..., description="音频文件路径列表", min_items=1)
    subtitle_paths: List[str] = Field(..., description="字幕文件路径列表", min_items=1)
    output_filename: str = Field(None, description="输出视频文件名，默认根据时间戳生成")
    transition_duration: float = Field(1.0, description="图片过渡持续时间(秒)")
    fade_duration: float = Field(0.5, description="淡入淡出持续时间(秒)")
    story_id: Optional[str] = Field(None, description="故事ID，用于关联到数据库")

# 段落视频生成响应模型
class ParagraphVideoResponse(BaseModel):
    status: str = Field(..., description="响应状态", example="success")
    video_path: str = Field(..., description="生成的视频文件路径")


@speech_router.post("/generate", response_model=SpeechGenerationResponse)
async def create_speech(request: SpeechGenerationRequest, db: Session = Depends(get_db)):
    """
    生成语音API

    - **text**: 需要转换为语音的文本内容
    - **emotion**: 语音情感类型 (默认 happy)

    返回生成的语音文件路径
    """
    try:
        speech_path = await generate_speech(
            text=request.text,
            emotion=request.emotion
        )

        return SpeechGenerationResponse(
            status="success",
            speech_path=speech_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@speech_router.get("/download/{filename}")
async def download_speech(filename: str):
    """
    下载语音文件API

    - **filename**: 语音文件名

    返回语音文件
    """
    try:
        file_path = Path(f"static/speech/{filename}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="audio/mpeg"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@speech_router.get("/emotions", response_model=List[Dict[str, str]])
async def get_emotions():
    """
    获取支持的情感类型列表
    """
    emotions = [
        {"value": "happy", "label": "开心"},
        {"value": "sad", "label": "悲伤"},
        {"value": "angry", "label": "愤怒"},
        {"value": "fear", "label": "恐惧"},
        {"value": "surprise", "label": "惊讶"},
        {"value": "neutral", "label": "平静"}
    ]
    return emotions


@speech_router.post("/generate_paragraph_audio", response_model=ParagraphAudioResponse)
async def create_paragraph_audio(request: ParagraphAudioRequest, db: Session = Depends(get_db)):
    """
    生成段落语音API

    - **title**: 标题，用于命名生成的音频文件
    - **paragraphs**: 段落文本列表
    - **emotion**: 语音情感类型 (默认 happy)
    - **story_id**: 故事ID，用于关联到数据库 (可选)
    - **paragraph_ids**: 段落ID列表，用于关联到数据库 (可选)

    返回生成的音频文件路径列表和字幕文件路径列表
    """
    try:
        # 生成音频和字幕
        results = await generate_paragraph_audio(
            title=request.title,
            paragraphs=request.paragraphs,
            emotion=request.emotion
        )
        
        # 从结果中提取音频路径、字幕路径和段落ID
        audio_paths = []
        subtitle_paths = []
        paragraph_ids = []
        
        for result in results:
            if "error" not in result:
                audio_paths.append(result["audio_path"])
                subtitle_paths.append(result["subtitle_path"])
                paragraph_ids.append(result["paragraph_id"])

        # 如果提供了故事ID和段落ID，保存到数据库
        if request.story_id and request.paragraph_ids:
            story = db_service.get_story(db, request.story_id)
            if story and len(audio_paths) == len(request.paragraph_ids):
                for i, (audio_path, paragraph_id) in enumerate(zip(audio_paths, request.paragraph_ids)):
                    # 获取音频时长（这里简化处理，实际应该从音频文件中获取）
                    duration = 0.0
                    
                    db_service.create_speech(
                        db,
                        request.story_id,
                        paragraph_id,
                        audio_path,
                        request.emotion,
                        duration
                    )

        return ParagraphAudioResponse(
            status="success",
            audio_paths=audio_paths,
            subtitle_paths=subtitle_paths,
            paragraph_ids=paragraph_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@speech_router.post("/generate_paragraph_video", response_model=ParagraphVideoResponse)
async def create_video_from_paragraphs(request: ParagraphVideoRequest, db: Session = Depends(get_db)):
    """
    生成段落视频API

    - **image_paths**: 图片文件路径列表，第一张作为封面
    - **audio_paths**: 音频文件路径列表
    - **subtitle_paths**: 字幕文件路径列表
    - **output_filename**: 输出视频文件名 (可选)
    - **transition_duration**: 图片过渡持续时间(秒) (默认 1.0)
    - **fade_duration**: 淡入淡出持续时间(秒) (默认 0.5)
    - **story_id**: 故事ID，用于关联到数据库 (可选)

    返回生成的视频文件路径
    """
    try:
        # 生成视频
        video_path = await create_paragraph_video(
            image_paths=request.image_paths,
            audio_paths=request.audio_paths,
            subtitle_paths=request.subtitle_paths,
            output_filename=request.output_filename,
            transition_duration=request.transition_duration,
            fade_duration=request.fade_duration
        )

        # 如果提供了故事ID，保存到数据库
        if request.story_id:
            story = db_service.get_story(db, request.story_id)
            if story:
                # 获取视频时长（这里简化处理，实际应该从视频文件中获取）
                duration = 0.0
                # 获取视频分辨率（这里简化处理，实际应该从视频文件中获取）
                resolution = "1920x1080"
                
                db_service.create_video(
                    db,
                    request.story_id,
                    video_path,
                    duration,
                    resolution
                )

        return ParagraphVideoResponse(
            status="success",
            video_path=video_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
