from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .config import ArtStyle, Language, StoryType, AgeRange  # 从config导入所有枚举类型


# 请求模型
class StoryRequest(BaseModel):
    theme: str = Field(..., description="故事主题", example="太空探险")
    story_type: StoryType = Field(..., description="故事类型")
    age_range: str = Field(..., description="适合的年龄范围", example="3-6岁")
    language: Language = Field(..., description="故事语言")
    word_count: int = Field(..., gt=100, lt=10000,
                            description="创作字数", example=1000)
    pages: int = Field(..., gt=1, lt=30, description="绘本页数", example=10)


# 人物描述模型
class CharacterDescription(BaseModel):
    name: str = Field(..., description="人物名称")
    role: str = Field(..., description="角色定位", example="主角/配角/反派")
    appearance: str = Field(..., description="外观描述",
                            example="红色头发，绿色眼睛，穿着蓝色连衣裙")
    traits: List[str] = Field(..., description="性格特点",
                              example=["勇敢", "聪明", "善良"])
    age: str = Field(..., description="年龄段", example="小孩/青少年/成人/老人")


# 响应模型
class StoryResponse(BaseModel):
    paragraphs: List[str] = Field(..., description="故事段落，每段对应一个绘本页")
    characters: List[CharacterDescription] = Field(
        default=[], description="故事中的主要人物描述")


# 图片描述请求模型
class ImageDescriptionRequest(BaseModel):
    theme: str = Field(..., description="故事主题", example="太空探险")
    paragraphs: List[str] = Field(...,
                                  description="故事段落，每段对应一个场景", min_items=1)
    style: ArtStyle = Field(ArtStyle.PICTURE_BOOK, description="图片风格描述")
    age_range: AgeRange = Field(AgeRange.CHILD, description="适合的年龄范围")
    characters: List[CharacterDescription] = Field(
        default=[], description="故事中的主要人物描述，用于保持图片中人物形象的一致性")
    story_id: Optional[str] = Field(None, description="故事ID，用于关联到数据库")


# 图片描述响应模型
class ImageDescriptionResponse(BaseModel):
    cover_description: str = Field(..., description="封面图片描述")
    descriptions: List[str] = Field(..., description="图片描述列表，按段落顺序排列")


# 图片生成请求模型
class ImageGenerationRequest(BaseModel):
    title: str = Field(..., description="图片标题", example="太空探险")
    descriptions: List[str] = Field(...,
                                    description="图片描述列表，每段对应一个场景", min_items=1)
    aspect_ratio: str = Field(..., description="图片比例", example="16:9")
    num: int = Field(..., gt=0, lt=10, description="每个描述生成图片数量", example=1)
    image_model: str = Field(None, description="图片生成模型名称",
                             example="black-forest-labs/FLUX-1-schnell")
    seed: int = Field(None, description="随机种子值，用于固定生成结果", example=1234)
    index: int = Field(None, gt=0, lt=100,
                       description="起始索引，用于分批处理", example=1)

    class Config:
        protected_namespaces = ()


# 图片生成响应模型
class ImageGenerationResponse(BaseModel):
    status: str = Field(..., description="响应状态", example="success")
    image_paths: List[str] = Field(..., description="图片路径列表")


# 文本拆分请求模型
class TextSplitRequest(BaseModel):
    text: str = Field(..., min_length=1, description="需要拆分的文本内容")
    use_newline: bool = Field(True, description="是否使用换行符拆分")
    use_punctuation: bool = Field(True, description="是否使用标点符号拆分")


# 文本拆分响应模型
class TextSplitResponse(BaseModel):
    sentences: List[str] = Field(..., description="拆分后的句子列表")


# 语音生成请求模型
class SpeechGenerationRequest(BaseModel):
    text: str = Field(..., min_length=1,
                      description="需要转换为语音的文本内容", example="小宇是一个非常喜欢星星的孩子。")
    emotion: str = Field("happy", description="语音情感类型", example="happy")


# 语音生成响应模型
class SpeechGenerationResponse(BaseModel):
    status: str = Field(..., description="响应状态", example="success")
    speech_path: str = Field(..., description="生成的语音文件路径")
