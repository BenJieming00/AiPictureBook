# AI绘本后端

## 系统要求

- Python 3.10+
- FFmpeg（用于视频和音频处理）
- 数据库（根据您的项目需要：MySQL/PostgreSQL/SQLite）

## 详细安装指南

### 1. 克隆仓库
```bash
git clone <repository-url>
cd backend
```

### 2. 创建并激活虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 4. FFmpeg安装指南

FFmpeg是处理音视频的必要组件，请根据您的操作系统按照以下方式安装：

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt-get install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel
```

**Windows:**
1. 从[FFmpeg官网](https://ffmpeg.org/download.html)下载Windows版本
2. 解压到指定目录（如 `C:\ffmpeg`）
3. 添加到系统环境变量PATH:
   - 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
   - 在"系统变量"中找到Path，编辑并添加ffmpeg的bin目录（如`C:\ffmpeg\bin`）
4. 重启命令提示符或PowerShell验证安装：
```bash
ffmpeg -version
```

### 5. 数据库初始化

根据项目使用的数据库类型，执行相应的初始化步骤：

**SQLite (默认):**
```bash
python init_db.py
```

**MySQL/PostgreSQL:**
1. 确保数据库服务已启动
2. 创建数据库
```bash
# MySQL
mysql -u root -p
CREATE DATABASE ai_picturebook;
```
3. 初始化表结构
```bash
python init_db.py
```

## 环境变量配置

在项目根目录创建`.env`文件，设置以下必要变量：

```
OPENAI_API_KEY=your_openai_api_key
```

## 运行

```bash
uvicorn main:app --reload
```

## 故障排除

### 视频没有声音
- 确保已正确安装FFmpeg
- 检查音频文件是否有效
- 检查日志中是否有FFmpeg相关错误 