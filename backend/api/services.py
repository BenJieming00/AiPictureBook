import time
import re
import os
import json
import requests
import base64
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
from google import genai
from pydantic import BaseModel, TypeAdapter, create_model, Field
from dotenv import load_dotenv
from .config import settings, validate_settings, ArtStyle, AgeRange, IMAGE_SIZES
from openai import OpenAI
from utils.logger import logger

# 加载环境变量
load_dotenv()

# 配置Gemini API
try:
    validate_settings()  # 验证必要设置
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    GEMINI_MODEL = settings.GEMINI_MODEL
except Exception as e:
    logger.error(f"Gemini API配置失败: {str(e)}")


# 定义数据模型
class ImagePrompt(BaseModel):
    image_prompt: list[str]


class ChapterContent(BaseModel):
    title: str
    content: str


class CharacterDetail(BaseModel):
    name: str
    role: str
    appearance: str
    traits: List[str]
    age: str


class StoryContent(BaseModel):
    @classmethod
    def create_dynamic_model(cls, chapter_count: int):
        fields = {
            'story_title': (str, ...),
            **{f'chapter_{i+1}': (ChapterContent, ...) for i in range(chapter_count)},
            'characters': (List[CharacterDetail], ...)
        }
        return create_model('DynamicStoryContent', **fields, __base__=BaseModel)


async def generate_story(
    theme: str,
    story_type: str,
    age_range: str,
    language: str,
    word_count: int,
    pages: int
) -> Tuple[List[str], List[CharacterDetail]]:
    """
    使用Google Gemini生成儿童故事并提取人物设定

    Args:
        theme: 故事主题
        story_type: 故事类型
        age_range: 适合的年龄范围
        language: 故事语言
        word_count: 创作字数
        pages: 绘本页数

    Returns:
        Tuple[List[str], List[CharacterDetail]]: 故事段落列表和人物描述列表
    """
    try:
        # 创建动态模型
        DynamicStoryContent = StoryContent.create_dynamic_model(pages)

        # 创建客户端
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 构建提示词
        prompt = f"""
用户输入内容：{theme}
========================================
# 角色
你是一位杰出的儿童漫画故事创作者，专注于打造充满想象力且寓教于乐的故事内容，这些故事专为{age_range}儿童创作，能极大地激发他们的创造力与好奇心。生成的故事要能引发小朋友们强烈的情感共鸣，具备高度互动性。

# 技能
## 技能 1: 生成创意故事
- 依据用户输入的内容，精心创作一个 {word_count} 字左右的儿童故事。
- 严格保留经典故事中的人物名称和角色，不得更改。
- 故事内容要自然流畅，贴合生活习惯，尽可能丰富多元。
- 选用简单直接的词汇，避免复杂句子结构和口语化词汇，以方便小朋友理解。
- 巧妙增加对话：在故事中合理穿插对话，以此增强故事的趣味性与互动感。
- 着重情感描写：适当增添故事中人物的情感刻画，让故事更具感染力。
- 构建引人入胜的情节，塑造生动鲜活的角色。
- 做好结尾呼应：故事结尾要给出温馨的总结，并附上鼓励小朋友的话语。
- 融入幽默感：在故事里巧妙加入幽默滑稽的情节，既能让孩子开怀大笑，又能维持他们对故事的浓厚兴趣。
- 确保故事长度适中，保障故事内容完整，情节连贯。

## 技能 2：人物设定与描述
- 为故事创建2-4个主要人物，包括至少一个主角和适当的配角
- 每个人物必须具有独特的外观特征，便于在图片中一致地呈现
- 为每个角色设定明确的性格特点和年龄段
- 人物设定需要符合故事主题和类型
- 人物形象要对目标年龄段的儿童有吸引力

返回的类型是:
{DynamicStoryContent}
完整返回格式示例：
{{
  "story_title": "故事总标题",
  "chapter_1": {{
    "title": "第一章标题",
    "content": "第一章内容"
  }},
  "chapter_2": {{
    "title": "第二章标题",
    "content": "第二章内容"
  }},
  "characters": [
    {{
      "name": "小明",
      "role": "主角",
      "appearance": "黑色短发，圆脸，总是穿红色T恤和蓝色短裤",
      "traits": ["好奇", "勇敢", "热心"],
      "age": "小学生"
    }},
    {{
      "name": "小花",
      "role": "配角",
      "appearance": "棕色长发扎成两个小辫子，大眼睛，穿粉色连衣裙",
      "traits": ["聪明", "细心", "乐于助人"],
      "age": "小学生"
    }}
  ]
}}
"""

        # 生成内容
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': DynamicStoryContent,
            },
        )

        # 解析响应
        story_model: DynamicStoryContent = response.parsed

        # 提取章节内容
        paragraphs = [
            getattr(story_model, f'chapter_{i+1}').content
            for i in range(pages)
        ]

        # 提取人物设定
        characters = story_model.characters

        return paragraphs, characters

    except Exception as e:
        print(f"故事生成失败: {str(e)}")
        raise e


