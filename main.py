"""
AI Content Security System - Main Entry Point

A comprehensive content security system supporting Zhipu content moderation API.
Provides both MCP server capabilities and direct content moderation functionality.
"""

import os
import sys
import time
import json
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from zhipu_agent_client import ZhipuAgentClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Content Security System")

# Create directories for storing files
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Load configuration
def load_config():
    """加载配置文件"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()

# Initialize clients
api_key = config.get("zhipu_api_key") or os.getenv("ZHIPU_API_KEY")
if not api_key:
    print("警告: 未找到智谱API密钥，请设置环境变量 ZHIPU_API_KEY 或在config.json中配置")

agent_base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
agent_client = ZhipuAgentClient(api_key=api_key or "", base_url=agent_base_url)

# Agent Dialogue Entry Point
class AgentDialogueGenerator:
    """主要的智能体对话入口类"""
    
    def __init__(self):
        self.agent_client = agent_client
        self.outputs_dir = OUTPUTS_DIR
    
    def chat_with_agent(self, agent_id: str, messages: List[Dict[str, Any]], conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        主要的智能体对话入口
        
        Args:
            agent_id: 智能体ID
            messages: 消息列表
            conversation_id: 对话ID
            
        Returns:
            对话结果
        """
        return self.agent_client.chat_with_agent(agent_id, messages, conversation_id)
    
    def chat_with_text(self, agent_id: str, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """发送文本消息与智能体对话"""
        return self.agent_client.chat_with_text(agent_id, user_message, conversation_id)
    
    def chat_with_file(self, agent_id: str, file_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """发送文件与智能体对话"""
        return self.agent_client.chat_with_file(agent_id, file_id, conversation_id)
    
    def moderate_content(self, input_text: str) -> Dict[str, Any]:
        """
        内容安全审核（保留原功能）
        
        Args:
            input_text: 需要审核的文本内容
            
        Returns:
            审核结果
        """
        return self.agent_client.moderate_content(input_text)
    
    def check_content_safety(self, input_text: str) -> Dict[str, Any]:
        """检查内容安全性并返回详细分析"""
        result = self.agent_client.moderate_content(input_text)
        formatted_result = self.agent_client.format_moderation_result(result)
        risk_summary = self.agent_client.get_risk_summary(result)
        
        return {
            "input": input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result
        }

# 创建全局智能体对话实例
agent_generator = AgentDialogueGenerator()

@mcp.tool()
def chat_with_agent(agent_id: str, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    与智能体进行对话
    
    Args:
        agent_id: 智能体ID
        user_message: 用户消息
        conversation_id: 可选的对话ID
    
    Returns:
        包含对话结果的字典
    """
    try:
        if not agent_id or not agent_id.strip():
            return {
                "success": False,
                "error": "智能体ID不能为空"
            }
        
        if not user_message or not user_message.strip():
            return {
                "success": False,
                "error": "用户消息不能为空"
            }
        
        # 验证参数
        messages = [{"role": "user", "content": user_message}]
        validation = agent_client.validate_agent_input(agent_id, messages)
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = agent_generator.chat_with_text(agent_id, user_message, conversation_id)
        
        # 格式化结果
        formatted_result = agent_client.format_agent_response(result)
        assistant_message = agent_client.extract_assistant_message(result)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "user_message": user_message,
            "conversation_id": result.get("conversation_id", ""),
            "assistant_message": assistant_message,
            "detailed_result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"智能体对话失败: {str(e)}"
        }

@mcp.tool()
def chat_with_agent_file(agent_id: str, file_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    使用文件与智能体进行对话
    
    Args:
        agent_id: 智能体ID
        file_id: 文件ID
        conversation_id: 可选的对话ID
    
    Returns:
        包含对话结果的字典
    """
    try:
        if not agent_id or not agent_id.strip():
            return {
                "success": False,
                "error": "智能体ID不能为空"
            }
        
        if not file_id or not file_id.strip():
            return {
                "success": False,
                "error": "文件ID不能为空"
            }
        
        result = agent_generator.chat_with_file(agent_id, file_id, conversation_id)
        
        # 格式化结果
        formatted_result = agent_client.format_agent_response(result)
        assistant_message = agent_client.extract_assistant_message(result)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "file_id": file_id,
            "conversation_id": result.get("conversation_id", ""),
            "assistant_message": assistant_message,
            "detailed_result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"智能体文件对话失败: {str(e)}"
        }

@mcp.tool()
def moderate_content(input_text: str) -> Dict[str, Any]:
    """
    执行内容安全审核（保留原功能）
    
    Args:
        input_text: 需要审核的文本内容
    
    Returns:
        包含审核结果的字典
    """
    try:
        if not input_text or not input_text.strip():
            return {
                "success": False,
                "error": "审核内容不能为空"
            }
        
        # 验证参数
        validation = agent_client.validate_moderation_input(input_text)
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = agent_generator.moderate_content(input_text)
        
        # 格式化结果
        formatted_result = agent_client.format_moderation_result(result)
        risk_summary = agent_client.get_risk_summary(result)
        
        return {
            "success": True,
            "input_text": input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"内容安全审核失败: {str(e)}"
        }

@mcp.tool()
def batch_moderate_content(input_texts: List[str]) -> Dict[str, Any]:
    """
    批量执行内容安全审核
    
    Args:
        input_texts: 需要审核的文本内容列表
    
    Returns:
        包含批量审核结果的字典
    """
    try:
        if not input_texts:
            return {
                "success": False,
                "error": "审核内容列表不能为空"
            }
        
        # 验证每个输入
        for i, text in enumerate(input_texts):
            validation = agent_client.validate_moderation_input(text)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"第{i+1}个文本验证失败: {', '.join(validation['errors'])}"
                }
        
        # 批量执行内容审核
        results = []
        for text in input_texts:
            try:
                result = agent_generator.moderate_content(text)
                results.append({
                    "success": True,
                    "input": text,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "input": text,
                    "error": str(e)
                })
        
        # 统计结果
        total_count = len(results)
        success_count = sum(1 for r in results if r["success"])
        unsafe_count = 0
        
        for result in results:
            if result["success"]:
                risk_summary = agent_client.get_risk_summary(result["result"])
                if not risk_summary["is_safe"]:
                    unsafe_count += 1
        
        return {
            "success": True,
            "total_count": total_count,
            "success_count": success_count,
            "unsafe_count": unsafe_count,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"批量内容安全审核失败: {str(e)}"
        }

@mcp.tool()
def test_agent_api(agent_id: Optional[str] = None, test_text: Optional[str] = None) -> Dict[str, Any]:
    """
    测试智能体API连接和功能
    
    Args:
        agent_id: 可选的智能体ID，默认使用general_translation
        test_text: 可选的测试文本内容
    
    Returns:
        包含测试结果的字典
    """
    try:
        # 测试API连接
        connection_test = agent_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "agent_api_endpoint": agent_client.agents_url,
            "moderation_api_endpoint": agent_client.moderation_url
        }
        
        # 如果提供了测试参数，进行智能体对话测试
        if agent_id or test_text:
            test_agent_id = agent_id or "general_translation"
            test_message = test_text or "Hello, this is a connection test."
            
            try:
                agent_result = agent_client.chat_with_text(test_agent_id, test_message)
                assistant_message = agent_client.extract_assistant_message(agent_result)
                
                agent_test_result = {
                    "success": True,
                    "agent_id": test_agent_id,
                    "test_message": test_message,
                    "assistant_message": assistant_message,
                    "conversation_id": agent_result.get("conversation_id", "")
                }
                result["agent_test"] = agent_test_result
            except Exception as e:
                result["agent_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"API测试失败: {str(e)}"
        }

