# AI Text Reranking System - 智谱GLM文本重排序系统

基于智谱AI GLM重排序模型的高质量文本重排序系统，对候选文档进行相关性排序，用于信息检索和文档排序。

## ✨ 主要特性

- 🔄 **文档重排序**: 基于智谱GLM重排序模型
- 🏆 **最相关文档**: 获取与查询最相关的前N个文档
- 🎯 **阈值筛选**: 根据相关性阈值筛选符合条件的文档
- 🌐 **Web界面**: 现代化的响应式Web界面
- 🔌 **MCP服务器**: 支持Model Context Protocol
- 📦 **批量处理**: 支持批量文档重排序
- 💾 **数据导出**: 支持重排序结果的保存和加载
- 🧪 **API测试**: 内置API连接测试功能

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
  "zhipu_api_key": "your_zhipu_api_key_here"
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
    "mcp-text-reranking": {
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
python rerank_server.py
```

然后访问 http://localhost:5000

#### 2. 交互式命令行模式

```bash
python main_rerank.py
```

#### 3. MCP服务器模式

```bash
python main_rerank.py --mcp
```

## 🎯 支持的模型

| 模型 | 描述 | 特点 |
|------|------|------|
| rerank | 智谱AI文本重排序模型 | 高质量文档相关性排序，推荐使用 |

## 🔄 主要功能

- **文档重排序** - 根据查询文本对候选文档进行相关性排序
- **最相关文档获取** - 获取与查询最相关的前N个文档
- **阈值筛选** - 根据相关性阈值筛选符合条件的文档
- **API测试** - 测试智谱AI重排序API的连接状态

## 🎨 使用示例

### Python API调用

```python
from zhipu_rerank_client import ZhipuRerankClient

# 初始化客户端
client = ZhipuRerankClient(api_key="your_api_key")

# 文档重排序
query = "人工智能的发展历史"
documents = [
    "人工智能起源于20世纪50年代，由图灵等科学家奠定基础",
    "今天的天气很好，适合出门散步",
    "机器学习是人工智能的重要分支",
    "深度学习在近年来取得了突破性进展"
]

result = client.rerank(
    query=query,
    documents=documents,
    model="rerank"
)

print("重排序结果:")
for i, item in enumerate(result["results"]):
    print(f"{i+1}. {item['document']} (相关性: {item['relevance_score']:.4f})")
```

### 获取最相关文档

```python
# 获取前3个最相关的文档
top_docs = client.get_ranked_documents(
    query=query,
    documents=documents,
    model="rerank",
    top_k=3
)

print("最相关的文档:")
for i, doc in enumerate(top_docs):
    print(f"{i+1}. {doc['document']} (相关性: {doc['relevance_score']:.4f})")
```

### 阈值筛选

```python
# 筛选相关性超过0.7的文档
relevant_docs = client.find_most_relevant(
    query=query,
    documents=documents,
    model="rerank",
    threshold=0.7
)

print(f"找到 {len(relevant_docs)} 个高相关性文档")
```

### MCP工具调用

```python
# 文档重排序
rerank_documents(
    query="查询文本",
    documents=["文档1", "文档2", "文档3"],
    model="rerank"
)

# 获取最相关文档
get_top_relevant_documents(
    query="查询文本",
    documents=["文档1", "文档2", "文档3"],
    top_k=5
)

# 阈值筛选
find_relevant_documents(
    query="查询文本",
    documents=["文档1", "文档2", "文档3"],
    threshold=0.5
)

# 测试API连接
test_rerank_api("测试查询", ["测试文档"])
```

## 🌐 Web界面功能

- **文档重排序**: 输入查询和候选文档，获得排序结果
- **最相关文档**: 获取前N个最相关的文档
- **阈值筛选**: 根据相关性阈值筛选文档
- **API测试**: 测试API连接状态和功能
- **实时状态监控**: 显示API连接状态
- **结果可视化**: 相关性分数条形图显示
- **下载功能**: 一键下载重排序结果

## 📁 项目结构

```
AI-Text-Reranking/
├── main_rerank.py          # 重排序主程序入口
├── zhipu_rerank_client.py  # 智谱重排序客户端
├── rerank_server.py        # Web服务器
├── rerank_interface.html   # Web界面
├── network_diagnostic.py   # 网络诊断工具
├── config.json            # 配置文件
├── outputs/               # 输出目录
└── docs/                  # 文档目录
```

## 🔧 配置选项

### API配置

```json
{
  "zhipu_api_key": "your_api_key",
  "text_rerank": {
    "base_url": "https://open.bigmodel.cn",
    "timeout": 30,
    "max_retries": 3
  }
}
```

### 重排序参数

- **query**: 查询文本（必需）
- **documents**: 候选文档列表（必需）
- **model**: 重排序模型（默认: rerank）

## 🛠️ 开发指南

### 添加新功能

1. 在 `zhipu_rerank_client.py` 中添加新的API方法
2. 在 `main_rerank.py` 中添加对应的MCP工具
3. 在 `rerank_server.py` 中添加Web API接口
4. 更新Web界面添加新功能

### 自定义输出格式

```python
# 修改保存格式
def save_custom_format(self, rerank_data, filename, format="json"):
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

3. **重排序失败**
   - 检查查询文本和文档是否为空
   - 确认文档数量不超过API限制
   - 尝试使用不同的查询文本

4. **Web界面无法访问**
   - 确认端口5000未被占用
   - 检查防火墙设置

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main_rerank.py
```

## 📊 性能优化

- 合理控制候选文档数量（建议不超过100个）
- 使用简洁明确的查询文本
- 批量处理时适当增加延迟避免API限制
- 根据需求设置合适的相关性阈值

## 🔌 API接口

### RESTful API

- `POST /api/rerank` - 文档重排序
- `POST /api/top_relevant` - 获取最相关文档
- `POST /api/relevant_by_threshold` - 按阈值筛选相关文档
- `GET /api/models` - 获取支持的模型
- `POST /api/test` - 测试API连接
- `GET /api/status` - 获取服务状态

### MCP工具

- `rerank_documents` - 文档重排序
- `get_top_relevant_documents` - 获取最相关文档
- `find_relevant_documents` - 查找相关文档
- `get_supported_rerank_models` - 获取支持的模型
- `test_rerank_api` - 测试API连接
- `save_rerank_results_to_file` - 保存结果到文件
- `load_rerank_results_from_file` - 从文件加载结果

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- 智谱AI提供的Rerank模型
- Flask和相关Web框架
- 所有贡献者和用户

## 📞 支持

如有问题或建议，请：

1. 查看文档和FAQ
2. 提交Issue
3. 联系开发团队

---

**享受AI文本重排序的便利！** 🔄✨