import json
import requests

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config.get("zhipu_api_key")
print(f"API Key: {api_key[:20]}...")

# 测试直接对话API
base_url = "https://open.bigmodel.cn"
chat_url = f"{base_url}/api/paas/v4/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 测试消息
test_message = "请将以下中文翻译为英文：列表内是您的全部 API keys，请不要与他人共享您的 API Keys，避免将其暴露在浏览器和其他客户端代码中。"

request_data = {
    "model": "glm-4",  # 使用GLM-4模型
    "messages": [
        {
            "role": "user",
            "content": test_message
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print("测试直接对话API...")
print(f"请求URL: {chat_url}")
print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

try:
    response = requests.post(
        chat_url,
        headers=headers,
        json=request_data,
        timeout=30
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 对话API调用成功!")
        
        # 提取回复内容
        choices = result.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            print(f"\n🤖 AI回复:")
            print(content)
        else:
            print("未找到回复内容")
    else:
        print("❌ 对话API调用失败")
        
except Exception as e:
    print(f"❌ 错误: {str(e)}")