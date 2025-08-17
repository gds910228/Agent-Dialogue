"""
语音转文本功能测试脚本
"""

import os
import json
from pathlib import Path
from zhipu_speech_client import ZhipuSpeechClient

def test_speech_to_text():
    """测试语音转文本功能"""
    print("=" * 60)
    print("🧪 AI语音转文本功能测试")
    print("=" * 60)
    
    # 初始化客户端
    client = ZhipuSpeechClient()
    
    # 测试1: API连接测试
    print("\n1. 测试API连接...")
    connection_result = client.test_connection()
    print(f"   连接状态: {'✅ 成功' if connection_result['success'] else '❌ 失败'}")
    if not connection_result['success']:
        print(f"   错误信息: {connection_result['error']}")
    else:
        print(f"   可用模型: {connection_result.get('models', [])}")
    
    # 测试2: 支持格式检查
    print("\n2. 检查支持的格式...")
    try:
        formats = client.get_supported_formats()
        print("   支持的格式:")
        for category, extensions in formats.items():
            print(f"     {category}: {', '.join(extensions)}")
    except Exception as e:
        print(f"   ❌ 获取格式失败: {e}")
    
    # 测试3: 模型信息
    print("\n3. 检查模型信息...")
    try:
        models = client.get_model_info()
        print("   可用模型:")
        for model_name, model_info in models.items():
            print(f"     {model_name}: {model_info['description']}")
            print(f"       最大文件大小: {model_info['max_file_size'] / 1024 / 1024:.1f}MB")
    except Exception as e:
        print(f"   ❌ 获取模型信息失败: {e}")
    
    # 测试4: 文件验证功能
    print("\n4. 测试文件验证功能...")
    
    # 测试不存在的文件
    validation = client._validate_audio_file("nonexistent.mp3")
    print(f"   不存在文件验证: {'✅ 正确识别' if not validation['valid'] else '❌ 验证失败'}")
    
    # 检查uploads目录中的文件
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        audio_files = []
        for file_path in uploads_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                all_formats = client.supported_formats["audio"] + client.supported_formats["video"]
                if ext in all_formats:
                    audio_files.append(file_path)
        
        if audio_files:
            print(f"   找到 {len(audio_files)} 个音频文件:")
            for audio_file in audio_files[:3]:  # 只显示前3个
                validation = client._validate_audio_file(str(audio_file))
                status = "✅ 有效" if validation["valid"] else "❌ 无效"
                size_mb = audio_file.stat().st_size / 1024 / 1024
                print(f"     {audio_file.name} ({size_mb:.2f}MB): {status}")
                if not validation["valid"]:
                    print(f"       错误: {validation['error']}")
        else:
            print("   📁 uploads目录中没有找到音频文件")
    else:
        print("   📁 uploads目录不存在")
    
    # 测试5: 实际转录测试（如果有测试文件）
    print("\n5. 实际转录测试...")
    test_files = []
    
    # 查找测试文件
    if uploads_dir.exists():
        for file_path in uploads_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                all_formats = client.supported_formats["audio"] + client.supported_formats["video"]
                if ext in all_formats:
                    validation = client._validate_audio_file(str(file_path))
                    if validation["valid"]:
                        test_files.append(file_path)
    
    if test_files:
        test_file = test_files[0]  # 使用第一个有效文件
        print(f"   使用测试文件: {test_file.name}")
        
        if connection_result['success']:
            try:
                print("   正在进行转录测试...")
                result = client.transcribe_audio(str(test_file))
                
                if result['success']:
                    print("   ✅ 转录成功!")
                    print(f"   转录文本: {result['text'][:100]}...")
                    if result.get('language'):
                        print(f"   检测语言: {result['language']}")
                    if result.get('file_info'):
                        info = result['file_info']
                        print(f"   文件信息: {info['name']} ({info['size']/1024/1024:.2f}MB)")
                else:
                    print(f"   ❌ 转录失败: {result['error']}")
            except Exception as e:
                print(f"   ❌ 转录测试异常: {e}")
        else:
            print("   ⏭️  跳过转录测试 (API连接失败)")
    else:
        print("   ⏭️  跳过转录测试 (没有有效的测试文件)")
        print("   💡 提示: 请将音频文件放入uploads目录进行测试")
    
    # 测试6: 配置文件检查
    print("\n6. 检查配置文件...")
    config_path = "config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            api_key = config.get("api_keys", {}).get("zhipu", "")
            if api_key:
                print(f"   ✅ API密钥已配置 (长度: {len(api_key)})")
            else:
                print("   ❌ API密钥未配置")
                print("   💡 请在config.json中设置zhipu API密钥")
        except Exception as e:
            print(f"   ❌ 配置文件读取失败: {e}")
    else:
        print("   ❌ 配置文件不存在")
        print("   💡 请创建config.json文件并配置API密钥")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)

def create_sample_config():
    """创建示例配置文件"""
    config = {
        "api_keys": {
            "zhipu": "your_zhipu_api_key_here"
        }
    }
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 已创建示例配置文件: {config_path}")
        print("💡 请编辑config.json文件，设置您的智谱API密钥")
    else:
        print("📄 配置文件已存在")

if __name__ == "__main__":
    # 检查并创建配置文件
    create_sample_config()
    
    # 运行测试
    test_speech_to_text()
    
    # 提供使用建议
    print("\n📋 使用建议:")
    print("1. 确保在config.json中配置了有效的智谱API密钥")
    print("2. 将音频文件放入uploads目录进行测试")
    print("3. 支持的音频格式: mp3, wav, flac, m4a, aac, ogg, wma")
    print("4. 支持的视频格式: mp4, avi, mov, mkv, webm, flv")
    print("5. 单个文件最大25MB")
    print("\n🚀 启动方式:")
    print("- 交互模式: python main.py")
    print("- MCP服务器: python main.py --mcp")
    print("- Web服务器: python main.py --web")