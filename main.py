"""
AI Multimodal Content Analyzer - Main Entry Point

A comprehensive AI content analysis system supporting multimodal inputs (text, images, videos, documents).
Provides both MCP server capabilities and direct vision reasoning functionality.
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
from zhipu_vision_client import ZhipuVisionClient

# Create an MCP server
mcp = FastMCP("AI Multimodal Content Analyzer")

# Create directories for storing files
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Initialize clients
vision_client = ZhipuVisionClient()

# Vision Reasoning Entry Point
class VisionReasoning:
    """主要的视觉推理入口类"""
    
    def __init__(self):
        self.vision_client = vision_client
        self.uploads_dir = UPLOADS_DIR
        
    def analyze_content(self, 
                       text: str = "",
                       files: List[str] = None,
                       urls: List[str] = None,
                       model: str = "glm-4v") -> Dict[str, Any]:
        """
        主要的内容分析入口
        
        Args:
            text: 文本内容或问题
            files: 文件路径列表
            urls: URL列表
            model: 使用的模型
            
        Returns:
            分析结果
        """
        return self.vision_client.analyze_multimodal_content(
            text=text,
            files=files or [],
            urls=urls or [],
            model=model
        )
    
    def process_image(self, image_path: str, question: str = "请描述这张图片") -> Dict[str, Any]:
        """处理图片"""
        return self.vision_client.describe_image(image_path, question)
    
    def process_video(self, video_path: str, question: str = "请分析这个视频") -> Dict[str, Any]:
        """处理视频"""
        return self.vision_client.analyze_video(video_path, question)
    
    def process_document(self, doc_path: str, question: str = "请总结文档内容") -> Dict[str, Any]:
        """处理文档"""
        return self.vision_client.extract_document_info(doc_path, question)
    
    def compare_contents(self, file_paths: List[str], question: str = "请比较这些内容") -> Dict[str, Any]:
        """比较多个内容"""
        return self.vision_client.compare_contents(file_paths, question)

# 创建全局视觉推理实例
vision_reasoning = VisionReasoning()

@mcp.tool()
def analyze_multimodal_content(
    text: str = "",
    file_paths: List[str] = None,
    urls: List[str] = None,
    model: str = "glm-4v",
    question: str = ""
) -> Dict[str, Any]:
    """
    Analyze multimodal content including text, images, videos, and documents.
    
    Args:
        text: Text content or description
        file_paths: List of local file paths to analyze
        urls: List of URLs to analyze
        model: Vision model to use (glm-4v, glm-4v-plus)
        question: Specific question about the content
    
    Returns:
        Dictionary with analysis results
    """
    try:
        if not text and not file_paths and not urls:
            return {
                "success": False,
                "error": "At least one type of content must be provided"
            }
        
        # Combine text and question
        combined_text = f"{text} {question}".strip() if question else text
        
        # Validate file paths
        valid_files = []
        if file_paths:
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists():
                    valid_files.append(str(path))
                else:
                    # Try relative to uploads directory
                    upload_path = UPLOADS_DIR / path.name
                    if upload_path.exists():
                        valid_files.append(str(upload_path))
        
        result = vision_reasoning.analyze_content(
            text=combined_text,
            files=valid_files,
            urls=urls or [],
            model=model
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Multimodal analysis failed: {str(e)}"
        }

@mcp.tool()
def describe_image(image_path: str, question: str = "请描述这张图片的内容") -> Dict[str, Any]:
    """
    Describe the content of an image.
    
    Args:
        image_path: Path to the image file
        question: Specific question about the image
    
    Returns:
        Dictionary with image description
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
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                image_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }
        
        result = vision_reasoning.process_image(image_path, question)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Image description failed: {str(e)}"
        }

@mcp.tool()
def analyze_video_content(video_path: str, question: str = "请分析这个视频的内容") -> Dict[str, Any]:
    """
    Analyze video content using vision model.
    
    Args:
        video_path: Path to the video file
        question: Specific question about the video
    
    Returns:
        Dictionary with video analysis results
    """
    try:
        if not video_path:
            return {
                "success": False,
                "error": "Video path cannot be empty"
            }
        
        # Check if file exists
        path = Path(video_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                video_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Video file not found: {video_path}"
                }
        
        result = vision_reasoning.process_video(video_path, question)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Video analysis failed: {str(e)}"
        }

@mcp.tool()
def extract_document_content(document_path: str, question: str = "请总结这个文档的主要内容") -> Dict[str, Any]:
    """
    Extract and analyze document content.
    
    Args:
        document_path: Path to the document file
        question: Specific question about the document
    
    Returns:
        Dictionary with document analysis results
    """
    try:
        if not document_path:
            return {
                "success": False,
                "error": "Document path cannot be empty"
            }
        
        # Check if file exists
        path = Path(document_path)
        if not path.exists():
            # Try relative to uploads directory
            upload_path = UPLOADS_DIR / path.name
            if upload_path.exists():
                document_path = str(upload_path)
            else:
                return {
                    "success": False,
                    "error": f"Document file not found: {document_path}"
                }
        
        result = vision_reasoning.process_document(document_path, question)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Document extraction failed: {str(e)}"
        }

@mcp.tool()
def compare_multiple_contents(file_paths: List[str], question: str = "请比较这些内容的异同") -> Dict[str, Any]:
    """
    Compare multiple files or contents.
    
    Args:
        file_paths: List of file paths to compare
        question: Specific question about the comparison
    
    Returns:
        Dictionary with comparison results
    """
    try:
        if not file_paths or len(file_paths) < 2:
            return {
                "success": False,
                "error": "At least two files are required for comparison"
            }
        
        # Validate file paths
        valid_files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                valid_files.append(str(path))
            else:
                # Try relative to uploads directory
                upload_path = UPLOADS_DIR / path.name
                if upload_path.exists():
                    valid_files.append(str(upload_path))
        
        if len(valid_files) < 2:
            return {
                "success": False,
                "error": "At least two valid files are required for comparison"
            }
        
        result = vision_reasoning.compare_contents(valid_files, question)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Content comparison failed: {str(e)}"
        }

@mcp.tool()
def upload_file(file_content: str, filename: str, encoding: str = "base64") -> Dict[str, Any]:
    """
    Upload a file to the server for analysis.
    
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
    Get list of supported file formats for multimodal analysis.
    
    Returns:
        Dictionary with supported formats
    """
    try:
        formats = vision_client.get_supported_formats()
        return {
            "success": True,
            "formats": formats,
            "models": list(vision_client.vision_models.keys())
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get supported formats: {str(e)}"
        }

