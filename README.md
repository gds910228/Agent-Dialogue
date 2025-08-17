# AI Content Security System

基于智谱AI内容安全API的综合内容审核系统，提供MCP服务器功能和直接内容审核功能。

## 功能特性

- 🛡️ **内容安全审核**: 对文本内容进行安全性检查
- 📊 **批量审核**: 支持批量处理多个文本内容
- 🔍 **详细分析**: 提供风险等级、风险类型等详细信息
- 💾 **结果保存**: 支持将审核结果保存到文件
- 🔧 **MCP服务器**: 提供Model Context Protocol服务器功能
- 🖥️ **交互模式**: 支持命令行交互式操作

## 安装要求

- Python 3.8+
- 智谱AI API密钥

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板：
```bash
cp config.json.example config.json
```

2. 编辑 `config.json` 文件，填入你的智谱AI API密钥：
```json
{
  "zhipu_api_key": "your_zhipu_api_key_here"
}
```

或者设置环境变量：
```bash
export ZHIPU_API_KEY="your_zhipu_api_key_here"
```

## 使用方法

### 1. 交互模式（推荐）

```bash
python main.py
```

支持的功能：
- 内容安全审核
- 批量内容审核  
- 内容安全检查
- 测试API连接
- 保存审核结果到文件
- 从文件加载审核结果
- 启动MCP服务器

### 2. MCP服务器模式

```bash
python main.py --mcp
```

## MCP配置
{
  "mcpServers":{
    "mcp-content-security": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}

### 3. 测试模式

```bash
python main.py --test
```

## API接口

### 内容安全审核

```python
from zhipu_moderation_client import ZhipuModerationClient

client = ZhipuModerationClient(api_key="your_api_key")

# 单个文本审核
result = client.moderate_content("需要审核的文本内容")
formatted_result = client.format_moderation_result(result)
risk_summary = client.get_risk_summary(result)
is_safe = client.is_content_safe(result)

# 批量审核
texts = ["文本1", "文本2", "文本3"]
batch_results = client.batch_moderate_content(texts)
```

### MCP工具

系统提供以下MCP工具：

- `moderate_content`: 执行内容安全审核
- `batch_moderate_content`: 批量执行内容安全审核
- `test_moderation_api`: 测试内容安全API连接和功能
- `save_moderation_results_to_file`: 将审核结果保存到文件
- `load_moderation_results_from_file`: 从文件加载审核结果

## 智谱AI内容安全API

本系统对接智谱AI的内容安全API：
- **端点**: `https://open.bigmodel.cn/api/paas/v4/moderations`
- **模型**: `moderation`
- **支持**: 文本内容安全审核

### API请求格式

```bash
curl --request POST \
  --url https://open.bigmodel.cn/api/paas/v4/moderations \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "moderation",
  "input": "审核内容安全样例字符串。"
}'
```

### API响应格式

```json
{
  "id": "<string>",
  "created": 123,
  "request_id": "<string>",
  "result_list": [
    {
      "content_type": "<string>",
      "risk_level": "<string>",
      "risk_type": [
        "<string>"
      ]
    }
  ],
  "usage": {
    "moderation_text": {
      "call_count": 123
    }
  }
}
```

## 项目结构

```
Content-Security/
├── main.py                      # 主程序入口
├── zhipu_moderation_client.py   # 智谱内容安全客户端
├── config.json                  # 配置文件
├── config.json.example          # 配置文件模板
├── requirements.txt             # 依赖包列表
├── README.md                    # 项目说明
├── outputs/                     # 输出文件目录
└── docs/                        # 文档目录
```

## 改造说明

本项目从智谱网络搜索功能改造为内容安全功能：

### 主要变更

1. **客户端改造**: `ZhipuWebSearchClient` → `ZhipuModerationClient`
2. **API端点**: `/web_search` → `/moderations`
3. **功能重构**: 网络搜索 → 内容安全审核
4. **配置更新**: 搜索相关配置 → 内容安全配置
5. **工具函数**: 搜索工具 → 审核工具

### 保留功能

- MCP服务器架构
- 交互式命令行界面
- 文件保存和加载功能
- 错误处理和验证机制
- 配置管理系统

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。