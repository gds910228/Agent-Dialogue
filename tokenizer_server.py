"""
智谱AI文本分词器服务器
提供Web界面和API接口，用于文本分词和Token计算
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from zhipu_tokenizer_client import ZhipuTokenizerClient

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
    return render_template('tokenizer_interface.html')

@app.route('/tokenizer_interface.html')
def tokenizer_interface():
    """分词器界面"""
    return send_from_directory('.', 'tokenizer_interface.html')

@app.route('/api/tokenize', methods=['POST'])
def tokenize():
    """分词API"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        messages = data.get('messages')
        model = data.get('model', 'glm-4-plus')
        
        if not messages:
            return jsonify({
                "success": False,
                "error": "消息列表不能为空"
            }), 400
        
        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                return jsonify({
                    "success": False,
                    "error": "消息格式错误，每个消息必须包含role和content字段"
                }), 400
        
        # 调用分词API
        result = tokenizer_client.tokenize(messages, model)
        
        return jsonify({
            "success": True,
            "model": model,
            "usage": result.get("usage", {}),
            "request_id": result.get("id", ""),
            "created": result.get("created", 0)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/token-count', methods=['POST'])
def token_count():
    """获取Token数量API"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        messages = data.get('messages')
        model = data.get('model', 'glm-4-plus')
        
        if not messages:
            return jsonify({
                "success": False,
                "error": "消息列表不能为空"
            }), 400
        
        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                return jsonify({
                    "success": False,
                    "error": "消息格式错误，每个消息必须包含role和content字段"
                }), 400
        
        # 调用分词API
        token_count = tokenizer_client.count_tokens_for_messages(messages, model)
        
        return jsonify({
            "success": True,
            "model": model,
            "token_count": token_count
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取支持的模型列表"""
    try:
        models = tokenizer_client.get_available_models()
        
        return jsonify({
            "success": True,
            "models": models,
            "default_model": "glm-4-plus"
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
    
    print(f"🔧 启动智谱AI文本分词器服务器 (http://{host}:{port})")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()