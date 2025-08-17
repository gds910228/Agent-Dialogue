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
        
        # 普通对话API端点
        self.chat_url = f"{self.base_url}/api/paas/v4/chat/completions"
        
        # 文件上传API端点
        self.files_url = f"{self.base_url}/api/paas/v4/files"
        
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
    
    def upload_text_as_file(self, text_content: str, filename: str = "user_input.txt") -> Optional[str]:
        """
        将文本内容上传为文件
        
        Args:
            text_content: 文本内容
            filename: 文件名
            
        Returns:
            文件ID，如果上传失败返回None
        """
        try:
            # 准备文件数据
            files = {
                'file': (filename, text_content.encode('utf-8'), 'text/plain')
            }
            
            # 准备额外的表单数据
            data = {
                'purpose': 'retrieval'  # 智谱AI可能需要指定用途
            }
            
            # 准备请求头（不包含Content-Type，让requests自动设置）
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            print(f"上传文件到: {self.files_url}")
            print(f"文件名: {filename}")
            print(f"内容长度: {len(text_content)} 字符")
            
            response = requests.post(
                self.files_url,
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"上传响应状态码: {response.status_code}")
            print(f"上传响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                file_id = result.get("id")
                print(f"文件上传成功，文件ID: {file_id}")
                return file_id
            else:
                print(f"文件上传失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"文件上传异常: {str(e)}")
            return None
    
    def chat_with_direct_api(
        self,
        user_message: str,
        model: str = "glm-4",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        使用普通对话API进行对话
        
        Args:
            user_message: 用户消息
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            对话结果字典
        """
        request_data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.chat_url,
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
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
        首先尝试智能体API，如果失败则使用普通对话API
        
        Args:
            agent_id: 智能体ID
            user_message: 用户消息文本
            conversation_id: 可选的对话ID
            
        Returns:
            对话结果字典
        """
        try:
            # 首先尝试智能体API（需要文件上传）
            file_id = self.upload_text_as_file(user_message)
            if file_id:
                # 使用文件ID进行智能体对话
                return self.chat_with_file(agent_id, file_id, conversation_id)
            else:
                # 如果文件上传失败，使用普通对话API作为回退
                print("智能体API文件上传失败，使用普通对话API作为回退...")
                result = self.chat_with_direct_api(user_message)
                
                # 转换为统一格式
                return {
                    "agent_id": agent_id,
                    "conversation_id": conversation_id or "",
                    "choices": result.get("choices", []),
                    "usage": result.get("usage", {}),
                    "fallback_to_direct_api": True
                }
        except Exception as e:
            # 如果智能体API完全失败，使用普通对话API作为回退
            try:
                print(f"智能体API失败: {str(e)}，使用普通对话API作为回退...")
                result = self.chat_with_direct_api(user_message)
                
                # 转换为统一格式
                return {
                    "agent_id": agent_id,
                    "conversation_id": conversation_id or "",
                    "choices": result.get("choices", []),
                    "usage": result.get("usage", {}),
                    "fallback_to_direct_api": True,
                    "original_error": str(e)
                }
            except Exception as fallback_error:
                return {
                    "error": f"智能体API和普通对话API都失败了。智能体API错误: {str(e)}，普通对话API错误: {str(fallback_error)}",
                    "agent_id": agent_id,
                    "original_message": user_message
                }
    
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
        根据智谱AI智能体API文档，优先处理标准格式：choices[0].messages[].content
        
        Args:
            agent_result: 智能体响应结果
            
        Returns:
            助手消息文本
        """
        try:
            # 优先处理智能体API标准格式：choices[0].messages[]
            choices = agent_result.get("choices", [])
            if choices and len(choices) > 0:
                first_choice = choices[0]
                
                # 智能体API格式：choices[0].messages[]
                messages = first_choice.get("messages", [])
                if messages:
                    # 查找role为assistant的消息，跳过空内容
                    for message in messages:
                        if isinstance(message, dict) and message.get("role") == "assistant":
                            content = message.get("content", "")
                            
                            # 处理content为字符串的情况
                            if isinstance(content, str) and content.strip():
                                return content.strip()
                            
                            # 处理content为对象的情况（智谱AI实际格式）
                            elif isinstance(content, dict):
                                # 检查是否有text字段
                                if "text" in content:
                                    text_content = content["text"]
                                    if isinstance(text_content, str) and text_content.strip():
                                        return text_content.strip()
                                
                                # 检查是否有content字段（嵌套结构）
                                elif "content" in content:
                                    nested_content = content["content"]
                                    if isinstance(nested_content, str) and nested_content.strip():
                                        return nested_content.strip()
                
                # 兼容普通对话API格式：choices[0].message.content
                if "message" in first_choice:
                    message = first_choice["message"]
                    if isinstance(message, dict) and message.get("role") == "assistant":
                        content = message.get("content", "")
                        if content and isinstance(content, str):
                            return content.strip()
            
            # 如果标准格式没有找到，尝试其他可能的字段（向后兼容）
            fallback_fields = ["message", "content", "response", "output"]
            for field in fallback_fields:
                if field in agent_result:
                    value = agent_result[field]
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                    elif isinstance(value, dict) and value.get("role") == "assistant":
                        content = value.get("content", "")
                        if content and isinstance(content, str):
                            return content.strip()
            
            # 如果都没有找到有效内容，返回调试信息
            return f"未找到助手消息。响应结构: {list(agent_result.keys())}"
            
        except Exception as e:
            return f"提取助手消息时出错: {str(e)}"
    
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
                "general_translation", 
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