#!/usr/bin/env python3
"""
智能体对话功能测试脚本
"""

import os
import json
from zhipu_agent_client import ZhipuAgentClient

def load_config():
    """加载配置文件"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def test_agent_dialogue():
    """测试智能体对话功能"""
    print("🤖 智能体对话功能测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("❌ 错误: 未找到智谱API密钥")
        print("请设置环境变量 ZHIPU_API_KEY 或在config.json中配置")
        return False
    
    # 初始化客户端
    base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
    client = ZhipuAgentClient(api_key=api_key, base_url=base_url)
    
    # 测试连接
    print("1. 测试API连接...")
    try:
        connection_result = client.test_connection()
        print(f"   智能体API: {'✅ 正常' if connection_result['agent_api'] else '❌ 失败'}")
        print(f"   内容安全API: {'✅ 正常' if connection_result['moderation_api'] else '❌ 失败'}")
        
        if connection_result['errors']:
            print("   错误信息:")
            for error in connection_result['errors']:
                print(f"   - {error}")
    except Exception as e:
        print(f"   ❌ 连接测试失败: {str(e)}")
        return False
    
    # 测试文本对话
    print("\n2. 测试智能体文本对话...")
    try:
        agent_id = "general_translation"
        test_message = "你好，请介绍一下你的功能。"
        
        print(f"   智能体ID: {agent_id}")
        print(f"   测试消息: {test_message}")
        
        result = client.chat_with_text(agent_id, test_message)
        
        if result:
            print("   ✅ 对话成功!")
            print(f"   对话ID: {result.get('conversation_id', 'N/A')}")
            
            # 提取助手回复
            assistant_message = client.extract_assistant_message(result)
            if assistant_message:
                print(f"   助手回复: {assistant_message[:200]}...")
            else:
                print("   ⚠️ 未获取到助手回复")
        else:
            print("   ❌ 对话失败: 未获取到结果")
            
    except Exception as e:
        print(f"   ❌ 文本对话测试失败: {str(e)}")
    
    # 测试内容安全功能
    print("\n3. 测试内容安全功能...")
    try:
        test_content = "这是一个测试内容安全功能的正常文本。"
        print(f"   测试内容: {test_content}")
        
        moderation_result = client.moderate_content(test_content)
        
        if moderation_result:
            print("   ✅ 内容安全审核成功!")
            
            # 获取风险摘要
            risk_summary = client.get_risk_summary(moderation_result)
            print(f"   安全状态: {'✅ 安全' if risk_summary['is_safe'] else '⚠️ 存在风险'}")
            print(f"   风险数量: {risk_summary['risk_count']}")
            
            if not risk_summary['is_safe']:
                print(f"   风险类型: {', '.join(risk_summary['risk_types'])}")
        else:
            print("   ❌ 内容安全审核失败: 未获取到结果")
            
    except Exception as e:
        print(f"   ❌ 内容安全测试失败: {str(e)}")
    
    print("\n🎉 测试完成!")
    return True

def test_validation():
    """测试输入验证功能"""
    print("\n🔍 输入验证功能测试")
    print("=" * 50)
    
    config = load_config()
    api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("❌ 跳过验证测试: 未找到API密钥")
        return
    
    base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
    client = ZhipuAgentClient(api_key=api_key, base_url=base_url)
    
    # 测试智能体输入验证
    print("1. 测试智能体输入验证...")
    
    # 有效输入
    valid_messages = [{"role": "user", "content": "Hello"}]
    validation = client.validate_agent_input("test_agent", valid_messages)
    print(f"   有效输入验证: {'✅ 通过' if validation['valid'] else '❌ 失败'}")
    
    # 无效输入 - 空智能体ID
    validation = client.validate_agent_input("", valid_messages)
    print(f"   空智能体ID验证: {'✅ 正确拒绝' if not validation['valid'] else '❌ 错误通过'}")
    
    # 无效输入 - 空消息列表
    validation = client.validate_agent_input("test_agent", [])
    print(f"   空消息列表验证: {'✅ 正确拒绝' if not validation['valid'] else '❌ 错误通过'}")
    
    # 测试内容安全输入验证
    print("\n2. 测试内容安全输入验证...")
    
    # 有效输入
    validation = client.validate_moderation_input("这是一个正常的测试文本")
    print(f"   有效输入验证: {'✅ 通过' if validation['valid'] else '❌ 失败'}")
    
    # 无效输入 - 空文本
    validation = client.validate_moderation_input("")
    print(f"   空文本验证: {'✅ 正确拒绝' if not validation['valid'] else '❌ 错误通过'}")
    
    # 无效输入 - 超长文本
    long_text = "测试" * 5001  # 超过10000字符
    validation = client.validate_moderation_input(long_text)
    print(f"   超长文本验证: {'✅ 正确拒绝' if not validation['valid'] else '❌ 错误通过'}")

if __name__ == "__main__":
    print("🚀 开始智能体对话功能测试")
    print("=" * 60)
    
    # 运行主要功能测试
    success = test_agent_dialogue()
    
    # 运行验证功能测试
    test_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试完成!")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")