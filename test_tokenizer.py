"""
智谱AI文本分词器测试脚本
用于测试分词功能和API连接
"""

import os
import json
import time
from typing import List, Dict, Any

from zhipu_tokenizer_client import ZhipuTokenizerClient

def load_config():
    """加载配置文件"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def test_tokenizer():
    """测试分词功能"""
    print("=" * 60)
    print("🧪 智谱AI文本分词器测试")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("❌ 错误: 未找到API密钥，请设置环境变量 ZHIPU_API_KEY 或在config.json中配置")
        return
    
    # 初始化客户端
    base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
    client = ZhipuTokenizerClient(api_key=api_key, base_url=base_url)
    
    # 测试API连接
    print("🔄 测试API连接...")
    if client.test_connection():
        print("✅ API连接成功")
    else:
        print("❌ API连接失败")
        return
    
    # 测试单条消息分词
    print("\n🔄 测试单条消息分词...")
    test_text = "What opportunities and challenges will the Chinese large model industry face in 2025?"
    
    try:
        start_time = time.time()
        token_count = client.count_tokens(test_text)
        elapsed_time = time.time() - start_time
        
        print(f"✅ 分词成功")
        print(f"文本: {test_text}")
        print(f"Token数量: {token_count}")
        print(f"耗时: {elapsed_time:.2f}秒")
    except Exception as e:
        print(f"❌ 分词失败: {str(e)}")
    
    # 测试多条消息分词
    print("\n🔄 测试多条消息分词...")
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI development in China."},
        {"role": "assistant", "content": "China has made significant progress in AI research and applications."}
    ]
    
    try:
        start_time = time.time()
        result = client.tokenize(test_messages)
        elapsed_time = time.time() - start_time
        
        token_count = result.get("usage", {}).get("prompt_tokens", 0)
        
        print(f"✅ 分词成功")
        print(f"消息数量: {len(test_messages)}")
        print(f"Token数量: {token_count}")
        print(f"请求ID: {result.get('id', 'N/A')}")
        print(f"创建时间: {result.get('created', 0)}")
        print(f"耗时: {elapsed_time:.2f}秒")
    except Exception as e:
        print(f"❌ 分词失败: {str(e)}")
    
    # 测试不同模型
    print("\n🔄 测试不同模型...")
    models = client.get_available_models()
    
    for model in models:
        print(f"\n测试模型: {model}")
        try:
            start_time = time.time()
            token_count = client.count_tokens(test_text, model=model)
            elapsed_time = time.time() - start_time
            
            print(f"✅ 分词成功")
            print(f"Token数量: {token_count}")
            print(f"耗时: {elapsed_time:.2f}秒")
        except Exception as e:
            print(f"❌ 分词失败: {str(e)}")
    
    print("\n🎉 测试完成")

if __name__ == "__main__":
    test_tokenizer()