async def generate_image_descriptions(
    theme: str,
    paragraphs: List[str],
    style: ArtStyle = ArtStyle.PICTURE_BOOK,
    age_range: AgeRange = AgeRange.CHILD,
    characters: List[CharacterDetail] = []
) -> Tuple[str, List[str]]:
    """
    根据故事段落和人物设定生成统一风格的图片描述，包括封面和内页

    Args:
        theme: 故事主题
        paragraphs: 故事段落列表，每段对应一个场景
        style: 图片风格描述 (枚举值)
        age_range: 适合的年龄范围 (枚举值)
        characters: 故事中的人物设定列表

    Returns:
        Tuple[str, List[str]]: 封面描述和内页图片描述列表
    """
    try:
        # 将枚举值转换为字符串
        style_value = style.value if isinstance(style, ArtStyle) else style
        age_range_value = age_range.value if isinstance(
            age_range, AgeRange) else age_range

        # 创建客户端
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 准备人物设定信息
        characters_info = ""
        if characters:
            characters_info = "故事人物设定：\n"
            for char in characters:
                characters_info += f"- {char.name}：{char.role}，外观：{char.appearance}，特点：{', '.join(char.traits)}，年龄：{char.age}\n"

        # 生成封面描述
        cover_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"""根据以下故事段落生成1个封面图片描述（必须用英文）：
            主题：{theme}
            第一段：{paragraphs[0]}
            最后一段：{paragraphs[-1]}
            
            {characters_info}

            要求：
            1. 保持{style_value}风格
            2. 描述需突出故事主题
            3. 包含场景细节和角色特征，确保角色特征与上述人物设定一致
            4. 必须生成恰好1个描述
            5. 描述必须是一个完整的英文句子""",
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[ImagePrompt],
            },
        )

        # 提取封面描述
        cover_description = cover_response.parsed[0].image_prompt[0] if cover_response.parsed else ""

        # 生成内页描述
        descriptions = []
        for para in paragraphs:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"""根据以下故事段落生成1个图片描述（必须用英文）：
                {para}
                
                {characters_info}

                要求：
                1. 保持{style_value}风格
                2. 描述需连贯展示故事发展
                3. 包含场景细节和角色特征，确保角色特征与上述人物设定一致
                4. 必须生成恰好1个描述
                5. 描述必须是一个完整的英文句子""",
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': list[ImagePrompt],
                },
            )

            # 提取当前段落的图片描述
            if response.parsed:
                descriptions.append(response.parsed[0].image_prompt[0])
            else:
                descriptions.append("")

        return cover_description, descriptions

    except Exception as e:
        logger.error(f"图片描述生成失败: {str(e)}")
        raise e


