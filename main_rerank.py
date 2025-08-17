"""
AI Text Reranking System - Main Entry Point

A comprehensive text reranking system supporting Zhipu rerank models.
Provides both MCP server capabilities and direct text reranking functionality.
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
from zhipu_rerank_client import ZhipuRerankClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Text Reranking System")

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

rerank_base_url = config.get("text_rerank", {}).get("base_url", "https://open.bigmodel.cn")
rerank_client = ZhipuRerankClient(api_key=api_key or "", base_url=rerank_base_url)

# Text Reranking Entry Point
class RerankGenerator:
    """主要的文本重排序入口类"""
    
    def __init__(self):
        self.rerank_client = rerank_client
        self.outputs_dir = OUTPUTS_DIR
    
    def rerank_documents(self, 
                        query: str,
                        documents: List[str],
                        model: str = "rerank") -> Dict[str, Any]:
        """
        主要的文本重排序入口
        
        Args:
            query: 查询文本
            documents: 候选文档列表
            model: 使用的重排序模型
            
        Returns:
            重排序结果
        """
        return self.rerank_client.rerank(
            query=query,
            documents=documents,
            model=model
        )
    
    def get_ranked_documents(self, query: str, documents: List[str], 
                           model: str = "rerank", top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取排序后的文档列表"""
        return self.rerank_client.get_ranked_documents(query, documents, model, top_k)
    
    def find_most_relevant(self, query: str, documents: List[str], 
                          model: str = "rerank", threshold: float = 0.5) -> List[Dict[str, Any]]:
        """找到与查询最相关的文档"""
        return self.rerank_client.find_most_relevant(query, documents, model, threshold)

# 创建全局文本重排序实例
rerank_generator = RerankGenerator()

