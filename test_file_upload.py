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

# 测试文本内容
test_text = "请将以下中文翻译为英文：列表内是您的全部 API keys，请不要与他人共享您的 API Keys，避免将其暴露在浏览器和其他客户端代码中。"

print("测试文件上传...")
try:
    file_id = client.upload_text_as_file(test_text)
    print(f"文件上传结果: {file_id}")
    
    if file_id:
        print("测试智能体对话...")
        result = client.chat_with_file("general_translation", file_id)
        print(f"对话结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 提取助手消息
        assistant_message = client.extract_assistant_message(result)
        print(f"助手回复: {assistant_message}")
    else:
        print("文件上传失败")
        
except Exception as e:
    print(f"错误: {str(e)}")