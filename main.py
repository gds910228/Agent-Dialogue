"""
AI Image Generator - Main Entry Point

A comprehensive AI image generation system supporting CogView-4 series models.
Provides both MCP server capabilities and direct image generation functionality.
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
from zhipu_image_client import ZhipuImageClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Image Generator")

# Create directories for storing files
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Initialize clients
image_client = ZhipuImageClient()

# Image Generation Entry Point
class ImageGenerator:
    """主要的图像生成入口类"""
    
    def __init__(self):
        self.image_client = image_client
        self.outputs_dir = OUTPUTS_DIR
    
    def generate_image(self, 
                      prompt: str,
                      model: str = "cogview-4",
                      size: str = "1024x1024",
                      quality: str = "standard") -> Dict[str, Any]:
        """
        主要的图像生成入口
        
        Args:
            prompt: 图像生成提示词
            model: 使用的模型 (cogview-4, cogview-4-250304, cogview-3-flash)
            size: 图像尺寸 (1024x1024, 1024x768, 768x1024, 512x512, 768x768)
            quality: 图像质量 (standard, hd)
            
        Returns:
            生成结果
        """
        return self.image_client.generate_image(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality
        )
    
    def generate_and_save_image(self, prompt: str, filename: Optional[str] = None, 
                               model: str = "cogview-4", size: str = "1024x1024",
                               quality: str = "standard") -> Dict[str, Any]:
        """生成图像并保存文件"""
        return self.image_client.generate_and_save_image(
            prompt=prompt, filename=filename, model=model, 
            size=size, quality=quality,
            output_dir=str(self.outputs_dir)
        )
    
    def batch_generate_images(self, prompts: List[str], model: str = "cogview-4", 
                             size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """批量图像生成"""
        return self.image_client.batch_generate_images(
            prompts=prompts, model=model, size=size, 
            quality=quality, output_dir=str(self.outputs_dir)
        )

# 创建全局图像生成实例
image_generator = ImageGenerator()

@mcp.tool()
def generate_image_from_prompt(
    prompt: str,
    model: str = "cogview-4",
    size: str = "1024x1024",
    quality: str = "standard",
    save_file: bool = True,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate image from text prompt using Zhipu's CogView-4 API.
    
    Args:
        prompt: Text prompt for image generation
        model: Image generation model (cogview-4, cogview-4-250304, cogview-3-flash)
        size: Image size (1024x1024, 1024x768, 768x1024, 512x512, 768x768)
        quality: Image quality (standard, hd)
        save_file: Whether to save the image file
        filename: Optional filename for saved image
    
    Returns:
        Dictionary with generation results
    """
    try:
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "error": "Prompt cannot be empty"
            }
        
        if save_file:
            result = image_generator.generate_and_save_image(
                prompt=prompt,
                filename=filename,
                model=model,
                size=size,
                quality=quality
            )
        else:
            result = image_generator.generate_image(
                prompt=prompt,
                model=model,
                size=size,
                quality=quality
            )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Image generation failed: {str(e)}"
        }

@mcp.tool()
def batch_generate_images(
    prompts: List[str],
    model: str = "cogview-4",
    size: str = "1024x1024",
    quality: str = "standard"
) -> Dict[str, Any]:
    """
    Generate multiple images from prompts in batch.
    
    Args:
        prompts: List of text prompts for image generation
        model: Image generation model (cogview-4, cogview-4-250304, cogview-3-flash)
        size: Image size (1024x1024, 1024x768, 768x1024, 512x512, 768x768)
        quality: Image quality (standard, hd)
    
    Returns:
        Dictionary with batch generation results
    """
    try:
        if not prompts:
            return {
                "success": False,
                "error": "Prompts list cannot be empty"
            }
        
        # Filter out empty prompts
        valid_prompts = [prompt.strip() for prompt in prompts if prompt and prompt.strip()]
        
        if not valid_prompts:
            return {
                "success": False,
                "error": "No valid prompts found"
            }
        
        result = image_generator.batch_generate_images(
            prompts=valid_prompts,
            model=model,
            size=size,
            quality=quality
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch image generation failed: {str(e)}"
        }

