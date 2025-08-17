"""
修复版本的main.py - 专门处理智能体响应解析问题
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

# Create an MCP server
mcp = FastMCP("AI Content Security System - Fixed")

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

@mcp.tool()
def chat_with_agent_debug(agent_id: str, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    与智能体进行对话 - 调试版本
    
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
        
        # 直接调用智能体客户端
        result = agent_client.chat_with_text(agent_id, user_message, conversation_id)
        
        # 详细记录原始响应
        debug_info = {
            "raw_result": result,
            "has_choices": "choices" in result,
            "choices_count": len(result.get("choices", [])),
            "choices_content": result.get("choices", [])
        }
        
        # 尝试多种方式提取助手消息
        assistant_message = ""
        
        # 方法1: 使用现有的extract_assistant_message方法
        assistant_message = agent_client.extract_assistant_message(result)
        
        # 方法2: 如果方法1失败，尝试直接从结果中提取
        if not assistant_message:
            # 检查是否有data字段
            if "data" in result:
                data = result["data"]
                if isinstance(data, dict):
                    if "choices" in data:
                        choices = data["choices"]
                        if choices and len(choices) > 0:
                            first_choice = choices[0]
                            if "message" in first_choice:
                                message = first_choice["message"]
                                if isinstance(message, dict) and message.get("role") == "assistant":
                                    assistant_message = message.get("content", "")
                            elif "messages" in first_choice:
                                messages = first_choice["messages"]
                                for msg in messages:
                                    if msg.get("role") == "assistant":
                                        assistant_message = msg.get("content", "")
                                        break
        
        # 方法3: 检查是否有其他可能的响应字段
        if not assistant_message:
            possible_fields = ["answer", "reply", "text", "result", "output"]
            for field in possible_fields:
                if field in result and isinstance(result[field], str):
                    assistant_message = result[field]
                    break
        
        return {
            "success": True,
            "agent_id": agent_id,
            "user_message": user_message,
            "conversation_id": result.get("conversation_id", ""),
            "assistant_message": assistant_message,
            "debug_info": debug_info,
            "detailed_result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"智能体对话失败: {str(e)}",
            "exception_type": type(e).__name__
        }

if __name__ == "__main__":
    print("🔧 启动修复版MCP服务器...")
    mcp.run(transport="sse")