@mcp.tool()
def rerank_documents(
    query: str,
    documents: List[str],
    model: str = "rerank"
) -> Dict[str, Any]:
    """
    对文档进行重排序
    
    Args:
        query: 查询文本
        documents: 候选文档列表
        model: 重排序模型名称
    
    Returns:
        包含重排序结果的字典
    """
    try:
        if not query or not query.strip():
            return {
                "success": False,
                "error": "查询文本不能为空"
            }
        
        if not documents or len(documents) == 0:
            return {
                "success": False,
                "error": "文档列表不能为空"
            }
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return {
                "success": False,
                "error": "没有找到有效的文档"
            }
        
        result = rerank_generator.rerank_documents(
            query=query,
            documents=valid_documents,
            model=model
        )
        
        return {
            "success": True,
            "query": query,
            "model": model,
            "results": result.get("results", []),
            "usage": result.get("usage", {}),
            "request_id": result.get("request_id", ""),
            "created": result.get("created", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"文档重排序失败: {str(e)}"
        }

@mcp.tool()
def get_top_relevant_documents(
    query: str,
    documents: List[str],
    model: str = "rerank",
    top_k: int = 5
) -> Dict[str, Any]:
    """
    获取最相关的前k个文档
    
    Args:
        query: 查询文本
        documents: 候选文档列表
        model: 重排序模型名称
        top_k: 返回前k个结果
    
    Returns:
        包含排序结果的字典
    """
    try:
        if not query or not query.strip():
            return {
                "success": False,
                "error": "查询文本不能为空"
            }
        
        if not documents:
            return {
                "success": False,
                "error": "文档列表不能为空"
            }
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return {
                "success": False,
                "error": "没有找到有效的文档"
            }
        
        ranked_docs = rerank_generator.get_ranked_documents(
            query=query,
            documents=valid_documents,
            model=model,
            top_k=top_k
        )
        
        return {
            "success": True,
            "query": query,
            "model": model,
            "total_documents": len(valid_documents),
            "top_k": len(ranked_docs),
            "results": ranked_docs
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取相关文档失败: {str(e)}"
        }

@mcp.tool()
def find_relevant_documents(
    query: str,
    documents: List[str],
    model: str = "rerank",
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    找到相关性超过阈值的文档
    
    Args:
        query: 查询文本
        documents: 候选文档列表
        model: 重排序模型名称
        threshold: 相关性阈值
    
    Returns:
        包含相关文档的结果字典
    """
    try:
        if not query or not query.strip():
            return {
                "success": False,
                "error": "查询文本不能为空"
            }
        
        if not documents:
            return {
                "success": False,
                "error": "文档列表不能为空"
            }
        
        # 过滤空文档
        valid_documents = [doc.strip() for doc in documents if doc and doc.strip()]
        
        if not valid_documents:
            return {
                "success": False,
                "error": "没有找到有效的文档"
            }
        
        relevant_docs = rerank_generator.find_most_relevant(
            query=query,
            documents=valid_documents,
            model=model,
            threshold=threshold
        )
        
        return {
            "success": True,
            "query": query,
            "model": model,
            "threshold": threshold,
            "total_documents": len(valid_documents),
            "relevant_count": len(relevant_docs),
            "results": relevant_docs
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"查找相关文档失败: {str(e)}"
        }

@mcp.tool()
def get_supported_rerank_models() -> Dict[str, Any]:
    """
    获取支持的重排序模型列表
    
    Returns:
        包含支持模型的结果字典
    """
    try:
        models = rerank_client.get_available_models()
        
        return {
            "success": True,
            "models": models,
            "default_model": "rerank",
            "model_info": {
                "rerank": "智谱AI文本重排序模型，用于对候选文档进行相关性排序"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取支持的模型失败: {str(e)}"
        }

@mcp.tool()
def test_rerank_api(test_query: Optional[str] = None, test_documents: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    测试文本重排序API连接和功能
    
    Args:
        test_query: 可选的测试查询
        test_documents: 可选的测试文档列表
    
    Returns:
        包含测试结果的字典
    """
    try:
        # 测试API连接
        connection_test = rerank_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_models": rerank_client.get_available_models()
        }
        
        # 如果提供了测试数据，进行重排序测试
        if test_query and test_documents:
            try:
                rerank_result = rerank_client.rerank(test_query, test_documents, "rerank")
                result["rerank_test"] = {
                    "success": True,
                    "query": test_query,
                    "document_count": len(test_documents),
                    "results_count": len(rerank_result.get("results", [])),
                    "sample_results": rerank_result.get("results", [])[:3]  # 显示前3个结果
                }
            except Exception as e:
                result["rerank_test"] = {
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
def save_rerank_results_to_file(
    query: str,
    documents: List[str],
    filename: str,
    model: str = "rerank"
) -> Dict[str, Any]:
    """
    将重排序结果保存到文件
    
    Args:
        query: 查询文本
        documents: 文档列表
        filename: 保存的文件名
        model: 重排序模型名称
    
    Returns:
        保存结果字典
    """
    try:
        if not query or not documents or not filename:
            return {
                "success": False,
                "error": "查询文本、文档列表和文件名都是必需的"
            }
        
        # 获取重排序结果
        rerank_result = rerank_generator.rerank_documents(query, documents, model)
        
        # 准备保存数据
        save_data = {
            "query": query,
            "model": model,
            "timestamp": time.time(),
            "total_documents": len(documents),
            "results": rerank_result.get("results", []),
            "usage": rerank_result.get("usage", {}),
            "request_id": rerank_result.get("request_id", "")
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
            "query": query,
            "document_count": len(documents),
            "results_count": len(save_data["results"]),
            "model": model
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存重排序结果失败: {str(e)}"
        }

@mcp.tool()
def load_rerank_results_from_file(filename: str) -> Dict[str, Any]:
    """
    从文件加载重排序结果
    
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
        
        return {
            "success": True,
            "filename": file_path.name,
            "query": data.get("query"),
            "model": data.get("model"),
            "document_count": data.get("total_documents"),
            "results_count": len(data.get("results", [])),
            "timestamp": data.get("timestamp"),
            "results": data.get("results", []),
            "usage": data.get("usage", {})
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"加载重排序结果失败: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式文本重排序模式"""
    print("=" * 60)
    print("🔄 AI文本重排序系统 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 文档重排序")
    print("2. 获取最相关文档")
    print("3. 查找相关文档（按阈值）")
    print("4. 查看支持的模型")
    print("5. 测试API连接")
    print("6. 保存重排序结果到文件")
    print("7. 从文件加载重排序结果")
    print("8. 启动MCP服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-8): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_document_rerank()
            elif choice == "2":
                handle_top_relevant_documents()
            elif choice == "3":
                handle_relevant_documents_by_threshold()
            elif choice == "4":
                handle_model_info()
            elif choice == "5":
                handle_api_test()
            elif choice == "6":
                handle_save_results()
            elif choice == "7":
                handle_load_results()
            elif choice == "8":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            else:
                print("❌ 无效选择，请输入0-8")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_document_rerank():
    """处理文档重排序"""
    print("\n🔄 文档重排序")
    query = input("请输入查询文本: ").strip()
    if not query:
        print("❌ 查询文本不能为空")
        return
    
    print("请输入候选文档 (每行一个，空行结束):")
    documents = []
    while True:
        doc = input().strip()
        if not doc:
            break
        documents.append(doc)
    
    if not documents:
        print("❌ 没有输入任何文档")
        return
    
    models = rerank_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: rerank): ").strip() or "rerank"
    
    print("🔍 重排序中...")
    try:
        result = rerank_documents(query, documents, model)
        
        if result["success"]:
            print(f"✅ 文档重排序成功!")
            print(f"查询: {result['query']}")
            print(f"模型: {result['model']}")
            print(f"文档数量: {len(documents)}")
            print("\n重排序结果:")
            for i, item in enumerate(result['results']):
                print(f"{i+1}. {item['document']} (相关性: {item['relevance_score']:.4f})")
            print(f"\n使用情况: {result.get('usage', {})}")
        else:
            print(f"❌ 重排序失败: {result['error']}")
    except Exception as e:
        print(f"❌ 重排序失败: {str(e)}")

def handle_top_relevant_documents():
    """处理获取最相关文档"""
    print("\n🔝 获取最相关文档")
    query = input("请输入查询文本: ").strip()
    if not query:
        print("❌ 查询文本不能为空")
        return
    
    print("请输入候选文档 (每行一个，空行结束):")
    documents = []
    while True:
        doc = input().strip()
        if not doc:
            break
        documents.append(doc)
    
    if not documents:
        print("❌ 没有输入任何文档")
        return
    
    top_k = input("请输入返回结果数量 (默认: 5): ").strip()
    try:
        top_k = int(top_k) if top_k else 5
    except ValueError:
        top_k = 5
    
    models = rerank_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: rerank): ").strip() or "rerank"
    
    print("🔍 获取中...")
    try:
        result = get_top_relevant_documents(query, documents, model, top_k)
        
        if result["success"]:
            print(f"✅ 获取成功!")
            print(f"查询: {result['query']}")
            print(f"总文档数: {result['total_documents']}")
            print(f"返回结果数: {result['top_k']}")
            print("\n最相关的文档:")
            for i, item in enumerate(result['results']):
                print(f"{i+1}. {item['document']} (相关性: {item['relevance_score']:.4f})")
        else:
            print(f"❌ 获取失败: {result['error']}")
    except Exception as e:
        print(f"❌ 获取失败: {str(e)}")

def handle_relevant_documents_by_threshold():
    """处理按阈值查找相关文档"""
    print("\n🎯 按阈值查找相关文档")
    query = input("请输入查询文本: ").strip()
    if not query:
        print("❌ 查询文本不能为空")
        return
    
    print("请输入候选文档 (每行一个，空行结束):")
    documents = []
    while True:
        doc = input().strip()
        if not doc:
            break
        documents.append(doc)
    
    if not documents:
        print("❌ 没有输入任何文档")
        return
    
    threshold = input("请输入相关性阈值 (0-1, 默认: 0.5): ").strip()
    try:
        threshold = float(threshold) if threshold else 0.5
    except ValueError:
        threshold = 0.5
    
    models = rerank_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: rerank): ").strip() or "rerank"
    
    print("🔍 查找中...")
    try:
        result = find_relevant_documents(query, documents, model, threshold)
        
        if result["success"]:
            print(f"✅ 查找成功!")
            print(f"查询: {result['query']}")
            print(f"阈值: {result['threshold']}")
            print(f"总文档数: {result['total_documents']}")
            print(f"相关文档数: {result['relevant_count']}")
            print("\n相关文档:")
            for i, item in enumerate(result['results']):
                print(f"{i+1}. {item['document']} (相关性: {item['relevance_score']:.4f})")
        else:
            print(f"❌ 查找失败: {result['error']}")
    except Exception as e:
        print(f"❌ 查找失败: {str(e)}")

