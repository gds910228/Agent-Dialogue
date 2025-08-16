"""
多模态内容分析功能测试脚本
"""

import asyncio
import json
from pathlib import Path
from zhipu_vision_client import ZhipuVisionClient

async def test_multimodal_analysis():
    """测试多模态内容分析功能"""
    print("🧪 开始测试多模态内容分析功能...")
    
    # 初始化客户端
    client = ZhipuVisionClient()
    
    # 测试1: 纯文本分析
    print("\n📝 测试1: 纯文本分析")
    result = client.analyze_multimodal_content(
        text="请解释什么是人工智能，并举例说明其应用领域",
        model="glm-4v"
    )
    print(f"结果: {result['success']}")
    if result['success']:
        print(f"内容: {result['content'][:200]}...")
    else:
        print(f"错误: {result['error']}")
    
    # 测试2: 获取支持的格式
    print("\n📋 测试2: 获取支持的文件格式")
    formats = client.get_supported_formats()
    print(f"支持的格式: {formats}")
    
    # 测试3: 检查配置
    print("\n⚙️ 测试3: 检查配置")
    print(f"API密钥: {client.api_key[:20]}...{client.api_key[-10:] if len(client.api_key) > 30 else client.api_key}")
    print(f"基础URL: {client.base_url}")
    print(f"支持的模型: {list(client.vision_models.keys())}")
    
    # 测试4: 如果有示例文件，测试文件分析
    print("\n🖼️ 测试4: 文件分析测试")
    
    # 检查是否有示例图片
    sample_images = list(Path(".").glob("*.jpg")) + list(Path(".").glob("*.png"))
    if sample_images:
        sample_image = str(sample_images[0])
        print(f"找到示例图片: {sample_image}")
        
        result = client.describe_image(
            sample_image, 
            "请详细描述这张图片的内容"
        )
        print(f"图片分析结果: {result['success']}")
        if result['success']:
            print(f"描述: {result['content'][:200]}...")
        else:
            print(f"错误: {result['error']}")
    else:
        print("未找到示例图片文件")
    
    # 测试5: URL分析（如果网络可用）
    print("\n🌐 测试5: URL内容分析")
    result = client.analyze_multimodal_content(
        text="请分析这个图片的内容",
        urls=["https://via.placeholder.com/300x200/0066CC/FFFFFF?text=Test+Image"],
        model="glm-4v"
    )
    print(f"URL分析结果: {result['success']}")
    if result['success']:
        print(f"分析: {result['content'][:200]}...")
    else:
        print(f"错误: {result['error']}")
    
    print("\n✅ 测试完成!")

def test_file_encoding():
    """测试文件编码功能"""
    print("\n🔧 测试文件编码功能...")
    
    client = ZhipuVisionClient()
    
    # 创建一个测试文本文件
    test_file = Path("test_file.txt")
    test_content = "这是一个测试文件，用于验证文件编码功能。"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # 测试文件编码
        encoded = client.encode_file_to_base64(str(test_file))
        print(f"编码结果: {encoded['type']}, 大小: {encoded['size']} bytes")
        print(f"文件名: {encoded['filename']}")
        print("✅ 文件编码测试通过")
        
    except Exception as e:
        print(f"❌ 文件编码测试失败: {e}")
    
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    print("🚀 启动多模态内容分析测试...")
    
    # 运行异步测试
    asyncio.run(test_multimodal_analysis())
    
    # 运行同步测试
    test_file_encoding()
    
    print("\n🎉 所有测试完成!")