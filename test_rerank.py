#!/usr/bin/env python3
"""
简单的重排序功能测试脚本
"""

from zhipu_rerank_client import ZhipuRerankClient
import json

def test_rerank():
    """测试重排序功能"""
    print("🔄 测试智谱文本重排序功能")
    print("=" * 50)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get('zhipu_api_key', '')
        if not api_key:
            print("❌ 未找到API密钥，请检查config.json配置")
            return False
        
        print(f"✅ API密钥已加载: {api_key[:10]}...")
        
        # 创建客户端
        client = ZhipuRerankClient(api_key=api_key)
        print("✅ 重排序客户端已创建")
        
        # 测试数据
        query = "人工智能的发展"
        documents = [
            "机器学习是人工智能的重要分支",
            "今天天气很好，适合出门散步",
            "深度学习推动了AI技术的快速进步",
            "我喜欢吃苹果和香蕉",
            "神经网络是深度学习的基础"
        ]
        
        print(f"\n📝 查询文本: {query}")
        print(f"📄 候选文档数量: {len(documents)}")
        print("\n候选文档:")
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc}")
        
        # 执行重排序
        print("\n🔍 执行重排序...")
        try:
            # 使用修复后的方法获取排序文档
            ranked_docs = client.get_ranked_documents(query, documents)
            
            if ranked_docs:
                print("✅ 重排序成功!")
                print(f"\n📊 重排序结果 (按相关性排序):")
                
                for i, item in enumerate(ranked_docs, 1):
                    doc = item['document']
                    score = item['relevance_score']
                    index = item['index']
                    
                    print(f"  {i}. {doc}")
                    print(f"     相关性得分: {score:.4f} (原索引: {index})")
                
                # 获取原始结果以显示使用情况
                raw_result = client.rerank(query, documents)
                if 'usage' in raw_result:
                    usage = raw_result['usage']
                    print(f"\n💰 API使用情况:")
                    print(f"  Token使用: {usage.get('total_tokens', 'N/A')}")
                
                return True
            else:
                print("❌ 重排序结果为空")
                return False
                
        except Exception as e:
            print(f"❌ 重排序执行失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试初始化失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_rerank()
    if success:
        print("\n🎉 重排序功能测试通过!")
    else:
        print("\n💥 重排序功能测试失败!")