async def generate_images(
    title: str,
    descriptions: List[str],
    aspect_ratio: str = "16:9",
    image_model: str = None,
    seed: int = None,
    index: int = None,
    flatten_result: bool = True
) -> Union[List[str], List[str]]:
    """
    使用DeepInfra API根据图片描述生成图片

    Args:
        title: 图片标题，用于命名文件
        descriptions: 图片描述列表
        aspect_ratio: 图片比例（如 "16:9", "4:3" 等）
        num: 每个描述生成的图片数量
        image_model: 使用的模型名称，如不指定则使用默认模型
        seed: 随机种子，用于固定生成结果
        index: 描述的起始索引，用于分批处理
        flatten_result: 是否将结果展平为一维数组

    Returns:
        Union[List[str], List[List[str]]]: 如果flatten_result为True，返回展平的图片路径列表；
                                          否则返回嵌套的路径列表（每个描述一个子列表）
    """
    try:
        # 图片存储目录
        static_dir = settings.UPLOAD_DIR

        # 获取图片尺寸
        if aspect_ratio not in IMAGE_SIZES:
            raise ValueError(f"不支持的图片比例: {aspect_ratio}")
        width, height = IMAGE_SIZES[aspect_ratio]

        # 清理标题中的特殊字符
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title)[:50]

        # 选择模型
        if image_model is None:
            # 使用默认模型
            model = next((m for m in settings.IMAGE_MODELS if m.get(
                "default") == "true"), settings.IMAGE_MODELS[0])
        else:
            # 使用指定模型
            model = next(
                (m for m in settings.IMAGE_MODELS if m["name"] == image_model), settings.IMAGE_MODELS[0])

        logger.info(f"使用模型: {model}")
        # 处理指定描述或全部描述
        targets = [descriptions[index-1]
                   ] if index is not None else descriptions
        paragraphs_images = []  # 存储每个描述的图片路径列表

        for i, description in enumerate(targets):
            image_paths = []  # 存储当前描述的图片路径
            # for j in range(num):
            #     # 如果生成多张图片 seed 需要加1
            #     if num > 1:
            #         seed = seed + j - 1
            # 生成带时间戳的文件名
            timestamp = int(time.time())
            filename = f"{clean_title}_{timestamp}_{i}.png"
            img_path = static_dir / filename

            # 构建完整提示词
            prompt = description

            try:
                # 调用DeepInfra API
                response = requests.post(
                    f"https://api.deepinfra.com/v1/openai/images/generations",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPINFRA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "size": f"{width}x{height}",
                        "model": model['name'],
                        "n": 1,
                        "seed": seed if seed is not None else settings.DEFAULT_SEED
                    },
                    timeout=300  # 设置300秒超时
                )
                # 打印请求参数
                # print(
                #     f"请求参数: {json.dumps(json.loads(response.request.body), indent=4)}")

                # 检查响应
                response.raise_for_status()
                result = response.json()

                # 处理响应结果
                if "data" in result and len(result["data"]) > 0:
                    image_data = result["data"][0].get("b64_json")
                    if image_data:
                        # 解码图片
                        image_bytes = base64.b64decode(image_data)

                        # 保存图片文件
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)

                        logger.info(f"图片已保存：{img_path}")

                        # 返回相对路径 - 使用以/static开头的URL路径
                        image_paths.append(f"/static/images/{filename}")
                    else:
                        logger.error("API响应中没有图片数据")
                        image_paths.append("")
                else:
                    logger.error(f"API响应格式错误: {result}")
                    image_paths.append("")

            except requests.exceptions.RequestException as req_err:
                logger.error(f"API请求失败: {req_err}")
                image_paths.append("")
            except Exception as api_err:
                logger.error(f"处理API响应时出错: {api_err}")
                image_paths.append("")

            paragraphs_images.append(image_paths)

        if flatten_result:
            return [img for sublist in paragraphs_images for img in sublist]
        else:
            return paragraphs_images

    except Exception as e:
        logger.error(f"图片生成失败: {str(e)}")
        raise e


# 文本拆分函数
def split_text(text, use_newline=True, use_punctuation=True):
    """
    可配置的文本拆分函数
    :param text: 输入文本
    :param use_newline: 是否使用换行符拆分 (默认True)
    :param use_punctuation: 是否使用标点拆分 (默认True)
    :return: 拆分后的句子列表
    """
    split_pattern = []

    # 构建正则表达式模式
    if use_newline:
        split_pattern.append(r'\n')
    if use_punctuation:
        split_pattern.append(r'([。！？])')  # 捕获标点符号

    # 无拆分条件时返回原文
    if not split_pattern:
        return [text.strip()]

    # 创建复合正则表达式
    pattern = '|'.join(split_pattern)
    elements = re.split(pattern, text)

    # 重组句子逻辑
    sentences = []
    current = []
    punctuation = {'。', '！', '？'}

    for elem in elements:
        if not elem:
            continue

        # 处理换行符
        if use_newline and elem == '\n':
            if current:
                sentences.append(''.join(current).strip())
                current = []
            continue

        # 处理标点符号
        if use_punctuation and elem in punctuation:
            if current:
                current.append(elem)
                sentences.append(''.join(current).strip())
                current = []
            continue

        current.append(elem)

    # 处理剩余内容
    if current:
        sentences.append(''.join(current).strip())

    # 过滤空字符串
    return [s for s in sentences if s]


