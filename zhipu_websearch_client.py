"""
智谱AI网络搜索客户端
提供网络搜索功能，对接智谱AI的网络搜索API
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional


class ZhipuWebSearchClient:
    """智谱AI网络搜索客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn", search_engine: str = "search_std"):
        """
        初始化客户端
        
        Args:
            api_key: 智谱AI API密钥
            base_url: API基础URL
            search_engine: 搜索引擎类型，默认为search_std
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        # 智谱AI网络搜索的正确端点
        # 检查base_url是否已经包含完整的API路径
        if "/api/paas/v4" in self.base_url:
            self.search_url = f"{self.base_url}/web_search"
        else:
            self.search_url = f"{self.base_url}/api/paas/v4/web_search"
        self.search_engine = search_engine
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, 
               search_query: str,
               search_intent: bool = False,
               count: int = 10,
               search_recency_filter: str = "noLimit") -> Dict[str, Any]:
        """
        执行网络搜索
        
        Args:
            search_query: 搜索查询字符串
            search_intent: 是否返回搜索意图分析
            count: 返回结果数量，默认10
            search_recency_filter: 搜索时效性过滤，可选值：noLimit, day, week, month, year
            
        Returns:
            搜索结果字典
        """
        if not search_query or not search_query.strip():
            raise ValueError("搜索查询不能为空")
        
        # 构建请求数据 - 使用智谱AI网络搜索的专用格式
        request_data = {
            "search_engine": self.search_engine,
            "search_intent": search_intent,
            "count": count,
            "search_recency_filter": search_recency_filter,
            "search_query": search_query.strip()
        }
        
        try:
            response = requests.post(
                self.search_url,
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
            
            # 网络搜索API直接返回搜索结果，不需要转换
            return result
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接错误，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("API响应格式错误")
    
    def _convert_to_standard_format(self, api_result: Dict[str, Any], search_query: str, search_intent: bool) -> Dict[str, Any]:
        """
        将智谱AI的响应转换为标准格式
        
        Args:
            api_result: 智谱AI API的原始响应
            search_query: 搜索查询
            search_intent: 是否包含搜索意图
            
        Returns:
            标准格式的搜索结果
        """
        standard_result = {
            "id": api_result.get("id", ""),
            "created": api_result.get("created", int(time.time())),
            "request_id": api_result.get("request_id", api_result.get("id", "")),
            "search_intent": [],
            "search_result": []
        }
        
        # 处理搜索意图（如果需要）
        if search_intent:
            standard_result["search_intent"] = [{
                "query": search_query,
                "intent": "信息搜索",
                "keywords": search_query
            }]
        
        # 从响应中提取搜索结果
        choices = api_result.get("choices", [])
        if choices:
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # 智谱AI将搜索结果直接包含在消息内容中
            if content and content.strip():
                standard_result["search_result"] = [{
                    "title": f"搜索结果：{search_query}",
                    "content": content,
                    "link": "",
                    "media": "",
                    "icon": "",
                    "refer": "智谱AI网络搜索",
                    "publish_date": ""
                }]
        
        return standard_result
    
    def search_with_intent(self, search_query: str, count: int = 10) -> Dict[str, Any]:
        """
        执行带搜索意图分析的网络搜索
        
        Args:
            search_query: 搜索查询字符串
            count: 返回结果数量
            
        Returns:
            包含搜索意图和搜索结果的字典
        """
        return self.search(
            search_query=search_query,
            search_intent=True,
            count=count
        )
    
    def search_recent(self, 
                     search_query: str, 
                     recency: str = "day",
                     count: int = 10) -> Dict[str, Any]:
        """
        搜索最近的内容
        
        Args:
            search_query: 搜索查询字符串
            recency: 时效性过滤，可选值：day, week, month, year
            count: 返回结果数量
            
        Returns:
            搜索结果字典
        """
        return self.search(
            search_query=search_query,
            search_recency_filter=recency,
            count=count
        )
    
    def format_search_results(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化搜索结果，提取关键信息
        
        Args:
            search_result: 原始搜索结果
            
        Returns:
            格式化后的结果
        """
        formatted_result = {
            "id": search_result.get("id", ""),
            "created": search_result.get("created", 0),
            "request_id": search_result.get("request_id", ""),
            "total_results": 0,
            "search_intent": [],
            "search_results": []
        }
        
        # 处理搜索意图
        if "search_intent" in search_result and search_result["search_intent"]:
            for intent in search_result["search_intent"]:
                formatted_result["search_intent"].append({
                    "query": intent.get("query", ""),
                    "intent": intent.get("intent", ""),
                    "keywords": intent.get("keywords", "")
                })
        
        # 处理搜索结果
        if "search_result" in search_result and search_result["search_result"]:
            formatted_result["total_results"] = len(search_result["search_result"])
            
            for result in search_result["search_result"]:
                formatted_result["search_results"].append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "link": result.get("link", ""),
                    "media": result.get("media", ""),
                    "icon": result.get("icon", ""),
                    "refer": result.get("refer", ""),
                    "publish_date": result.get("publish_date", "")
                })
        
        return formatted_result
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            # 使用简单的聊天请求测试连接
            test_data = {
                "model": "glm-4-plus",
                "messages": [
                    {
                        "role": "user",
                        "content": "你好"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.search_url,
                headers=self.headers,
                json=test_data,
                timeout=10
            )
            
            print(f"测试连接响应状态码: {response.status_code}")
            if response.status_code != 200:
                print(f"响应内容: {response.text}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"连接测试异常: {str(e)}")
            return False
    
    def get_available_recency_filters(self) -> List[str]:
        """
        获取可用的时效性过滤选项
        
        Returns:
            时效性过滤选项列表
        """
        return ["noLimit", "day", "week", "month", "year"]
    
    def validate_search_params(self, 
                              search_query: str,
                              count: int,
                              search_recency_filter: str) -> Dict[str, Any]:
        """
        验证搜索参数
        
        Args:
            search_query: 搜索查询
            count: 结果数量
            search_recency_filter: 时效性过滤
            
        Returns:
            验证结果
        """
        errors = []
        
        # 验证搜索查询
        if not search_query or not search_query.strip():
            errors.append("搜索查询不能为空")
        elif len(search_query.strip()) > 1000:
            errors.append("搜索查询长度不能超过1000个字符")
        
        # 验证结果数量
        if not isinstance(count, int) or count < 1 or count > 50:
            errors.append("结果数量必须是1-50之间的整数")
        
        # 验证时效性过滤
        valid_filters = self.get_available_recency_filters()
        if search_recency_filter not in valid_filters:
            errors.append(f"时效性过滤必须是以下值之一: {', '.join(valid_filters)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }