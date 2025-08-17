"""
文本转语音Web服务器
支持文本输入和语音生成功能
"""

import os
import json
import base64
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from zhipu_tts_client import ZhipuTTSClient

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize TTS client
tts_client = ZhipuTTSClient()

# Create directories
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """主页面"""
    with open('tts_interface.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/convert', methods=['POST'])
def convert_text_to_speech():
    """文本转语音API"""
    try:
        data = request.get_json()
        
        text = data.get('text', '').strip()
        voice = data.get('voice', 'tongtong')
        model = data.get('model', 'cogtts')
        response_format = data.get('response_format', 'wav')
        save_file = data.get('save_file', True)
        filename = data.get('filename')
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Text content is required"
            }), 400
        
        # Validate text
        validation = tts_client.validate_text(text)
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": f"Text validation failed: {validation['error']}"
            }), 400
        
        # Perform text-to-speech conversion
        if save_file:
            result = tts_client.text_to_speech_file(
                text=text,
                filename=filename,
                voice=voice,
                model=model,
                response_format=response_format,
                output_dir=str(OUTPUTS_DIR)
            )
        else:
            result = tts_client.text_to_speech(
                text=text,
                voice=voice,
                model=model,
                response_format=response_format
            )
            
            # If not saving file, encode audio data as base64 for response
            if result["success"]:
                result["audio_base64"] = base64.b64encode(result["audio_data"]).decode('utf-8')
                # Remove binary data from response
                del result["audio_data"]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Text-to-speech conversion failed: {str(e)}"
        }), 500

@app.route('/api/batch_convert', methods=['POST'])
def batch_convert_text_to_speech():
    """批量文本转语音API"""
    try:
        data = request.get_json()
        
        texts = data.get('texts', [])
        voice = data.get('voice', 'tongtong')
        model = data.get('model', 'cogtts')
        response_format = data.get('response_format', 'wav')
        
        if not texts:
            return jsonify({
                "success": False,
                "error": "Texts list is required"
            }), 400
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not valid_texts:
            return jsonify({
                "success": False,
                "error": "No valid texts found"
            }), 400
        
        # Perform batch conversion
        result = tts_client.batch_text_to_speech(
            texts=valid_texts,
            voice=voice,
            model=model,
            response_format=response_format,
            output_dir=str(OUTPUTS_DIR)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Batch conversion failed: {str(e)}"
        }), 500

@app.route('/api/voice_types', methods=['GET'])
def get_voice_types():
    """获取可用语音类型API"""
    try:
        voice_types = tts_client.get_voice_types()
        audio_formats = tts_client.get_audio_formats()
        models = tts_client.get_model_info()
        
        return jsonify({
            "success": True,
            "voice_types": voice_types,
            "audio_formats": audio_formats,
            "models": list(models.keys()),
            "model_details": models
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get voice types: {str(e)}"
        }), 500

@app.route('/api/validate_text', methods=['POST'])
def validate_text():
    """验证文本输入API"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        validation = tts_client.validate_text(text)
        
        return jsonify({
            "success": True,
            "validation": validation
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Text validation failed: {str(e)}"
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """获取生成的音频文件列表API"""
    try:
        files = []
        for file_path in OUTPUTS_DIR.iterdir():
            if file_path.is_file():
                # Check if it's an audio file
                ext = file_path.suffix.lower()
                
                if ext in ['.wav', '.mp3']:
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime,
                        "type": ext,
                        "category": "audio"
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

@app.route('/api/audio_info/<path:filename>', methods=['GET'])
def get_audio_info(filename):
    """获取音频文件信息API"""
    try:
        file_path = OUTPUTS_DIR / filename
        
        if not file_path.exists():
            return jsonify({
                "success": False,
                "error": f"Audio file not found: {filename}"
            }), 404
        
        # Get file information
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix.lower()
        
        return jsonify({
            "success": True,
            "filename": file_path.name,
            "path": str(file_path),
            "size": file_size,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "format": file_ext,
            "supported": file_ext in ['.wav', '.mp3']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get audio info: {str(e)}"
        }), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试API连接"""
    try:
        connection_test = tts_client.test_connection()
        
        return jsonify({
            "success": True,
            "connection_test": connection_test,
            "voice_types": tts_client.get_voice_types(),
            "audio_formats": tts_client.get_audio_formats(),
            "available_models": list(tts_client.get_model_info().keys())
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"API test failed: {str(e)}"
        }), 500

@app.route('/api/save_text', methods=['POST'])
def save_text():
    """保存文本内容API"""
    try:
        data = request.get_json()
        
        text_content = data.get('text_content', '')
        filename = data.get('filename', 'text_content.txt')
        
        if not text_content:
            return jsonify({
                "success": False,
                "error": "Text content is required"
            }), 400
        
        # Create unique filename
        import uuid
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".txt"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # Save text file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return jsonify({
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to save text: {str(e)}"
        }), 500

@app.route('/outputs/<filename>')
def output_file(filename):
    """提供生成文件的访问"""
    return send_from_directory(OUTPUTS_DIR, filename)

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "Content too large. Maximum size is 50MB."
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
    print("🚀 AI文本转语音服务器启动中...")
    print("📁 输出目录:", OUTPUTS_DIR.absolute())
    print("🌐 访问地址: http://localhost:5000")
    print("🎭 支持的语音类型:")
    
    try:
        voice_types = tts_client.get_voice_types()
        for voice, desc in voice_types.items():
            print(f"   {voice}: {desc}")
        
        audio_formats = tts_client.get_audio_formats()
        print(f"📄 支持的音频格式: {', '.join(audio_formats)}")
        
    except Exception as e:
        print(f"   获取信息失败: {e}")
    
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)