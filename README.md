# AI语音转文本转换器

基于智谱AI Whisper模型的高精度语音识别工具，支持多种音频和视频格式的语音转文本功能。

## 🌟 主要功能

### 语音识别支持
- **音频转录**: 支持多种音频格式的语音转文本
- **视频转录**: 从视频文件中提取音频并转录
- **批量处理**: 支持多个文件的批量转录
- **实时转录**: 快速准确的语音识别

### 高级功能
- **时间戳**: 提供详细的时间戳信息
- **字幕生成**: 自动生成SRT、VTT字幕文件
- **多语言支持**: 自动检测或指定语言
- **提示词优化**: 使用提示词提高转录准确性

### 用户友好界面
- **拖拽上传**: 支持音频文件拖拽上传
- **实时预览**: 音频播放和预览功能
- **多格式支持**: 支持常见的音频、视频格式
- **结果管理**: 转录结果的复制、下载和管理

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

## MCP配置
{
    "mcpServers":{
    "mcp-speech-to-text": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
    }
}

### 3. 启动服务

```bash
python main.py
```

选择启动模式：
- **交互模式**: 命令行交互界面
- **Web界面模式**: 提供友好的Web界面
- **MCP服务器模式**: 作为MCP服务器运行
- **运行测试**: 测试功能是否正常

### 4. 访问界面

打开浏览器访问: http://localhost:5000

## 📁 支持的文件格式

### 音频格式
- MP3
- WAV


## 🔧 API接口

### 文件上传
```
POST /api/upload
Content-Type: application/json

{
    "file_content": "base64编码的音频内容",
    "filename": "文件名",
    "encoding": "base64"
}
```

### 语音转文本
```
POST /api/transcribe
Content-Type: application/json

{
    "audio_path": "音频文件路径",
    "model": "whisper-1",
    "language": "zh",
    "prompt": "提示词",
    "response_format": "json"
}
```

### 带时间戳转录
```
POST /api/transcribe/timestamps
Content-Type: application/json

{
    "audio_path": "音频文件路径",
    "model": "whisper-1"
}
```

### 生成SRT字幕
```
POST /api/transcribe/srt
Content-Type: application/json

{
    "audio_path": "音频文件路径",
    "model": "whisper-1"
}
```

### 批量转录
```
POST /api/batch_transcribe
Content-Type: application/json

{
    "audio_files": ["文件路径列表"],
    "model": "whisper-1"
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

### 获取音频信息
```
GET /api/audio_info/<filename>
```

### 测试API连接
```
GET /api/test
```

## 🛠️ MCP工具

项目同时提供MCP服务器功能，包含以下工具：

### 语音转文本工具
- `transcribe_audio_file`: 转录音频文件
- `transcribe_with_timestamps`: 带时间戳转录
- `transcribe_to_srt`: 生成SRT字幕
- `batch_transcribe_audio`: 批量转录
- `get_audio_info`: 获取音频信息
- `test_speech_api`: 测试API连接

### 文件管理工具
- `upload_file`: 上传音频文件
- `list_uploaded_files`: 列出上传的文件
- `get_supported_formats`: 获取支持的格式

## MCP配置
```json
{
    "mcpServers": {
        "ai-speech-to-text": {
            "disabled": false,
            "timeout": 60,
            "type": "sse",
            "url": "http://127.0.0.1:8000/sse"
        }
    }
}
```

## 📊 使用示例

### 基本语音转录
```python
from zhipu_speech_client import ZhipuSpeechClient

client = ZhipuSpeechClient()
result = client.transcribe_audio("audio.mp3")
print(result['text'])
```

### 带时间戳转录
```python
result = client.transcribe_with_timestamps("audio.mp3")
print(result['text'])
for segment in result['segments']:
    print(f"{segment['start']:.2f}s - {segment['end']:.2f}s: {segment['text']}")
```

### 生成SRT字幕
```python
result = client.transcribe_to_srt("audio.mp3")
with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(result['srt_content'])
```

### 批量转录
```python
audio_files = ["audio1.mp3", "audio2.wav", "audio3.m4a"]
result = client.batch_transcribe(audio_files)
print(f"成功: {result['successful']}, 失败: {result['failed']}")
```

## 🔍 测试功能

运行测试脚本验证功能：

```bash
python test_speech.py
```

测试包括：
- API连接测试
- 支持格式检查
- 文件验证功能
- 实际转录测试（如果有音频文件）
- 配置文件检查

## 📝 项目结构

```
├── main.py                     # MCP服务器主文件
├── zhipu_speech_client.py      # 智谱语音转文本客户端
├── speech_server.py            # Web服务器
├── speech_interface.html       # Web界面
├── test_speech.py              # 测试脚本
├── config.json                 # 配置文件
├── docs/
│   └── tasks.md               # 任务进度
├── uploads/                   # 上传文件目录
└── README.md                  # 项目文档
```

## 🚨 注意事项

1. **API密钥**: 确保在config.json中正确配置智谱API密钥
2. **文件大小**: 单个文件最大支持25MB
3. **网络连接**: 需要稳定的网络连接访问智谱API
4. **存储空间**: 确保有足够的磁盘空间存储上传的文件

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   - 检查config.json中的密钥是否正确
   - 确认密钥有语音转文本API访问权限

2. **文件上传失败**
   - 检查文件大小是否超过25MB限制
   - 确认文件格式是否支持

3. **转录失败**
   - 检查网络连接
   - 查看控制台错误信息
   - 确认音频文件质量

4. **依赖包缺失**
   ```bash
   pip install flask requests pathlib
   ```

## 📈 更新日志

- v3.0.0: 重构为语音转文本转换器
  - 支持多种音频、视频格式转录
  - 新增时间戳和字幕生成功能
  - 集成智谱Whisper模型
  - 提供Web界面和MCP服务器
- v2.x.x: 多模态内容分析器（已废弃）
- v1.x.x: 视频生成功能（已废弃）

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License