# 语音生成函数
async def generate_speech(text: str, emotion: str = "happy") -> str:
    """
    生成带有情感的语音文件

    Args:
        text (str): 要转换成语音的文本内容
        emotion (str): 情感类型，默认为happy

    Returns:
        str: 生成的语音文件路径（URL格式）
    """
    try:
        # 保存语音文件的目录
        speech_dir = settings.SPEECH_DIR

        # 确保目录存在
        os.makedirs(speech_dir, exist_ok=True)

        # 生成唯一文件名
        timestamp = int(time.time())
        filename = f"speech-{timestamp}.mp3"
        speech_file_path = speech_dir / filename

        # 创建OpenAI客户端 - 使用安全的创建方式，避免代理设置问题
        import httpx
        # 使用工厂模式显式创建客户端，避免全局设置影响
        http_client = httpx.Client()
        client = OpenAI(
            api_key=settings.SILICONFLOW_API_KEY,
            base_url=settings.SILICONFLOW_URL,
            http_client=http_client
        )

        # 根据情感类型构建提示词
        emotion_prompts = {
            "happy": "你能用高兴的情感说吗？",
            "sad": "你能用悲伤的情感说吗？",
            "excited": "你能用兴奋的情感说吗？",
            "calm": "你能用平静的情感说吗？",
            "curious": "你能用好奇的情感说吗？"
        }

        emotion_prompt = emotion_prompts.get(emotion, emotion_prompts["happy"])
        prompt = f"{emotion_prompt}<|endofprompt|> {text}"

        # 调用API生成语音
        response = client.audio.speech.create(
            model=settings.SILICONFLOW_MODEL,
            voice=settings.SILICONFLOW_VOICE,
            input=prompt,
            response_format="mp3"
        )

        # 保存响应到文件
        response.stream_to_file(str(speech_file_path))

        # 打印文件路径信息用于调试
        # print(
        #     f"语音文件已保存到: {speech_file_path} (绝对路径: {os.path.abspath(speech_file_path)})")

        # 返回URL格式的路径
        return f"/static/speech/{filename}"
    except Exception as e:
        logger.error(f"语音生成错误: {str(e)}")
        raise e


