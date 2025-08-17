"""
文本嵌入Web服务器
提供基于智谱GLM嵌入模型的文本嵌入服务的Web界面
"""

import os
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from zhipu_embedding_client import ZhipuEmbeddingClient
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 创建输出目录
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# 初始化嵌入客户端
embedding_client = None

def initialize_client():
    """初始化嵌入客户端"""
    global embedding_client
    try:
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            # 尝试从配置文件读取
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get("api_keys", {}).get("zhipu")
        
        if api_key:
            embedding_client = ZhipuEmbeddingClient(api_key)
            logger.info("嵌入客户端初始化成功")
            return True
        else:
            logger.error("未找到API密钥")
            return False
    except Exception as e:
        logger.error(f"初始化嵌入客户端失败: {e}")
        return False

# 路由定义
@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'embedding_interface.html')

@app.route('/get_text_embeddings', methods=['POST'])
def get_text_embeddings():
    """获取文本嵌入向量"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        input_text = data.get('input_text')
        model = data.get('model', 'embedding-3')
        
        if not input_text:
            return jsonify({
                "success": False,
                "error": "输入文本不能为空"
            })
        
        result = embedding_client.get_embeddings(input_text, model)
        
        return jsonify({
            "success": True,
            "model": result.get("model"),
            "data": result.get("data"),
            "usage": result.get("usage")
        })
        
    except Exception as e:
        logger.error(f"获取文本嵌入失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取文本嵌入失败: {str(e)}"
        })

@app.route('/get_batch_embeddings', methods=['POST'])
def get_batch_embeddings():
    """批量获取文本嵌入向量"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        texts = data.get('texts', [])
        model = data.get('model', 'embedding-3')
        
        if not texts:
            return jsonify({
                "success": False,
                "error": "文本列表不能为空"
            })
        
        # 过滤空文本
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not valid_texts:
            return jsonify({
                "success": False,
                "error": "没有找到有效的文本"
            })
        
        embeddings = embedding_client.get_batch_embeddings(valid_texts, model)
        
        return jsonify({
            "success": True,
            "model": model,
            "embeddings": embeddings,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        })
        
    except Exception as e:
        logger.error(f"批量获取文本嵌入失败: {e}")
        return jsonify({
            "success": False,
            "error": f"批量获取文本嵌入失败: {str(e)}"
        })

@app.route('/calculate_text_similarity', methods=['POST'])
def calculate_text_similarity():
    """计算文本相似度"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        text1 = data.get('text1')
        text2 = data.get('text2')
        model = data.get('model', 'embedding-3')
        
        if not text1 or not text2:
            return jsonify({
                "success": False,
                "error": "两个文本都不能为空"
            })
        
        # 获取两个文本的嵌入向量
        embedding1 = embedding_client.get_single_embedding(text1, model)
        embedding2 = embedding_client.get_single_embedding(text2, model)
        
        # 计算相似度
        similarity = embedding_client.calculate_similarity(embedding1, embedding2)
        
        return jsonify({
            "success": True,
            "text1": text1,
            "text2": text2,
            "similarity": similarity,
            "model": model,
            "interpretation": {
                "score": similarity,
                "level": "高" if similarity > 0.8 else "中" if similarity > 0.5 else "低",
                "description": f"两个文本的语义相似度为 {similarity:.4f}"
            }
        })
        
    except Exception as e:
        logger.error(f"计算文本相似度失败: {e}")
        return jsonify({
            "success": False,
            "error": f"计算文本相似度失败: {str(e)}"
        })

@app.route('/find_similar_texts', methods=['POST'])
def find_similar_texts():
    """查找相似文本"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        query_text = data.get('query_text')
        candidate_texts = data.get('candidate_texts', [])
        model = data.get('model', 'embedding-3')
        top_k = data.get('top_k', 5)
        
        if not query_text:
            return jsonify({
                "success": False,
                "error": "查询文本不能为空"
            })
        
        if not candidate_texts:
            return jsonify({
                "success": False,
                "error": "候选文本列表不能为空"
            })
        
        # 过滤空文本
        valid_candidates = [text.strip() for text in candidate_texts if text and text.strip()]
        
        if not valid_candidates:
            return jsonify({
                "success": False,
                "error": "没有找到有效的候选文本"
            })
        
        # 找到最相似的文本
        results = embedding_client.find_most_similar(
            query_text=query_text,
            candidate_texts=valid_candidates,
            model=model
        )
        
        # 限制返回结果数量
        top_results = results[:min(top_k, len(results))]
        
        return jsonify({
            "success": True,
            "query": query_text,
            "model": model,
            "total_candidates": len(valid_candidates),
            "top_k": len(top_results),
            "results": top_results
        })
        
    except Exception as e:
        logger.error(f"查找相似文本失败: {e}")
        return jsonify({
            "success": False,
            "error": f"查找相似文本失败: {str(e)}"
        })

