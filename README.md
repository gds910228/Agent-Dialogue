# 智谱AI文本分词器

一个基于智谱AI API的文本分词工具，用于计算文本的token数量。适用于文本长度评估、模型输入预估、对话上下文截断、费用计算等场景。

## 功能特点

- 支持智谱AI的多种模型分词（GLM-4-Plus、GLM-4、GLM-3-Turbo）
- 支持多条消息的token计算
- 提供Web界面和API接口
- 支持MCP服务器模式
- 支持交互式命令行模式

## 安装

### 环境要求

- Python 3.8+
- 智谱AI API密钥

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/Text-Tokenizer.git
cd Text-Tokenizer
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置API密钥

复制配置文件模板并填入你的API密钥：

```bash
cp config.json.example config.json
```

然后编辑 `config.json` 文件，填入你的智谱AI API密钥。

## 使用方法

### 命令行交互模式

运行以下命令启动交互式命令行模式：

```bash
python main.py
```

在交互式模式中，你可以：
- 计算文本的token数量
- 查看支持的模型
- 测试API连接
- 保存和加载分词结果

### Web界面模式

运行以下命令启动Web服务器：

```bash
python tokenizer_server.py
```

然后在浏览器中访问 `http://localhost:5000` 即可使用Web界面。

### MCP服务器模式

运行以下命令启动MCP服务器：

```bash
python main.py --mcp
```

## API接口

### 分词接口

```
POST /api/tokenize
```

请求体：

```json
{
  "model": "glm-4-plus",
  "messages": [
    {
      "role": "user",
      "content": "What opportunities and challenges will the Chinese large model industry face in 2025?"
    }
  ]
}
```

响应：

```json
{
  "success": true,
  "model": "glm-4-plus",
  "usage": {
    "prompt_tokens": 123
  },
  "request_id": "20241120141244890ab4ee4af84acf",
  "created": 1727156815
}
```

### 获取Token数量接口

```
POST /api/token-count
```

请求体与分词接口相同，响应略有不同：

```json
{
  "success": true,
  "model": "glm-4-plus",
  "token_count": 123
}
```

### 获取支持的模型接口

```
GET /api/models
```

响应：

```json
{
  "success": true,
  "models": ["glm-4-plus", "glm-4", "glm-3-turbo"],
  "default_model": "glm-4-plus"
}
```

## 项目结构

- `main.py`: 主程序入口，包含MCP服务器和交互式命令行模式
- `tokenizer_server.py`: Web服务器，提供Web界面和API接口
- `zhipu_tokenizer_client.py`: 智谱AI分词客户端
- `tokenizer_interface.html`: Web界面
- `config.json`: 配置文件

## 智谱API文档

更多关于智谱AI文本分词器的信息，请参考[智谱官方文档](https://docs.bigmodel.cn/api-reference/%E6%A8%A1%E5%9E%8B-api/%E6%96%87%E6%9C%AC%E5%88%86%E8%AF%8D%E5%99%A8)。

## 许可证

MIT