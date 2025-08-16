# AI多模态内容分析器

基于智谱清言视觉模型的多模态内容分析工具，支持文本、图片、视频、文档等多种内容类型的智能分析。

## 🌟 主要功能

### 多模态内容支持
- **文本分析**: 智能文本理解和问答
- **图片分析**: 图像内容描述、物体识别、场景理解
- **视频分析**: 视频内容理解和总结
- **文档分析**: PDF、Word、文本文档的内容提取和总结
- **URL分析**: 网络资源的智能分析

### 智能分析能力
- **内容描述**: 详细描述图片、视频内容
- **问答交互**: 针对上传内容进行智能问答
- **内容比较**: 多个文件或内容的对比分析
- **信息提取**: 从文档中提取关键信息

### 用户友好界面
- **拖拽上传**: 支持文件拖拽上传
- **实时预览**: 上传文件的即时预览
- **多格式支持**: 支持常见的图片、视频、文档格式
- **历史记录**: 查看之前上传和分析的文件

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask requests pathlib
```

### 2. 配置API密钥

在 `config.json` 中设置智谱API密钥：

```json
{
    "api_keys": {
        "zhipu": "你的智谱API密钥"
    }
}
```

### 3. 启动服务

```bash
python start_multimodal.py
```

选择启动模式：
- **Web界面模式**: 提供友好的Web界面
- **MCP服务器模式**: 作为MCP服务器运行
- **运行测试**: 测试功能是否正常

### 4. 访问界面

打开浏览器访问: http://localhost:5000

## 📁 支持的文件格式

### 图片格式
- JPG/JPEG
- PNG
- GIF
- BMP
- WebP

### 视频格式
- MP4
- AVI
- MOV
- MKV
- WebM

### 文档格式
- PDF
- DOC/DOCX
- TXT
- Markdown

## 🔧 API接口

### 文件上传
```
POST /api/upload
Content-Type: application/json

{
    "file_content": "base64编码的文件内容",
    "filename": "文件名",
    "encoding": "base64"
}
```

### 多模态分析
```
POST /api/analyze
Content-Type: application/json

{
    "text": "文本内容或问题",
    "file_paths": ["文件路径列表"],
    "urls": ["URL列表"],
    "model": "glm-4v"
}
```

### 获取文件列表
```
GET /api/files
```

### 获取支持格式
```
GET /api/formats
```

## 🛠️ MCP工具

项目同时提供MCP服务器功能，包含以下工具：

### 多模态分析工具
- `analyze_multimodal_content`: 分析多模态内容
- `describe_image`: 描述图片内容
- `analyze_video_content`: 分析视频内容
- `extract_document_content`: 提取文档内容
- `compare_multiple_contents`: 比较多个内容

### 文件管理工具
- `upload_file`: 上传文件
- `list_uploaded_files`: 列出上传的文件
- `get_supported_formats`: 获取支持的格式

### 视频生成工具（向后兼容）
- `generate_video`: 生成视频
- `submit_video_task`: 提交视频任务
- `get_video_task_result`: 获取视频结果
- `get_video_history`: 获取视频历史

## MCP配置
{
    "mcpServers": {
    "mcp-aicontent-analyzer": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
    }
}

## 📊 使用示例

### 图片分析
```python
from zhipu_vision_client import ZhipuVisionClient

client = ZhipuVisionClient()
result = client.describe_image("image.jpg", "请描述这张图片的内容")
print(result['content'])
```

### 视频分析
```python
result = client.analyze_video("video.mp4", "这个视频讲了什么？")
print(result['content'])
```

### 文档分析
```python
result = client.extract_document_info("document.pdf", "请总结文档的主要内容")
print(result['content'])
```

### 多内容比较
```python
result = client.compare_contents(
    ["image1.jpg", "image2.jpg"], 
    "请比较这两张图片的异同"
)
print(result['content'])
```

## 🔍 测试功能

运行测试脚本验证功能：

```bash
python test_multimodal.py
```

测试包括：
- 纯文本分析
- 文件格式支持检查
- 配置验证
- 文件分析（如果有示例文件）
- URL分析
- 文件编码功能

## 📝 项目结构

```
├── main.py                     # MCP服务器主文件
├── zhipu_vision_client.py      # 智谱视觉模型客户端
├── multimodal_server.py        # Web服务器
├── multimodal_interface.html   # Web界面
├── start_multimodal.py         # 启动脚本
├── test_multimodal.py          # 测试脚本
├── config.json                 # 配置文件
├── docs/
│   └── tasks.md               # 任务进度
├── uploads/                   # 上传文件目录
└── generated_videos/          # 生成视频目录
```

## 🚨 注意事项

1. **API密钥**: 确保在config.json中正确配置智谱API密钥
2. **文件大小**: 单个文件最大支持100MB
3. **网络连接**: 需要稳定的网络连接访问智谱API
4. **存储空间**: 确保有足够的磁盘空间存储上传的文件

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   - 检查config.json中的密钥是否正确
   - 确认密钥有视觉模型访问权限

2. **文件上传失败**
   - 检查文件大小是否超过限制
   - 确认文件格式是否支持

3. **分析失败**
   - 检查网络连接
   - 查看控制台错误信息

4. **依赖包缺失**
   ```bash
   pip install flask requests pathlib
   ```

## 📈 更新日志

- v2.0.0: 重构为多模态内容分析器
  - 支持图片、视频、文档分析
  - 新增Web界面
  - 支持文件拖拽上传
  - 集成智谱视觉模型
- v1.x.x: 原视频生成功能（向后兼容）

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License