@app.route('/get_supported_models', methods=['POST'])
def get_supported_models():
    """获取支持的模型"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        models = embedding_client.get_available_models()
        
        return jsonify({
            "success": True,
            "models": models,
            "default_model": "embedding-3",
            "model_info": {
                "embedding-3": "最新的嵌入模型，提供高质量的文本向量表示",
                "embedding-2": "较早版本的嵌入模型，兼容性更好"
            }
        })
        
    except Exception as e:
        logger.error(f"获取支持的模型失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取支持的模型失败: {str(e)}"
        })

@app.route('/test_embedding_api', methods=['POST'])
def test_embedding_api():
    """测试嵌入API"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        test_text = data.get('test_text')
        
        # 测试API连接
        connection_test = embedding_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_models": embedding_client.get_available_models()
        }
        
        # 如果提供了测试文本，进行嵌入测试
        if test_text:
            try:
                embedding = embedding_client.get_single_embedding(test_text, "embedding-3")
                result["embedding_test"] = {
                    "success": True,
                    "text": test_text,
                    "dimension": len(embedding),
                    "sample_values": embedding[:5] if len(embedding) >= 5 else embedding
                }
            except Exception as e:
                result["embedding_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试嵌入API失败: {e}")
        return jsonify({
            "success": False,
            "error": f"测试嵌入API失败: {str(e)}"
        })

@app.route('/save_embeddings', methods=['POST'])
def save_embeddings():
    """保存嵌入向量到文件"""
    try:
        if not embedding_client:
            return jsonify({
                "success": False,
                "error": "嵌入客户端未初始化"
            })
        
        data = request.get_json()
        texts = data.get('texts', [])
        filename = data.get('filename', 'embeddings.json')
        model = data.get('model', 'embedding-3')
        
        if not texts or not filename:
            return jsonify({
                "success": False,
                "error": "文本列表和文件名都是必需的"
            })
        
        # 获取嵌入向量
        embeddings = embedding_client.get_batch_embeddings(texts, model)
        
        # 准备保存数据
        save_data = {
            "model": model,
            "timestamp": time.time(),
            "count": len(texts),
            "dimension": len(embeddings[0]) if embeddings else 0,
            "data": [
                {
                    "text": text,
                    "embedding": embedding
                }
                for text, embedding in zip(texts, embeddings)
            ]
        }
        
        # 创建唯一文件名
        import uuid
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".json"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size,
            "count": len(texts),
            "dimension": save_data["dimension"],
            "model": model
        })
        
    except Exception as e:
        logger.error(f"保存嵌入向量失败: {e}")
        return jsonify({
            "success": False,
            "error": f"保存嵌入向量失败: {str(e)}"
        })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "client_initialized": embedding_client is not None
    })

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

def main():
    """主函数"""
    print("=" * 60)
    print("🔤 AI文本嵌入生成器 - Web服务器")
    print("=" * 60)
    
    # 初始化客户端
    print("🔧 初始化嵌入客户端...")
    if initialize_client():
        print("✅ 嵌入客户端初始化成功")
    else:
        print("❌ 嵌入客户端初始化失败")
        print("💡 请检查:")
        print("  1. 环境变量 ZHIPU_API_KEY 是否设置")
        print("  2. config.json 文件是否存在且包含正确的API密钥")
        return
    
    # 启动服务器
    print("🌐 启动Web服务器...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 API文档: http://localhost:5000/health")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

if __name__ == '__main__':
    main()