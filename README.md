# 智谱AI智能体对话系统 (Zhipu AI Agent Dialogue System)

一个综合的智能体对话系统，支持智谱AI的智能体对话API和内容安全API。提供MCP服务器功能和直接对话功能。

## 功能特性

- 🤖 **智能体对话**: 使用智谱AI智能体进行文本和文件对话
- 🛡️ **内容安全审核**: 高级文本内容安全分析（保留原功能）
- 🔧 **MCP服务器**: 模型上下文协议服务器，可与AI助手集成
- 📊 **批量处理**: 支持批量内容审核
- 🖥️ **交互模式**: 命令行界面直接使用
- 💾 **文件操作**: 保存和加载对话及审核结果
- 🔍 **网络诊断**: 内置连接测试和故障排除

## 安装要求

- Python 3.8+
- 智谱AI API密钥

## 安装

1. 克隆仓库:
```bash
git clone <repository-url>
cd Agent-Dialogue
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 配置API密钥:
```bash
# 复制示例配置
cp config.json.example config.json

# 编辑config.json并添加您的智谱API密钥
```

## 配置

基于 `config.json.example` 创建 `config.json` 文件:

```json
{
  "zhipu_api_key": "your_zhipu_api_key_here",
  "agent_dialogue": {
    "base_url": "https://open.bigmodel.cn",
    "agents_endpoint": "/api/v1/agents",
    "timeout": 30,
    "max_retries": 3,
    "default_agent_id": "doc_translation_agent"
  },
  "content_moderation": {
    "base_url": "https://open.bigmodel.cn",
    "moderation_endpoint": "/api/paas/v4/moderations",
    "timeout": 30,
    "max_retries": 3,
    "model": "moderation"
  },
  "api_settings": {
    "timeout": 120,
    "max_retries": 3,
    "base_url": "https://open.bigmodel.cn"
  }
}
```

或者设置环境变量：
```bash
export ZHIPU_API_KEY="your_zhipu_api_key_here"
```

## 使用方法

### 交互模式

运行系统交互模式:

```bash
python main.py
```

这将显示包含以下选项的菜单:
1. 智能体文本对话
2. 智能体文件对话
3. 内容安全审核
4. 批量内容审核
5. 测试API连接
6. 保存对话结果到文件
7. 保存审核结果到文件
8. 从文件加载结果
9. 启动MCP服务器

### MCP服务器模式

作为MCP服务器启动:

```bash
python main.py --mcp
```

### API测试

测试API连接:

```bash
python main.py --test
```

## MCP配置

在您的MCP客户端中添加以下配置：

```json
{
  "mcpServers": {
    "zhipu-agent-dialogue": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

## MCP工具

作为MCP服务器运行时，提供以下工具:

### 智能体对话工具
- `chat_with_agent(agent_id, user_message, conversation_id)`: 与智能体进行文本对话
- `chat_with_agent_file(agent_id, file_id, conversation_id)`: 使用文件与智能体对话

### 内容安全工具
- `moderate_content(input_text)`: 执行内容安全审核
- `batch_moderate_content(input_texts)`: 批量内容审核

### 测试和文件工具
- `test_agent_api(agent_id, test_text)`: 测试API连接和功能
- `save_agent_dialogue_to_file(...)`: 保存智能体对话结果到文件
- `save_moderation_results_to_file(...)`: 保存审核结果到文件
- `load_results_from_file(filename)`: 从文件加载结果

## API参考

### 智能体对话API

系统使用智谱AI的智能体对话API进行:
- 文本消息对话
- 文件处理对话
- 多轮对话支持
- 对话状态管理

#### 智能体对话请求格式

```bash
curl --request POST \
  --url https://open.bigmodel.cn/api/v1/agents \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "agent_id": "doc_translation_agent",
  "messages": [
    {
      "role": "user",
      "content": "你好，请介绍一下你的功能"
    }
  ]
}'
```

#### 智能体文件对话请求格式

```bash
curl --request POST \
  --url https://open.bigmodel.cn/api/v1/agents \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "agent_id": "doc_translation_agent",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "file_id",
          "file_id": "agent_1750681215_9b92722d788f4b32bab28cc333293584"
        }
      ]
    }
  ]
}'
```

#### 智能体对话响应格式

```json
{
  "id": "<string>",
  "agent_id": "<string>",
  "conversation_id": "<string>",
  "async_id": "<string>",
  "choices": [
    {
      "index": 123,
      "messages": [
        {
          "role": "assistant",
          "content": "<string>"
        }
      ],
      "finish_reason": "<string>"
    }
  ],
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 123,
    "total_tokens": 123
  }
}
```

### 内容安全API

系统使用智谱AI的内容安全API分析文本:
- 有害内容检测
- 风险等级评估
- 内容类型分类
- 详细安全分析

#### 内容安全请求格式

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

#### 内容安全响应格式

```json
{
  "success": true,
  "input_text": "您的输入文本",
  "is_safe": true,
  "risk_summary": {
    "is_safe": true,
    "risk_count": 0,
    "risk_types": [],
    "highest_risk_level": "low"
  },
  "detailed_result": {
    "id": "...",
    "results": [...]
  }
}
```

## 开发

### 运行测试

```bash
# 测试智能体对话功能
python test_agent_dialogue.py

# 测试内容安全功能
python test_moderation.py
```

### 项目结构

```
Agent-Dialogue/
├── main.py                    # 主应用程序入口
├── zhipu_agent_client.py      # 智谱AI智能体客户端实现
├── zhipu_moderation_client.py # 智谱AI内容安全客户端（保留）
├── network_diagnostic.py      # 网络诊断工具
├── config.json.example        # 配置模板
├── requirements.txt           # Python依赖
├── test_agent_dialogue.py     # 智能体对话测试套件
├── test_moderation.py         # 内容安全测试套件
└── outputs/                   # 输出文件目录
```

## 代码示例

### 智能体对话

```python
from zhipu_agent_client import ZhipuAgentClient

client = ZhipuAgentClient(api_key="your_api_key")

# 文本对话
result = client.chat_with_text("doc_translation_agent", "你好，请介绍一下你的功能")
assistant_message = client.extract_assistant_message(result)
print(f"智能体回复: {assistant_message}")

# 文件对话
result = client.chat_with_file("doc_translation_agent", "file_id_here")
assistant_message = client.extract_assistant_message(result)
print(f"智能体回复: {assistant_message}")
```

### 内容安全审核

```python
from zhipu_agent_client import ZhipuAgentClient

client = ZhipuAgentClient(api_key="your_api_key")

# 单个文本审核
result = client.moderate_content("需要审核的文本内容")
formatted_result = client.format_moderation_result(result)
risk_summary = client.get_risk_summary(result)
is_safe = client.is_content_safe(result)

print(f"内容安全: {is_safe}")
print(f"风险摘要: {risk_summary}")
```

## 更新日志

### v2.0.0 - 智能体对话支持
- ✅ 添加智谱AI智能体对话API支持
- ✅ 支持文本消息和文件对话
- ✅ 保留原有内容安全功能
- ✅ 更新配置文件格式
- ✅ 新增智能体对话测试套件
- ✅ 更新交互式界面
- ✅ 统一客户端架构

### v1.0.0 - 内容安全系统
- 智谱AI内容安全API集成
- MCP服务器支持
- 批量处理功能
- 交互式命令行界面

## 改造说明

本项目从智谱内容安全功能改造为智能体对话系统：

### 主要变更

1. **客户端升级**: `ZhipuModerationClient` → `ZhipuAgentClient`
2. **API端点**: 添加 `/api/v1/agents` 智能体对话端点
3. **功能扩展**: 内容安全 + 智能体对话
4. **配置更新**: 添加智能体对话相关配置
5. **工具函数**: 新增智能体对话工具

### 保留功能

- MCP服务器架构
- 内容安全审核功能
- 交互式命令行界面
- 文件保存和加载功能
- 错误处理和验证机制
- 配置管理系统

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 支持

如有问题和疑问，请在仓库中创建issue。