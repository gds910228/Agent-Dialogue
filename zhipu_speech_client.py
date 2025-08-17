"""
智谱语音转文本客户端
支持多种音频格式的语音识别功能
"""

import os
import json
import time
import base64
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

class ZhipuSpeechClient:
    """智谱语音转文本客户端"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.api_key = self._load_api_key()
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        
        # 支持的音频格式
        # 支持的音频格式（根据智谱API实际规格）
        self.supported_formats = {
            "audio": [".wav", ".mp3"]  # 智谱API仅支持 .wav 和 .mp3 格式
        }
        
        # 语音转文本模型配置
        self.speech_models = {
            "glm-asr": {
                "name": "GLM-ASR",
                "description": "智谱语音识别模型",
                "max_file_size": 25 * 1024 * 1024,  # 25MB
                "max_duration": 60,  # 60秒
                "supported_formats": ["wav", "mp3"]
            }
        }
    
    def _load_api_key(self) -> str:
        """加载API密钥"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("api_keys", {}).get("zhipu", "")
            return ""
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return ""
    
    def _validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            验证结果
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                "valid": False,
                "error": f"文件不存在: {file_path}"
            }
        
        # 检查文件扩展名
        # 检查文件扩展名
        ext = path.suffix.lower()
        supported_formats = self.supported_formats["audio"]
        
        if ext not in supported_formats:
            return {
                "valid": False,
                "error": f"不支持的文件格式: {ext}，智谱API仅支持: {', '.join(supported_formats)}"
            }
        
        # 检查文件大小
        file_size = path.stat().st_size
        max_size = self.speech_models["glm-asr"]["max_file_size"]
        
        if file_size > max_size:
            return {
                "valid": False,
                "error": f"文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持: {max_size / 1024 / 1024}MB"
            }
        
        return {
            "valid": True,
            "size": file_size,
            "format": ext,
            "duration": None,  # 智谱API限制音频时长 ≤ 60秒
            "info": f"文件大小: {file_size / 1024 / 1024:.2f}MB，格式: {ext}"
        }
    
    def transcribe_audio(self, 
                        audio_path: str, 
                        model: str = "whisper-1",
                        language: Optional[str] = None,
                        prompt: Optional[str] = None,
                        response_format: str = "json",
                        temperature: float = 0.0) -> Dict[str, Any]:
        """
        语音转文本
        
        Args:
            audio_path: 音频文件路径
            model: 使用的模型
            language: 音频语言（可选，如 'zh', 'en'）
            prompt: 提示词（可选）
            response_format: 响应格式 ('json', 'text', 'srt', 'verbose_json', 'vtt')
            temperature: 采样温度 (0.0-1.0)
            
        Returns:
            转录结果
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "API密钥未配置，请在config.json中设置zhipu API密钥"
                }
            
            # 验证音频文件
            validation = self._validate_audio_file(audio_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"]
                }
            
            # 准备请求
            url = f"{self.base_url}/audio/transcriptions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 准备文件和数据
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (Path(audio_path).name, audio_file, 'audio/mpeg')
                }
                
                data = {
                    'model': model,
                    'response_format': response_format,
                    'temperature': temperature
                }
                
                if language:
                    data['language'] = language
                
                if prompt:
                    data['prompt'] = prompt
                
                # 配置会话和重试
                session = requests.Session()
                
                # 设置适配器
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=2,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST"]
                )
                
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # 发送请求，增加超时和错误处理
                response = session.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    data=data,
                    timeout=(30, 300),  # (连接超时30秒, 读取超时300秒)
                    stream=False
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result.get("text", ""),
                    "language": result.get("language"),
                    "duration": result.get("duration"),
                    "segments": result.get("segments", []),
                    "model": model,
                    "file_info": {
                        "name": Path(audio_path).name,
                        "size": validation["size"],
                        "format": validation["format"]
                    }
                }
            else:
                try:
                    error_info = response.json() if response.content else {"error": "Unknown error"}
                    error_msg = error_info.get('error', {}).get('message', 'Unknown error')
                except:
                    error_msg = response.text or "Unknown error"
                
                return {
                    "success": False,
                    "error": f"API请求失败 ({response.status_code}): {error_msg}"
                }
                
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": f"网络连接失败，请检查网络连接或代理设置。详细错误: {str(e)}"
            }
        except requests.exceptions.Timeout as e:
            return {
                "success": False,
                "error": f"请求超时，音频文件可能过大或网络较慢，请稍后重试。详细错误: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"网络请求异常: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"语音转文本失败: {str(e)}"
            }
    
    
    def transcribe_with_timestamps(self, audio_path: str, model: str = "glm-asr") -> Dict[str, Any]:
        """
        带时间戳的语音转文本
        
        Args:
            audio_path: 音频文件路径
            model: 使用的模型
            
        Returns:
            带时间戳的转录结果
        """
        return self.transcribe_audio(
            audio_path=audio_path,
            model=model,
            response_format="verbose_json"
        )
    
    def transcribe_to_srt(self, audio_path: str, model: str = "glm-asr") -> Dict[str, Any]:
        """
        转录为SRT字幕格式
        
        Args:
            audio_path: 音频文件路径
            model: 使用的模型
            
        Returns:
            SRT格式的转录结果
        """
        result = self.transcribe_audio(
            audio_path=audio_path,
            model=model,
            response_format="srt"
        )
        
        if result["success"]:
            # 对于SRT格式，text字段包含完整的SRT内容
            result["srt_content"] = result["text"]
        
        return result
    
    def batch_transcribe(self, audio_files: List[str], model: str = "glm-asr") -> Dict[str, Any]:
        """
        批量语音转文本
        
        Args:
            audio_files: 音频文件路径列表
            model: 使用的模型
            
        Returns:
            批量转录结果
        """
        results = []
        successful = 0
        failed = 0
        
        for audio_file in audio_files:
            print(f"正在处理: {audio_file}")
            result = self.transcribe_audio(audio_file, model)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
            
            results.append({
                "file": audio_file,
                "result": result
            })
        
        return {
            "success": True,
            "total": len(audio_files),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取支持的文件格式"""
        return self.supported_formats
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return self.speech_models
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接和网络状态"""
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "API密钥未配置，请在config.json中设置zhipu API密钥"
                }
            
            # 验证API密钥格式
            if len(self.api_key) < 10:
                return {
                    "success": False,
                    "error": "API密钥格式不正确，请检查config.json中的zhipu API密钥"
                }
            
            # 测试网络连接
            try:
                import socket
                socket.create_connection(("open.bigmodel.cn", 443), timeout=10)
                network_status = "网络连接正常"
            except Exception as e:
                return {
                    "success": False,
                    "error": f"无法连接到智谱API服务器，请检查网络连接或防火墙设置: {str(e)}"
                }
            
            # 测试HTTP请求
            try:
                response = requests.get("https://open.bigmodel.cn", timeout=10)
                http_status = f"HTTP连接正常 (状态码: {response.status_code})"
            except Exception as e:
                return {
                    "success": False,
                    "error": f"HTTP请求失败，可能需要配置代理: {str(e)}"
                }
            
            return {
                "success": True,
                "message": "API连接测试通过",
                "details": {
                    "api_key_status": "已配置",
                    "network_status": network_status,
                    "http_status": http_status,
                    "available_models": list(self.speech_models.keys())
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"连接测试失败: {str(e)}"
            }

# 创建全局客户端实例
speech_client = ZhipuSpeechClient()

if __name__ == "__main__":
    # 测试代码
    client = ZhipuSpeechClient()
    
    print("智谱语音转文本客户端测试")
    print("=" * 40)
    
    # 测试连接
    test_result = client.test_connection()
    print(f"连接测试: {test_result}")
    
    # 显示支持的格式
    formats = client.get_supported_formats()
    print(f"支持的格式: {formats}")
    
    # 显示模型信息
    models = client.get_model_info()
    print(f"可用模型: {list(models.keys())}")