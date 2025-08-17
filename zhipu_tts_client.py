"""
智谱文本转语音客户端
支持多种语音类型和音频格式
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ZhipuTTSClient:
    """智谱文本转语音客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱TTS客户端
        
        Args:
            api_key: 智谱API密钥，如果不提供则从配置文件或环境变量获取
        """
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("智谱API密钥未设置。请在config.json中配置或设置环境变量ZHIPU_API_KEY")
        
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/audio/speech"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 支持的语音类型
        self.voice_types = {
            "tongtong": "童童 - 女声，温柔甜美",
            "xiaoxiao": "小小 - 女声，活泼可爱", 
            "xiaomo": "小墨 - 男声，沉稳磁性",
            "xiaobei": "小贝 - 女声，知性优雅",
            "xiaoxuan": "小轩 - 男声，阳光帅气"
        }
        
        # 支持的音频格式
        self.audio_formats = ["wav", "mp3"]
        
        # 支持的模型
        self.tts_models = {
            "cogtts": "CogTTS - 智谱文本转语音模型"
        }
    
    def _get_api_key(self) -> Optional[str]:
        """
        获取API密钥，优先级：环境变量 > config.json
        
        Returns:
            API密钥字符串，如果未找到则返回None
        """
        # 首先尝试从环境变量获取
        api_key = os.getenv("ZHIPU_API_KEY")
        if api_key:
            return api_key
        
        # 然后尝试从config.json获取
        try:
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get("api_keys", {}).get("zhipu")
                    if api_key and api_key != "your_zhipu_api_key_here":
                        return api_key
        except Exception as e:
            logger.warning(f"读取config.json失败: {str(e)}")
        
        return None
    
    def text_to_speech(
        self, 
        text: str, 
        voice: str = "tongtong",
        model: str = "cogtts",
        response_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            voice: 语音类型 (tongtong, xiaoxiao, xiaomo, xiaobei, xiaoxuan)
            model: 模型名称 (cogtts)
            response_format: 音频格式 (wav, mp3)
            
        Returns:
            包含转换结果的字典
        """
        try:
            # 验证参数
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "文本内容不能为空"
                }
            
            if voice not in self.voice_types:
                return {
                    "success": False,
                    "error": f"不支持的语音类型: {voice}。支持的类型: {list(self.voice_types.keys())}"
                }
            
            if response_format not in self.audio_formats:
                return {
                    "success": False,
                    "error": f"不支持的音频格式: {response_format}。支持的格式: {self.audio_formats}"
                }
            
            # 构建请求数据
            payload = {
                "model": model,
                "input": text.strip(),
                "voice": voice,
                "response_format": response_format
            }
            
            # 发送请求
            logger.info(f"发送TTS请求: {payload}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # 检查响应状态
            if response.status_code == 200:
                # 成功返回音频数据
                audio_data = response.content
                
                return {
                    "success": True,
                    "audio_data": audio_data,
                    "text": text,
                    "voice": voice,
                    "format": response_format,
                    "size": len(audio_data),
                    "content_type": response.headers.get("content-type", f"audio/{response_format}")
                }
            else:
                # 请求失败
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "未知错误")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                
                return {
                    "success": False,
                    "error": f"TTS请求失败: {error_msg}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时，请检查网络连接"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "网络连接错误，请检查网络设置"
            }
        except Exception as e:
            logger.error(f"TTS转换异常: {str(e)}")
            return {
                "success": False,
                "error": f"TTS转换失败: {str(e)}"
            }
    
    def save_audio(
        self, 
        audio_data: bytes, 
        filename: str, 
        output_dir: str = "outputs"
    ) -> Dict[str, Any]:
        """
        保存音频数据到文件
        
        Args:
            audio_data: 音频数据字节流
            filename: 文件名
            output_dir: 输出目录
            
        Returns:
            保存结果
        """
        try:
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # 构建完整文件路径
            file_path = output_path / filename
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "size": len(audio_data),
                "directory": str(output_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"保存音频文件失败: {str(e)}"
            }
    
    def text_to_speech_file(
        self,
        text: str,
        filename: Optional[str] = None,
        voice: str = "tongtong",
        model: str = "cogtts",
        response_format: str = "wav",
        output_dir: str = "outputs"
    ) -> Dict[str, Any]:
        """
        将文本转换为语音并保存为文件
        
        Args:
            text: 要转换的文本
            filename: 输出文件名，如果不提供则自动生成
            voice: 语音类型
            model: 模型名称
            response_format: 音频格式
            output_dir: 输出目录
            
        Returns:
            转换和保存结果
        """
        try:
            # 执行文本转语音
            tts_result = self.text_to_speech(text, voice, model, response_format)
            
            if not tts_result["success"]:
                return tts_result
            
            # 生成文件名
            if not filename:
                timestamp = int(time.time())
                safe_text = "".join(c for c in text[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_text = safe_text.replace(' ', '_')
                filename = f"tts_{safe_text}_{timestamp}.{response_format}"
            
            # 确保文件名有正确的扩展名
            if not filename.endswith(f".{response_format}"):
                filename = f"{filename}.{response_format}"
            
            # 保存音频文件
            save_result = self.save_audio(tts_result["audio_data"], filename, output_dir)
            
            if save_result["success"]:
                return {
                    "success": True,
                    "text": text,
                    "voice": voice,
                    "format": response_format,
                    "file_path": save_result["file_path"],
                    "filename": save_result["filename"],
                    "size": save_result["size"],
                    "audio_data": tts_result["audio_data"]
                }
            else:
                return save_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"文本转语音文件失败: {str(e)}"
            }
    
    def batch_text_to_speech(
        self,
        texts: List[str],
        voice: str = "tongtong",
        model: str = "cogtts", 
        response_format: str = "wav",
        output_dir: str = "outputs"
    ) -> Dict[str, Any]:
        """
        批量文本转语音
        
        Args:
            texts: 文本列表
            voice: 语音类型
            model: 模型名称
            response_format: 音频格式
            output_dir: 输出目录
            
        Returns:
            批量转换结果
        """
        try:
            if not texts:
                return {
                    "success": False,
                    "error": "文本列表不能为空"
                }
            
            results = []
            successful = 0
            failed = 0
            
            for i, text in enumerate(texts):
                print(f"正在处理第 {i+1}/{len(texts)} 个文本...")
                
                # 生成文件名
                timestamp = int(time.time())
                filename = f"batch_tts_{i+1}_{timestamp}.{response_format}"
                
                # 转换单个文本
                result = self.text_to_speech_file(
                    text=text,
                    filename=filename,
                    voice=voice,
                    model=model,
                    response_format=response_format,
                    output_dir=output_dir
                )
                
                results.append({
                    "index": i + 1,
                    "text": text,
                    "result": result
                })
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                
                # 短暂延迟避免请求过快
                time.sleep(0.5)
            
            return {
                "success": True,
                "total": len(texts),
                "successful": successful,
                "failed": failed,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"批量转换失败: {str(e)}"
            }
    
    def get_voice_types(self) -> Dict[str, str]:
        """获取支持的语音类型"""
        return self.voice_types.copy()
    
    def get_audio_formats(self) -> List[str]:
        """获取支持的音频格式"""
        return self.audio_formats.copy()
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return self.tts_models.copy()
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 使用简短文本测试连接
            test_text = "测试"
            result = self.text_to_speech(test_text, voice="tongtong")
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "API连接正常",
                    "test_audio_size": result["size"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API连接测试失败: {result['error']}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"连接测试异常: {str(e)}"
            }
    
    def validate_text(self, text: str) -> Dict[str, Any]:
        """验证文本内容"""
        try:
            if not text:
                return {
                    "valid": False,
                    "error": "文本不能为空"
                }
            
            text = text.strip()
            if not text:
                return {
                    "valid": False,
                    "error": "文本不能只包含空白字符"
                }
            
            # 检查文本长度（智谱API可能有长度限制）
            if len(text) > 5000:
                return {
                    "valid": False,
                    "error": "文本长度超过5000字符限制"
                }
            
            return {
                "valid": True,
                "length": len(text),
                "word_count": len(text.split())
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"文本验证失败: {str(e)}"
            }