@mcp.tool()
def list_uploaded_files() -> Dict[str, Any]:
    """
    List all uploaded files available for analysis.
    
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
    """运行交互式视觉推理模式"""
    print("=" * 60)
    print("🧠 AI多模态内容分析器 - 视觉推理模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 图片分析")
    print("2. 视频分析") 
    print("3. 文档分析")
    print("4. 多内容比较")
    print("5. 自定义多模态分析")
    print("6. 启动MCP服务器")
    print("7. 启动Web服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_image_analysis()
            elif choice == "2":
                handle_video_analysis()
            elif choice == "3":
                handle_document_analysis()
            elif choice == "4":
                handle_content_comparison()
            elif choice == "5":
                handle_custom_analysis()
            elif choice == "6":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            elif choice == "7":
                print("🌐 启动Web服务器...")
                import subprocess
                subprocess.run([sys.executable, "multimodal_server.py"])
                break
            else:
                print("❌ 无效选择，请输入0-7")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_image_analysis():
    """处理图片分析"""
    print("\n📸 图片分析")
    image_path = input("请输入图片路径: ").strip()
    if not image_path:
        print("❌ 图片路径不能为空")
        return
    
    question = input("请输入问题 (回车使用默认): ").strip()
    if not question:
        question = "请详细描述这张图片的内容"
    
    print("🔍 分析中...")
    result = vision_reasoning.process_image(image_path, question)
    
    if result["success"]:
        print(f"✅ 分析结果:\n{result['content']}")
    else:
        print(f"❌ 分析失败: {result['error']}")

def handle_video_analysis():
    """处理视频分析"""
    print("\n🎥 视频分析")
    video_path = input("请输入视频路径: ").strip()
    if not video_path:
        print("❌ 视频路径不能为空")
        return
    
    question = input("请输入问题 (回车使用默认): ").strip()
    if not question:
        question = "请分析这个视频的内容"
    
    print("🔍 分析中...")
    result = vision_reasoning.process_video(video_path, question)
    
    if result["success"]:
        print(f"✅ 分析结果:\n{result['content']}")
    else:
        print(f"❌ 分析失败: {result['error']}")

def handle_document_analysis():
    """处理文档分析"""
    print("\n📄 文档分析")
    doc_path = input("请输入文档路径: ").strip()
    if not doc_path:
        print("❌ 文档路径不能为空")
        return
    
    question = input("请输入问题 (回车使用默认): ").strip()
    if not question:
        question = "请总结这个文档的主要内容"
    
    print("🔍 分析中...")
    result = vision_reasoning.process_document(doc_path, question)
    
    if result["success"]:
        print(f"✅ 分析结果:\n{result['content']}")
    else:
        print(f"❌ 分析失败: {result['error']}")

def handle_content_comparison():
    """处理内容比较"""
    print("\n🔄 多内容比较")
    print("请输入要比较的文件路径 (每行一个，空行结束):")
    
    file_paths = []
    while True:
        path = input().strip()
        if not path:
            break
        file_paths.append(path)
    
    if len(file_paths) < 2:
        print("❌ 至少需要两个文件进行比较")
        return
    
    question = input("请输入比较问题 (回车使用默认): ").strip()
    if not question:
        question = "请比较这些内容的异同"
    
    print("🔍 比较中...")
    result = vision_reasoning.compare_contents(file_paths, question)
    
    if result["success"]:
        print(f"✅ 比较结果:\n{result['content']}")
    else:
        print(f"❌ 比较失败: {result['error']}")

def handle_custom_analysis():
    """处理自定义分析"""
    print("\n🎯 自定义多模态分析")
    
    text = input("请输入文本内容 (可选): ").strip()
    
    print("请输入文件路径 (每行一个，空行结束):")
    file_paths = []
    while True:
        path = input().strip()
        if not path:
            break
        file_paths.append(path)
    
    print("请输入URL (每行一个，空行结束):")
    urls = []
    while True:
        url = input().strip()
        if not url:
            break
        urls.append(url)
    
    if not text and not file_paths and not urls:
        print("❌ 至少需要提供一种类型的内容")
        return
    
    model = input("请选择模型 (glm-4v/glm-4v-plus，回车使用默认): ").strip()
    if not model:
        model = "glm-4v"
    
    print("🔍 分析中...")
    result = vision_reasoning.analyze_content(
        text=text,
        files=file_paths if file_paths else [],
        urls=urls if urls else [],
        model=model
    )
    
    if result["success"]:
        print(f"✅ 分析结果:\n{result['content']}")
    else:
        print(f"❌ 分析失败: {result['error']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--mcp":
            print("🔧 启动MCP服务器模式...")
            mcp.run(transport="sse")
        elif sys.argv[1] == "--web":
            print("🌐 启动Web服务器模式...")
            import subprocess
            subprocess.run([sys.executable, "multimodal_server.py"])
        elif sys.argv[1] == "--test":
            print("🧪 运行测试...")
            import subprocess
            subprocess.run([sys.executable, "test_multimodal.py"])
        else:
            print("❌ 未知参数，支持的参数: --mcp, --web, --test")
    else:
        # 默认运行交互式模式
        run_interactive_mode()