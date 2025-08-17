"""
AI Text-to-Speech Converter - Main Entry Point

A comprehensive AI text-to-speech system supporting multiple voice types and audio formats.
Provides both MCP server capabilities and direct text-to-speech functionality.
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
from zhipu_tts_client import ZhipuTTSClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Text-to-Speech Converter")

# Create directories for storing files
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Initialize clients
tts_client = ZhipuTTSClient()

# Text-to-Speech Entry Point
class TextToSpeech:
    """主要的文本转语音入口类"""
    
    def __init__(self):
        self.tts_client = tts_client
        self.outputs_dir = OUTPUTS_DIR
        
    
    
    def text_to_speech(self, 
                      text: str,
                      voice: str = "tongtong",
                      model: str = "cogtts",
                      response_format: str = "wav") -> Dict[str, Any]:
        """
        主要的文本转语音入口
        
        Args:
            text: 要转换的文本
            voice: 语音类型 (tongtong, xiaoxiao, xiaomo, xiaobei, xiaoxuan)
            model: 使用的模型 (cogtts)
            response_format: 音频格式 (wav, mp3)
            
        Returns:
            转换结果
        """
        return self.tts_client.text_to_speech(
            text=text,
            voice=voice,
            model=model,
            response_format=response_format
        )
    
    def text_to_speech_file(self, text: str, filename: Optional[str] = None, 
                           voice: str = "tongtong", model: str = "cogtts",
                           response_format: str = "wav") -> Dict[str, Any]:
        """文本转语音并保存文件"""
        return self.tts_client.text_to_speech_file(
            text=text, filename=filename, voice=voice, 
            model=model, response_format=response_format,
            output_dir=str(self.outputs_dir)
        )
    
    def batch_text_to_speech(self, texts: List[str], voice: str = "tongtong", 
                            model: str = "cogtts", response_format: str = "wav") -> Dict[str, Any]:
        """批量文本转语音"""
        return self.tts_client.batch_text_to_speech(
            texts=texts, voice=voice, model=model, 
            response_format=response_format, output_dir=str(self.outputs_dir)
        )

# 创建全局文本转语音实例
text_to_speech = TextToSpeech()

@mcp.tool()
def convert_text_to_speech(
    text: str,
    voice: str = "tongtong",
    model: str = "cogtts",
    response_format: str = "wav",
    save_file: bool = True,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert text to speech using Zhipu's text-to-speech API.
    
    Args:
        text: Text to convert to speech
        voice: Voice type (tongtong, xiaoxiao, xiaomo, xiaobei, xiaoxuan)
        model: TTS model to use (cogtts)
        response_format: Audio format (wav, mp3)
        save_file: Whether to save the audio file
        filename: Optional filename for saved audio
    
    Returns:
        Dictionary with conversion results
    """
    try:
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Text cannot be empty"
            }
        
        if save_file:
            result = text_to_speech.text_to_speech_file(
                text=text,
                filename=filename,
                voice=voice,
                model=model,
                response_format=response_format
            )
        else:
            result = text_to_speech.text_to_speech(
                text=text,
                voice=voice,
                model=model,
                response_format=response_format
            )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Text-to-speech conversion failed: {str(e)}"
        }

@mcp.tool()
def batch_text_to_speech(
    texts: List[str],
    voice: str = "tongtong",
    model: str = "cogtts",
    response_format: str = "wav"
) -> Dict[str, Any]:
    """
    Convert multiple texts to speech in batch.
    
    Args:
        texts: List of texts to convert
        voice: Voice type (tongtong, xiaoxiao, xiaomo, xiaobei, xiaoxuan)
        model: TTS model to use (cogtts)
        response_format: Audio format (wav, mp3)
    
    Returns:
        Dictionary with batch conversion results
    """
    try:
        if not texts:
            return {
                "success": False,
                "error": "Texts list cannot be empty"
            }
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not valid_texts:
            return {
                "success": False,
                "error": "No valid texts found"
            }
        
        result = text_to_speech.batch_text_to_speech(
            texts=valid_texts,
            voice=voice,
            model=model,
            response_format=response_format
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch text-to-speech conversion failed: {str(e)}"
        }

@mcp.tool()
def get_voice_types() -> Dict[str, Any]:
    """
    Get available voice types for text-to-speech conversion.
    
    Returns:
        Dictionary with available voice types and their descriptions
    """
    try:
        voice_types = tts_client.get_voice_types()
        audio_formats = tts_client.get_audio_formats()
        model_info = tts_client.get_model_info()
        
        return {
            "success": True,
            "voice_types": voice_types,
            "audio_formats": audio_formats,
            "models": model_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get voice types: {str(e)}"
        }

