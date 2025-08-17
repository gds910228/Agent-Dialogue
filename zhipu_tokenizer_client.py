"""
智谱AI文本分词器客户端
支持文本分词功能，计算文本的token数量
"""

import json
import requests
import time
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuTokenizerClient:
    """智谱AI文本分词器客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn"):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def tokenize(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "glm-4-plus",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        对文本进行分词计算
        
        Args:
            messages: 消息列表，每个消息包含role和content
            model: 分词模型名称
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            
        Returns:
            包含分词结果的响应字典
        """
        # 智谱AI分词API端点
        url = f"{self.base_url}/paas/v4/tokenizer"
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages
        }
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"发送分词请求 (尝试 {attempt + 1}/{max_retries + 1})")
                logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
                
                response = self.session.post(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("分词请求成功")
                    return result
                else:
                    error_msg = f"API请求失败: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    if attempt < max_retries:
                        logger.info(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        raise Exception(error_msg)
                        
            except requests.exceptions.RequestException as e:
                error_msg = f"网络请求异常: {str(e)}"
                logger.error(error_msg)
                
                if attempt < max_retries:
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception(error_msg)
        
        raise Exception("所有重试都失败了")
    
    def count_tokens(
        self, 
        text: str,
        role: str = "user",
        model: str = "glm-4-plus"
    ) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 要计算的文本内容
            role: 消息角色，默认为user
            model: 分词模型名称
            
        Returns:
            token数量
        """
        messages = [{"role": role, "content": text}]
        result = self.tokenize(messages, model)
        
        # 从结果中提取token数量
        return result.get("usage", {}).get("prompt_tokens", 0)
    
    def count_tokens_for_messages(
        self, 
        messages: List[Dict[str, str]],
        model: str = "glm-4-plus"
    ) -> int:
        """
        计算消息列表的token数量
        
        Args:
            messages: 消息列表，每个消息包含role和content
            model: 分词模型名称
            
        Returns:
            token数量
        """
        result = self.tokenize(messages, model)
        return result.get("usage", {}).get("prompt_tokens", 0)
    
    def get_available_models(self) -> List[str]:
        """
        获取可用的分词模型列表
        
        Returns:
            模型名称列表
        """
        # 智谱AI支持的分词模型
        return ["glm-4-plus", "glm-4", "glm-3-turbo"]
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            result = self.tokenize(
                messages=[{"role": "user", "content": "测试文本"}],
                model="glm-4-plus"
            )
            return "usage" in result and "prompt_tokens" in result.get("usage", {})
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False
    
    def get_usage_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从API响应中提取使用信息
        
        Args:
            result: API响应结果
            
        Returns:
            使用信息字典
        """
        usage = result.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "request_id": result.get("request_id", ""),
            "created": result.get("created", 0),
            "id": result.get("id", "")
        }

def main():
    """测试函数"""
    import os
    
    # 从环境变量获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return
    
    client = ZhipuTokenizerClient(api_key)
    
    # 测试连接
    print("测试API连接...")
    if client.test_connection():
        print("✓ 连接成功")
    else:
        print("✗ 连接失败")
        return
    
    # 测试文本分词
    print("\n测试文本分词...")
    text = "What opportunities and challenges will the Chinese large model industry face in 2025?"
    
    try:
        token_count = client.count_tokens(text)
        print(f"文本: {text}")
        print(f"Token数量: {token_count}")
        
        # 测试多条消息
        print("\n测试多条消息分词...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about AI development."},
            {"role": "assistant", "content": "AI has evolved significantly over the years."}
        ]
        
        tokens = client.count_tokens_for_messages(messages)
        print(f"消息列表Token数量: {tokens}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()