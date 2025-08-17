"""
智谱图像生成测试脚本

用于测试智谱CogView-4图像生成功能
"""

import os
import time
import json
from pathlib import Path
from zhipu_image_client import ZhipuImageClient

# 测试提示词
TEST_PROMPTS = [
    "一只可爱的柯基狗",
    "未来风格的城市夜景",
    "山间湖泊的日出",
    "宇航员在太空中漂浮",
    "水晶球中的微缩世界"
]

# 测试模型
TEST_MODELS = ["cogview-3-flash", "cogview-4"]

# 测试尺寸
TEST_SIZES = ["512x512", "1024x1024"]

# 测试质量
TEST_QUALITIES = ["standard"]

def run_basic_test():
    """运行基本功能测试"""
    print("=" * 60)
    print("🧪 运行基本功能测试")
    print("=" * 60)
    
    client = ZhipuImageClient()
    
    # 测试API连接
    print("测试API连接...")
    connection_test = client.test_connection()
    print(f"连接测试结果: {connection_test}")
    
    if not connection_test["success"]:
        print("❌ API连接测试失败，无法继续测试")
        return False
    
    # 测试获取支持的选项
    print("\n获取支持的选项...")
    print(f"支持的模型: {client.get_supported_models()}")
    print(f"支持的尺寸: {client.get_supported_sizes()}")
    print(f"质量选项: {client.get_quality_options()}")
    
    # 测试提示词验证
    print("\n测试提示词验证...")
    for prompt in TEST_PROMPTS[:2]:  # 只测试前两个提示词
        validation = client.validate_prompt(prompt)
        print(f"提示词 '{prompt}' 验证结果: {validation}")
    
    return True

def run_generation_test():
    """运行图像生成测试"""
    print("\n" + "=" * 60)
    print("🧪 运行图像生成测试")
    print("=" * 60)
    
    client = ZhipuImageClient()
    outputs_dir = Path("test_outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 使用最快的模型和最小的尺寸进行测试
    model = "cogview-3-flash"
    size = "512x512"
    quality = "standard"
    
    print(f"使用模型: {model}, 尺寸: {size}, 质量: {quality}")
    
    # 测试单个图像生成
    print("\n测试单个图像生成...")
    prompt = TEST_PROMPTS[0]
    print(f"提示词: {prompt}")
    
    start_time = time.time()
    result = client.generate_and_save_image(
        prompt=prompt,
        model=model,
        size=size,
        quality=quality,
        output_dir=str(outputs_dir)
    )
    elapsed = time.time() - start_time
    
    if result["success"]:
        print(f"✅ 图像生成成功 ({elapsed:.2f}秒)")
        print(f"文件路径: {result['file_path']}")
        print(f"图像URL: {result['image_url']}")
    else:
        print(f"❌ 图像生成失败: {result['error']}")
        return False
    
    return True

def run_batch_test():
    """运行批量生成测试"""
    print("\n" + "=" * 60)
    print("🧪 运行批量生成测试")
    print("=" * 60)
    
    client = ZhipuImageClient()
    outputs_dir = Path("test_outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 使用最快的模型和最小的尺寸进行测试
    model = "cogview-3-flash"
    size = "512x512"
    quality = "standard"
    
    print(f"使用模型: {model}, 尺寸: {size}, 质量: {quality}")
    
    # 测试批量图像生成 (只使用前3个提示词)
    print("\n测试批量图像生成...")
    prompts = TEST_PROMPTS[:3]
    for i, prompt in enumerate(prompts):
        print(f"提示词 {i+1}: {prompt}")
    
    start_time = time.time()
    result = client.batch_generate_images(
        prompts=prompts,
        model=model,
        size=size,
        quality=quality,
        output_dir=str(outputs_dir)
    )
    elapsed = time.time() - start_time
    
    if result["success"]:
        print(f"✅ 批量生成完成 ({elapsed:.2f}秒)")
        print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")
        
        for item in result['results']:
            file_result = item['result']
            if file_result['success']:
                print(f"✅ 提示词 {item['index']}: {file_result['file_path']}")
            else:
                print(f"❌ 提示词 {item['index']}: {file_result['error']}")
    else:
        print(f"❌ 批量生成失败: {result['error']}")
        return False
    
    return True

def run_comprehensive_test():
    """运行综合测试"""
    print("\n" + "=" * 60)
    print("🧪 运行综合测试")
    print("=" * 60)
    
    client = ZhipuImageClient()
    outputs_dir = Path("test_outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 测试不同模型和尺寸的组合
    test_combinations = [
        {"model": "cogview-3-flash", "size": "512x512", "quality": "standard"},
        {"model": "cogview-4", "size": "1024x1024", "quality": "standard"}
    ]
    
    prompt = "一只可爱的柯基狗"
    print(f"使用提示词: {prompt}")
    
    for config in test_combinations:
        print(f"\n测试配置: 模型={config['model']}, 尺寸={config['size']}, 质量={config['quality']}")
        
        start_time = time.time()
        result = client.generate_and_save_image(
            prompt=prompt,
            model=config['model'],
            size=config['size'],
            quality=config['quality'],
            output_dir=str(outputs_dir)
        )
        elapsed = time.time() - start_time
        
        if result["success"]:
            print(f"✅ 图像生成成功 ({elapsed:.2f}秒)")
            print(f"文件路径: {result['file_path']}")
        else:
            print(f"❌ 图像生成失败: {result['error']}")
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 智谱图像生成测试")
    print("=" * 60)
    
    # 创建测试输出目录
    outputs_dir = Path("test_outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 运行测试
    basic_test_success = run_basic_test()
    
    if not basic_test_success:
        print("\n❌ 基本功能测试失败，跳过后续测试")
        return
    
    generation_test_success = run_generation_test()
    
    if not generation_test_success:
        print("\n❌ 图像生成测试失败，跳过后续测试")
        return
    
    batch_test_success = run_batch_test()
    comprehensive_test_success = run_comprehensive_test()
    
    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print("📊 测试结果摘要")
    print("=" * 60)
    print(f"基本功能测试: {'✅ 通过' if basic_test_success else '❌ 失败'}")
    print(f"图像生成测试: {'✅ 通过' if generation_test_success else '❌ 失败'}")
    print(f"批量生成测试: {'✅ 通过' if batch_test_success else '❌ 失败'}")
    print(f"综合测试: {'✅ 通过' if comprehensive_test_success else '❌ 失败'}")
    
    overall_success = all([
        basic_test_success, 
        generation_test_success, 
        batch_test_success, 
        comprehensive_test_success
    ])
    
    print("\n" + "=" * 60)
    print(f"总体结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()