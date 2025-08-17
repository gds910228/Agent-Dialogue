"""
AI图像生成器Web服务器
提供基于智谱CogView-4的图像生成Web界面
"""

import os
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from zhipu_image_client import ZhipuImageClient

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 创建输出目录
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# 初始化图像生成客户端
try:
    image_client = ZhipuImageClient()
    print("✅ 智谱图像生成客户端初始化成功")
except Exception as e:
    print(f"❌ 智谱图像生成客户端初始化失败: {e}")
    image_client = None

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'image_interface.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """生成图像API端点"""
    try:
        if not image_client:
            return jsonify({
                "success": False,
                "error": "图像生成客户端未初始化"
            }), 500
        
        data = request.get_json()
        
        # 获取参数
        prompt = data.get('prompt', '').strip()
        model = data.get('model', 'cogview-4')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        # 验证参数
        if not prompt:
            return jsonify({
                "success": False,
                "error": "提示词不能为空"
            }), 400
        
        # 生成图像并保存
        result = image_client.generate_and_save_image(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            output_dir=str(OUTPUTS_DIR)
        )
        
        if result["success"]:
            # 返回成功结果
            return jsonify({
                "success": True,
                "prompt": result["prompt"],
                "model": result["model"],
                "size": result["size"],
                "quality": result["quality"],
                "image_url": result["image_url"],
                "file_path": f"/outputs/{Path(result['file_path']).name}",
                "file_size": result["file_size"],
                "created": result["created"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500

@app.route('/batch-generate', methods=['POST'])
def batch_generate():
    """批量生成图像API端点"""
    try:
        if not image_client:
            return jsonify({
                "success": False,
                "error": "图像生成客户端未初始化"
            }), 500
        
        data = request.get_json()
        
        # 获取参数
        prompts = data.get('prompts', [])
        model = data.get('model', 'cogview-4')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        # 验证参数
        if not prompts:
            return jsonify({
                "success": False,
                "error": "提示词列表不能为空"
            }), 400
        
        # 批量生成图像
        result = image_client.batch_generate_images(
            prompts=prompts,
            model=model,
            size=size,
            quality=quality,
            output_dir=str(OUTPUTS_DIR)
        )
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}"
        }), 500

@app.route('/test-api', methods=['POST'])
def test_api():
    """测试API连接"""
    try:
        if not image_client:
            return jsonify({
                "success": False,
                "error": "图像生成客户端未初始化"
            }), 500
        
        # 测试API连接
        result = image_client.test_connection()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"测试失败: {str(e)}"
        }), 500

@app.route('/get-options', methods=['GET'])
def get_options():
    """获取支持的选项"""
    try:
        if not image_client:
            return jsonify({
                "success": False,
                "error": "图像生成客户端未初始化"
            }), 500
        
        models = image_client.get_supported_models()
        sizes = image_client.get_supported_sizes()
        quality_options = image_client.get_quality_options()
        
        return jsonify({
            "success": True,
            "models": models,
            "sizes": sizes,
            "quality_options": quality_options
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取选项失败: {str(e)}"
        }), 500

@app.route('/validate-prompt', methods=['POST'])
def validate_prompt():
    """验证提示词"""
    try:
        if not image_client:
            return jsonify({
                "success": False,
                "error": "图像生成客户端未初始化"
            }), 500
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "提示词不能为空"
            }), 400
        
        # 验证提示词
        result = image_client.validate_prompt(prompt)
        return jsonify({
            "success": True,
            "validation": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"验证失败: {str(e)}"
        }), 500

@app.route('/list-files', methods=['GET'])
def list_files():
    """列出生成的图像文件"""
    try:
        files = []
        for file_path in OUTPUTS_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']:
                files.append({
                    "filename": file_path.name,
                    "path": f"/outputs/{file_path.name}",
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "type": file_path.suffix.lower()
                })
        
        # 按修改时间排序（最新的在前）
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return jsonify({
            "success": True,
            "files": files,
            "total": len(files)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取文件列表失败: {str(e)}"
        }), 500

@app.route('/outputs/<filename>')
def serve_output_file(filename):
    """提供输出文件的访问"""
    try:
        return send_from_directory(OUTPUTS_DIR, filename)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"文件不存在: {filename}"
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": time.time(),
        "client_initialized": image_client is not None
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "error": "页面未找到"
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
    print("🎨 AI图像生成器Web服务器")
    print("=" * 60)
    print(f"📁 输出目录: {OUTPUTS_DIR.absolute()}")
    print(f"🔧 客户端状态: {'✅ 正常' if image_client else '❌ 未初始化'}")
    print("🌐 启动Web服务器...")
    print("📱 访问地址: http://localhost:5000")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")