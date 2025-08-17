import json
from zhipu_agent_client import ZhipuAgentClient

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config.get("zhipu_api_key")
print(f"API Key: {api_key[:20]}...")

# 创建客户端
client = ZhipuAgentClient(api_key=api_key)

# 测试消息
test_message = "请将以下中文翻译为英文：列表内是您的全部 API keys，请不要与他人共享您的 API Keys，避免将其暴露在浏览器和其他客户端代码中。为了保护您帐户的安全,我们还可能会自动更换我们发现已公开泄露的密钥信息。 新版机制中平台颁发的 API Key 同时包含 \"用户标识 id\" 和 \"签名密钥 secret\""

print("测试修复后的智能体对话功能...")
try:
    # 使用修复后的 chat_with_text 方法
    result = client.chat_with_text("general_translation", test_message)
    
    print("对话结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 提取助手消息
    assistant_message = client.extract_assistant_message(result)
    print(f"\n🤖 助手回复:")
    print(assistant_message)
    
    # 检查是否使用了回退API
    if result.get("fallback_to_direct_api"):
        print("\n✅ 成功使用普通对话API作为回退")
    else:
        print("\n✅ 成功使用智能体API")
        
except Exception as e:
    print(f"❌ 错误: {str(e)}")