@mcp.tool()
def validate_text_input(text: str) -> Dict[str, Any]:
    """
    Validate text input for text-to-speech conversion.
    
    Args:
        text: Text to validate
    
    Returns:
        Dictionary with validation results
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "Text cannot be empty"
            }
        
        result = tts_client.validate_text(text)
        return {
            "success": True,
            "validation": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Text validation failed: {str(e)}"
        }

@mcp.tool()
def get_audio_file_info(audio_path: str) -> Dict[str, Any]:
    """
    Get information about a generated audio file.
    
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
            # Try relative to outputs directory
            output_path = OUTPUTS_DIR / path.name
            if output_path.exists():
                path = output_path
            else:
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_path}"
                }
        
        # Get file information
        file_size = path.stat().st_size
        file_ext = path.suffix.lower()
        
        return {
            "success": True,
            "filename": path.name,
            "path": str(path),
            "size": file_size,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "format": file_ext,
            "supported": file_ext in ['.wav', '.mp3']
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get audio info: {str(e)}"
        }

@mcp.tool()
def test_tts_api(test_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Test the text-to-speech API connection and functionality.
    
    Args:
        test_text: Optional test text for conversion
    
    Returns:
        Dictionary with test results
    """
    try:
        # Test API connection
        connection_test = tts_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "voice_types": tts_client.get_voice_types(),
            "audio_formats": tts_client.get_audio_formats(),
            "available_models": list(tts_client.get_model_info().keys())
        }
        
        # If test text provided, try conversion
        if test_text:
            conversion_test = tts_client.text_to_speech(test_text)
            if conversion_test["success"]:
                result["conversion_test"] = {
                    "success": True,
                    "audio_size": conversion_test["size"],
                    "format": conversion_test["format"]
                }
            else:
                result["conversion_test"] = conversion_test
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"API test failed: {str(e)}"
        }

@mcp.tool()
def save_text_content(text_content: str, filename: str) -> Dict[str, Any]:
    """
    Save text content to a file for later TTS conversion.
    
    Args:
        text_content: Text content to save
        filename: Name of the file
    
    Returns:
        Dictionary with save result
    """
    try:
        if not text_content or not filename:
            return {
                "success": False,
                "error": "Text content and filename are required"
            }
        
        # Create unique filename to avoid conflicts
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".txt"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # Save text file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
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
            "error": f"File save failed: {str(e)}"
        }

@mcp.tool()
def get_supported_options() -> Dict[str, Any]:
    """
    Get list of supported options for text-to-speech conversion.
    
    Returns:
        Dictionary with supported options
    """
    try:
        voice_types = tts_client.get_voice_types()
        audio_formats = tts_client.get_audio_formats()
        models = tts_client.get_model_info()
        return {
            "success": True,
            "voice_types": voice_types,
            "audio_formats": audio_formats,
            "models": list(models.keys()),
            "model_details": models
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get supported options: {str(e)}"
        }

@mcp.tool()
def list_generated_files() -> Dict[str, Any]:
    """
    List all generated audio files.
    
    Returns:
        Dictionary with file list
    """
    try:
        files = []
        for file_path in OUTPUTS_DIR.iterdir():
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
    """运行交互式文本转语音模式"""
    print("=" * 60)
    print("🔊 AI文本转语音转换器 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 文本转语音")
    print("2. 批量文本转语音")
    print("3. 查看语音类型")
    print("4. 查看生成的音频文件")
    print("5. 测试API连接")
    print("6. 网络诊断")
    print("7. 启动MCP服务器")
    print("8. 启动Web服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-8): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_text_to_speech()
            elif choice == "2":
                handle_batch_text_to_speech()
            elif choice == "3":
                handle_voice_types()
            elif choice == "4":
                handle_list_audio_files()
            elif choice == "5":
                handle_api_test()
            elif choice == "6":
                handle_network_diagnostic()
            elif choice == "7":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            elif choice == "8":
                print("🌐 启动Web服务器...")
                import subprocess
                subprocess.run([sys.executable, "tts_server.py"])
                break
            else:
                print("❌ 无效选择，请输入0-8")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_text_to_speech():
    """处理文本转语音"""
    print("\n🔊 文本转语音")
    text = input("请输入要转换的文本: ").strip()
    if not text:
        print("❌ 文本内容不能为空")
        return
    
    # 显示可用的语音类型
    voice_types = tts_client.get_voice_types()
    print("\n可用的语音类型:")
    for voice, desc in voice_types.items():
        print(f"  {voice}: {desc}")
    
    voice = input(f"\n请选择语音类型 (默认: tongtong): ").strip() or "tongtong"
    format_choice = input("请选择音频格式 (wav/mp3，默认: wav): ").strip() or "wav"
    
    print("🔍 转换中...")
    result = text_to_speech.text_to_speech_file(
        text=text, 
        voice=voice, 
        response_format=format_choice
    )
    
    if result["success"]:
        print(f"✅ 转换成功!")
        print(f"文件路径: {result['file_path']}")
        print(f"文件大小: {result['size']} 字节")
        print(f"语音类型: {result['voice']}")
        print(f"音频格式: {result['format']}")
    else:
        print(f"❌ 转换失败: {result['error']}")

def handle_batch_text_to_speech():
    """处理批量文本转语音"""
    print("\n📁 批量文本转语音")
    print("请输入要转换的文本 (每行一个，空行结束):")
    
    texts = []
    while True:
        text = input().strip()
        if not text:
            break
        texts.append(text)
    
    if not texts:
        print("❌ 没有输入任何文本")
        return
    
    # 显示可用的语音类型
    voice_types = tts_client.get_voice_types()
    print("\n可用的语音类型:")
    for voice, desc in voice_types.items():
        print(f"  {voice}: {desc}")
    
    voice = input(f"\n请选择语音类型 (默认: tongtong): ").strip() or "tongtong"
    format_choice = input("请选择音频格式 (wav/mp3，默认: wav): ").strip() or "wav"
    
    print(f"🔍 批量转换 {len(texts)} 个文本...")
    result = text_to_speech.batch_text_to_speech(
        texts=texts, 
        voice=voice, 
        response_format=format_choice
    )
    
    if result["success"]:
        print(f"✅ 批量转换完成!")
        print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")
        
        for item in result['results']:
            file_result = item['result']
            if file_result['success']:
                print(f"✅ 文本 {item['index']}: {file_result['file_path']}")
            else:
                print(f"❌ 文本 {item['index']}: {file_result['error']}")
    else:
        print(f"❌ 批量转换失败: {result['error']}")

def handle_voice_types():
    """处理语音类型查看"""
    print("\n🎭 语音类型信息")
    
    try:
        voice_types = tts_client.get_voice_types()
        audio_formats = tts_client.get_audio_formats()
        models = tts_client.get_model_info()
        
        print("✅ 可用的语音类型:")
        for voice, desc in voice_types.items():
            print(f"  {voice}: {desc}")
        
        print(f"\n支持的音频格式: {', '.join(audio_formats)}")
        
        print("\n可用的模型:")
        for model, desc in models.items():
            print(f"  {model}: {desc}")
            
    except Exception as e:
        print(f"❌ 获取信息失败: {str(e)}")

def handle_list_audio_files():
    """处理音频文件列表查看"""
    print("\n📂 生成的音频文件")
    
    result = list_generated_files()
    
    if result["success"]:
        files = result["files"]
        if files:
            print(f"✅ 找到 {result['total']} 个文件:")
            for file_info in files[:10]:  # 只显示前10个文件
                size_mb = round(file_info['size'] / 1024 / 1024, 2)
                print(f"  {file_info['filename']} ({size_mb} MB, {file_info['type']})")
            
            if len(files) > 10:
                print(f"  ... 还有 {len(files) - 10} 个文件")
        else:
            print("📭 没有找到任何音频文件")
    else:
        print(f"❌ 获取文件列表失败: {result['error']}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_text = input("请输入测试文本 (可选): ").strip() or None
    
    print("🔍 测试中...")
    result = test_tts_api(test_text)
    
    if result["success"]:
        print("✅ API测试结果:")
        print(f"  连接状态: {'正常' if result['connection_test']['success'] else '失败'}")
        print(f"  可用模型: {', '.join(result['available_models'])}")
        print(f"  支持格式: {result['audio_formats']}")
        print(f"  语音类型: {', '.join(result['voice_types'].keys())}")
        
        if 'conversion_test' in result:
            conv_result = result['conversion_test']
            if conv_result['success']:
                print(f"  测试转换: 成功生成 {conv_result['audio_size']} 字节的 {conv_result['format']} 音频")
            else:
                print(f"  测试转换失败: {conv_result['error']}")
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
            subprocess.run([sys.executable, "tts_server.py"])
        elif sys.argv[1] == "--test":
            print("🧪 运行测试...")
            import subprocess
            subprocess.run([sys.executable, "test_tts.py"])
        else:
            print("❌ 未知参数，支持的参数: --mcp, --web, --test")
    else:
        # 默认运行交互式模式
        run_interactive_mode()
