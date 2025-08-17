"""
智谱图像生成客户端

提供对智谱CogView-4系列模型的图像生成API的访问
支持cogview-4-250304、cogview-4、cogview-3-flash等模型
"""

import os
import json
import time
import uuid
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class ZhipuImageClient:
    """智谱图像生成客户端类"""
    
    def __init__(self, api_key: Optional[str] = None, config_path: str = "config.json"):
        """
        初始化智谱图像生成客户端
        
        Args:
            api_key: API密钥，如果为None则从配置文件读取
            config_path: 配置文件路径
        """
        self.api_key = api_key
        self.config_path = config_path
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        self.supported_models = {
            "cogview-4": "最新的CogView-4模型，提供高质量图像生成",
            "cogview-4-250304": "CogView-4的特定版本，针对特定场景优化",
            "cogview-3-flash": "快速版CogView-3模型，生成速度更快"
        }
        self.supported_sizes = ["1024x1024", "1024x768", "768x1024", "512x512", "768x768"]
        self.quality_options = ["standard", "hd"]
        
        # 如果没有提供API密钥，尝试从配置文件加载
        if not self.api_key:
            self._load_config()
    
    def _load_config(self):
        """从配置文件加载API密钥和其他设置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key")
                    
                    # 可选：加载其他配置
                    if "base_url" in config:
                        self.base_url = config["base_url"]
                    if "supported_models" in config:
                        self.supported_models.update(config["supported_models"])
                    if "supported_sizes" in config:
                        self.supported_sizes = config["supported_sizes"]
                    if "quality_options" in config:
                        self.quality_options = config["quality_options"]
            else:
                print(f"⚠️ 配置文件 {self.config_path} 不存在，使用默认设置")
                
                # 尝试从环境变量加载API密钥
                self.api_key = os.environ.get("ZHIPU_API_KEY")
                
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
            # 尝试从环境变量加载API密钥
            self.api_key = os.environ.get("ZHIPU_API_KEY")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        if not self.api_key:
            raise ValueError("API密钥未设置，请在初始化时提供API密钥或在配置文件中设置")
        
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接
        
        Returns:
            测试结果
        """
        try:
            # 发送一个简单的请求来测试连接
            headers = self._get_headers()
            response = requests.post(
                self.base_url,
                headers=headers,
                json={
                    "model": "cogview-3-flash",
                    "prompt": "测试连接",
                    "size": "512x512",
                    "quality": "standard"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "API连接正常"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"API连接失败: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API连接测试失败: {str(e)}"
            }
    
    def get_supported_models(self) -> Dict[str, str]:
        """
        获取支持的模型列表
        
        Returns:
            支持的模型及其描述
        """
        return self.supported_models
    
    def get_supported_sizes(self) -> List[str]:
        """
        获取支持的图像尺寸
        
        Returns:
            支持的图像尺寸列表
        """
        return self.supported_sizes
    
    def get_quality_options(self) -> List[str]:
        """
        获取支持的质量选项
        
        Returns:
            支持的质量选项列表
        """
        return self.quality_options
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        验证提示词
        
        Args:
            prompt: 要验证的提示词
            
        Returns:
            验证结果
        """
        # 简单验证
        result = {
            "valid": True,
            "length": len(prompt),
            "warnings": []
        }
        
        # 检查长度
        if len(prompt) < 5:
            result["warnings"].append("提示词过短，可能导致生成结果不理想")
        elif len(prompt) > 500:
            result["warnings"].append("提示词过长，可能被截断")
        
        # 检查语言
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in prompt)
        has_english = any('a' <= char.lower() <= 'z' for char in prompt)
        
        if has_chinese and has_english:
            result["language"] = "混合(中英文)"
        elif has_chinese:
            result["language"] = "中文"
        elif has_english:
            result["language"] = "英文"
        else:
            result["language"] = "其他"
            
        return result
    
    def generate_image(self, 
                      prompt: str,
                      model: str = "cogview-4",
                      size: str = "1024x1024",
                      quality: str = "standard") -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 图像生成提示词
            model: 使用的模型 (cogview-4, cogview-4-250304, cogview-3-flash)
            size: 图像尺寸 (1024x1024, 1024x768, 768x1024, 512x512, 768x768)
            quality: 图像质量 (standard, hd)
            
        Returns:
            生成结果
        """
        try:
            # 验证参数
            if not prompt:
                return {"success": False, "error": "提示词不能为空"}
            
            if model not in self.supported_models:
                return {"success": False, "error": f"不支持的模型: {model}"}
            
            if size not in self.supported_sizes:
                return {"success": False, "error": f"不支持的图像尺寸: {size}"}
            
            if quality not in self.quality_options:
                return {"success": False, "error": f"不支持的质量选项: {quality}"}
            
            # 准备请求数据
            request_data = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "quality": quality
            }
            
            # 发送请求
            headers = self._get_headers()
            response = requests.post(
                self.base_url,
                headers=headers,
                json=request_data,
                timeout=30  # 图像生成可能需要较长时间
            )
            
            # 处理响应
            if response.status_code == 200:
                response_data = response.json()
                
                # 示例响应: {"created":1755397896,"data":[{"url":"https://aigc-files.bigmodel.cn/api/cogview/202508171031365ac6ec5af086489a_0.png"}]}
                if "data" in response_data and len(response_data["data"]) > 0:
                    image_url = response_data["data"][0]["url"]
                    created = response_data.get("created", int(time.time()))
                    
                    return {
                        "success": True,
                        "prompt": prompt,
                        "model": model,
                        "size": size,
                        "quality": quality,
                        "image_url": image_url,
                        "created": created
                    }
                else:
                    return {
                        "success": False,
                        "error": "API返回数据格式不正确",
                        "response": response_data
                    }
            else:
                return {
                    "success": False,
                    "error": f"API请求失败: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"图像生成失败: {str(e)}"
            }
    
    def download_image(self, image_url: str, output_path: str) -> Dict[str, Any]:
        """
        下载图像
        
        Args:
            image_url: 图像URL
            output_path: 输出路径
            
        Returns:
            下载结果
        """
        try:
            # 发送请求下载图像
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # 保存图像
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # 获取文件大小
                file_size = os.path.getsize(output_path)
                
                return {
                    "success": True,
                    "file_path": output_path,
                    "file_size": file_size,
                    "content_type": response.headers.get("Content-Type", "image/png")
                }
            else:
                return {
                    "success": False,
                    "error": f"下载图像失败: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"下载图像失败: {str(e)}"
            }
    
    def generate_and_save_image(self, 
                               prompt: str,
                               filename: Optional[str] = None,
                               model: str = "cogview-4",
                               size: str = "1024x1024",
                               quality: str = "standard",
                               output_dir: str = "outputs") -> Dict[str, Any]:
        """
        生成图像并保存到文件
        
        Args:
            prompt: 图像生成提示词
            filename: 文件名，如果为None则自动生成
            model: 使用的模型
            size: 图像尺寸
            quality: 图像质量
            output_dir: 输出目录
            
        Returns:
            生成结果
        """
        try:
            # 生成图像
            result = self.generate_image(
                prompt=prompt,
                model=model,
                size=size,
                quality=quality
            )
            
            if not result["success"]:
                return result
            
            # 准备文件名和路径
            if not filename:
                # 生成唯一文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:20])
                filename = f"{safe_prompt}_{timestamp}_{unique_id}.png"
            
            # 确保文件名有扩展名
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                filename += '.png'
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建完整路径
            output_path = os.path.join(output_dir, filename)
            
            # 下载并保存图像
            download_result = self.download_image(
                image_url=result["image_url"],
                output_path=output_path
            )
            
            if not download_result["success"]:
                return download_result
            
            # 合并结果
            return {
                "success": True,
                "prompt": prompt,
                "model": model,
                "size": size,
                "quality": quality,
                "image_url": result["image_url"],
                "file_path": output_path,
                "file_size": download_result["file_size"],
                "created": result["created"]
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"生成并保存图像失败: {str(e)}"
            }
    
    def batch_generate_images(self, 
                             prompts: List[str],
                             model: str = "cogview-4",
                             size: str = "1024x1024",
                             quality: str = "standard",
                             output_dir: str = "outputs") -> Dict[str, Any]:
        """
        批量生成图像
        
        Args:
            prompts: 提示词列表
            model: 使用的模型
            size: 图像尺寸
            quality: 图像质量
            output_dir: 输出目录
            
        Returns:
            批量生成结果
        """
        try:
            if not prompts:
                return {
                    "success": False,
                    "error": "提示词列表不能为空"
                }
            
            results = []
            successful = 0
            failed = 0
            
            # 处理每个提示词
            for i, prompt in enumerate(prompts):
                print(f"正在生成图像 {i+1}/{len(prompts)}: {prompt[:30]}...")
                
                result = self.generate_and_save_image(
                    prompt=prompt,
                    model=model,
                    size=size,
                    quality=quality,
                    output_dir=output_dir
                )
                
                # 记录结果
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "result": result
                })
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                
                # 添加短暂延迟，避免API限流
                if i < len(prompts) - 1:
                    time.sleep(1)
            
            return {
                "success": True,
                "total": len(prompts),
                "successful": successful,
                "failed": failed,
                "results": results
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"批量生成图像失败: {str(e)}"
            }


# 测试代码
if __name__ == "__main__":
    client = ZhipuImageClient()
    
    # 测试API连接
    print("测试API连接...")
    connection_test = client.test_connection()
    print(f"连接测试结果: {connection_test}")
    
    if connection_test["success"]:
        # 测试图像生成
        print("\n测试图像生成...")
        result = client.generate_and_save_image(
            prompt="一只可爱的柯基狗",
            model="cogview-3-flash",  # 使用较快的模型进行测试
            size="512x512",  # 使用较小的尺寸进行测试
            quality="standard"
        )
        
        if result["success"]:
            print(f"图像生成成功: {result['file_path']}")
        else:
            print(f"图像生成失败: {result['error']}")