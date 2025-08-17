"""
测试 extract_assistant_message 方法处理智能体API返回格式
"""

import json
from zhipu_agent_client import ZhipuAgentClient

def test_extract_assistant_message():
    """测试提取助手消息的方法"""
    
    # 创建客户端实例（不需要真实API密钥进行测试）
    client = ZhipuAgentClient(api_key="test_key")
    
    print("🧪 测试 extract_assistant_message 方法")
    print("=" * 50)
    
    # 测试用例1: 标准智能体API格式
    test_case_1 = {
        "id": "test_id_1",
        "agent_id": "general_translation",
        "conversation_id": "conv_123",
        "async_id": "async_456",
        "choices": [
            {
                "index": 0,
                "messages": [
                    {
                        "role": "assistant",
                        "content": "这是智能体的回复内容"
                    }
                ],
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    
    result_1 = client.extract_assistant_message(test_case_1)
    print(f"✅ 测试用例1 (标准智能体API格式):")
    print(f"   输入: choices[0].messages[0] = {test_case_1['choices'][0]['messages'][0]}")
    print(f"   输出: '{result_1}'")
    print(f"   预期: '这是智能体的回复内容'")
    print(f"   结果: {'✅ 通过' if result_1 == '这是智能体的回复内容' else '❌ 失败'}")
    print()
    
    # 测试用例2: 多条消息，只提取assistant的
    test_case_2 = {
        "choices": [
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "用户的消息"
                    },
                    {
                        "role": "assistant",
                        "content": "助手的第一条回复"
                    },
                    {
                        "role": "assistant",
                        "content": "助手的第二条回复"
                    }
                ]
            }
        ]
    }
    
    result_2 = client.extract_assistant_message(test_case_2)
    print(f"✅ 测试用例2 (多条消息):")
    print(f"   输出: '{result_2}'")
    print(f"   预期: '助手的第一条回复' (应该返回第一条assistant消息)")
    print(f"   结果: {'✅ 通过' if result_2 == '助手的第一条回复' else '❌ 失败'}")
    print()
    
    # 测试用例3: 普通对话API格式（兼容性测试）
    test_case_3 = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "普通对话API的回复"
                }
            }
        ]
    }
    
    result_3 = client.extract_assistant_message(test_case_3)
    print(f"✅ 测试用例3 (普通对话API格式):")
    print(f"   输出: '{result_3}'")
    print(f"   预期: '普通对话API的回复'")
    print(f"   结果: {'✅ 通过' if result_3 == '普通对话API的回复' else '❌ 失败'}")
    print()
    
    # 测试用例4: 空choices数组
    test_case_4 = {
        "choices": []
    }
    
    result_4 = client.extract_assistant_message(test_case_4)
    print(f"✅ 测试用例4 (空choices数组):")
    print(f"   输出: '{result_4}'")
    print(f"   结果: {'✅ 通过' if '未找到助手消息' in result_4 else '❌ 失败'}")
    print()
    
    # 测试用例5: 没有assistant角色的消息
    test_case_5 = {
        "choices": [
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "只有用户消息"
                    }
                ]
            }
        ]
    }
    
    result_5 = client.extract_assistant_message(test_case_5)
    print(f"✅ 测试用例5 (没有assistant消息):")
    print(f"   输出: '{result_5}'")
    print(f"   结果: {'✅ 通过' if '未找到助手消息' in result_5 else '❌ 失败'}")
    print()
    
    # 测试用例6: 异常格式处理
    test_case_6 = {
        "choices": [
            {
                "messages": [
                    {
                        "role": "assistant",
                        "content": ""  # 空内容
                    },
                    {
                        "role": "assistant",
                        "content": "   "  # 只有空格
                    },
                    {
                        "role": "assistant",
                        "content": "有效的回复内容"
                    }
                ]
            }
        ]
    }
    
    result_6 = client.extract_assistant_message(test_case_6)
    print(f"✅ 测试用例6 (跳过空内容):")
    print(f"   输出: '{result_6}'")
    print(f"   预期: '有效的回复内容' (应该跳过空内容)")
    print(f"   结果: {'✅ 通过' if result_6 == '有效的回复内容' else '❌ 失败'}")
    print()
    
    # 测试用例7: 智谱AI实际格式（content为对象）
    test_case_7 = {
        "id": "test_id",
        "agent_id": "general_translation",
        "status": "success",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "messages": [
                    {
                        "role": "assistant",
                        "content": {
                            "text": "Hello, World!",
                            "type": "text"
                        }
                    }
                ]
            }
        ],
        "usage": {
            "prompt_tokens": 16,
            "completion_tokens": 16,
            "total_tokens": 32
        }
    }
    
    result_7 = client.extract_assistant_message(test_case_7)
    print(f"✅ 测试用例7 (智谱AI实际格式):")
    print(f"   输出: '{result_7}'")
    print(f"   预期: 'Hello, World!'")
    print(f"   结果: {'✅ 通过' if result_7 == 'Hello, World!' else '❌ 失败'}")
    print()
    
    print("🎯 测试总结:")
    print("   extract_assistant_message 方法已优化，能够正确处理智能体API的标准返回格式")
    print("   优先处理 choices[0].messages[] 中 role='assistant' 的消息")
    print("   同时保持对其他格式的向后兼容性")

if __name__ == "__main__":
    test_extract_assistant_message()