@mcp.tool()
def get_supported_options() -> Dict[str, Any]:
    """
    Get available options for image generation.
    
    Returns:
        Dictionary with available models, sizes, and quality options
    """
    try:
        models = image_client.get_supported_models()
        sizes = image_client.get_supported_sizes()
        quality_options = image_client.get_quality_options()
        
        return {
            "success": True,
            "models": models,
            "sizes": sizes,
            "quality_options": quality_options
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get supported options: {str(e)}"
        }

@mcp.tool()
def validate_prompt_input(prompt: str) -> Dict[str, Any]:
    """
    Validate prompt input for image generation.
    
    Args:
        prompt: Prompt to validate
    
    Returns:
        Dictionary with validation results
    """
    try:
        if not prompt:
            return {
                "success": False,
                "error": "Prompt cannot be empty"
            }
        
        result = image_client.validate_prompt(prompt)
        return {
            "success": True,
            "validation": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Prompt validation failed: {str(e)}"
        }

@mcp.tool()
def get_image_file_info(image_path: str) -> Dict[str, Any]:
    """
    Get information about a generated image file.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with image file information
    """
    try:
        if not image_path:
            return {
                "success": False,
                "error": "Image path cannot be empty"
            }
        
        # Check if file exists
        path = Path(image_path)
        if not path.exists():
            # Try relative to outputs directory
            output_path = OUTPUTS_DIR / path.name
            if output_path.exists():
                path = output_path
            else:
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
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
            "supported": file_ext in ['.png', '.jpg', '.jpeg', '.webp']
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get image info: {str(e)}"
        }