def generate_subtitle_file(sentences: List[Tuple[str, float, float]], output_path: str):
    """
    生成srt格式的字幕文件
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, (text, start_time, end_time) in enumerate(sentences, 1):
            # 将秒数转换为 srt 时间格式 (HH:MM:SS,mmm)
            start = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d},000"
            end = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d},000"

            f.write(f"{idx}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")


# 为段落生成语音、字幕和视频文件
async def generate_paragraph_audio(title: str, paragraphs: List[str], emotion: str = "happy") -> List[Dict[str, str]]:
    """
    为一组段落文本生成语音文件、字幕文件和合并后的视频文件

    Args:
        paragraphs: 段落文本列表
        emotion: 语音情感类型，默认为happy

    Returns:
        List[Dict[str, str]]: 每个段落对应的语音、字幕和视频文件路径
    """
    results = []

    # 确保目录存在
    subtitle_dir = settings.SUBTITLE_DIR
    os.makedirs(subtitle_dir, exist_ok=True)

    audio_dir = settings.AUDIO_DIR
    os.makedirs(audio_dir, exist_ok=True)

    temp_audio_dir = settings.TEMP_AUDIO_DIR
    os.makedirs(temp_audio_dir, exist_ok=True)

    paragraphs = [title] + paragraphs

    for idx, paragraph in enumerate(paragraphs):
        try:
            # 创建段落标识符
            para_id = f"paragraph_{idx+1}_{int(time.time())}"

            # 1. 使用split_text拆分文本
            sentences = split_text(
                paragraph, use_newline=True, use_punctuation=True)

            # 2. 为每个句子生成临时语音文件并直接保存到临时目录
            temp_audio_files = []
            sentence_timings = []
            current_time = 0.0

            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue

                # 生成语音文件
                speech_url = await generate_speech(sentence, emotion)

                # 获取源文件路径 (绝对路径)
                src_file_path = os.path.abspath(
                    speech_url.replace("/static/", "static/"))

                # 生成唯一的目标文件路径 (绝对路径)
                temp_filename = f"temp_{para_id}_sentence_{i}.mp3"
                temp_audio_path = os.path.abspath(
                    os.path.join(str(temp_audio_dir), temp_filename))

                # 将生成的语音文件复制到临时目录
                try:
                    if os.path.exists(src_file_path):
                        import shutil
                        shutil.copy2(src_file_path, temp_audio_path)
                        # print(f"已复制文件: {src_file_path} -> {temp_audio_path}")
                        # 将绝对路径添加到列表
                        temp_audio_files.append(temp_audio_path)
                    else:
                        logger.error(f"源文件不存在: {src_file_path}")
                        # 尝试查找在当前目录下的文件
                        alt_path = os.path.join(os.getcwd(), src_file_path)
                        if os.path.exists(alt_path):
                            shutil.copy2(alt_path, temp_audio_path)
                            logger.info(
                                f"使用替代路径复制文件: {alt_path} -> {temp_audio_path}")
                            temp_audio_files.append(temp_audio_path)
                        else:
                            logger.error(
                                f"无法找到源文件，尝试的路径: {src_file_path}, {alt_path}")
                except Exception as e:
                    logger.error(f"复制语音文件失败: {e}")
                    continue

                # 估算语音持续时间（每个中文字符约0.3秒，每个英文单词约0.4秒）
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sentence))
                english_words = len(re.findall(r'[a-zA-Z]+', sentence))
                duration = chinese_chars * 0.3 + english_words * 0.4
                duration = max(duration, 1.0)  # 最小1秒

                # 记录时间轴
                start_time = current_time
                end_time = current_time + duration
                sentence_timings.append((sentence, start_time, end_time))
                current_time = end_time

            # 3. 生成字幕文件
            subtitle_file = subtitle_dir / f"{para_id}.srt"
            generate_subtitle_file(sentence_timings, str(subtitle_file))

            # 4. 合并所有语音文件
            merged_audio = audio_dir / f"{para_id}.mp3"
            merged_audio_abs = os.path.abspath(str(merged_audio))

            # 使用ffmpeg合并音频文件
            if len(temp_audio_files) > 0:
                # 创建输入文件列表 (使用绝对路径)
                concat_file = os.path.abspath(os.path.join(
                    str(temp_audio_dir), f"{para_id}_list.txt"))

                with open(concat_file, 'w', encoding='utf-8') as f:
                    for audio_file in temp_audio_files:
                        # 使用单引号包裹的绝对路径
                        f.write(f"file '{audio_file}'\n")

                # 打印concat文件内容用于调试
                # print(f"concat文件内容 ({concat_file}):")
                # with open(concat_file, 'r', encoding='utf-8') as f:
                #     print(f.read())

                # 执行合并命令 (使用绝对路径)
                try:
                    cmd = [
                        'ffmpeg',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', concat_file,
                        '-c', 'copy',
                        merged_audio_abs
                    ]
                    # print(f"执行命令: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True, capture_output=True)
                    # print(f"成功合并音频文件: {merged_audio_abs}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"合并音频文件失败: {e}")
                    logger.error(
                        f"错误输出: {e.stderr.decode() if e.stderr else '无错误输出'}")

                    # 尝试使用替代方法
                    try:
                        alternate_cmd = [
                            'ffmpeg',
                            '-i', temp_audio_files[0]  # 使用第一个文件
                        ]

                        # 添加其余文件
                        for audio_file in temp_audio_files[1:]:
                            alternate_cmd.extend(['-i', audio_file])

                        # 添加合并滤镜
                        filter_complex = ""
                        for i in range(len(temp_audio_files)):
                            filter_complex += f"[{i}:0]"
                        filter_complex += f"concat=n={len(temp_audio_files)}:v=0:a=1[out]"

                        alternate_cmd.extend([
                            '-filter_complex', filter_complex,
                            '-map', '[out]',
                            merged_audio_abs
                        ])

                        logger.info(f"尝试替代命令: {' '.join(alternate_cmd)}")
                        subprocess.run(alternate_cmd, check=True,
                                       capture_output=True)
                        logger.info(
                            f"使用替代方法成功合并音频文件: {merged_audio_abs}")
                    except subprocess.CalledProcessError as alt_e:
                        logger.error(f"替代方法合并失败: {alt_e}")
                        logger.error(
                            f"错误输出: {alt_e.stderr.decode() if alt_e.stderr else '无错误输出'}")

                        # 如果合并失败，使用第一个音频文件作为结果
                        if temp_audio_files:
                            # 复制第一个文件到最终位置
                            try:
                                import shutil
                                shutil.copy2(
                                    temp_audio_files[0], merged_audio_abs)
                                logger.info(
                                    f"已将第一个音频文件复制到最终位置: {merged_audio_abs}")
                            except Exception as copy_err:
                                logger.error(
                                    f"复制第一个音频文件失败: {copy_err}")

                # 删除临时的concat文件
                try:
                    os.remove(concat_file)
                except Exception as rm_err:
                    logger.error(f"删除临时文件失败: {rm_err}")

                # 清理临时音频文件
                for temp_file in temp_audio_files:
                    try:
                        os.remove(temp_file)
                    except Exception as rm_err:
                        logger.error(
                            f"删除临时音频文件失败: {temp_file}, {rm_err}")

            # 添加结果
            results.append({
                "paragraph_id": para_id,
                "audio_path": f"/static/audio/{merged_audio.name}",
                "subtitle_path": f"/static/subtitles/{subtitle_file.name}",
            })

        except Exception as e:
            logger.error(f"处理段落 {idx+1} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                "paragraph_id": f"paragraph_{idx+1}_{int(time.time())}",
                "error": str(e),
            })

    return results


# 为段落生成完整视频
async def create_paragraph_video(
    image_paths: List[str],
    audio_paths: List[str],
    subtitle_paths: List[str],
    output_filename: str = None,
    transition_duration: float = 1.0,
    fade_duration: float = 0.5
) -> str:
    """
    根据图片、音频和字幕文件合成视频

    Args:
        image_paths: 图片文件路径列表，第一张作为封面
        audio_paths: 音频文件路径列表，每段音频对应一张图片
        subtitle_paths: 字幕文件路径列表，每个字幕对应一段音频
        output_filename: 输出视频文件名，默认为根据时间戳生成
        transition_duration: 图片过渡持续时间(秒)
        fade_duration: 淡入淡出持续时间(秒)

    Returns:
        str: 生成的视频文件URL路径
    """
    if len(image_paths) < 2:
        raise ValueError("至少需要两张图片（一张封面和一张内容图片）")

    if len(audio_paths) != len(image_paths):
        raise ValueError("音频文件数量应等于图片数量")

    if len(subtitle_paths) != len(audio_paths):
        raise ValueError("字幕文件数量应等于音频文件数量")

    # 创建输出文件名
    timestamp = int(time.time())
    if not output_filename or output_filename == "string" or not output_filename.strip():
        output_filename = f"video_{timestamp}.mp4"
    else:
        # 确保文件名有效并以.mp4结尾
        output_filename = output_filename.strip()
        if not output_filename.endswith('.mp4'):
            output_filename = f"{output_filename}.mp4"

    # 确保输出目录存在
    output_dir = Path("static/videos")
    os.makedirs(output_dir, exist_ok=True)
    output_path = output_dir / output_filename

    # 打印输出文件路径用于调试
    logger.info(
        f"视频将输出到: {output_path} (绝对路径: {os.path.abspath(output_path)})")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    logger.info(f"使用临时目录: {temp_dir}")

    try:
        # 创建段落视频片段
        segment_paths = []

        # 为每个段落创建视频
        for i in range(len(audio_paths)):
            # 处理路径（去掉/static/前缀）
            image_path = image_paths[i].replace("/static/", "static/")
            audio_path = audio_paths[i].replace("/static/", "static/")
            subtitle_path = subtitle_paths[i].replace("/static/", "static/")

            # 获取音频持续时间
            duration_cmd = ['ffprobe', '-v', 'error', '-show_entries',
                            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
            result = subprocess.run(
                duration_cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())

            # 段落视频输出路径
            segment_output = os.path.join(temp_dir, f"segment_{i}.mp4")

            # 如果是第一个段落（封面），添加额外的2秒延迟
            extra_delay = 2.0 if i == 0 else 0.0
            total_duration = duration + extra_delay

            # 创建带有音频和字幕的视频片段
            segment_cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', image_path,
                '-i', audio_path,
                '-i', subtitle_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-pix_fmt', 'yuv420p'
            ]

            # 构建视频过滤器
            vf_filter = f"fade=t=in:st=0:d={fade_duration}"

            # 如果是第一个段落（封面），添加额外的延迟
            if i == 0:
                # 音频结束后保持图像显示2秒
                # 使用apad过滤器延长音频
                segment_cmd.extend([
                    '-af', f"apad=pad_dur={extra_delay}"
                ])
                # 淡出效果从延长后的总时长开始
                vf_filter += f",fade=t=out:st={total_duration-fade_duration}:d={fade_duration}"
            else:
                vf_filter += f",fade=t=out:st={duration-fade_duration}:d={fade_duration}"

            # 添加字幕
            vf_filter += f",subtitles='{subtitle_path}'"
            segment_cmd.extend(['-vf', vf_filter])

            # 设置总时长
            segment_cmd.extend([
                '-t', str(total_duration + 0.5),  # 额外添加0.5秒确保字幕完全显示
                segment_output
            ])

            # 对于Windows系统，需要修改字幕过滤器路径格式
            if os.name == 'nt':
                segment_cmd[-2] = segment_cmd[-2].replace("'", "")

            subprocess.run(segment_cmd, check=True, capture_output=True)
            segment_paths.append(segment_output)

        # 3. 创建合并文件列表
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w', encoding='utf-8') as f:
            for segment in segment_paths:
                f.write(f"file '{segment}'\n")

        # 4. 合并所有视频片段
        merge_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            str(output_path)
        ]
        logger.info(f"执行合并命令: {' '.join(merge_cmd)}")
        try:
            result = subprocess.run(merge_cmd, check=True, capture_output=True)
            logger.info(f"视频成功生成: {output_path}")

            # 检查生成的视频文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"生成的视频文件大小: {file_size} 字节")

                # 获取视频元数据
                try:
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_format',
                                 '-show_streams', '-of', 'json', str(output_path)]
                    probe_result = subprocess.run(
                        probe_cmd, capture_output=True, text=True)
                    # print(f"视频文件元数据: {probe_result.stdout}")
                except Exception as probe_err:
                    logger.error(f"获取视频元数据失败: {probe_err}")
            else:
                logger.warning(f"警告: 视频文件不存在: {output_path}")

            return f"/static/videos/{output_filename}"
        except subprocess.CalledProcessError as e:
            logger.error(f"视频生成失败: {e}")
            logger.error(
                f"错误输出: {e.stderr.decode() if e.stderr else '无错误输出'}")

            # 尝试使用替代方法 - 使用较为保守的参数
            try:
                alt_merge_cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-c:v', 'libx264',  # 使用固定编码器
                    '-c:a', 'aac',      # 添加音频编码器
                    '-preset', 'medium',  # 使用中等压缩率
                    '-crf', '23',       # 合理的质量
                    str(output_path)
                ]
                logger.info(f"尝试替代命令: {' '.join(alt_merge_cmd)}")
                subprocess.run(alt_merge_cmd, check=True, capture_output=True)
                logger.info(f"使用替代方法成功生成视频: {output_path}")
                return f"/static/videos/{output_filename}"
            except subprocess.CalledProcessError as alt_e:
                logger.error(f"替代方法也失败: {alt_e}")
                logger.error(
                    f"错误输出: {alt_e.stderr.decode() if alt_e.stderr else '无错误输出'}")
                raise ValueError(f"无法合并视频: {e}")

    except Exception as e:
        logger.error(f"视频生成失败: {e}")
        import traceback
        traceback.print_exc()
        raise e

    finally:
        # 在生产环境中，应该清理临时文件
        try:
            # 检查临时目录内容用于调试
            # print(f"临时目录内容: {os.listdir(temp_dir)}")

            # 检查concat文件内容（如果存在）
            concat_file_path = os.path.join(temp_dir, "concat_list.txt")
            if os.path.exists(concat_file_path):
                # print(f"Concat文件内容:")
                with open(concat_file_path, 'r') as f:
                    logger.info(f.read())

            # 根据环境变量决定是否保留临时文件用于调试
            if os.environ.get("DEBUG_MODE", "0") != "1":
                shutil.rmtree(temp_dir)
                logger.info(f"临时目录已删除: {temp_dir}")
            else:
                logger.info(f"调试模式: 保留临时目录 {temp_dir} 用于检查")
        except Exception as e:
            logger.error(f"处理临时目录时出错: {e}")
