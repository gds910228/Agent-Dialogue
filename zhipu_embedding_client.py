"""
智谱AI文本嵌入客户端
支持多种嵌入模型，将文本转换为高维向量表示
"""

import json
import requests
import time
from typing import List, Dict, Any, Optional, Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZhipuEmbeddingClient:
    """智谱AI文本嵌入客户端"""
    
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
    
    def get_embeddings(
        self, 
        input_text: Union[str, List[str]], 
        model: str = "embedding-3",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        获取文本嵌入向量
        
        Args:
            input_text: 输入文本，可以是单个字符串或字符串列表
            model: 嵌入模型名称
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            
        Returns:
            包含嵌入向量的响应字典
        """
        # 智谱AI嵌入API的正确端点
        url = f"{self.base_url}/api/paas/v4/embeddings"
        
        # 构建请求数据
        data = {
            "model": model,
            "input": input_text
        }
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"发送嵌入请求 (尝试 {attempt + 1}/{max_retries + 1})")
                logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
                
                response = self.session.post(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("嵌入请求成功")
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
    
    def get_single_embedding(
        self, 
        text: str, 
        model: str = "embedding-3"
    ) -> List[float]:
        """
        获取单个文本的嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型名称
            
        Returns:
            嵌入向量列表
        """
        result = self.get_embeddings(text, model)
        if result.get("data") and len(result["data"]) > 0:
            return result["data"][0]["embedding"]
        else:
            raise Exception("未能获取到嵌入向量")
    
    def get_batch_embeddings(
        self, 
        texts: List[str], 
        model: str = "embedding-3"
    ) -> List[List[float]]:
        """
        批量获取文本嵌入向量
        
        Args:
            texts: 文本列表
            model: 嵌入模型名称
            
        Returns:
            嵌入向量列表的列表
        """
        result = self.get_embeddings(texts, model)
        embeddings = []
        
        if result.get("data"):
            # 按索引排序确保顺序正确
            sorted_data = sorted(result["data"], key=lambda x: x["index"])
            embeddings = [item["embedding"] for item in sorted_data]
        
        return embeddings
    
    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        计算两个嵌入向量的余弦相似度
        
        Args:
            embedding1: 第一个嵌入向量
            embedding2: 第二个嵌入向量
            
        Returns:
            余弦相似度值 (-1 到 1)
        """
        import math
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # 计算向量长度
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(a * a for a in embedding2))
        
        # 避免除零
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # 计算余弦相似度
        similarity = dot_product / (norm1 * norm2)
        return similarity
    
    def find_most_similar(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        model: str = "embedding-3"
    ) -> List[Dict[str, Any]]:
        """
        找到与查询文本最相似的候选文本
        
        Args:
            query_text: 查询文本
            candidate_texts: 候选文本列表
            model: 嵌入模型名称
            
        Returns:
            按相似度排序的结果列表，每个元素包含text, similarity, index
        """
        # 获取查询文本的嵌入
        query_embedding = self.get_single_embedding(query_text, model)
        
        # 获取候选文本的嵌入
        candidate_embeddings = self.get_batch_embeddings(candidate_texts, model)
        
        # 计算相似度
        results = []
        for i, (text, embedding) in enumerate(zip(candidate_texts, candidate_embeddings)):
            similarity = self.calculate_similarity(query_embedding, embedding)
            results.append({
                "text": text,
                "similarity": similarity,
                "index": i
            })
        
        # 按相似度降序排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results
    
    def get_available_models(self) -> List[str]:
        """
        获取可用的嵌入模型列表
        
        Returns:
            模型名称列表
        """
        # 智谱AI支持的嵌入模型
        return [
            "embedding-3",
            "embedding-2"
        ]
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            result = self.get_embeddings("测试连接", "embedding-3")
            return "data" in result and len(result["data"]) > 0
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False

def main():
    """测试函数"""
    import os
    
    # 从环境变量获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return
    
    client = ZhipuEmbeddingClient(api_key)
    
    # 测试连接
    print("测试API连接...")
    if client.test_connection():
        print("✓ 连接成功")
    else:
        print("✗ 连接失败")
        return
    
    # 测试单个文本嵌入
    print("\n测试单个文本嵌入...")
    text = "人工智能是计算机科学的一个分支"
    try:
        embedding = client.get_single_embedding(text)
        print(f"文本: {text}")
        print(f"嵌入维度: {len(embedding)}")
        print(f"前5个值: {embedding[:5]}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试相似度搜索
    print("\n测试相似度搜索...")
    query = "机器学习算法"
    candidates = [
        "深度学习是机器学习的一个子领域",
        "今天天气很好",
        "神经网络是人工智能的重要技术",
        "我喜欢吃苹果",
        "自然语言处理属于AI领域"
    ]
    
    try:
        results = client.find_most_similar(query, candidates)
        print(f"查询: {query}")
        print("最相似的文本:")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result['text']} (相似度: {result['similarity']:.4f})")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()