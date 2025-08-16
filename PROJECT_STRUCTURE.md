# 项目结构说明

## 核心文件

### 主要入口
- **main.py** - 主要入口文件，支持交互式视觉推理和MCP服务器模式
- **zhipu_vision_client.py** - 智谱视觉模型客户端，处理多模态内容分析

### Web界面
- **multimodal_server.py** - Web服务器，提供RESTful API
- **multimodal_interface.html** - Web用户界面，支持拖拽上传和多模态分析

### 工具和测试
- **start_multimodal.py** - 启动脚本，提供多种启动选项
- **test_multimodal.py** - 功能测试脚本

### 配置和文档
- **config.json** - 配置文件，包含API密钥等设置
- **README.md** - 项目说明文档
- **docs/tasks.md** - 项目任务进度管理

### 目录结构
```
mcp13/
├── main.py                     # 主入口文件
├── zhipu_vision_client.py      # 视觉模型客户端
├── multimodal_server.py        # Web服务器
├── multimodal_interface.html   # Web界面
├── start_multimodal.py         # 启动脚本
├── test_multimodal.py          # 测试脚本
├── config.json                 # 配置文件
├── README.md                   # 项目文档
├── pyproject.toml              # Python项目配置
├── uv.lock                     # 依赖锁定文件
├── docs/
│   └── tasks.md               # 任务管理
└── uploads/                   # 文件上传目录
```

## 功能模块

### 1. 多模态内容分析
- 支持文本、图片、视频、文档分析
- 基于智谱GLM-4V视觉模型
- 支持内容比较和问答

### 2. 交互式界面
- 命令行交互模式
- Web拖拽上传界面
- 多种启动选项

### 3. MCP服务器
- 提供MCP工具接口
- 支持外部调用
- 向后兼容

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

### 使用启动脚本
```bash
python start_multimodal.py
```

## 已清理的文件

以下文件已从项目中移除：
- main_backup.py
- main_old.py
- create_valid_video.py
- example_usage.py
- index.html
- script.js
- simple_web_server.py
- video_status.html
- web_server.py
- ZHIPU_VIDEO_API.md
- zhipu_client.py
- generated_videos/ (目录)

项目现在专注于多模态内容分析功能，结构更加清晰简洁。