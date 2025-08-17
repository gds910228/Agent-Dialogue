"""
AI Web Search System - Main Entry Point

A comprehensive web search system supporting Zhipu web search API.
Provides both MCP server capabilities and direct web search functionality.
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
from zhipu_websearch_client import ZhipuWebSearchClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Web Search System")

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

websearch_base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
search_engine = config.get("search_engine", "search_std")
websearch_client = ZhipuWebSearchClient(api_key=api_key or "", base_url=websearch_base_url, search_engine=search_engine)

# Web Search Entry Point
class WebSearchGenerator:
    """主要的网络搜索入口类"""
    
    def __init__(self):
        self.websearch_client = websearch_client
        self.outputs_dir = OUTPUTS_DIR
    
    def search_web(self, 
                   search_query: str,
                   search_intent: bool = False,
                   count: int = 10,
                   search_recency_filter: str = "noLimit") -> Dict[str, Any]:
        """
        主要的网络搜索入口
        
        Args:
            search_query: 搜索查询字符串
            search_intent: 是否返回搜索意图分析
            count: 返回结果数量
            search_recency_filter: 搜索时效性过滤
            
        Returns:
            搜索结果
        """
        return self.websearch_client.search(
            search_query=search_query,
            search_intent=search_intent,
            count=count,
            search_recency_filter=search_recency_filter
        )
    
    def search_with_intent(self, search_query: str, count: int = 10) -> Dict[str, Any]:
        """执行带搜索意图分析的网络搜索"""
        return self.websearch_client.search_with_intent(search_query, count)
    
    def search_recent(self, search_query: str, recency: str = "day", count: int = 10) -> Dict[str, Any]:
        """搜索最近的内容"""
        return self.websearch_client.search_recent(search_query, recency, count)

# 创建全局网络搜索实例
websearch_generator = WebSearchGenerator()

@mcp.tool()
def web_search(
    search_query: str,
    search_intent: bool = False,
    count: int = 10,
    search_recency_filter: str = "noLimit"
) -> Dict[str, Any]:
    """
    执行网络搜索
    
    Args:
        search_query: 搜索查询字符串
        search_intent: 是否返回搜索意图分析
        count: 返回结果数量，默认10
        search_recency_filter: 搜索时效性过滤，可选值：noLimit, day, week, month, year
    
    Returns:
        包含搜索结果的字典
    """
    try:
        if not search_query or not search_query.strip():
            return {
                "success": False,
                "error": "搜索查询不能为空"
            }
        
        # 验证参数
        validation = websearch_client.validate_search_params(
            search_query, count, search_recency_filter
        )
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = websearch_generator.search_web(
            search_query=search_query,
            search_intent=search_intent,
            count=count,
            search_recency_filter=search_recency_filter
        )
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(result)
        
        return {
            "success": True,
            "search_query": search_query,
            "search_intent": search_intent,
            "count": count,
            "search_recency_filter": search_recency_filter,
            "result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"网络搜索失败: {str(e)}"
        }

@mcp.tool()
def web_search_with_intent(
    search_query: str,
    count: int = 10
) -> Dict[str, Any]:
    """
    执行带搜索意图分析的网络搜索
    
    Args:
        search_query: 搜索查询字符串
        count: 返回结果数量，默认10
    
    Returns:
        包含搜索意图和搜索结果的字典
    """
    try:
        if not search_query or not search_query.strip():
            return {
                "success": False,
                "error": "搜索查询不能为空"
            }
        
        # 验证参数
        validation = websearch_client.validate_search_params(
            search_query, count, "noLimit"
        )
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = websearch_generator.search_with_intent(
            search_query=search_query,
            count=count
        )
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(result)
        
        return {
            "success": True,
            "search_query": search_query,
            "count": count,
            "result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"搜索意图分析失败: {str(e)}"
        }

@mcp.tool()
def web_search_recent(
    search_query: str,
    recency: str = "day",
    count: int = 10
) -> Dict[str, Any]:
    """
    搜索最近的内容
    
    Args:
        search_query: 搜索查询字符串
        recency: 时效性过滤，可选值：day, week, month, year
        count: 返回结果数量，默认10
    
    Returns:
        包含最近搜索结果的字典
    """
    try:
        if not search_query or not search_query.strip():
            return {
                "success": False,
                "error": "搜索查询不能为空"
            }
        
        # 验证参数
        validation = websearch_client.validate_search_params(
            search_query, count, recency
        )
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = websearch_generator.search_recent(
            search_query=search_query,
            recency=recency,
            count=count
        )
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(result)
        
        return {
            "success": True,
            "search_query": search_query,
            "recency": recency,
            "count": count,
            "result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"最近内容搜索失败: {str(e)}"
        }

@mcp.tool()
def test_websearch_api(test_query: Optional[str] = None) -> Dict[str, Any]:
    """
    测试网络搜索API连接和功能
    
    Args:
        test_query: 可选的测试搜索查询
    
    Returns:
        包含测试结果的字典
    """
    try:
        # 测试API连接
        connection_test = websearch_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_recency_filters": websearch_client.get_available_recency_filters()
        }
        
        # 如果提供了测试查询，进行搜索测试
        if test_query:
            try:
                search_result = websearch_client.search(test_query, count=3)
                formatted_result = websearch_client.format_search_results(search_result)
                search_test_result = {
                    "success": True,
                    "search_query": test_query,
                    "result_count": formatted_result.get("total_results", 0)
                }
                result["search_test"] = search_test_result
            except Exception as e:
                result["search_test"] = {
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
def save_search_results_to_file(
    search_query: str,
    filename: str,
    search_intent: bool = False,
    count: int = 10,
    search_recency_filter: str = "noLimit"
) -> Dict[str, Any]:
    """
    将搜索结果保存到文件
    
    Args:
        search_query: 搜索查询字符串
        filename: 保存的文件名
        search_intent: 是否返回搜索意图分析
        count: 返回结果数量
        search_recency_filter: 搜索时效性过滤
    
    Returns:
        保存结果字典
    """
    try:
        if not search_query or not filename:
            return {
                "success": False,
                "error": "搜索查询和文件名都是必需的"
            }
        
        # 获取搜索结果
        search_result = websearch_generator.search_web(
            search_query=search_query,
            search_intent=search_intent,
            count=count,
            search_recency_filter=search_recency_filter
        )
        
        # 格式化结果
        formatted_result = websearch_client.format_search_results(search_result)
        
        # 准备保存数据
        save_data = {
            "search_query": search_query,
            "search_intent": search_intent,
            "count": count,
            "search_recency_filter": search_recency_filter,
            "timestamp": time.time(),
            "result": formatted_result
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
            "search_query": search_query,
            "result_count": formatted_result.get("total_results", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存搜索结果失败: {str(e)}"
        }

@mcp.tool()
def load_search_results_from_file(filename: str) -> Dict[str, Any]:
    """
    从文件加载搜索结果
    
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
            "search_query": data.get("search_query"),
            "result_count": data.get("result", {}).get("total_results", 0),
            "timestamp": data.get("timestamp"),
            "search_intent": data.get("search_intent", False),
            "count": data.get("count", 0),
            "search_recency_filter": data.get("search_recency_filter", "noLimit"),
            "result": data.get("result", {})
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"加载搜索结果失败: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式网络搜索模式"""
    print("=" * 60)
    print("🔍 AI网络搜索系统 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 网络搜索")
    print("2. 搜索意图分析")
    print("3. 最近内容搜索")
    print("4. 测试API连接")
    print("5. 保存搜索结果到文件")
    print("6. 从文件加载搜索结果")
    print("7. 启动MCP服务器")
    print("0. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n请选择功能 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                handle_web_search()
            elif choice == "2":
                handle_search_with_intent()
            elif choice == "3":
                handle_search_recent()
            elif choice == "4":
                handle_api_test()
            elif choice == "5":
                handle_save_results()
            elif choice == "6":
                handle_load_results()
            elif choice == "7":
                print("🔧 启动MCP服务器...")
                mcp.run(transport="sse")
                break
            else:
                print("❌ 无效选择，请输入0-7")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def handle_web_search():
    """处理网络搜索"""
    print("\n🔍 网络搜索")
    
    search_query = input("请输入搜索查询: ").strip()
    if not search_query:
        print("❌ 搜索查询不能为空")
        return
    
    count = input("请输入结果数量 (默认: 10): ").strip()
    try:
        count = int(count) if count else 10
    except ValueError:
        count = 10
    
    recency_filters = websearch_client.get_available_recency_filters()
    print(f"\n可用的时效性过滤: {', '.join(recency_filters)}")
    search_recency_filter = input("请选择时效性过滤 (默认: noLimit): ").strip() or "noLimit"
    
    search_intent = input("是否启用搜索意图分析? (y/n, 默认: n): ").strip().lower() == "y"
    
    print("🔍 搜索中...")
    try:
        result = web_search(search_query, search_intent, count, search_recency_filter)
        
        if result["success"]:
            print(f"✅ 网络搜索成功!")
            print(f"搜索查询: {result['search_query']}")
            print(f"结果数量: {result['result']['total_results']}")
            
            # 显示搜索意图
            if result['result']['search_intent']:
                print(f"\n🎯 搜索意图:")
                for intent in result['result']['search_intent']:
                    print(f"  查询: {intent['query']}")
                    print(f"  意图: {intent['intent']}")
                    print(f"  关键词: {intent['keywords']}")
            
            # 显示搜索结果
            print(f"\n📋 搜索结果:")
            for i, item in enumerate(result['result']['search_results'][:5], 1):
                print(f"{i}. {item['title']}")
                print(f"   链接: {item['link']}")
                print(f"   内容: {item['content'][:100]}...")
                if item['publish_date']:
                    print(f"   发布时间: {item['publish_date']}")
                print()
        else:
            print(f"❌ 搜索失败: {result['error']}")
    except Exception as e:
        print(f"❌ 搜索失败: {str(e)}")

def handle_search_with_intent():
    """处理搜索意图分析"""
    print("\n🎯 搜索意图分析")
    
    search_query = input("请输入搜索查询: ").strip()
    if not search_query:
        print("❌ 搜索查询不能为空")
        return
    
    count = input("请输入结果数量 (默认: 10): ").strip()
    try:
        count = int(count) if count else 10
    except ValueError:
        count = 10
    
    print("🔍 分析搜索意图并搜索中...")
    try:
        result = web_search_with_intent(search_query, count)
        
        if result["success"]:
            print(f"✅ 搜索意图分析成功!")
            print(f"搜索查询: {result['search_query']}")
            print(f"结果数量: {result['result']['total_results']}")
            
            # 显示搜索意图
            if result['result']['search_intent']:
                print(f"\n🎯 搜索意图分析:")
                for intent in result['result']['search_intent']:
                    print(f"  原始查询: {intent['query']}")
                    print(f"  搜索意图: {intent['intent']}")
                    print(f"  提取关键词: {intent['keywords']}")
                    print()
            
            # 显示搜索结果
            print(f"📋 搜索结果:")
            for i, item in enumerate(result['result']['search_results'][:3], 1):
                print(f"{i}. {item['title']}")
                print(f"   链接: {item['link']}")
                print(f"   内容: {item['content'][:150]}...")
                print()
        else:
            print(f"❌ 搜索意图分析失败: {result['error']}")
    except Exception as e:
        print(f"❌ 搜索意图分析失败: {str(e)}")

def handle_search_recent():
    """处理最近内容搜索"""
    print("\n📅 最近内容搜索")
    
    search_query = input("请输入搜索查询: ").strip()
    if not search_query:
        print("❌ 搜索查询不能为空")
        return
    
    recency_filters = websearch_client.get_available_recency_filters()
    print(f"\n可用的时效性过滤: {', '.join(recency_filters[1:])}")  # 排除noLimit
    recency = input("请选择时效性过滤 (默认: day): ").strip() or "day"
    
    count = input("请输入结果数量 (默认: 10): ").strip()
    try:
        count = int(count) if count else 10
    except ValueError:
        count = 10
    
    print("🔍 搜索最近内容中...")
    try:
        result = web_search_recent(search_query, recency, count)
        
        if result["success"]:
            print(f"✅ 最近内容搜索成功!")
            print(f"搜索查询: {result['search_query']}")
            print(f"时效性: {result['recency']}")
            print(f"结果数量: {result['result']['total_results']}")
            
            # 显示搜索结果
            print(f"\n📋 最近搜索结果:")
            for i, item in enumerate(result['result']['search_results'][:5], 1):
                print(f"{i}. {item['title']}")
                print(f"   链接: {item['link']}")
                print(f"   内容: {item['content'][:100]}...")
                if item['publish_date']:
                    print(f"   发布时间: {item['publish_date']}")
                print()
        else:
            print(f"❌ 最近内容搜索失败: {result['error']}")
    except Exception as e:
        print(f"❌ 最近内容搜索失败: {str(e)}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_query = None
    
    use_test_data = input("是否使用测试查询? (y/n, 默认: y): ").strip().lower() or "y"
    if use_test_data == "y":
        test_query = "北京天气"
    
    print("🔍 测试中...")
    try:
        result = test_websearch_api(test_query)
        
        if result["success"]:
            print("✅ API测试结果:")
            conn_test = result["connection_test"]
            print(f"  连接状态: {'正常' if conn_test else '失败'}")
            print(f"  支持的时效性过滤: {', '.join(result['supported_recency_filters'])}")
            
            if 'search_test' in result:
                search_test = result['search_test']
                if search_test['success']:
                    print(f"  测试搜索: 成功搜索 '{search_test['search_query']}'")
                    print(f"  结果数量: {search_test['result_count']}")
                else:
                    print(f"  测试搜索失败: {search_test['error']}")
        else:
            print(f"❌ API测试失败: {result['error']}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def handle_save_results():
    """处理保存搜索结果"""
    print("\n💾 保存搜索结果到文件")
    
    search_query = input("请输入搜索查询: ").strip()
    if not search_query:
        print("❌ 搜索查询不能为空")
        return
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    count = input("请输入结果数量 (默认: 10): ").strip()
    try:
        count = int(count) if count else 10
    except ValueError:
        count = 10
    
    recency_filters = websearch_client.get_available_recency_filters()
    print(f"\n可用的时效性过滤: {', '.join(recency_filters)}")
    search_recency_filter = input("请选择时效性过滤 (默认: noLimit): ").strip() or "noLimit"
    
    search_intent = input("是否启用搜索意图分析? (y/n, 默认: n): ").strip().lower() == "y"
    
    print("💾 搜索并保存中...")
    try:
        result = save_search_results_to_file(search_query, filename, search_intent, count, search_recency_filter)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"搜索查询: {result['search_query']}")
            print(f"结果数量: {result['result_count']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_load_results():
    """处理加载搜索结果"""
    print("\n📂 从文件加载搜索结果")
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("📂 加载中...")
    try:
        result = load_search_results_from_file(filename)
        
        if result["success"]:
            print(f"✅ 加载成功!")
            print(f"文件名: {result['filename']}")
            print(f"搜索查询: {result['search_query']}")
            print(f"结果数量: {result['result_count']}")
            print(f"时效性过滤: {result['search_recency_filter']}")
            print(f"搜索意图分析: {'是' if result['search_intent'] else '否'}")
            
            # 显示搜索结果
            if result['result']['search_results']:
                print("\n搜索结果:")
                for i, item in enumerate(result['result']['search_results'][:3], 1):
                    print(f"{i}. {item['title']}")
                    print(f"   链接: {item['link']}")
                    print(f"   内容: {item['content'][:80]}...")
                    print()
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