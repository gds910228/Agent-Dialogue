"""
智谱清言视觉模型 API 客户端
支持多模态内容（文本、图片、视频、文件）
基于智谱官方文档：https://docs.bigmodel.cn/api-reference/模型-api/对话补全#视频
"""

import json
import requests
import time
import uuid
import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuVisionClient:
    def __init__(self, config_path: str = "config.json"):
        """初始化智谱视觉模型客户端"""
        self.config = self.load_config(config_path)
        self.api_key = self.config["api_keys"]["zhipu"]
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        
        # 支持的模型列表
        self.vision_models = {
            "glm-4v": "GLM-4V 视觉理解模型",
            "glm-4v-plus": "GLM-4V Plus 增强视觉模型"
        }
        
        # 支持的文件类型
        self.supported_image_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.supported_video_types = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        self.supported_document_types = {'.pdf', '.doc', '.docx', '.txt', '.md'}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {"api_keys": {"zhipu": ""}}
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_file_to_base64(self, file_path: str) -> Dict[str, str]:
        """将文件编码为base64格式"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                # 根据文件扩展名推断MIME类型
                ext = file_path.suffix.lower()
                if ext in self.supported_image_types:
                    mime_type = f"image/{ext[1:]}"
                elif ext in self.supported_video_types:
                    mime_type = f"video/{ext[1:]}"
                elif ext in self.supported_document_types:
                    mime_type = "application/octet-stream"
                else:
                    mime_type = "application/octet-stream"
            
            # 读取文件并编码
            with open(file_path, 'rb') as f:
                file_content = f.read()
                base64_content = base64.b64encode(file_content).decode('utf-8')
            
            return {
                "type": self._get_content_type(file_path.suffix.lower()),
                "media": f"data:{mime_type};base64,{base64_content}",
                "filename": file_path.name,
                "size": len(file_content)
            }
            
        except Exception as e:
            logger.error(f"文件编码失败: {e}")
            raise
    
    def _get_content_type(self, file_extension: str) -> str:
        """根据文件扩展名确定内容类型"""
        if file_extension in self.supported_image_types:
            return "image"
        elif file_extension in self.supported_video_types:
            return "video"
        elif file_extension in self.supported_document_types:
            return "document"
        else:
            return "file"
    
    def create_multimodal_message(self, 
                                text: str = "",
                                files: List[str] = None,
                                urls: List[str] = None) -> List[Dict[str, Any]]:
        """创建多模态消息内容"""
        content = []
        
        # 添加文本内容
        if text.strip():
            content.append({
                "type": "text",
                "text": text
            })
        
        # 添加文件内容
        if files:
            for file_path in files:
                try:
                    file_data = self.encode_file_to_base64(file_path)
                    
                    if file_data["type"] == "image":
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": file_data["media"]
                            }
                        })
                    elif file_data["type"] == "video":
                        content.append({
                            "type": "video_url",
                            "video_url": {
                                "url": file_data["media"]
                            }
                        })
                    else:
                        # 对于文档和其他文件类型，作为附件处理
                        content.append({
                            "type": "file",
                            "file": {
                                "url": file_data["media"],
                                "filename": file_data["filename"]
                            }
                        })
                        
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 失败: {e}")
                    continue
        
        # 添加URL内容
        if urls:
            for url in urls:
                # 简单判断URL类型
                if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": url
                        }
                    })
                elif any(url.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov']):
                    content.append({
                        "type": "video_url",
                        "video_url": {
                            "url": url
                        }
                    })
                else:
                    # 作为通用链接处理
                    content.append({
                        "type": "text",
                        "text": f"链接内容: {url}"
                    })
        
        return content
    
    def analyze_multimodal_content(self, 
                                 text: str = "",
                                 files: List[str] = None,
                                 urls: List[str] = None,
                                 model: str = "glm-4v",
                                 temperature: float = 0.7,
                                 max_tokens: int = 1024) -> Dict[str, Any]:
        """
        分析多模态内容
        
        Args:
            text: 文本内容或问题
            files: 本地文件路径列表
            urls: 网络资源URL列表
            model: 使用的模型名称
            temperature: 生成温度
            max_tokens: 最大token数
            
        Returns:
            分析结果
        """
        try:
            # 创建多模态消息内容
            content = self.create_multimodal_message(text, files, urls)
            
            if not content:
                return {
                    "success": False,
                    "error": "没有提供任何内容进行分析"
                }
            
            # 构建请求数据
            request_data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 详细日志
            logger.info("=" * 60)
            logger.info("智谱视觉模型API调用:")
            logger.info(f"  模型: {model}")
            logger.info(f"  内容类型数量: {len(content)}")
            logger.info(f"  温度: {temperature}")
            logger.info(f"  最大tokens: {max_tokens}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.get_headers(),
                json=request_data,
                timeout=60
            )
            
            logger.info(f"  响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 提取回复内容
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0]["message"]
                    content_text = message.get("content", "")
                    
                    return {
                        "success": True,
                        "content": content_text,
                        "model": model,
                        "usage": result.get("usage", {}),
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "success": False,
                        "error": "响应格式异常",
                        "details": result
                    }
            else:
                error_info = response.json() if response.content else {}
                logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API错误: {response.status_code}",
                    "details": error_info
                }
                
        except Exception as e:
            logger.error(f"多模态内容分析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def describe_image(self, image_path: str, question: str = "请描述这张图片") -> Dict[str, Any]:
        """描述图片内容"""
        return self.analyze_multimodal_content(
            text=question,
            files=[image_path],
            model="glm-4v"
        )
    
    def analyze_video(self, video_path: str, question: str = "请分析这个视频的内容") -> Dict[str, Any]:
        """分析视频内容"""
        return self.analyze_multimodal_content(
            text=question,
            files=[video_path],
            model="glm-4v-plus"  # 使用增强模型处理视频
        )
    
    def extract_document_info(self, document_path: str, question: str = "请总结这个文档的主要内容") -> Dict[str, Any]:
        """提取文档信息"""
        return self.analyze_multimodal_content(
            text=question,
            files=[document_path],
            model="glm-4v"
        )
    
    def compare_contents(self, files: List[str], question: str = "请比较这些内容的异同") -> Dict[str, Any]:
        """比较多个内容"""
        return self.analyze_multimodal_content(
            text=question,
            files=files,
            model="glm-4v-plus"
        )
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取支持的文件格式"""
        return {
            "images": list(self.supported_image_types),
            "videos": list(self.supported_video_types),
            "documents": list(self.supported_document_types)
        }