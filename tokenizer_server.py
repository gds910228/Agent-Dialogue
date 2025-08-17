"""
智谱AI网络搜索服务器
提供Web界面和API接口，用于网络搜索功能
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from zhipu_websearch_client import ZhipuWebSearchClient

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域请求

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
    print("警告: 未找到智谱API密钥，请设置环境变量 ZHIPU_API_KEY 或在config.json中配置")

tokenizer_base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
tokenizer_client = ZhipuTokenizerClient(api_key=api_key or "", base_url=tokenizer_base_url)

# 创建输出目录
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """主页"""
    return render_template('websearch_interface.html')

@app.route('/websearch_interface.html')
def websearch_interface():
    """网络搜索界面"""
    return send_from_directory('.', 'websearch_interface.html')

@app.route('/api/search', methods=['POST'])
def search():
    """网络搜索API"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        search_query = data.get('search_query')
        search_intent = data.get('search_intent', False)
        count = data.get('count', 10)
        search_recency_filter = data.get('search_recency_filter', 'noLimit')
        
        if not search_query:
            return jsonify({
                "success": False,
                "error": "搜索查询不能为空"
            }), 400
        
        # 验证参数
        validation = websearch_client.validate_search_params(
            search_query, count, search_recency_filter
        )
        
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }), 400
        
        # 调用搜索API
        result = websearch_client.search(
            search_query=search_query,
            search_intent=search_intent,
            count=count,
            search_recency_filter=search_recency_filter
        )
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(result)
        
        return jsonify({
            "success": True,
            "search_query": search_query,
            "search_intent": search_intent,
            "count": count,
            "search_recency_filter": search_recency_filter,
            "result": formatted_result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search-with-intent', methods=['POST'])
def search_with_intent():
    """带搜索意图分析的网络搜索API"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        search_query = data.get('search_query')
        count = data.get('count', 10)
        
        if not search_query:
            return jsonify({
                "success": False,
                "error": "搜索查询不能为空"
            }), 400
        
        # 验证参数
        validation = websearch_client.validate_search_params(
            search_query, count, "noLimit"
        )
        
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }), 400
        
        # 调用搜索API
        result = websearch_client.search_with_intent(search_query, count)
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(result)
        
        return jsonify({
            "success": True,
            "search_query": search_query,
            "count": count,
            "result": formatted_result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search-filters', methods=['GET'])
def get_search_filters():
    """获取支持的搜索过滤选项"""
    try:
        filters = websearch_client.get_available_recency_filters()
        
        return jsonify({
            "success": True,
            "recency_filters": filters,
            "default_filter": "noLimit"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def main():
    """主函数"""
    # 获取服务器配置
    server_settings = config.get("server_settings", {})
    host = server_settings.get("host", "0.0.0.0")
    port = server_settings.get("port", 5000)
    debug = server_settings.get("debug", True)
    
    print(f"🔧 启动智谱AI网络搜索服务器 (http://{host}:{port})")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()