"""
语音转文本Web服务器
支持音频文件上传和语音转文本功能
"""

import os
import json
import base64
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from zhipu_speech_client import ZhipuSpeechClient

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize speech client
speech_client = ZhipuSpeechClient()

# Create directories
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """主页面"""
    with open('speech_interface.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """音频文件上传API"""
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
        
        # Validate audio file
        validation = speech_client._validate_audio_file(str(file_path))
        
        return jsonify({
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size,
            "validation": validation
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """语音转文本API"""
    try:
        data = request.get_json()
        
        audio_path = data.get('audio_path', '')
        model = data.get('model', 'whisper-1')
        language = data.get('language')
        prompt = data.get('prompt')
        response_format = data.get('response_format', 'json')
        
        if not audio_path:
            return jsonify({
                "success": False,
                "error": "Audio path is required"
            }), 400
        
        # Validate file path
        path = Path(audio_path)
        if not path.exists():
            return jsonify({
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }), 404
        
        # Perform transcription
        result = speech_client.transcribe_audio(
            audio_path=audio_path,
            model=model,
            language=language,
            prompt=prompt,
            response_format=response_format
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Transcription failed: {str(e)}"
        }), 500

@app.route('/api/transcribe/timestamps', methods=['POST'])
def transcribe_with_timestamps():
    """带时间戳的语音转文本API"""
    try:
        data = request.get_json()
        
        audio_path = data.get('audio_path', '')
        model = data.get('model', 'whisper-1')
        
        if not audio_path:
            return jsonify({
                "success": False,
                "error": "Audio path is required"
            }), 400
        
        # Validate file path
        path = Path(audio_path)
        if not path.exists():
            return jsonify({
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }), 404
        
        # Perform transcription with timestamps
        result = speech_client.transcribe_with_timestamps(audio_path, model)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Timestamp transcription failed: {str(e)}"
        }), 500

@app.route('/api/transcribe/srt', methods=['POST'])
def transcribe_to_srt():
    """生成SRT字幕API"""
    try:
        data = request.get_json()
        
        audio_path = data.get('audio_path', '')
        model = data.get('model', 'whisper-1')
        
        if not audio_path:
            return jsonify({
                "success": False,
                "error": "Audio path is required"
            }), 400
        
        # Validate file path
        path = Path(audio_path)
        if not path.exists():
            return jsonify({
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }), 404
        
        # Perform SRT transcription
        result = speech_client.transcribe_to_srt(audio_path, model)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"SRT transcription failed: {str(e)}"
        }), 500

@app.route('/api/batch_transcribe', methods=['POST'])
def batch_transcribe():
    """批量转录API"""
    try:
        data = request.get_json()
        
        audio_files = data.get('audio_files', [])
        model = data.get('model', 'whisper-1')
        
        if not audio_files:
            return jsonify({
                "success": False,
                "error": "Audio files list is required"
            }), 400
        
        # Validate file paths
        valid_files = []
        for audio_path in audio_files:
            path = Path(audio_path)
            if path.exists():
                valid_files.append(str(path))
        
        if not valid_files:
            return jsonify({
                "success": False,
                "error": "No valid audio files found"
            }), 400
        
        # Perform batch transcription
        result = speech_client.batch_transcribe(valid_files, model)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Batch transcription failed: {str(e)}"
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """获取上传文件列表API"""
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                # Check if it's an audio file
                ext = file_path.suffix.lower()
                all_formats = speech_client.supported_formats["audio"] + speech_client.supported_formats["video"]
                
                if ext in all_formats:
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime,
                        "type": ext,
                        "category": "audio" if ext in speech_client.supported_formats["audio"] else "video"
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
        formats = speech_client.get_supported_formats()
        models = speech_client.get_model_info()
        return jsonify({
            "success": True,
            "formats": formats,
            "models": list(models.keys()),
            "model_details": models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get formats: {str(e)}"
        }), 500

@app.route('/api/audio_info/<path:filename>', methods=['GET'])
def get_audio_info(filename):
    """获取音频文件信息API"""
    try:
        file_path = UPLOADS_DIR / filename
        
        if not file_path.exists():
            return jsonify({
                "success": False,
                "error": f"Audio file not found: {filename}"
            }), 404
        
        # Get file information
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix.lower()
        
        # Validate audio format
        validation = speech_client._validate_audio_file(str(file_path))
        
        return jsonify({
            "success": True,
            "filename": file_path.name,
            "path": str(file_path),
            "size": file_size,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "format": file_ext,
            "validation": validation,
            "supported": validation["valid"]
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
        connection_test = speech_client.test_connection()
        
        return jsonify({
            "success": True,
            "connection_test": connection_test,
            "supported_formats": speech_client.get_supported_formats(),
            "available_models": list(speech_client.speech_models.keys())
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"API test failed: {str(e)}"
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
    print("🚀 AI语音转文本服务器启动中...")
    print("📁 上传目录:", UPLOADS_DIR.absolute())
    print("🌐 访问地址: http://localhost:5000")
    print("📚 支持格式:")
    
    try:
        formats = speech_client.get_supported_formats()
        for category, extensions in formats.items():
            print(f"   {category}: {', '.join(extensions)}")
    except Exception as e:
        print(f"   获取格式信息失败: {e}")
    
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)