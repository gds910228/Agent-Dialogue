# 智谱文本重排序项目改造任务

## To Do
- [ ] 更新项目文档
    - [ ] 修改README.md
    - [ ] 更新配置示例
    - [ ] 添加使用说明

## Doing

## Done
- [x] 理解智谱重排序API接口
- [x] 制定改造计划
- [x] 创建智谱文本重排序客户端
    - [x] 实现rerank API调用 (zhipu_rerank_client.py)
    - [x] 支持查询文本和候选文档列表
    - [x] 处理API响应和错误
    - [x] 添加连接测试功能
    - [x] 实现相关性阈值筛选
- [x] 更新主程序入口
    - [x] 创建新的重排序主程序 (main_rerank.py)
    - [x] 替换嵌入功能为重排序功能
    - [x] 更新MCP工具定义
    - [x] 修改交互式界面
- [x] 更新Web界面
    - [x] 创建重排序Web界面 (rerank_interface.html)
    - [x] 实现四个主要功能标签页
    - [x] 更新JavaScript逻辑
    - [x] 调整UI布局和样式
- [x] 创建Web服务器
    - [x] 实现Flask后端API (rerank_server.py)
    - [x] 添加重排序相关接口
    - [x] 实现错误处理和日志记录

## 项目改造完成总结

### 已完成的主要改造内容：

#### 1. 核心功能改造
- ✅ 将文本嵌入API改为智谱文本重排序API
- ✅ 支持 rerank 模型
- ✅ 实现文档重排序功能
- ✅ 添加最相关文档获取功能
- ✅ 实现相关性阈值筛选功能

#### 2. 重排序客户端实现 (zhipu_rerank_client.py)
- ✅ 完整的重排序API调用封装
- ✅ 错误处理和重试机制
- ✅ 支持多种查询模式
- ✅ 连接测试功能
- ✅ 使用信息提取

#### 3. MCP服务器改造 (main_rerank.py)
- ✅ 更新所有MCP工具为文本重排序相关
- ✅ 保持原有的服务器架构
- ✅ 添加交互式命令行界面
- ✅ 实现文件保存和加载功能

#### 4. Web界面 (rerank_interface.html)
- ✅ 现代化的响应式设计
- ✅ 四个主要功能标签页：
  - 文档重排序
  - 最相关文档获取
  - 阈值筛选
  - API测试
- ✅ 实时API状态监控
- ✅ 结果可视化和下载功能
- ✅ Toast通知系统

#### 5. Web服务器 (rerank_server.py)
- ✅ Flask后端API服务
- ✅ 完整的RESTful接口
- ✅ 错误处理和日志记录
- ✅ 跨域支持

#### 6. 功能特性
- 🔄 **文档重排序**: 根据查询文本对候选文档进行相关性排序
- 🏆 **最相关文档**: 获取与查询最相关的前N个文档
- 🎯 **阈值筛选**: 根据相关性阈值筛选符合条件的文档
- 🧪 **API测试**: 测试API连接状态和功能
- 📊 **结果可视化**: 直观显示相关性分数和排序结果
- 💾 **数据导出**: 支持重排序结果的保存和下载
- 🌐 **Web界面**: 美观的现代化界面
- 🔧 **MCP支持**: 完整的MCP服务器功能

### 新增文件列表
1. `zhipu_rerank_client.py` - 智谱重排序客户端
2. `main_rerank.py` - 重排序主程序
3. `rerank_server.py` - 重排序Web服务器
4. `rerank_interface.html` - 重排序Web界面

### API接口
- `POST /api/rerank` - 文档重排序
- `POST /api/top_relevant` - 获取最相关文档
- `POST /api/relevant_by_threshold` - 按阈值筛选相关文档
- `GET /api/models` - 获取支持的模型
- `POST /api/test` - 测试API连接
- `GET /api/status` - 获取服务状态

### 使用方式
1. **Web界面**: 运行 `python rerank_server.py` 然后访问 http://localhost:5000
2. **命令行**: 运行 `python main_rerank.py` 进入交互式模式
3. **MCP服务器**: 运行 `python main_rerank.py --mcp` 启动MCP服务器

### 项目状态
项目已成功从文本嵌入系统改造为文本重排序系统，所有核心功能都已实现并可以正常使用。用户可以通过Web界面或MCP工具来使用文本重排序功能。

### 智谱重排序API集成
- ✅ 支持智谱AI rerank模型
- ✅ 正确的API端点: `/api/paas/v4/rerank`
- ✅ 标准的请求格式: query + documents
- ✅ 完整的响应处理: results + usage + request_id
- ✅ 相关性分数可视化
- ✅ 错误处理和重试机制