"""
调试智谱智能体API的脚本
用于查看原始API响应格式
"""

import os
import json
import requests
from zhipu_agent_client import ZhipuAgentClient

def load_config():
    """加载配置文件"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def debug_api_call():
    """调试API调用"""
    config = load_config()
    api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("❌ 未找到API密钥")
        return
    
    # 创建客户端
    client = ZhipuAgentClient(api_key=api_key)
    
    # 测试消息
    test_message = "请将这句话翻译为英文：你好，世界！"
    agent_id = "general_translation"
    
    print(f"🔍 调试智能体API调用")
    print(f"智能体ID: {agent_id}")
    print(f"测试消息: {test_message}")
    print(f"API端点: {client.agents_url}")
    print("-" * 50)
    
    try:
        # 构建请求数据
        messages = [{"role": "user", "content": test_message}]
        request_data = {
            "agent_id": agent_id,
            "messages": messages
        }
        
        print(f"📤 请求数据:")
        print(json.dumps(request_data, ensure_ascii=False, indent=2))
        print("-" * 50)
        
        # 发送请求
        response = requests.post(
            client.agents_url,
            headers=client.headers,
            json=request_data,
            timeout=30
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 原始响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("-" * 50)
            
            # 尝试提取助手消息
            assistant_message = client.extract_assistant_message(result)
            print(f"🤖 提取的助手消息: '{assistant_message}'")
            
            # 分析响应结构
            print(f"\n📊 响应结构分析:")
            print(f"  - 包含choices: {'choices' in result}")
            print(f"  - choices数量: {len(result.get('choices', []))}")
            print(f"  - 包含data: {'data' in result}")
            print(f"  - 包含message: {'message' in result}")
            print(f"  - 包含content: {'content' in result}")
            print(f"  - 所有字段: {list(result.keys())}")
            
            if 'choices' in result and result['choices']:
                choice = result['choices'][0]
                print(f"  - 第一个choice的字段: {list(choice.keys())}")
                if 'messages' in choice and choice['messages']:
                    msg = choice['messages'][0]
                    print(f"  - 第一个message的字段: {list(msg.keys())}")
                    print(f"  - message内容: {msg}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_call()