"""
AI Speech-to-Text Converter - Main Entry Point

A comprehensive AI speech recognition system supporting multiple audio formats.
Provides both MCP server capabilities and direct speech-to-text functionality.
"""

import os
import sys
import time
import json
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from zhipu_speech_client import ZhipuSpeechClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Speech-to-Text Converter")

# Create directories for storing files
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Initialize clients
speech_client = ZhipuSpeechClient()

# Speech Recognition Entry Point
class SpeechRecognition:
    """主要的语音识别入口类"""
    
    def __init__(self):
        self.speech_client = speech_client
        self.uploads_dir = UPLOADS_DIR
        
    
    
    def transcribe_audio(self, 
                        audio_path: str,
                        model: str = "glm-asr",
                        language: Optional[str] = None,
                        prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        主要的语音转文本入口
        
        Args:
            audio_path: 音频文件路径
            model: 使用的模型 (glm-asr)
            language: 音频语言
            prompt: 提示词
            
        Returns:
            转录结果
        """
        return self.speech_client.transcribe_audio(
            audio_path=audio_path,
            model=model,
            language=language,
            prompt=prompt
        )
    
    def transcribe_with_timestamps(self, audio_path: str, model: str = "glm-asr") -> Dict[str, Any]:
        """带时间戳的语音转文本"""
        return self.speech_client.transcribe_with_timestamps(audio_path, model)
    
    def transcribe_to_srt(self, audio_path: str, model: str = "glm-asr") -> Dict[str, Any]:
        """转录为SRT字幕格式"""
        return self.speech_client.transcribe_to_srt(audio_path, model)
    
    def batch_transcribe(self, audio_files: List[str], model: str = "glm-asr") -> Dict[str, Any]:
        """批量语音转文本"""
        return self.speech_client.batch_transcribe(audio_files, model)

# 创建全局语音识别实例
speech_recognition = SpeechRecognition()

@mcp.tool()
@mcp.tool()
def transcribe_audio_file(
    audio_path: str,
    model: str = "glm-asr",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    response_format: str = "json"
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using Zhipu's speech-to-text API.
    
    Args:
        audio_path: Path to the audio file (.wav/.mp3, ≤25MB, ≤60s)
        model: Speech recognition model to use (glm-asr)
        language: Language of the audio (optional, e.g., 'zh', 'en')
        prompt: Optional prompt to guide the transcription
        response_format: Response format (json, text, srt, verbose_json, vtt)
    
    Returns:
        Dictionary with transcription results
    """
    try:
        if not audio_path:
            return {
                "success": False,
                "error": "Audio path cannot be empty"
            }
        
        # Check if file exists
        path = Path(audio_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                audio_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_path}"
                }
        
        result = speech_recognition.speech_client.transcribe_audio(
            audio_path=audio_path,
            model=model,
            language=language,
            prompt=prompt,
            response_format=response_format
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Audio transcription failed: {str(e)}"
        }

@mcp.tool()
def transcribe_with_timestamps(audio_path: str, model: str = "whisper-1") -> Dict[str, Any]:
    """
    Transcribe audio with detailed timestamps and segments.
    
    Args:
        audio_path: Path to the audio file
        model: Speech recognition model to use
    
    Returns:
        Dictionary with detailed transcription results including timestamps
    """
    try:
        if not audio_path:
            return {
                "success": False,
                "error": "Audio path cannot be empty"
            }
        
        # Check if file exists
        path = Path(audio_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                audio_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_path}"
                }
        
        result = speech_recognition.transcribe_with_timestamps(audio_path, model)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Timestamp transcription failed: {str(e)}"
        }

@mcp.tool()
@mcp.tool()
def transcribe_to_srt(audio_path: str, model: str = "glm-asr") -> Dict[str, Any]:
    """
    Transcribe audio to SRT subtitle format.
    
    Args:
        audio_path: Path to the audio file (.wav/.mp3, ≤25MB, ≤60s)
        model: Speech recognition model to use (glm-asr)
    
    Returns:
        Dictionary with SRT format transcription
    """
    try:
        if not audio_path:
            return {
                "success": False,
                "error": "Audio path cannot be empty"
            }
        
        # Check if file exists
        path = Path(audio_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                audio_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_path}"
                }
        
        result = speech_recognition.transcribe_to_srt(audio_path, model)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"SRT transcription failed: {str(e)}"
        }

@mcp.tool()
@mcp.tool()
def batch_transcribe_audio(audio_files: List[str], model: str = "glm-asr") -> Dict[str, Any]:
    """
    Batch transcribe multiple audio files.
    
    Args:
        audio_files: List of audio file paths (.wav/.mp3, ≤25MB, ≤60s each)
        model: Speech recognition model to use (glm-asr)
    
    Returns:
        Dictionary with batch transcription results
    """
    try:
        if not audio_files:
            return {
                "success": False,
                "error": "Audio files list cannot be empty"
            }
        
        # Validate file paths
        valid_files = []
        for audio_path in audio_files:
            path = Path(audio_path)
            if path.exists():
                valid_files.append(str(path))
            else:
                # Try relative to uploads directory
                upload_path = UPLOADS_DIR / path.name
                if upload_path.exists():
                    valid_files.append(str(upload_path))
        
        if not valid_files:
            return {
                "success": False,
                "error": "No valid audio files found"
            }
        
        result = speech_recognition.batch_transcribe(valid_files, model)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch transcription failed: {str(e)}"
        }