@mcp.tool()
def test_image_api(test_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Test the image generation API connection and functionality.
    
    Args:
        test_prompt: Optional test prompt for generation
    
    Returns:
        Dictionary with test results
    """
    try:
        # Test API connection
        connection_test = image_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_models": list(image_client.get_supported_models().keys()),
            "supported_sizes": image_client.get_supported_sizes(),
            "quality_options": image_client.get_quality_options()
        }
        
        # If test prompt provided, try generation
        if test_prompt:
            generation_test = image_client.generate_image(test_prompt, model="cogview-3-flash", size="512x512")
            if generation_test["success"]:
                result["generation_test"] = {
                    "success": True,
                    "image_url": generation_test["image_url"],
                    "model": generation_test["model"],
                    "size": generation_test["size"]
                }
            else:
                result["generation_test"] = generation_test
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"API test failed: {str(e)}"
        }

@mcp.tool()
def save_prompt_content(prompt_content: str, filename: str) -> Dict[str, Any]:
    """
    Save prompt content to a file for later image generation.
    
    Args:
        prompt_content: Prompt content to save
        filename: Name of the file
    
    Returns:
        Dictionary with save result
    """
    try:
        if not prompt_content or not filename:
            return {
                "success": False,
                "error": "Prompt content and filename are required"
            }
        
        # Create unique filename to avoid conflicts
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".txt"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # Save prompt file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
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
def list_generated_files() -> Dict[str, Any]:
    """
    List all generated image files.
    
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
    """运行交互式图像生成模式"""
    print("=" * 60)
    print("🎨 AI图像生成器 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 文本生成图像")
    print("2. 批量图像生成")
    print("3. 查看支持的模型和选项")
    print("4. 查看生成的图像文件")
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
                handle_image_generation()
            elif choice == "2":
                handle_batch_image_generation()
            elif choice == "3":
                handle_model_options()
            elif choice == "4":
                handle_list_image_files()
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
                subprocess.run([sys.executable, "image_server.py"])
                break
            else:
                print("❌ 无效选择，请输入0-8")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_image_generation():
    """处理图像生成"""
    print("\n🎨 文本生成图像")
    prompt = input("请输入图像生成提示词: ").strip()
    if not prompt:
        print("❌ 提示词不能为空")
        return
    
    # 显示可用的模型
    models = image_client.get_supported_models()
    print("\n可用的模型:")
    for model, desc in models.items():
        print(f"  {model}: {desc}")
    
    model = input(f"\n请选择模型 (默认: cogview-4): ").strip() or "cogview-4"
    
    # 显示可用的尺寸
    sizes = image_client.get_supported_sizes()
    print(f"\n可用的图像尺寸: {', '.join(sizes)}")
    size = input("请选择图像尺寸 (默认: 1024x1024): ").strip() or "1024x1024"
    
    # 显示质量选项
    quality_options = image_client.get_quality_options()
    print(f"\n质量选项: {', '.join(quality_options)}")
    quality = input("请选择图像质量 (默认: standard): ").strip() or "standard"
    
    print("🔍 生成中...")
    result = image_generator.generate_and_save_image(
        prompt=prompt, 
        model=model, 
        size=size,
        quality=quality
    )
    
    if result["success"]:
        print(f"✅ 生成成功!")
        print(f"文件路径: {result['file_path']}")
        print(f"文件大小: {result['file_size']} 字节")
        print(f"图像URL: {result['image_url']}")
        print(f"模型: {result['model']}")
        print(f"尺寸: {result['size']}")
        print(f"质量: {result['quality']}")
    else:
        print(f"❌ 生成失败: {result['error']}")

def handle_batch_image_generation():
    """处理批量图像生成"""
    print("\n📁 批量图像生成")
    print("请输入要生成的提示词 (每行一个，空行结束):")
    
    prompts = []
    while True:
        prompt = input().strip()
        if not prompt:
            break
        prompts.append(prompt)
    
    if not prompts:
        print("❌ 没有输入任何提示词")
        return
    
    # 显示可用的模型
    models = image_client.get_supported_models()
    print("\n可用的模型:")
    for model, desc in models.items():
        print(f"  {model}: {desc}")
    
    model = input(f"\n请选择模型 (默认: cogview-4): ").strip() or "cogview-4"
    
    # 显示可用的尺寸
    sizes = image_client.get_supported_sizes()
    print(f"\n可用的图像尺寸: {', '.join(sizes)}")
    size = input("请选择图像尺寸 (默认: 1024x1024): ").strip() or "1024x1024"
    
    # 显示质量选项
    quality_options = image_client.get_quality_options()
    print(f"\n质量选项: {', '.join(quality_options)}")
    quality = input("请选择图像质量 (默认: standard): ").strip() or "standard"
    
    print(f"🔍 批量生成 {len(prompts)} 张图像...")
    result = image_generator.batch_generate_images(
        prompts=prompts, 
        model=model, 
        size=size,
        quality=quality
    )
    
    if result["success"]:
        print(f"✅ 批量生成完成!")
        print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")
        
        for item in result['results']:
            file_result = item['result']
            if file_result['success']:
                print(f"✅ 提示词 {item['index']}: {file_result['file_path']}")
            else:
                print(f"❌ 提示词 {item['index']}: {file_result['error']}")
    else:
        print(f"❌ 批量生成失败: {result['error']}")

def handle_model_options():
    """处理模型选项查看"""
    print("\n🔧 模型和选项信息")
    
    try:
        models = image_client.get_supported_models()
        sizes = image_client.get_supported_sizes()
        quality_options = image_client.get_quality_options()
        
        print("✅ 可用的模型:")
        for model, desc in models.items():
            print(f"  {model}: {desc}")
        
        print(f"\n支持的图像尺寸: {', '.join(sizes)}")
        print(f"\n质量选项: {', '.join(quality_options)}")
            
    except Exception as e:
        print(f"❌ 获取信息失败: {str(e)}")

def handle_list_image_files():
    """处理图像文件列表查看"""
    print("\n📂 生成的图像文件")
    
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
            print("📭 没有找到任何图像文件")
    else:
        print(f"❌ 获取文件列表失败: {result['error']}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_prompt = input("请输入测试提示词 (可选): ").strip() or None
    
    print("🔍 测试中...")
    result = test_image_api(test_prompt)
    
    if result["success"]:
        print("✅ API测试结果:")
        print(f"  连接状态: {'正常' if result['connection_test']['success'] else '失败'}")
        print(f"  可用模型: {', '.join(result['supported_models'])}")
        print(f"  支持尺寸: {', '.join(result['supported_sizes'])}")
        print(f"  质量选项: {', '.join(result['quality_options'])}")
        
        if 'generation_test' in result:
            gen_result = result['generation_test']
            if gen_result['success']:
                print(f"  测试生成: 成功生成图像 {gen_result['image_url']}")
            else:
                print(f"  测试生成失败: {gen_result['error']}")
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
            subprocess.run([sys.executable, "image_server.py"])
        elif sys.argv[1] == "--test":
            print("🧪 运行测试...")
            import subprocess
            subprocess.run([sys.executable, "test_image.py"])
        else:
            print("❌ 未知参数，支持的参数: --mcp, --web, --test")
    else:
        # 默认运行交互式模式
        run_interactive_mode()