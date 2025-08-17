# 项目结构说明

## 核心文件

### 主要入口
- **main.py** - 主要入口文件，支持交互式语音转录和MCP服务器模式
- **zhipu_speech_client.py** - 智谱语音转文本客户端，处理音频转录功能

### Web界面
- **speech_server.py** - Web服务器，提供RESTful API
- **speech_interface.html** - Web用户界面，支持拖拽上传和语音转文本

### 工具和测试
- **test_speech.py** - 功能测试脚本

### 配置和文档
- **config.json** - 配置文件，包含API密钥等设置
- **README.md** - 项目说明文档
- **docs/tasks.md** - 项目任务进度管理

### 目录结构
```
AI-Speech-To-Text/
├── main.py                     # 主入口文件
├── zhipu_speech_client.py      # 语音转文本客户端
├── speech_server.py            # Web服务器
├── speech_interface.html       # Web界面
├── test_speech.py              # 测试脚本
├── config.json                 # 配置文件
├── README.md                   # 项目文档
├── PROJECT_STRUCTURE.md        # 项目结构说明
├── pyproject.toml              # Python项目配置
├── uv.lock                     # 依赖锁定文件
├── docs/
│   └── tasks.md               # 任务管理
└── uploads/                   # 文件上传目录
```

## 功能模块

### 1. 语音转文本
- 支持多种音频和视频格式
- 基于智谱Whisper模型
- 支持批量处理和时间戳

### 2. 交互式界面
- 命令行交互模式
- Web拖拽上传界面
- 多种启动选项

### 3. MCP服务器
- 提供MCP工具接口
- 支持外部调用
- 语音转文本专用工具

## 使用方式

### 直接运行
```bash
python main.py
```

### 指定模式
```bash
python main.py --mcp    # MCP服务器模式
python main.py --web    # Web服务器模式
python main.py --test   # 测试模式
```

### Web服务器
```bash
python speech_server.py
```

## 已清理的文件

以下文件已从项目中移除或重构：
- multimodal_server.py (保留但不再使用)
- multimodal_interface.html (保留但不再使用)
- start_multimodal.py (保留但不再使用)
- test_multimodal.py (保留但不再使用)
- zhipu_vision_client.py (保留但不再使用)

项目现在专注于语音转文本功能，结构更加清晰简洁。

## 核心技术

### 智谱AI Whisper模型
- 高精度语音识别
- 多语言支持
- 自动语言检测
- 时间戳生成

### Web技术栈
- Flask Web框架
- HTML5 + CSS3 + JavaScript
- Tailwind CSS样式框架
- Font Awesome图标库

### MCP集成
- FastMCP框架
- SSE传输协议
- 工具化API接口

## 配置要求

### 系统要求
- Python 3.8+
- 网络连接（访问智谱API）
- 磁盘空间（存储上传文件）

### 依赖包
- flask: Web服务器
- requests: HTTP请求
- pathlib: 文件路径处理
- mcp.server.fastmcp: MCP服务器框架

### API配置
- 智谱AI API密钥
- 语音转文本API访问权限

## 扩展性

项目设计支持以下扩展：
1. 添加更多语音模型
2. 支持实时语音流转录
3. 集成更多音频处理功能
4. 添加语音质量评估
5. 支持多用户并发处理