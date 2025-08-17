#!/usr/bin/env python3
"""
测试内容安全功能
"""

import os
import sys
from zhipu_moderation_client import ZhipuModerationClient

def test_moderation_client():
    """测试内容安全客户端"""
    print("🧪 测试内容安全客户端")
    
    # 获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 未找到API密钥，请设置环境变量 ZHIPU_API_KEY")
        return False
    
    # 创建客户端
    client = ZhipuModerationClient(api_key=api_key)
    
    # 测试连接
    print("🔍 测试API连接...")
    connection_ok = client.test_connection()
    print(f"连接状态: {'✅ 正常' if connection_ok else '❌ 失败'}")
    
    if not connection_ok:
        return False
    
    # 测试内容审核
    test_texts = [
        "这是一个正常的测试文本内容。",
        "今天天气很好，适合出门散步。",
        "我喜欢学习新的技术知识。"
    ]
    
    print("\n🛡️ 测试内容审核...")
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"\n测试 {i}: {text}")
            
            # 验证输入
            validation = client.validate_input(text)
            if not validation["valid"]:
                print(f"❌ 输入验证失败: {', '.join(validation['errors'])}")
                continue
            
            # 执行审核
            result = client.moderate_content(text)
            formatted_result = client.format_moderation_result(result)
            risk_summary = client.get_risk_summary(result)
            is_safe = client.is_content_safe(result)
            
            print(f"审核结果: {'✅ 安全' if is_safe else '⚠️ 存在风险'}")
            print(f"风险数量: {risk_summary['risk_count']}")
            
            if not is_safe:
                print(f"风险类型: {', '.join(risk_summary['risk_types'])}")
                print(f"最高风险等级: {risk_summary['highest_risk_level']}")
            
        except Exception as e:
            print(f"❌ 审核失败: {str(e)}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️ 内容安全系统测试")
    print("=" * 60)
    
    success = test_moderation_client()
    
    if success:
        print("\n✅ 测试完成!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)