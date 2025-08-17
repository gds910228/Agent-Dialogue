"""
文本转语音功能测试脚本
测试智谱TTS API的各种功能
"""

import os
import sys
import time
from pathlib import Path
from zhipu_tts_client import ZhipuTTSClient

def test_basic_tts():
    """测试基本文本转语音功能"""
    print("=" * 50)
    print("🔊 测试基本文本转语音功能")
    print("=" * 50)
    
    try:
        # 初始化客户端
        client = ZhipuTTSClient()
        
        # 测试文本
        test_text = "你好，这是一个文本转语音的测试。"
        
        print(f"测试文本: {test_text}")
        print("正在转换...")
        
        # 执行转换
        result = client.text_to_speech_file(
            text=test_text,
            voice="tongtong",
            response_format="wav"
        )
        
        if result["success"]:
            print("✅ 转换成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"语音类型: {result['voice']}")
            print(f"音频格式: {result['format']}")
        else:
            print(f"❌ 转换失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_voice_types():
    """测试不同语音类型"""
    print("\n" + "=" * 50)
    print("🎭 测试不同语音类型")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        voice_types = client.get_voice_types()
        
        print("可用的语音类型:")
        for voice, desc in voice_types.items():
            print(f"  {voice}: {desc}")
        
        # 测试每种语音类型
        test_text = "这是语音类型测试。"
        
        for voice in list(voice_types.keys())[:2]:  # 只测试前两种避免过多请求
            print(f"\n测试语音类型: {voice}")
            result = client.text_to_speech_file(
                text=test_text,
                voice=voice,
                filename=f"test_{voice}.wav"
            )
            
            if result["success"]:
                print(f"✅ {voice} 转换成功: {result['filename']}")
            else:
                print(f"❌ {voice} 转换失败: {result['error']}")
                
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_audio_formats():
    """测试不同音频格式"""
    print("\n" + "=" * 50)
    print("🎵 测试不同音频格式")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        formats = client.get_audio_formats()
        
        print(f"支持的音频格式: {formats}")
        
        test_text = "这是音频格式测试。"
        
        for format_type in formats:
            print(f"\n测试格式: {format_type}")
            result = client.text_to_speech_file(
                text=test_text,
                response_format=format_type,
                filename=f"test_format.{format_type}"
            )
            
            if result["success"]:
                print(f"✅ {format_type} 格式转换成功: {result['filename']}")
            else:
                print(f"❌ {format_type} 格式转换失败: {result['error']}")
                
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_batch_conversion():
    """测试批量转换"""
    print("\n" + "=" * 50)
    print("📁 测试批量转换")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        
        # 测试文本列表
        test_texts = [
            "这是第一个测试文本。",
            "这是第二个测试文本。",
            "这是第三个测试文本。"
        ]
        
        print(f"批量转换 {len(test_texts)} 个文本...")
        
        result = client.batch_text_to_speech(
            texts=test_texts,
            voice="tongtong",
            response_format="wav"
        )
        
        if result["success"]:
            print("✅ 批量转换完成!")
            print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")
            
            for item in result['results']:
                file_result = item['result']
                if file_result['success']:
                    print(f"✅ 文本 {item['index']}: {file_result['filename']}")
                else:
                    print(f"❌ 文本 {item['index']}: {file_result['error']}")
        else:
            print(f"❌ 批量转换失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_text_validation():
    """测试文本验证"""
    print("\n" + "=" * 50)
    print("✅ 测试文本验证")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        
        # 测试不同的文本
        test_cases = [
            ("", "空文本"),
            ("   ", "空白文本"),
            ("正常文本", "正常文本"),
            ("a" * 6000, "超长文本"),
            ("Hello World! 你好世界！", "中英混合文本")
        ]
        
        for text, description in test_cases:
            print(f"\n测试 {description}:")
            validation = client.validate_text(text)
            
            if validation["valid"]:
                print(f"✅ 验证通过 - 长度: {validation['length']}")
            else:
                print(f"❌ 验证失败: {validation['error']}")
                
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_api_connection():
    """测试API连接"""
    print("\n" + "=" * 50)
    print("🔧 测试API连接")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        
        print("正在测试API连接...")
        result = client.test_connection()
        
        if result["success"]:
            print("✅ API连接正常")
            print(f"测试音频大小: {result['test_audio_size']} 字节")
        else:
            print(f"❌ API连接失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_long_text():
    """测试长文本转换"""
    print("\n" + "=" * 50)
    print("📄 测试长文本转换")
    print("=" * 50)
    
    try:
        client = ZhipuTTSClient()
        
        # 长文本示例
        long_text = """
        人工智能技术正在快速发展，文本转语音技术作为其中的重要分支，
        已经在各个领域得到了广泛应用。从智能助手到有声读物，
        从导航系统到无障碍辅助工具，TTS技术正在改变我们与机器交互的方式。
        随着深度学习和神经网络技术的进步，现代的TTS系统能够生成
        更加自然、流畅的语音，为用户提供更好的体验。
        """
        
        print(f"长文本长度: {len(long_text)} 字符")
        print("正在转换长文本...")
        
        result = client.text_to_speech_file(
            text=long_text.strip(),
            voice="xiaobei",
            response_format="mp3",
            filename="long_text_test.mp3"
        )
        
        if result["success"]:
            print("✅ 长文本转换成功!")
            print(f"文件: {result['filename']}")
            print(f"大小: {result['size']} 字节")
        else:
            print(f"❌ 长文本转换失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def show_generated_files():
    """显示生成的文件"""
    print("\n" + "=" * 50)
    print("📂 生成的音频文件")
    print("=" * 50)
    
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        files = list(outputs_dir.glob("*"))
        if files:
            print(f"找到 {len(files)} 个文件:")
            for file_path in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
                size_mb = file_path.stat().st_size / 1024 / 1024
                print(f"  {file_path.name} ({size_mb:.2f} MB)")
        else:
            print("没有找到生成的文件")
    else:
        print("输出目录不存在")

def main():
    """主测试函数"""
    print("🚀 AI文本转语音功能测试")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("ZHIPU_API_KEY"):
        print("❌ 错误: 未设置ZHIPU_API_KEY环境变量")
        print("请设置环境变量后重试:")
        print("export ZHIPU_API_KEY=your_api_key")
        return
    
    try:
        # 运行所有测试
        test_api_connection()
        test_basic_tts()
        test_voice_types()
        test_audio_formats()
        test_text_validation()
        test_batch_conversion()
        test_long_text()
        show_generated_files()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()