@mcp.tool()
def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """
    Get information about an audio file.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        Dictionary with audio file information
    """
    try:
        if not audio_path:
            return {
                "success": False,
                "error": "Audio path cannot be empty"
            }
        
        # Check if file exists
        path = Path(audio_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                path = upload_path
            else:
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_path}"
                }
        
        # Get file information
        file_size = path.stat().st_size
        file_ext = path.suffix.lower()
        
        # Validate audio format
        validation = speech_client._validate_audio_file(str(path))
        
        return {
            "success": True,
            "filename": path.name,
            "path": str(path),
            "size": file_size,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "format": file_ext,
            "validation": validation,
            "supported": validation["valid"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get audio info: {str(e)}"
        }

@mcp.tool()
def test_speech_api(test_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Test the speech-to-text API connection and functionality.
    
    Args:
        test_file: Optional path to a test audio file
    
    Returns:
        Dictionary with test results
    """
    try:
        # Test API connection
        connection_test = speech_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_formats": speech_client.get_supported_formats(),
            "available_models": list(speech_client.speech_models.keys())
        }
        
        # If test file provided, try transcription
        if test_file:
            path = Path(test_file)
            if path.exists() or (UPLOADS_DIR / path.name).exists():
                if not path.exists():
                    path = UPLOADS_DIR / path.name
                
                transcription_test = speech_client.transcribe_audio(str(path))
                result["transcription_test"] = transcription_test
            else:
                result["transcription_test"] = {
                    "success": False,
                    "error": f"Test file not found: {test_file}"
                }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"API test failed: {str(e)}"
        }

@mcp.tool()
def upload_file(file_content: str, filename: str, encoding: str = "base64") -> Dict[str, Any]:
    """
    Upload an audio file to the server for transcription.
    
    Args:
        file_content: File content (base64 encoded or text)
        filename: Name of the file
        encoding: Encoding type (base64, text)
    
    Returns:
        Dictionary with upload result
    """
    try:
        if not file_content or not filename:
            return {
                "success": False,
                "error": "File content and filename are required"
            }
        
        # Create unique filename to avoid conflicts
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file based on encoding
        if encoding == "base64":
            import base64
            try:
                file_data = base64.b64decode(file_content)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Base64 decoding failed: {str(e)}"
                }
        else:
            # Assume text content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"File upload failed: {str(e)}"
        }

@mcp.tool()
def get_supported_formats() -> Dict[str, Any]:
    """
    Get list of supported audio formats for speech-to-text conversion.
    
    Returns:
        Dictionary with supported formats
    """
    try:
        formats = speech_client.get_supported_formats()
        models = speech_client.get_model_info()
        return {
            "success": True,
            "formats": formats,
            "models": list(models.keys()),
            "model_details": models
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get supported formats: {str(e)}"
        }

@mcp.tool()
def list_uploaded_files() -> Dict[str, Any]:
    """
    List all uploaded audio files available for transcription.
    
    Returns:
        Dictionary with file list
    """
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
        
        return {
            "success": True,
            "files": files,
            "total": len(files)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式语音转文本模式"""
    print("=" * 60)
    print("🎤 AI语音转文本转换器 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 语音转文本")
    print("2. 带时间戳转录")
    print("3. 生成SRT字幕")
    print("4. 批量转录")
    print("5. 查看音频信息")
    print("6. 测试API连接")
    print("7. 网络诊断")
    print("8. 启动MCP服务器")
    print("9. 启动Web服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-9): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_audio_transcription()
            elif choice == "2":
                handle_timestamp_transcription()
            elif choice == "3":
                handle_srt_generation()
            elif choice == "4":
                handle_batch_transcription()
            elif choice == "5":
                handle_audio_info()
            elif choice == "6":
                handle_api_test()
            elif choice == "7":
                handle_network_diagnostic()
            elif choice == "8":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            elif choice == "9":
                print("🌐 启动Web服务器...")
                import subprocess
                subprocess.run([sys.executable, "speech_server.py"])
                break
            else:
                print("❌ 无效选择，请输入0-9")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_audio_transcription():
    """处理音频转录"""
    print("\n🎤 语音转文本")
    audio_path = input("请输入音频文件路径: ").strip()
    if not audio_path:
        print("❌ 音频路径不能为空")
        return
    
    language = input("请输入音频语言 (可选，如zh/en): ").strip() or None
    prompt = input("请输入提示词 (可选): ").strip() or None
    
    print("🔍 转录中...")
    result = speech_recognition.transcribe_audio(audio_path, language=language, prompt=prompt)
    
    if result["success"]:
        print(f"✅ 转录结果:\n{result['text']}")
        if result.get('language'):
            print(f"检测到的语言: {result['language']}")
    else:
        print(f"❌ 转录失败: {result['error']}")

def handle_timestamp_transcription():
    """处理带时间戳转录"""
    print("\n⏰ 带时间戳转录")
    audio_path = input("请输入音频文件路径: ").strip()
    if not audio_path:
        print("❌ 音频路径不能为空")
        return
    
    print("🔍 转录中...")
    result = speech_recognition.transcribe_with_timestamps(audio_path)
    
    if result["success"]:
        print(f"✅ 转录结果:\n{result['text']}")
        if result.get('segments'):
            print("\n时间戳信息:")
            for segment in result['segments'][:5]:  # 只显示前5个片段
                print(f"  {segment.get('start', 0):.2f}s - {segment.get('end', 0):.2f}s: {segment.get('text', '')}")
    else:
        print(f"❌ 转录失败: {result['error']}")

def handle_srt_generation():
    """处理SRT字幕生成"""
    print("\n📝 生成SRT字幕")
    audio_path = input("请输入音频文件路径: ").strip()
    if not audio_path:
        print("❌ 音频路径不能为空")
        return
    
    print("🔍 生成字幕中...")
    result = speech_recognition.transcribe_to_srt(audio_path)
    
    if result["success"]:
        print("✅ SRT字幕生成成功!")
        srt_content = result.get('srt_content', result.get('text', ''))
        print("SRT内容预览:")
        print(srt_content[:500] + "..." if len(srt_content) > 500 else srt_content)
        
        # 保存SRT文件
        srt_path = Path(audio_path).with_suffix('.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        print(f"SRT文件已保存到: {srt_path}")
    else:
        print(f"❌ 字幕生成失败: {result['error']}")

def handle_batch_transcription():
    """处理批量转录"""
    print("\n📁 批量转录")
    print("请输入音频文件路径 (每行一个，空行结束):")
    
    audio_files = []
    while True:
        path = input().strip()
        if not path:
            break
        audio_files.append(path)
    
    if not audio_files:
        print("❌ 没有输入任何文件")
        return
    
    print(f"🔍 批量转录 {len(audio_files)} 个文件...")
    result = speech_recognition.batch_transcribe(audio_files)
    
    if result["success"]:
        print(f"✅ 批量转录完成!")
        print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")
        
        for item in result['results']:
            file_result = item['result']
            if file_result['success']:
                print(f"✅ {item['file']}: {file_result['text'][:100]}...")
            else:
                print(f"❌ {item['file']}: {file_result['error']}")
    else:
        print(f"❌ 批量转录失败: {result['error']}")

def handle_audio_info():
    """处理音频信息查看"""
    print("\n📊 音频信息")
    audio_path = input("请输入音频文件路径: ").strip()
    if not audio_path:
        print("❌ 音频路径不能为空")
        return
    
    result = get_audio_info(audio_path)
    
    if result["success"]:
        print("✅ 音频信息:")
        print(f"  文件名: {result['filename']}")
        print(f"  大小: {result['size_mb']} MB")
        print(f"  格式: {result['format']}")
        print(f"  支持转录: {'是' if result['supported'] else '否'}")
        if not result['supported']:
            print(f"  错误: {result['validation']['error']}")
    else:
        print(f"❌ 获取信息失败: {result['error']}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_file = input("请输入测试音频文件路径 (可选): ").strip() or None
    
    print("🔍 测试中...")
    result = test_speech_api(test_file)
    
    if result["success"]:
        print("✅ API测试结果:")
        print(f"  连接状态: {'正常' if result['connection_test']['success'] else '失败'}")
        print(f"  可用模型: {', '.join(result['available_models'])}")
        print(f"  支持格式: {result['supported_formats']}")
        
        if 'transcription_test' in result:
            trans_result = result['transcription_test']
            if trans_result['success']:
                print(f"  测试转录: {trans_result['text'][:100]}...")
            else:
                print(f"  测试转录失败: {trans_result['error']}")
    else:
        print(f"❌ API测试失败: {result['error']}")

def handle_network_diagnostic():
    """处理网络诊断"""
    print("\n🔍 网络诊断")
    print("正在检查网络连接和API可达性...")
    
    try:
        diagnostic = NetworkDiagnostic()
        diagnostic.run_full_diagnostic()
    except Exception as e:
        print(f"❌ 网络诊断失败: {str(e)}")
        print("💡 建议:")
        print("  1. 检查网络连接")
        print("  2. 确认API密钥配置正确")
        print("  3. 尝试使用VPN或代理")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--mcp":
            print("🔧 启动MCP服务器模式...")
            mcp.run(transport="sse")
        elif sys.argv[1] == "--web":
            print("🌐 启动Web服务器模式...")
            import subprocess
            subprocess.run([sys.executable, "speech_server.py"])
        elif sys.argv[1] == "--test":
            print("🧪 运行测试...")
            import subprocess
            subprocess.run([sys.executable, "test_speech.py"])
        else:
            print("❌ 未知参数，支持的参数: --mcp, --web, --test")
    else:
        # 默认运行交互式模式
        run_interactive_mode()