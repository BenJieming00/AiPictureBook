from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
import datetime
from .database import Base
from .config import ArtStyle, Language, StoryType, AgeRange

def generate_uuid():
    return str(uuid.uuid4())

class Story(Base):
    """故事表"""
    __tablename__ = "stories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    theme = Column(String(100), nullable=False, comment="故事主题")
    story_type = Column(String(50), nullable=False, comment="故事类型")
    age_range = Column(String(50), nullable=False, comment="适合的年龄范围")
    language = Column(String(20), nullable=False, comment="故事语言")
    word_count = Column(Integer, nullable=False, comment="创作字数")
    pages = Column(Integer, nullable=False, comment="绘本页数")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    paragraphs = relationship("Paragraph", back_populates="story", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    image_descriptions = relationship("ImageDescription", back_populates="story", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="story", cascade="all, delete-orphan")
    speeches = relationship("Speech", back_populates="story", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="story", cascade="all, delete-orphan")

class Paragraph(Base):
    """段落表"""
    __tablename__ = "paragraphs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    content = Column(Text, nullable=False, comment="段落内容")
    page_number = Column(Integer, nullable=False, comment="页码")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="paragraphs")
    image_description = relationship("ImageDescription", back_populates="paragraph", uselist=False)
    images = relationship("Image", back_populates="paragraph")
    speech = relationship("Speech", back_populates="paragraph", uselist=False)

class Character(Base):
    """人物表"""
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="人物名称")
    role = Column(String(50), nullable=False, comment="角色定位")
    appearance = Column(Text, nullable=False, comment="外观描述")
    traits = Column(JSON, nullable=False, comment="性格特点")
    age = Column(String(50), nullable=False, comment="年龄段")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="characters")

class ImageDescription(Base):
    """图片描述表"""
    __tablename__ = "image_descriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    paragraph_id = Column(String(36), ForeignKey("paragraphs.id"), nullable=True)
    description = Column(Text, nullable=False, comment="图片描述")
    is_cover = Column(Boolean, default=False, comment="是否为封面")
    style = Column(String(50), nullable=False, comment="图片风格")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="image_descriptions")
    paragraph = relationship("Paragraph", back_populates="image_description")
    images = relationship("Image", back_populates="image_description")

class Image(Base):
    """图片表"""
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    paragraph_id = Column(String(36), ForeignKey("paragraphs.id"), nullable=True)
    image_description_id = Column(String(36), ForeignKey("image_descriptions.id"), nullable=False)
    file_path = Column(String(255), nullable=False, comment="文件路径")
    is_cover = Column(Boolean, default=False, comment="是否为封面")
    aspect_ratio = Column(String(10), nullable=False, comment="图片比例")
    model = Column(String(100), nullable=True, comment="生成模型")
    seed = Column(Integer, nullable=True, comment="随机种子")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="images")
    paragraph = relationship("Paragraph", back_populates="images")
    image_description = relationship("ImageDescription", back_populates="images")

class Speech(Base):
    """语音表"""
    __tablename__ = "speeches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    paragraph_id = Column(String(36), ForeignKey("paragraphs.id"), nullable=False)
    file_path = Column(String(255), nullable=False, comment="文件路径")
    emotion = Column(String(50), nullable=True, comment="情感类型")
    duration = Column(Float, nullable=True, comment="语音时长(秒)")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="speeches")
    paragraph = relationship("Paragraph", back_populates="speech")

class Video(Base):
    """视频表"""
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    file_path = Column(String(255), nullable=False, comment="文件路径")
    duration = Column(Float, nullable=True, comment="视频时长(秒)")
    resolution = Column(String(20), nullable=True, comment="视频分辨率")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    
    # 关系
    story = relationship("Story", back_populates="videos") 