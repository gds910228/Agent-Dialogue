# 网络搜索 MCP 服务器

一个基于模型上下文协议 (MCP) 的服务器，使用智谱AI的网络搜索API提供网络搜索功能。

## 功能特性

- 支持自定义参数的网络搜索
- 搜索意图分析
- 最近内容过滤
- 搜索结果保存和加载
- 交互式命令行界面
- MCP服务器模式，可与MCP客户端集成

## 安装步骤

1. 克隆仓库：
```bash
git clone <repository-url>
cd Web-Search-MCP
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置API密钥：
   - 复制 `config.json.example` 为 `config.json`
   - 在配置文件中添加您的智谱AI API密钥

## 配置说明

创建 `config.json` 配置文件：

```json
{
  "zhipu_api_key": "your_api_key_here",
  "search_engine": "search_std",
  "api_settings": {
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "timeout": 120,
    "max_retries": 3
  },
  "server_settings": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true
  },
  "mcp_settings": {
    "transport": "sse",
    "timeout": 60
  }
}
```

### 搜索引擎选项

- `search_std`: 智慧基础版搜索引擎（推荐）
- `search_pro`: 智慧高阶版搜索引擎
- `search_pro_sogou`: 搜狗搜索引擎
- `search_pro_quark`: 夸克搜索引擎

## 使用方法

### 交互模式
以交互模式运行服务器：
```bash
python main.py
```

### MCP服务器模式
启动MCP服务器：
```bash
python main.py --mcp
```

### API测试
测试API连接：
```bash
python main.py --test
```

## MCP客户端配置

在您的MCP客户端配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "mcp-web-search": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

## MCP工具

服务器提供以下MCP工具：

- `web_search`: 执行网络搜索，支持各种参数
- `web_search_with_intent`: 带搜索意图分析的搜索
- `web_search_recent`: 搜索最近内容
- `test_websearch_api`: 测试API连接
- `save_search_results_to_file`: 将搜索结果保存到文件
- `load_search_results_from_file`: 从文件加载搜索结果

## 故障排除

### 常见错误

1. **搜索引擎不能为空错误**
   - 确保在 `config.json` 中设置了 `search_engine` 字段
   - 推荐使用 `search_std` 作为默认值

2. **API密钥错误**
   - 检查智谱AI API密钥是否正确配置
   - 确保API密钥有效且有足够的配额

3. **连接超时**
   - 检查网络连接
   - 适当增加 `timeout` 配置值

## 许可证

MIT License