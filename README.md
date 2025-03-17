# AI儿童绘本生成平台

这是一个基于人工智能技术的儿童绘本生成平台，可以根据用户输入的主题自动生成故事内容、图片描述、配图、语音朗读，并最终合成为完整的绘本视频。

## 功能特点

- 自动生成儿童故事内容
- 为故事生成图片描述
- 根据描述生成插图
- 为故事生成语音朗读
- 合成绘本视频
- 支持多种艺术风格和年龄段

## 环境要求

### 后端环境

- Python 3.8+
- FastAPI
- SQLAlchemy
- FFmpeg (用于音视频处理)
- 其他依赖库

### 前端环境

- Node.js 14+
- Vue.js 3
- Element Plus
- Axios

## 安装步骤

### 1. 克隆代码库

```bash
git clone https://github.com/yourusername/AiPictureBook.git
cd AiPictureBook
```

### 2. 后端环境安装

#### 安装Python

macOS用户可以使用Homebrew安装Python：

```bash
brew install python3
```

Windows用户可以从[Python官网](https://www.python.org/downloads/)下载安装包。

#### 安装FFmpeg

macOS用户：

```bash
brew install ffmpeg
```

Windows用户可以从[FFmpeg官网](https://ffmpeg.org/download.html)下载安装包。

#### 创建虚拟环境并安装依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或者
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

如果没有requirements.txt文件，可以手动安装以下依赖：

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-multipart google-generativeai openai pillow python-dotenv
```

#### 配置环境变量

创建`.env`文件：

```bash
cd backend
touch .env
```

在`.env`文件中添加以下内容：

```
# API密钥
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
DEEPINFRA_API_KEY=your_deepinfra_api_key

# 应用设置
APP_NAME="AI儿童绘本生成平台"
APP_VERSION="1.0.0"
DATABASE_URL="sqlite:///./database/app.db"
```

### 3. 前端环境安装

```bash
cd frontend
npm install
```

## 运行步骤

### 1. 启动后端服务

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# 或者
# venv\Scripts\activate  # Windows

python main.py
```

后端服务将在`http://localhost:8000`上运行。

### 2. 启动前端服务

```bash
cd frontend
npm run serve
```

前端服务将在`http://localhost:8080`上运行。

## API文档

启动后端服务后，可以访问`http://localhost:8000/docs`查看API文档。

## 使用流程

1. 访问前端页面，点击"创建绘本"
2. 输入故事主题、类型、适合年龄段等信息，生成故事内容
3. 选择图片风格，生成图片描述
4. 选择图片比例和生成模型，生成插图
5. 选择语音情感，生成语音朗读
6. 设置视频参数，生成绘本视频
7. 预览并下载绘本视频

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本是否为3.8+
   - 确保所有依赖库已正确安装
   - 检查`.env`文件是否配置正确

2. **图片生成失败**
   - 确保DEEPINFRA_API_KEY配置正确
   - 检查网络连接是否正常

3. **语音生成失败**
   - 确保OPENAI_API_KEY配置正确
   - 检查网络连接是否正常

4. **视频生成失败**
   - 确保FFmpeg已正确安装
   - 检查生成的图片和音频文件是否存在

### 日志查看

后端日志位于`backend/logs`目录下，可以查看日志文件了解详细错误信息。

## 数据库

本项目使用SQLite数据库，数据库文件位于`backend/database/app.db`。

## 贡献指南

欢迎提交Pull Request或Issue来改进项目。

## 许可证

[MIT License](LICENSE)