def handle_model_info():
    """处理模型信息查看"""
    print("\n🔧 支持的重排序模型")
    try:
        result = get_supported_rerank_models()
        
        if result["success"]:
            print("✅ 可用的模型:")
            for model in result["models"]:
                info = result["model_info"].get(model, "无描述")
                print(f"  {model}: {info}")
            print(f"\n默认模型: {result['default_model']}")
        else:
            print(f"❌ 获取模型信息失败: {result['error']}")
    except Exception as e:
        print(f"❌ 获取模型信息失败: {str(e)}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_query = input("请输入测试查询 (可选): ").strip() or None
    
    test_documents = None
    if test_query:
        print("请输入测试文档 (每行一个，空行结束，可选):")
        docs = []
        while True:
            doc = input().strip()
            if not doc:
                break
            docs.append(doc)
        if docs:
            test_documents = docs
    
    print("🔍 测试中...")
    try:
        result = test_rerank_api(test_query, test_documents)
        
        if result["success"]:
            print("✅ API测试结果:")
            conn_test = result["connection_test"]
            print(f"  连接状态: {'正常' if conn_test else '失败'}")
            print(f"  支持的模型: {', '.join(result['supported_models'])}")
            
            if 'rerank_test' in result:
                rerank_test = result['rerank_test']
                if rerank_test['success']:
                    print(f"  测试重排序: 成功处理 {rerank_test['document_count']} 个文档")
                    print(f"  返回结果数: {rerank_test['results_count']}")
                    if rerank_test['sample_results']:
                        print("  示例结果:")
                        for i, item in enumerate(rerank_test['sample_results']):
                            print(f"    {i+1}. {item['document'][:50]}... (相关性: {item['relevance_score']:.4f})")
                else:
                    print(f"  测试重排序失败: {rerank_test['error']}")
        else:
            print(f"❌ API测试失败: {result['error']}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def handle_save_results():
    """处理保存重排序结果"""
    print("\n💾 保存重排序结果到文件")
    query = input("请输入查询文本: ").strip()
    if not query:
        print("❌ 查询文本不能为空")
        return
    
    print("请输入候选文档 (每行一个，空行结束):")
    documents = []
    while True:
        doc = input().strip()
        if not doc:
            break
        documents.append(doc)
    
    if not documents:
        print("❌ 没有输入任何文档")
        return
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    models = rerank_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: rerank): ").strip() or "rerank"
    
    print("💾 保存中...")
    try:
        result = save_rerank_results_to_file(query, documents, filename, model)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"查询: {result['query']}")
            print(f"文档数量: {result['document_count']}")
            print(f"结果数量: {result['results_count']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_load_results():
    """处理加载重排序结果"""
    print("\n📂 从文件加载重排序结果")
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("📂 加载中...")
    try:
        result = load_rerank_results_from_file(filename)
        
        if result["success"]:
            print(f"✅ 加载成功!")
            print(f"文件名: {result['filename']}")
            print(f"查询: {result['query']}")
            print(f"模型: {result['model']}")
            print(f"文档数量: {result['document_count']}")
            print(f"结果数量: {result['results_count']}")
            
            # 显示前几个结果
            results = result['results']
            print("\n前3个结果:")
            for i, item in enumerate(results[:3]):
                print(f"{i+1}. {item['document'][:50]}... (相关性: {item['relevance_score']:.4f})")
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