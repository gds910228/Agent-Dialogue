"""
智谱AI文本重排序客户端
支持文本重排序功能，对候选文档进行相关性排序
"""

import json
import requests
import time
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuRerankClient:
    """智谱AI文本重排序客户端"""
    
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
    
    def rerank(
        self, 
        query: str,
        documents: List[str], 
        model: str = "rerank",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            model: 重排序模型名称
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            
        Returns:
            包含重排序结果的响应字典
        """
        # 智谱AI重排序API端点
        url = f"{self.base_url}/api/paas/v4/rerank"
        
        # 构建请求数据
        data = {
            "model": model,
            "query": query,
            "documents": documents
        }
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"发送重排序请求 (尝试 {attempt + 1}/{max_retries + 1})")
                logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
                
                response = self.session.post(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("重排序请求成功")
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
    
    def get_ranked_documents(
        self, 
        query: str,
        documents: List[str], 
        model: str = "rerank",
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取排序后的文档列表
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            model: 重排序模型名称
            top_k: 返回前k个结果，None表示返回所有结果
            
        Returns:
            排序后的文档列表，每个元素包含document, relevance_score, index
        """
        result = self.rerank(query, documents, model)
        
        if not result.get("results"):
            return []
        
        # 获取排序结果并添加文档内容
        ranked_results = []
        for item in result["results"]:
            index = item.get("index", 0)
            relevance_score = item.get("relevance_score", 0)
            
            # 根据索引获取对应的文档内容
            if 0 <= index < len(documents):
                ranked_results.append({
                    "document": documents[index],
                    "relevance_score": relevance_score,
                    "index": index
                })
        
        # 如果指定了top_k，则只返回前k个结果
        if top_k is not None:
            ranked_results = ranked_results[:top_k]
        
        return ranked_results
    
    def find_most_relevant(
        self, 
        query: str,
        documents: List[str], 
        model: str = "rerank",
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        找到与查询最相关的文档
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            model: 重排序模型名称
            threshold: 相关性阈值，只返回超过此阈值的文档
            
        Returns:
            相关性超过阈值的文档列表
        """
        ranked_docs = self.get_ranked_documents(query, documents, model)
        
        # 过滤相关性分数超过阈值的文档
        relevant_docs = [
            doc for doc in ranked_docs 
            if doc.get("relevance_score", 0) >= threshold
        ]
        
        return relevant_docs
    
    def get_available_models(self) -> List[str]:
        """
        获取可用的重排序模型列表
        
        Returns:
            模型名称列表
        """
        # 智谱AI支持的重排序模型
        return ["rerank"]
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            result = self.rerank(
                query="测试查询",
                documents=["测试文档1", "测试文档2"],
                model="rerank"
            )
            return "results" in result and len(result["results"]) > 0
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
            "total_tokens": usage.get("total_tokens", 0),
            "request_id": result.get("request_id", ""),
            "created": result.get("created", 0)
        }

def main():
    """测试函数"""
    import os
    
    # 从环境变量获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return
    
    client = ZhipuRerankClient(api_key)
    
    # 测试连接
    print("测试API连接...")
    if client.test_connection():
        print("✓ 连接成功")
    else:
        print("✗ 连接失败")
        return
    
    # 测试文本重排序
    print("\n测试文本重排序...")
    query = "人工智能的发展历史"
    documents = [
        "人工智能起源于20世纪50年代，由图灵等科学家奠定基础",
        "今天的天气很好，适合出门散步",
        "机器学习是人工智能的重要分支，包括监督学习和无监督学习",
        "我喜欢吃苹果和香蕉",
        "深度学习在近年来取得了突破性进展，推动了AI技术的发展"
    ]
    
    try:
        result = client.rerank(query, documents)
        print(f"查询: {query}")
        print("重排序结果:")
        
        for i, item in enumerate(result.get("results", [])):
            print(f"{i+1}. {item['document']} (相关性: {item['relevance_score']:.4f})")
        
        # 显示使用信息
        usage_info = client.get_usage_info(result)
        print(f"\n使用信息:")
        print(f"  提示词tokens: {usage_info['prompt_tokens']}")
        print(f"  总tokens: {usage_info['total_tokens']}")
        print(f"  请求ID: {usage_info['request_id']}")
        
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试获取最相关文档
    print("\n测试获取最相关文档 (阈值: 0.7)...")
    try:
        relevant_docs = client.find_most_relevant(query, documents, threshold=0.7)
        print(f"找到 {len(relevant_docs)} 个相关文档:")
        for i, doc in enumerate(relevant_docs):
            print(f"{i+1}. {doc['document']} (相关性: {doc['relevance_score']:.4f})")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()