import json
import requests
from zhipu_agent_client import ZhipuAgentClient

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config.get("zhipu_api_key")
print(f"API Key: {api_key[:20]}...")

# 创建客户端
client = ZhipuAgentClient(api_key=api_key)

print("测试智能体API连接...")
try:
    # 直接测试API请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "agent_id": "general_translation",
        "messages": [
            {
                "role": "user",
                "content": "Hello, test message"
            }
        ]
    }
    
    print(f"请求URL: {client.agents_url}")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        client.agents_url,
        headers=headers,
        json=request_data,
        timeout=10
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API调用成功!")
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("❌ API调用失败")
        
except Exception as e:
    print(f"❌ 错误: {str(e)}")