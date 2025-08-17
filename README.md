# AI文本转语音转换器

基于智谱AI CogTTS模型的高质量文本转语音工具，支持多种语音类型和音频格式的语音合成功能。

## 🌟 主要功能

### 语音合成支持
- **文本转语音**: 支持中文文本的高质量语音合成
- **多种语音**: 提供5种不同风格的语音选择
- **批量处理**: 支持多个文本的批量转换
- **实时合成**: 快速准确的语音生成

### 高级功能
- **多种语音**: 童童语音风格
- **格式支持**: 支持WAV音频格式输出
- **文本验证**: 自动检测文本长度和内容有效性
- **文件管理**: 自动保存和管理生成的音频文件

### MCP服务器支持
- **MCP工具集成**: 提供完整的MCP工具接口
- **批量转换**: 支持批量文本转语音处理
- **文件管理**: 音频文件信息查询和管理
- **API测试**: 内置API连接测试功能

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask requests pathlib uvicorn fastapi
```

### 2. 配置API密钥

设置智谱API密钥环境变量：

```bash
export ZHIPU_API_KEY=你的智谱API密钥
```

或在代码中直接配置：

```python
from zhipu_tts_client import ZhipuTTSClient
client = ZhipuTTSClient(api_key="你的智谱API密钥")
```

### 3. 启动MCP服务器

```bash
python main.py
```

选择启动模式：
- **交互模式**: 命令行交互界面
- **Web界面模式**: 提供友好的Web界面
- **MCP服务器模式**: 作为MCP服务器运行
- **运行测试**: 测试功能是否正常

### 4. MCP配置

在MCP客户端中添加以下配置：
```json
{
    "mcpServers": {
        "ai-text-to-speech": {
            "disabled": false,
            "timeout": 60,
            "type": "sse",
            "url": "http://127.0.0.1:8000/sse"
        }
    }
}
```

## 🎭 支持的语音类型

- **tongtong**: 童童 - 女声，温柔甜美
- **xiaoxiao**: 小小 - 女声，活泼可爱
- **xiaomo**: 小墨 - 男声，沉稳磁性
- **xiaobei**: 小贝 - 女声，知性优雅
- **xiaoxuan**: 小轩 - 男声，阳光帅气

## 📁 支持的音频格式

- **WAV**: 无损音质，适合高质量需求
- **MP3**: 压缩格式，文件较小

## 🛠️ MCP工具

项目提供以下MCP工具：

### 文本转语音工具
- `convert_text_to_speech`: 转换文本为语音
- `batch_text_to_speech`: 批量文本转语音
- `get_voice_types`: 获取可用语音类型
- `validate_text_input`: 验证文本输入
- `test_tts_api`: 测试API连接

### 文件管理工具
- `save_text_content`: 保存文本内容
- `list_generated_files`: 列出生成的文件
- `get_audio_file_info`: 获取音频文件信息
- `get_supported_options`: 获取支持的选项

## 📊 使用示例

### 基本文本转语音
```python
from zhipu_tts_client import ZhipuTTSClient

client = ZhipuTTSClient()
result = client.text_to_speech_file(
    text="你好，这是一个测试。",
    voice="tongtong",
    response_format="wav"
)
print(f"音频文件: {result['file_path']}")
```

### 选择不同语音类型
```python
result = client.text_to_speech_file(
    text="欢迎使用文本转语音功能。",
    voice="xiaobei",  # 知性优雅的女声
    response_format="mp3"
)
```

### 批量转换
```python
texts = [
    "这是第一段文本。",
    "这是第二段文本。",
    "这是第三段文本。"
]
result = client.batch_text_to_speech(
    texts=texts,
    voice="xiaomo",  # 沉稳磁性的男声
    response_format="wav"
)
print(f"成功: {result['successful']}, 失败: {result['failed']}")
```

### MCP工具使用示例
```python
# 使用MCP工具转换文本
result = use_mcp_tool(
    server_name="mcp-text-to-speech",
    tool_name="convert_text_to_speech",
    arguments={
        "text": "基于智谱AI CogTTS模型的高质量文本转语音工具",
        "voice": "tongtong",
        "response_format": "wav",
        "save_file": True
    }
)
```

## 🔍 测试功能

运行测试脚本验证功能：

```bash
python test_tts.py
```

测试包括：
- API连接测试
- 基本文本转语音功能
- 不同语音类型测试
- 不同音频格式测试
- 批量转换测试
- 文本验证测试
- 长文本转换测试

## 📝 项目结构

```
├── main.py                     # MCP服务器主文件
├── zhipu_tts_client.py         # 智谱文本转语音客户端
├── tts_server.py               # Web服务器
├── tts_interface.html          # Web界面
├── test_tts.py                 # 测试脚本
├── network_diagnostic.py       # 网络诊断工具
├── pyproject.toml              # 项目配置
├── uv.lock                     # 依赖锁定文件
├── docs/
│   └── tasks.md               # 任务进度
├── outputs/                   # 输出文件目录
│   ├── demo_output.wav        # 示例输出文件
│   └── tts_*.wav             # 生成的音频文件
└── README.md                  # 项目文档
```

## 🚨 注意事项

1. **API密钥**: 确保正确设置ZHIPU_API_KEY环境变量
2. **文本长度**: 单次转换文本建议不超过5000字符
3. **网络连接**: 需要稳定的网络连接访问智谱API
4. **存储空间**: 确保有足够的磁盘空间存储生成的音频文件
5. **编码问题**: 确保文本使用UTF-8编码

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   - 检查ZHIPU_API_KEY环境变量是否正确设置
   - 确认密钥有文本转语音API访问权限

2. **文本转换失败**
   - 检查文本长度是否超过限制
   - 确认文本内容是否有效
   - 检查语音类型参数是否正确

3. **网络连接问题**
   - 检查网络连接
   - 查看控制台错误信息
   - 尝试使用网络诊断工具

4. **依赖包缺失**
   ```bash
   pip install flask requests pathlib uvicorn fastapi
   ```

5. **编码问题**
   - 确保文本使用UTF-8编码
   - 检查系统环境变量设置

## 📈 更新日志

- v4.0.0: 改造为文本转语音转换器
  - 支持多种语音类型和风格
  - 新增批量文本转语音功能
  - 集成智谱CogTTS模型
  - 提供完整的MCP服务器功能
  - 支持WAV和MP3音频格式
  - 优化错误处理和编码支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License