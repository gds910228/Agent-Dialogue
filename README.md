# AI Text Embedding Generator - 智谱GLM文本嵌入生成器

基于智谱AI GLM嵌入模型的高质量文本嵌入系统，将文本转换为高维向量表示，用于语义相似性和搜索。

## ✨ 主要特性

- 🔤 **文本嵌入生成**: 基于智谱GLM嵌入模型
- 🔧 **多模型支持**: embedding-3、embedding-2
- 🔍 **相似度计算**: 计算文本间的语义相似度
- 🔎 **相似文本搜索**: 在候选文本中找到最相似的内容
- 🌐 **Web界面**: 现代化的响应式Web界面
- 🔌 **MCP服务器**: 支持Model Context Protocol
- 📦 **批量处理**: 支持批量文本嵌入
- 💾 **数据导出**: 支持嵌入向量的保存和加载

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 智谱AI API密钥

### 安装依赖

```bash
# 使用uv安装依赖（推荐）
uv sync

# 或使用pip安装
pip install -r requirements.txt
```

### 配置API密钥

创建 `config.json` 文件：

```json
{
  "api_keys": {
    "zhipu": "your_zhipu_api_key_here"
  }
}
```

或设置环境变量：

```bash
export ZHIPU_API_KEY="your_zhipu_api_key_here"
```

### MCP配置
```json
{
  "mcpServers":{
    "mcp-text-embedding": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

### 运行方式

#### 1. Web界面模式（推荐）

```bash
python embedding_server.py
```

然后访问 http://localhost:5000

#### 2. 交互式命令行模式

```bash
python main.py
```

#### 3. MCP服务器模式

```bash
python main.py --mcp
```

## 🎯 支持的模型

| 模型 | 描述 | 特点 |
|------|------|------|
| embedding-3 | 最新的嵌入模型 | 高质量文本向量表示，推荐使用 |
| embedding-2 | 较早版本的嵌入模型 | 兼容性更好，稳定性高 |

## 🔤 主要功能

- **单文本嵌入** - 将单个文本转换为高维向量
- **批量文本嵌入** - 同时处理多个文本
- **相似度计算** - 计算两个文本的语义相似度
- **相似文本搜索** - 在候选文本中找到最相似的内容

## 🎨 使用示例

### Python API调用

```python
from zhipu_image_client import ZhipuImageClient

# 初始化客户端
client = ZhipuImageClient()

# 生成图像
result = client.generate_and_save_image(
    prompt="一只可爱的柯基犬在樱花树下奔跑",
    model="cogview-4",
    size="1024x1024",
    quality="standard"
)

if result["success"]:
    print(f"图像已保存到: {result['file_path']}")
    print(f"图像URL: {result['image_url']}")
else:
    print(f"生成失败: {result['error']}")
```

### 批量生成

```python
# 批量生成多张图像
prompts = [
    "一只橘猫在阳光下打盹",
    "未来科技城市夜景",
    "水彩画风格的山水画"
]

result = client.batch_generate_images(
    prompts=prompts,
    model="cogview-4",
    size="1024x1024"
)

print(f"成功生成: {result['successful']}/{result['total']} 张图像")
```

### MCP工具调用

```python
# 生成图像
generate_image_from_prompt(
    prompt="一朵红色的玫瑰花",
    model="cogview-4",
    size="1024x1024",
    quality="hd",
    save_file=True
)

# 批量生成
batch_generate_images(
    prompts=["猫咪", "狗狗", "兔子"],
    model="cogview-3-flash",
    size="512x512"
)

# 获取支持的选项
get_supported_options()

# 测试API连接
test_image_api("测试图像")
```

## 🌐 Web界面功能

- **智能提示词输入**: 支持多行文本输入和示例提示词
- **参数配置**: 可视化选择模型、尺寸和质量
- **实时预览**: 生成后立即显示图像
- **历史记录**: 保存最近的生成历史
- **下载功能**: 一键下载生成的图像
- **API状态监控**: 实时显示API连接状态

## 📁 项目结构

```
AI-Image-Generator/
├── main.py                 # 主程序入口
├── zhipu_image_client.py   # 智谱图像生成客户端
├── image_server.py         # Web服务器
├── image_interface.html    # Web界面
├── network_diagnostic.py   # 网络诊断工具
├── config.json            # 配置文件
├── outputs/               # 输出目录
└── docs/                  # 文档目录
```

## 🔧 配置选项

### API配置

```json
{
  "api_keys": {
    "zhipu": "your_api_key"
  },
  "api_settings": {
    "timeout": 120,
    "max_retries": 3,
    "base_url": "https://open.bigmodel.cn/api/paas/v4/images/generations"
  }
}
```

### 生成参数

- **prompt**: 图像描述提示词（必需）
- **model**: 生成模型（默认: cogview-4）
- **size**: 图像尺寸（默认: 1024x1024）
- **quality**: 图像质量（默认: standard）

## 🛠️ 开发指南

### 添加新模型

1. 在 `zhipu_image_client.py` 中更新 `image_models` 字典
2. 确保API支持新模型
3. 更新Web界面的模型选项

### 自定义输出格式

```python
# 修改保存格式
def save_custom_format(self, image_data, filename, format="png"):
    # 自定义保存逻辑
    pass
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   - 检查config.json中的API密钥
   - 确认环境变量ZHIPU_API_KEY设置正确

2. **网络连接问题**
   - 运行网络诊断: `python network_diagnostic.py`
   - 检查防火墙和代理设置

3. **图像生成失败**
   - 检查提示词是否包含敏感内容
   - 尝试使用不同的模型或参数

4. **Web界面无法访问**
   - 确认端口5000未被占用
   - 检查防火墙设置

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py
```

## 📊 性能优化

- 使用 `cogview-3-flash` 模型获得更快的生成速度
- 批量生成时适当增加延迟避免API限制
- 选择合适的图像尺寸平衡质量和速度

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- 智谱AI提供的CogView-4模型
- Flask和相关Web框架
- 所有贡献者和用户

## 📞 支持

如有问题或建议，请：

1. 查看文档和FAQ
2. 提交Issue
3. 联系开发团队

---

**享受AI图像生成的乐趣！** 🎨✨