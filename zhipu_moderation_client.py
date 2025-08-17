"""
智谱AI内容安全客户端
提供内容安全审核功能，对接智谱AI的内容安全API
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional


class ZhipuModerationClient:
    """智谱AI内容安全客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn"):
        """
        初始化客户端
        
        Args:
            api_key: 智谱AI API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        # 智谱AI内容安全的正确端点
        if "/api/paas/v4" in self.base_url:
            self.moderation_url = f"{self.base_url}/moderations"
        else:
            self.moderation_url = f"{self.base_url}/api/paas/v4/moderations"
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def moderate_content(self, input_text: str) -> Dict[str, Any]:
        """
        执行内容安全审核
        
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
    
    def batch_moderate_content(self, input_texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量执行内容安全审核
        
        Args:
            input_texts: 需要审核的文本内容列表
            
        Returns:
            审核结果列表
        """
        if not input_texts:
            raise ValueError("审核内容列表不能为空")
        
        results = []
        for text in input_texts:
            try:
                result = self.moderate_content(text)
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
        
        return results
    
    def format_moderation_result(self, moderation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化审核结果，提取关键信息
        
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
        判断内容是否安全
        
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
        获取风险摘要
        
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
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            # 使用简单的测试文本
            test_result = self.moderate_content("测试内容安全API连接")
            return True
        except Exception as e:
            print(f"连接测试异常: {str(e)}")
            return False
    
    def validate_input(self, input_text: str) -> Dict[str, Any]:
        """
        验证输入参数
        
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