"""
智谱AI文本重排序Web服务器
提供RESTful API接口和Web界面
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from zhipu_rerank_client import ZhipuRerankClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 加载配置
def load_config():
    """加载配置文件"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()

# 初始化客户端
api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
if not api_key:
    logger.warning("未找到智谱API密钥，请设置环境变量 ZHIPU_API_KEY 或在config.json中配置")

rerank_base_url = config.get("text_rerank", {}).get("base_url", "https://open.bigmodel.cn")
rerank_client = ZhipuRerankClient(api_key=api_key or "", base_url=rerank_base_url)

@app.route('/')
def index():
    """主页 - 返回Web界面"""
    return send_from_directory('.', 'rerank_interface.html')

@app.route('/api/rerank', methods=['POST'])
def api_rerank():
    """文档重排序API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据不能为空"
            }), 400
        
        query = data.get('query', '').strip()
        documents = data.get('documents', [])
        model = data.get('model', 'rerank')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "查询文本不能为空"
            }), 400
        
        if not documents or len(documents) == 0:
            return jsonify({
                "success": False,
                "error": "文档列表不能为空"
            }), 400
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return jsonify({
                "success": False,
                "error": "没有找到有效的文档"
            }), 400
        
        # 调用重排序API
        result = rerank_client.rerank(query, valid_documents, model)
        
        return jsonify({
            "success": True,
            "query": query,
            "model": model,
            "total_documents": len(valid_documents),
            "results": result.get("results", []),
            "usage": result.get("usage", {}),
            "request_id": result.get("request_id", ""),
            "created": result.get("created", 0)
        })
        
    except Exception as e:
        logger.error(f"重排序API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"重排序失败: {str(e)}"
        }), 500

@app.route('/api/top_relevant', methods=['POST'])
def api_top_relevant():
    """获取最相关文档API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据不能为空"
            }), 400
        
        query = data.get('query', '').strip()
        documents = data.get('documents', [])
        model = data.get('model', 'rerank')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "查询文本不能为空"
            }), 400
        
        if not documents:
            return jsonify({
                "success": False,
                "error": "文档列表不能为空"
            }), 400
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return jsonify({
                "success": False,
                "error": "没有找到有效的文档"
            }), 400
        
        # 获取排序后的文档
        ranked_docs = rerank_client.get_ranked_documents(query, valid_documents, model, top_k)
        
        return jsonify({
            "success": True,
            "query": query,
            "model": model,
            "total_documents": len(valid_documents),
            "top_k": len(ranked_docs),
            "results": ranked_docs
        })
        
    except Exception as e:
        logger.error(f"获取相关文档API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取相关文档失败: {str(e)}"
        }), 500

@app.route('/api/relevant_by_threshold', methods=['POST'])
def api_relevant_by_threshold():
    """按阈值获取相关文档API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据不能为空"
            }), 400
        
        query = data.get('query', '').strip()
        documents = data.get('documents', [])
        model = data.get('model', 'rerank')
        threshold = data.get('threshold', 0.5)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "查询文本不能为空"
            }), 400
        
        if not documents:
            return jsonify({
                "success": False,
                "error": "文档列表不能为空"
            }), 400
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return jsonify({
                "success": False,
                "error": "没有找到有效的文档"
            }), 400
        
        # 获取相关文档
        relevant_docs = rerank_client.find_most_relevant(query, valid_documents, model, threshold)
        
        return jsonify({
            "success": True,
            "query": query,
            "model": model,
            "threshold": threshold,
            "total_documents": len(valid_documents),
            "relevant_count": len(relevant_docs),
            "results": relevant_docs
        })
        
    except Exception as e:
        logger.error(f"按阈值获取相关文档API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"按阈值获取相关文档失败: {str(e)}"
        }), 500

@app.route('/api/models', methods=['GET'])
def api_models():
    """获取支持的模型列表API"""
    try:
        models = rerank_client.get_available_models()
        
        return jsonify({
            "success": True,
            "models": models,
            "default_model": "rerank",
            "model_info": {
                "rerank": "智谱AI文本重排序模型，用于对候选文档进行相关性排序"
            }
        })
        
    except Exception as e:
        logger.error(f"获取模型列表API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取模型列表失败: {str(e)}"
        }), 500

@app.route('/api/test', methods=['POST'])
def api_test():
    """测试API连接"""
    try:
        data = request.get_json() or {}
        test_query = data.get('query')
        test_documents = data.get('documents')
        
        # 测试API连接
        connection_test = rerank_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_models": rerank_client.get_available_models(),
            "timestamp": datetime.now().isoformat()
        }
        
        # 如果提供了测试数据，进行重排序测试
        if test_query and test_documents:
            try:
                rerank_result = rerank_client.rerank(test_query, test_documents, "rerank")
                result["rerank_test"] = {
                    "success": True,
                    "query": test_query,
                    "document_count": len(test_documents),
                    "results_count": len(rerank_result.get("results", [])),
                    "sample_results": rerank_result.get("results", [])[:3]  # 显示前3个结果
                }
            except Exception as e:
                result["rerank_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"API测试失败: {str(e)}"
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """获取服务状态"""
    try:
        # 检查API密钥
        has_api_key = bool(api_key)
        
        # 测试连接
        connection_ok = False
        if has_api_key:
            try:
                connection_ok = rerank_client.test_connection()
            except:
                connection_ok = False
        
        return jsonify({
            "success": True,
            "status": "running",
            "has_api_key": has_api_key,
            "connection_ok": connection_ok,
            "supported_models": rerank_client.get_available_models() if has_api_key else [],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取状态API错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取状态失败: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "error": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 智谱AI文本重排序Web服务器")
    print("=" * 60)
    print("服务器信息:")
    print(f"  地址: http://localhost:5000")
    print(f"  API密钥状态: {'已配置' if api_key else '未配置'}")
    print(f"  支持的模型: {', '.join(rerank_client.get_available_models())}")
    print("=" * 60)
    print("可用的API接口:")
    print("  POST /api/rerank - 文档重排序")
    print("  POST /api/top_relevant - 获取最相关文档")
    print("  POST /api/relevant_by_threshold - 按阈值获取相关文档")
    print("  GET  /api/models - 获取支持的模型")
    print("  POST /api/test - 测试API连接")
    print("  GET  /api/status - 获取服务状态")
    print("=" * 60)
    
    if not api_key:
        print("⚠️  警告: 未配置API密钥，请设置环境变量 ZHIPU_API_KEY")
        print("   或在 config.json 中添加 'zhipu_api_key' 字段")
        print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)