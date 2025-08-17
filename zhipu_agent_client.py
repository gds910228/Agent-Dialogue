"""
智谱AI智能体对话客户端
提供智能体对话功能，对接智谱AI的智能体对话API
同时保留内容安全功能
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Union


class ZhipuAgentClient:
    """智谱AI智能体对话客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn"):
        """
        初始化客户端
        
        Args:
            api_key: 智谱AI API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        # 智能体对话API端点
        self.agents_url = f"{self.base_url}/api/v1/agents"
        
        # 内容安全API端点（保留原功能）
        self.moderation_url = f"{self.base_url}/api/paas/v4/moderations"
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_with_agent(
        self, 
        agent_id: str, 
        messages: List[Dict[str, Any]], 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        与智能体进行对话
        
        Args:
            agent_id: 智能体ID
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            conversation_id: 可选的对话ID，用于继续之前的对话
            
        Returns:
            对话结果字典
        """
        if not agent_id or not agent_id.strip():
            raise ValueError("智能体ID不能为空")
        
        if not messages:
            raise ValueError("消息列表不能为空")
        
        # 构建请求数据
        request_data = {
            "agent_id": agent_id.strip(),
            "messages": messages
        }
        
        # 如果提供了对话ID，添加到请求中
        if conversation_id:
            request_data["conversation_id"] = conversation_id
        
        try:
            response = requests.post(
                self.agents_url,
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f", 错误信息: {error_data['error']['message']}"
                    elif "message" in error_data:
                        error_msg += f", 错误信息: {error_data['message']}"
                except:
                    error_msg += f", 响应内容: {response.text}"
                raise Exception(error_msg)
            
            # 解析响应
            result = response.json()
            return result
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接错误，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("API响应格式错误")
    
    def chat_with_text(
        self, 
        agent_id: str, 
        user_message: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送文本消息与智能体对话
        
        Args:
            agent_id: 智能体ID
            user_message: 用户消息文本
            conversation_id: 可选的对话ID
            
        Returns:
            对话结果字典
        """
        messages = [
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        return self.chat_with_agent(agent_id, messages, conversation_id)
    
    def chat_with_file(
        self, 
        agent_id: str, 
        file_id: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送文件与智能体对话
        
        Args:
            agent_id: 智能体ID
            file_id: 文件ID
            conversation_id: 可选的对话ID
            
        Returns:
            对话结果字典
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "file_id",
                        "file_id": file_id
                    }
                ]
            }
        ]
        
        return self.chat_with_agent(agent_id, messages, conversation_id)
    
    def moderate_content(self, input_text: str) -> Dict[str, Any]:
        """
        执行内容安全审核（保留原功能）
        
        Args:
            input_text: 需要审核的文本内容
            
        Returns:
            审核结果字典
        """
        if not input_text or not input_text.strip():
            raise ValueError("审核内容不能为空")
        
        # 构建请求数据
        request_data = {
            "model": "moderation",
            "input": input_text.strip()
        }
        
        try:
            response = requests.post(
                self.moderation_url,
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f", 错误信息: {error_data['error']['message']}"
                    elif "message" in error_data:
                        error_msg += f", 错误信息: {error_data['message']}"
                except:
                    error_msg += f", 响应内容: {response.text}"
                raise Exception(error_msg)
            
            # 解析响应
            result = response.json()
            return result
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接错误，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("API响应格式错误")
    
    def format_agent_response(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化智能体响应结果
        
        Args:
            agent_result: 原始智能体响应结果
            
        Returns:
            格式化后的结果
        """
        formatted_result = {
            "id": agent_result.get("id", ""),
            "agent_id": agent_result.get("agent_id", ""),
            "conversation_id": agent_result.get("conversation_id", ""),
            "async_id": agent_result.get("async_id", ""),
            "choices": [],
            "usage": agent_result.get("usage", {})
        }
        
        # 处理选择列表
        choices = agent_result.get("choices", [])
        for choice in choices:
            formatted_choice = {
                "index": choice.get("index", 0),
                "messages": choice.get("messages", []),
                "finish_reason": choice.get("finish_reason", "")
            }
            formatted_result["choices"].append(formatted_choice)
        
        return formatted_result
    
    def extract_assistant_message(self, agent_result: Dict[str, Any]) -> str:
        """
        从智能体响应中提取助手消息
        
        Args:
            agent_result: 智能体响应结果
            
        Returns:
            助手消息文本
        """
        choices = agent_result.get("choices", [])
        if not choices:
            return ""
        
        # 获取第一个选择的消息
        first_choice = choices[0]
        messages = first_choice.get("messages", [])
        
        for message in messages:
            if message.get("role") == "assistant":
                return message.get("content", "")
        
        return ""
    
    def format_moderation_result(self, moderation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化审核结果，提取关键信息（保留原功能）
        
        Args:
            moderation_result: 原始审核结果
            
        Returns:
            格式化后的结果
        """
        formatted_result = {
            "id": moderation_result.get("id", ""),
            "created": moderation_result.get("created", 0),
            "request_id": moderation_result.get("request_id", ""),
            "results": [],
            "usage": moderation_result.get("usage", {})
        }
        
        # 处理审核结果列表
        result_list = moderation_result.get("result_list", [])
        for result in result_list:
            formatted_result["results"].append({
                "content_type": result.get("content_type", ""),
                "risk_level": result.get("risk_level", ""),
                "risk_type": result.get("risk_type", [])
            })
        
        return formatted_result
    
    def is_content_safe(self, moderation_result: Dict[str, Any]) -> bool:
        """
        判断内容是否安全（保留原功能）
        
        Args:
            moderation_result: 审核结果
            
        Returns:
            内容是否安全
        """
        result_list = moderation_result.get("result_list", [])
        
        for result in result_list:
            risk_level = result.get("risk_level", "").lower()
            # 如果风险等级为高风险，则认为不安全
            if risk_level in ["high", "高"]:
                return False
        
        return True
    
    def get_risk_summary(self, moderation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取风险摘要（保留原功能）
        
        Args:
            moderation_result: 审核结果
            
        Returns:
            风险摘要
        """
        result_list = moderation_result.get("result_list", [])
        
        risk_summary = {
            "is_safe": True,
            "risk_count": 0,
            "risk_types": [],
            "highest_risk_level": "low",
            "details": []
        }
        
        for result in result_list:
            risk_level = result.get("risk_level", "").lower()
            risk_types = result.get("risk_type", [])
            content_type = result.get("content_type", "")
            
            if risk_level in ["medium", "high", "中", "高"]:
                risk_summary["is_safe"] = False
                risk_summary["risk_count"] += 1
                
                # 更新最高风险等级
                if risk_level in ["high", "高"]:
                    risk_summary["highest_risk_level"] = "high"
                elif risk_level in ["medium", "中"] and risk_summary["highest_risk_level"] != "high":
                    risk_summary["highest_risk_level"] = "medium"
                
                # 收集风险类型
                for risk_type in risk_types:
                    if risk_type not in risk_summary["risk_types"]:
                        risk_summary["risk_types"].append(risk_type)
                
                # 添加详细信息
                risk_summary["details"].append({
                    "content_type": content_type,
                    "risk_level": risk_level,
                    "risk_types": risk_types
                })
        
        return risk_summary
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接
        
        Returns:
            连接测试结果
        """
        test_results = {
            "agent_api": False,
            "moderation_api": False,
            "errors": []
        }
        
        # 测试智能体API连接
        try:
            # 使用一个简单的测试请求
            test_agent_result = self.chat_with_text(
                "doc_translation_agent", 
                "Hello, this is a connection test."
            )
            test_results["agent_api"] = True
        except Exception as e:
            test_results["errors"].append(f"智能体API连接失败: {str(e)}")
        
        # 测试内容安全API连接
        try:
            test_moderation_result = self.moderate_content("测试内容安全API连接")
            test_results["moderation_api"] = True
        except Exception as e:
            test_results["errors"].append(f"内容安全API连接失败: {str(e)}")
        
        return test_results
    
    def validate_agent_input(
        self, 
        agent_id: str, 
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        验证智能体输入参数
        
        Args:
            agent_id: 智能体ID
            messages: 消息列表
            
        Returns:
            验证结果
        """
        errors = []
        
        # 验证智能体ID
        if not agent_id or not agent_id.strip():
            errors.append("智能体ID不能为空")
        
        # 验证消息列表
        if not messages:
            errors.append("消息列表不能为空")
        else:
            for i, message in enumerate(messages):
                if not isinstance(message, dict):
                    errors.append(f"第{i+1}个消息格式错误，必须是字典")
                    continue
                
                if "role" not in message:
                    errors.append(f"第{i+1}个消息缺少role字段")
                
                if "content" not in message:
                    errors.append(f"第{i+1}个消息缺少content字段")
                
                role = message.get("role", "")
                if role not in ["user", "assistant", "system"]:
                    errors.append(f"第{i+1}个消息的role字段值无效: {role}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_moderation_input(self, input_text: str) -> Dict[str, Any]:
        """
        验证内容安全输入参数（保留原功能）
        
        Args:
            input_text: 输入文本
            
        Returns:
            验证结果
        """
        errors = []
        
        # 验证输入文本
        if not input_text or not input_text.strip():
            errors.append("输入文本不能为空")
        elif len(input_text.strip()) > 10000:
            errors.append("输入文本长度不能超过10000个字符")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }