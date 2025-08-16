"""
多模态内容分析Web服务器
支持文件上传和多模态内容分析
"""

import os
import json
import base64
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from zhipu_vision_client import ZhipuVisionClient

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize vision client
vision_client = ZhipuVisionClient()

# Create directories
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """主页面"""
    with open('multimodal_interface.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传API"""
    try:
        data = request.get_json()
        
        if not data or 'file_content' not in data or 'filename' not in data:
            return jsonify({
                "success": False,
                "error": "Missing file_content or filename"
            }), 400
        
        file_content = data['file_content']
        filename = secure_filename(data['filename'])
        encoding = data.get('encoding', 'base64')
        
        # Generate unique filename
        import uuid
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        if encoding == 'base64':
            try:
                file_data = base64.b64decode(file_content)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Base64 decoding failed: {str(e)}"
                }), 400
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        
        return jsonify({
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_content():
    """多模态内容分析API"""
    try:
        data = request.get_json()
        
        text = data.get('text', '')
        file_paths = data.get('file_paths', [])
        urls = data.get('urls', [])
        model = data.get('model', 'glm-4v')
        
        if not text and not file_paths and not urls:
            return jsonify({
                "success": False,
                "error": "At least one type of content must be provided"
            }), 400
        
        # Validate file paths
        valid_files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                valid_files.append(str(path))
        
        # Perform analysis
        result = vision_client.analyze_multimodal_content(
            text=text,
            files=valid_files,
            urls=urls,
            model=model
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """获取上传文件列表API"""
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "type": file_path.suffix.lower()
                })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return jsonify({
            "success": True,
            "files": files,
            "total": len(files)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }), 500

@app.route('/api/formats', methods=['GET'])
def get_supported_formats():
    """获取支持的文件格式API"""
    try:
        formats = vision_client.get_supported_formats()
        return jsonify({
            "success": True,
            "formats": formats,
            "models": list(vision_client.vision_models.keys())
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get formats: {str(e)}"
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(UPLOADS_DIR, filename)

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 100MB."
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI多模态内容分析器启动中...")
    print("📁 上传目录:", UPLOADS_DIR.absolute())
    print("🌐 访问地址: http://localhost:5000")
    print("📚 支持格式:")
    
    try:
        formats = vision_client.get_supported_formats()
        for category, extensions in formats.items():
            print(f"   {category}: {', '.join(extensions)}")
    except Exception as e:
        print(f"   获取格式信息失败: {e}")
    
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)