@mcp.tool()
def save_agent_dialogue_to_file(
    agent_id: str,
    user_message: str,
    assistant_message: str,
    conversation_id: str,
    filename: str
) -> Dict[str, Any]:
    """
    将智能体对话结果保存到文件
    
    Args:
        agent_id: 智能体ID
        user_message: 用户消息
        assistant_message: 助手回复
        conversation_id: 对话ID
        filename: 保存的文件名
    
    Returns:
        保存结果字典
    """
    try:
        if not agent_id or not user_message or not filename:
            return {
                "success": False,
                "error": "智能体ID、用户消息和文件名都是必需的"
            }
        
        # 准备保存数据
        save_data = {
            "agent_id": agent_id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "conversation_id": conversation_id,
            "timestamp": time.time(),
            "type": "agent_dialogue"
        }
        
        # 创建唯一文件名
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".json"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size,
            "agent_id": agent_id,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存智能体对话失败: {str(e)}"
        }

@mcp.tool()
def save_moderation_results_to_file(
    input_text: str,
    filename: str
) -> Dict[str, Any]:
    """
    将审核结果保存到文件（保留原功能）
    
    Args:
        input_text: 审核的文本内容
        filename: 保存的文件名
    
    Returns:
        保存结果字典
    """
    try:
        if not input_text or not filename:
            return {
                "success": False,
                "error": "审核内容和文件名都是必需的"
            }
        
        # 获取审核结果
        moderation_result = agent_generator.moderate_content(input_text)
        
        # 格式化结果
        formatted_result = agent_client.format_moderation_result(moderation_result)
        risk_summary = agent_client.get_risk_summary(moderation_result)
        
        # 准备保存数据
        save_data = {
            "input_text": input_text,
            "timestamp": time.time(),
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result,
            "raw_result": moderation_result,
            "type": "content_moderation"
        }
        
        # 创建唯一文件名
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".json"
        unique_filename = f"{name}_{file_id}{ext}"
        file_path = OUTPUTS_DIR / unique_filename
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "size": file_path.stat().st_size,
            "input_text": input_text[:100] + "..." if len(input_text) > 100 else input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_count": risk_summary["risk_count"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存审核结果失败: {str(e)}"
        }

@mcp.tool()
def load_results_from_file(filename: str) -> Dict[str, Any]:
    """
    从文件加载结果（支持智能体对话和内容审核）
    
    Args:
        filename: 文件名
    
    Returns:
        加载结果字典
    """
    try:
        if not filename:
            return {
                "success": False,
                "error": "文件名不能为空"
            }
        
        # 检查文件是否存在
        file_path = Path(filename)
        if not file_path.exists():
            # 尝试在输出目录中查找
            output_path = OUTPUTS_DIR / file_path.name
            if output_path.exists():
                file_path = output_path
            else:
                return {
                    "success": False,
                    "error": f"文件不存在: {filename}"
                }
        
        # 加载文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 根据文件类型返回不同的结果
        file_type = data.get("type", "unknown")
        
        base_result = {
            "success": True,
            "filename": file_path.name,
            "timestamp": data.get("timestamp"),
            "type": file_type
        }
        
        if file_type == "agent_dialogue":
            base_result.update({
                "agent_id": data.get("agent_id", ""),
                "user_message": data.get("user_message", ""),
                "assistant_message": data.get("assistant_message", ""),
                "conversation_id": data.get("conversation_id", "")
            })
        elif file_type == "content_moderation":
            base_result.update({
                "input_text": data.get("input_text", ""),
                "is_safe": data.get("is_safe", True),
                "risk_summary": data.get("risk_summary", {}),
                "detailed_result": data.get("detailed_result", {}),
                "raw_result": data.get("raw_result", {})
            })
        else:
            # 兼容旧格式
            base_result.update({
                "input_text": data.get("input_text", ""),
                "is_safe": data.get("is_safe", True),
                "risk_summary": data.get("risk_summary", {}),
                "detailed_result": data.get("detailed_result", {}),
                "raw_result": data.get("raw_result", {})
            })
        
        return base_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"加载结果失败: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式智能体对话系统"""
    print("=" * 60)
    print("🤖 智谱AI智能体对话系统 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 智能体文本对话")
    print("2. 智能体文件对话")
    print("3. 内容安全审核")
    print("4. 批量内容审核")
    print("5. 测试API连接")
    print("6. 保存对话结果到文件")
    print("7. 保存审核结果到文件")
    print("8. 从文件加载结果")
    print("9. 启动MCP服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-9): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_agent_text_chat()
            elif choice == "2":
                handle_agent_file_chat()
            elif choice == "3":
                handle_content_moderation()
            elif choice == "4":
                handle_batch_moderation()
            elif choice == "5":
                handle_api_test()
            elif choice == "6":
                handle_save_dialogue_results()
            elif choice == "7":
                handle_save_moderation_results()
            elif choice == "8":
                handle_load_results()
            elif choice == "9":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            else:
                print("❌ 无效选择，请输入0-9")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_agent_text_chat():
    """处理智能体文本对话"""
    print("\n🤖 智能体文本对话")
    
    agent_id = input("请输入智能体ID (默认: general_translation): ").strip()
    if not agent_id:
        agent_id = "general_translation"
    
    user_message = input("请输入您的消息: ").strip()
    if not user_message:
        print("❌ 用户消息不能为空")
        return
    
    conversation_id = input("请输入对话ID (可选，按回车跳过): ").strip()
    if not conversation_id:
        conversation_id = None
    
    print("🤖 智能体思考中...")
    try:
        result = chat_with_agent(agent_id, user_message, conversation_id)
        
        if result["success"]:
            print(f"✅ 智能体对话完成!")
            print(f"智能体ID: {result['agent_id']}")
            print(f"用户消息: {result['user_message']}")
            print(f"对话ID: {result['conversation_id']}")
            print(f"\n🤖 智能体回复:")
            print(f"{result['assistant_message']}")
        else:
            print(f"❌ 对话失败: {result['error']}")
    except Exception as e:
        print(f"❌ 对话失败: {str(e)}")

def handle_agent_file_chat():
    """处理智能体文件对话"""
    print("\n📁 智能体文件对话")
    
    agent_id = input("请输入智能体ID (默认: general_translation): ").strip()
    if not agent_id:
        agent_id = "general_translation"
    
    file_id = input("请输入文件ID: ").strip()
    if not file_id:
        print("❌ 文件ID不能为空")
        return
    
    conversation_id = input("请输入对话ID (可选，按回车跳过): ").strip()
    if not conversation_id:
        conversation_id = None
    
    print("🤖 智能体处理文件中...")
    try:
        result = chat_with_agent_file(agent_id, file_id, conversation_id)
        
        if result["success"]:
            print(f"✅ 智能体文件对话完成!")
            print(f"智能体ID: {result['agent_id']}")
            print(f"文件ID: {result['file_id']}")
            print(f"对话ID: {result['conversation_id']}")
            print(f"\n🤖 智能体回复:")
            print(f"{result['assistant_message']}")
        else:
            print(f"❌ 文件对话失败: {result['error']}")
    except Exception as e:
        print(f"❌ 文件对话失败: {str(e)}")

def handle_content_moderation():
    """处理内容安全审核"""
    print("\n🛡️ 内容安全审核")
    
    input_text = input("请输入需要审核的文本内容: ").strip()
    if not input_text:
        print("❌ 审核内容不能为空")
        return
    
    print("🛡️ 审核中...")
    try:
        result = moderate_content(input_text)
        
        if result["success"]:
            print(f"✅ 内容安全审核完成!")
            print(f"审核内容: {input_text[:50]}{'...' if len(input_text) > 50 else ''}")
            print(f"安全状态: {'✅ 安全' if result['is_safe'] else '⚠️ 存在风险'}")
            
            # 显示风险摘要
            risk_summary = result['risk_summary']
            if not risk_summary['is_safe']:
                print(f"\n⚠️ 风险分析:")
                print(f"  风险数量: {risk_summary['risk_count']}")
                print(f"  最高风险等级: {risk_summary['highest_risk_level']}")
                print(f"  风险类型: {', '.join(risk_summary['risk_types'])}")
                
                # 显示详细风险信息
                for detail in risk_summary['details']:
                    print(f"  - 内容类型: {detail['content_type']}")
                    print(f"    风险等级: {detail['risk_level']}")
                    print(f"    风险类型: {', '.join(detail['risk_types'])}")
            else:
                print("✅ 内容安全，未发现风险")
        else:
            print(f"❌ 审核失败: {result['error']}")
    except Exception as e:
        print(f"❌ 审核失败: {str(e)}")

def handle_save_dialogue_results():
    """处理保存智能体对话结果"""
    print("\n💾 保存智能体对话结果到文件")
    
    agent_id = input("请输入智能体ID: ").strip()
    if not agent_id:
        print("❌ 智能体ID不能为空")
        return
    
    user_message = input("请输入用户消息: ").strip()
    if not user_message:
        print("❌ 用户消息不能为空")
        return
    
    assistant_message = input("请输入助手回复: ").strip()
    if not assistant_message:
        print("❌ 助手回复不能为空")
        return
    
    conversation_id = input("请输入对话ID: ").strip()
    if not conversation_id:
        conversation_id = ""
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("💾 保存中...")
    try:
        result = save_agent_dialogue_to_file(agent_id, user_message, assistant_message, conversation_id, filename)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"智能体ID: {result['agent_id']}")
            print(f"用户消息: {result['user_message']}")
            print(f"对话ID: {result['conversation_id']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_batch_moderation():
    """处理批量内容审核"""
    print("\n🛡️ 批量内容审核")
    
    print("请输入需要审核的文本内容（每行一个，输入空行结束）:")
    input_texts = []
    while True:
        text = input().strip()
        if not text:
            break
        input_texts.append(text)
    
    if not input_texts:
        print("❌ 未输入任何内容")
        return
    
    print(f"🛡️ 批量审核 {len(input_texts)} 个文本中...")
    try:
        result = batch_moderate_content(input_texts)
        
        if result["success"]:
            print(f"✅ 批量审核完成!")
            print(f"总数量: {result['total_count']}")
            print(f"成功数量: {result['success_count']}")
            print(f"风险内容数量: {result['unsafe_count']}")
            
            # 显示详细结果
            print(f"\n📋 审核结果:")
            for i, item in enumerate(result['results'], 1):
                if item['success']:
                    risk_summary = agent_client.get_risk_summary(item['result'])
                    status = "✅ 安全" if risk_summary['is_safe'] else "⚠️ 风险"
                    print(f"{i}. {item['input'][:30]}... - {status}")
                    if not risk_summary['is_safe']:
                        print(f"   风险类型: {', '.join(risk_summary['risk_types'])}")
                else:
                    print(f"{i}. {item['input'][:30]}... - ❌ 审核失败: {item['error']}")
        else:
            print(f"❌ 批量审核失败: {result['error']}")
    except Exception as e:
        print(f"❌ 批量审核失败: {str(e)}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    
    agent_id = input("请输入智能体ID (可选，默认: general_translation): ").strip()
    if not agent_id:
        agent_id = "general_translation"
    
    test_text = input("请输入测试文本 (可选): ").strip()
    if not test_text:
        test_text = "Hello, this is a connection test."
    
    print("🔍 测试中...")
    try:
        result = test_agent_api(agent_id, test_text)
        
        if result["success"]:
            print("✅ API测试结果:")
            conn_test = result["connection_test"]
            print(f"  智能体API连接: {'正常' if conn_test.get('agent_api', False) else '失败'}")
            print(f"  内容安全API连接: {'正常' if conn_test.get('moderation_api', False) else '失败'}")
            print(f"  智能体API端点: {result['agent_api_endpoint']}")
            print(f"  内容安全API端点: {result['moderation_api_endpoint']}")
            
            if 'agent_test' in result:
                agent_test = result['agent_test']
                if agent_test['success']:
                    print(f"  测试对话: 成功与智能体 '{agent_test['agent_id']}' 对话")
                    print(f"  测试消息: '{agent_test['test_message']}'")
                    print(f"  智能体回复: '{agent_test['assistant_message'][:100]}...'")
                    print(f"  对话ID: {agent_test['conversation_id']}")
                else:
                    print(f"  测试对话失败: {agent_test['error']}")
            
            if conn_test.get('errors'):
                print(f"  错误信息: {'; '.join(conn_test['errors'])}")
        else:
            print(f"❌ API测试失败: {result['error']}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def handle_save_moderation_results():
    """处理保存审核结果"""
    print("\n💾 保存审核结果到文件")
    
    input_text = input("请输入需要审核的文本内容: ").strip()
    if not input_text:
        print("❌ 审核内容不能为空")
        return
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("💾 审核并保存中...")
    try:
        result = save_moderation_results_to_file(input_text, filename)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"审核内容: {result['input_text']}")
            print(f"安全状态: {'安全' if result['is_safe'] else '存在风险'}")
            print(f"风险数量: {result['risk_count']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_load_results():
    """处理加载结果"""
    print("\n📂 从文件加载结果")
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("📂 加载中...")
    try:
        result = load_results_from_file(filename)
        
        if result["success"]:
            print(f"✅ 加载成功!")
            print(f"文件名: {result['filename']}")
            print(f"文件类型: {result['type']}")
            
            if result['type'] == 'agent_dialogue':
                print(f"智能体ID: {result['agent_id']}")
                print(f"用户消息: {result['user_message'][:100]}{'...' if len(result['user_message']) > 100 else ''}")
                print(f"助手回复: {result['assistant_message'][:100]}{'...' if len(result['assistant_message']) > 100 else ''}")
                print(f"对话ID: {result['conversation_id']}")
            elif result['type'] == 'content_moderation' or result['type'] == 'unknown':
                print(f"审核内容: {result['input_text'][:100]}{'...' if len(result['input_text']) > 100 else ''}")
                print(f"安全状态: {'安全' if result['is_safe'] else '存在风险'}")
                
                # 显示风险摘要
                risk_summary = result['risk_summary']
                if not result['is_safe']:
                    print(f"\n风险分析:")
                    print(f"  风险数量: {risk_summary.get('risk_count', 0)}")
                    print(f"  最高风险等级: {risk_summary.get('highest_risk_level', 'unknown')}")
                    print(f"  风险类型: {', '.join(risk_summary.get('risk_types', []))}")
        else:
            print(f"❌ 加载失败: {result['error']}")
    except Exception as e:
        print(f"❌ 加载失败: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--mcp":
            print("🔧 启动MCP服务器模式...")
            mcp.run(transport="sse")
        elif sys.argv[1] == "--test":
            print("🧪 运行测试...")
            handle_api_test()
        else:
            print("❌ 未知参数，支持的参数: --mcp, --test")
    else:
        # 默认运行交互式模式
        run_interactive_mode()