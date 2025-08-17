"""
AI Content Security System - Main Entry Point

A comprehensive content security system supporting Zhipu content moderation API.
Provides both MCP server capabilities and direct content moderation functionality.
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
from zhipu_moderation_client import ZhipuModerationClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Content Security System")

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

moderation_base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
moderation_client = ZhipuModerationClient(api_key=api_key or "", base_url=moderation_base_url)

# Content Security Entry Point
class ContentModerationGenerator:
    """主要的内容安全入口类"""
    
    def __init__(self):
        self.moderation_client = moderation_client
        self.outputs_dir = OUTPUTS_DIR
    
    def moderate_content(self, input_text: str) -> Dict[str, Any]:
        """
        主要的内容安全审核入口
        
        Args:
            input_text: 需要审核的文本内容
            
        Returns:
            审核结果
        """
        return self.moderation_client.moderate_content(input_text)
    
    def batch_moderate_content(self, input_texts: List[str]) -> List[Dict[str, Any]]:
        """批量执行内容安全审核"""
        return self.moderation_client.batch_moderate_content(input_texts)
    
    def check_content_safety(self, input_text: str) -> Dict[str, Any]:
        """检查内容安全性并返回详细分析"""
        result = self.moderation_client.moderate_content(input_text)
        formatted_result = self.moderation_client.format_moderation_result(result)
        risk_summary = self.moderation_client.get_risk_summary(result)
        
        return {
            "input": input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result
        }

# 创建全局内容安全实例
moderation_generator = ContentModerationGenerator()

@mcp.tool()
def moderate_content(input_text: str) -> Dict[str, Any]:
    """
    执行内容安全审核
    
    Args:
        input_text: 需要审核的文本内容
    
    Returns:
        包含审核结果的字典
    """
    try:
        if not input_text or not input_text.strip():
            return {
                "success": False,
                "error": "审核内容不能为空"
            }
        
        # 验证参数
        validation = moderation_client.validate_input(input_text)
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"参数验证失败: {', '.join(validation['errors'])}"
            }
        
        result = moderation_generator.moderate_content(input_text)
        
        # 格式化结果
        formatted_result = moderation_client.format_moderation_result(result)
        risk_summary = moderation_client.get_risk_summary(result)
        
        return {
            "success": True,
            "input_text": input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"内容安全审核失败: {str(e)}"
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
def batch_moderate_content(input_texts: List[str]) -> Dict[str, Any]:
    """
    批量执行内容安全审核
    
    Args:
        input_texts: 需要审核的文本内容列表
    
    Returns:
        包含批量审核结果的字典
    """
    try:
        if not input_texts:
            return {
                "success": False,
                "error": "审核内容列表不能为空"
            }
        
        # 验证每个输入
        for i, text in enumerate(input_texts):
            validation = moderation_client.validate_input(text)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"第{i+1}个文本验证失败: {', '.join(validation['errors'])}"
                }
        
        results = moderation_generator.batch_moderate_content(input_texts)
        
        # 统计结果
        total_count = len(results)
        success_count = sum(1 for r in results if r["success"])
        unsafe_count = 0
        
        for result in results:
            if result["success"]:
                risk_summary = moderation_client.get_risk_summary(result["result"])
                if not risk_summary["is_safe"]:
                    unsafe_count += 1
        
        return {
            "success": True,
            "total_count": total_count,
            "success_count": success_count,
            "unsafe_count": unsafe_count,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"批量内容安全审核失败: {str(e)}"
        }

@mcp.tool()
def test_moderation_api(test_text: Optional[str] = None) -> Dict[str, Any]:
    """
    测试内容安全API连接和功能
    
    Args:
        test_text: 可选的测试文本内容
    
    Returns:
        包含测试结果的字典
    """
    try:
        # 测试API连接
        connection_test = moderation_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "api_endpoint": moderation_client.moderation_url
        }
        
        # 如果提供了测试文本，进行审核测试
        if test_text:
            try:
                moderation_result = moderation_client.moderate_content(test_text)
                formatted_result = moderation_client.format_moderation_result(moderation_result)
                risk_summary = moderation_client.get_risk_summary(moderation_result)
                
                moderation_test_result = {
                    "success": True,
                    "test_text": test_text,
                    "is_safe": risk_summary["is_safe"],
                    "risk_count": risk_summary["risk_count"]
                }
                result["moderation_test"] = moderation_test_result
            except Exception as e:
                result["moderation_test"] = {
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
def save_moderation_results_to_file(
    input_text: str,
    filename: str
) -> Dict[str, Any]:
    """
    将审核结果保存到文件
    
    Args:
        input_text: 审核的文本内容
        filename: 保存的文件名
    
    Returns:
        保存结果字典
    """
    try:
        if not input_text or not filename:
            return {
                "success": False,
                "error": "审核内容和文件名都是必需的"
            }
        
        # 获取审核结果
        moderation_result = moderation_generator.moderate_content(input_text)
        
        # 格式化结果
        formatted_result = moderation_client.format_moderation_result(moderation_result)
        risk_summary = moderation_client.get_risk_summary(moderation_result)
        
        # 准备保存数据
        save_data = {
            "input_text": input_text,
            "timestamp": time.time(),
            "is_safe": risk_summary["is_safe"],
            "risk_summary": risk_summary,
            "detailed_result": formatted_result,
            "raw_result": moderation_result
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
            "input_text": input_text[:100] + "..." if len(input_text) > 100 else input_text,
            "is_safe": risk_summary["is_safe"],
            "risk_count": risk_summary["risk_count"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存审核结果失败: {str(e)}"
        }

@mcp.tool()
def load_moderation_results_from_file(filename: str) -> Dict[str, Any]:
    """
    从文件加载审核结果
    
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
            "input_text": data.get("input_text", ""),
            "timestamp": data.get("timestamp"),
            "is_safe": data.get("is_safe", True),
            "risk_summary": data.get("risk_summary", {}),
            "detailed_result": data.get("detailed_result", {}),
            "raw_result": data.get("raw_result", {})
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"加载审核结果失败: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式内容安全模式"""
    print("=" * 60)
    print("🛡️ AI内容安全系统 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 内容安全审核")
    print("2. 批量内容审核")
    print("3. 内容安全检查")
    print("4. 测试API连接")
    print("5. 保存审核结果到文件")
    print("6. 从文件加载审核结果")
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
                handle_content_moderation()
            elif choice == "2":
                handle_batch_moderation()
            elif choice == "3":
                handle_content_safety_check()
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

def handle_content_moderation():
    """处理内容安全审核"""
    print("\n🛡️ 内容安全审核")
    
    input_text = input("请输入需要审核的文本内容: ").strip()
    if not input_text:
        print("❌ 审核内容不能为空")
        return
    
    print("🛡️ 审核中...")
    try:
        result = moderate_content(input_text)
        
        if result["success"]:
            print(f"✅ 内容安全审核完成!")
            print(f"审核内容: {input_text[:50]}{'...' if len(input_text) > 50 else ''}")
            print(f"安全状态: {'✅ 安全' if result['is_safe'] else '⚠️ 存在风险'}")
            
            # 显示风险摘要
            risk_summary = result['risk_summary']
            if not risk_summary['is_safe']:
                print(f"\n⚠️ 风险分析:")
                print(f"  风险数量: {risk_summary['risk_count']}")
                print(f"  最高风险等级: {risk_summary['highest_risk_level']}")
                print(f"  风险类型: {', '.join(risk_summary['risk_types'])}")
                
                # 显示详细风险信息
                for detail in risk_summary['details']:
                    print(f"  - 内容类型: {detail['content_type']}")
                    print(f"    风险等级: {detail['risk_level']}")
                    print(f"    风险类型: {', '.join(detail['risk_types'])}")
            else:
                print("✅ 内容安全，未发现风险")
        else:
            print(f"❌ 审核失败: {result['error']}")
    except Exception as e:
        print(f"❌ 审核失败: {str(e)}")

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

def handle_batch_moderation():
    """处理批量内容审核"""
    print("\n🛡️ 批量内容审核")
    
    print("请输入需要审核的文本内容（每行一个，输入空行结束）:")
    input_texts = []
    while True:
        text = input().strip()
        if not text:
            break
        input_texts.append(text)
    
    if not input_texts:
        print("❌ 未输入任何内容")
        return
    
    print(f"🛡️ 批量审核 {len(input_texts)} 个文本中...")
    try:
        result = batch_moderate_content(input_texts)
        
        if result["success"]:
            print(f"✅ 批量审核完成!")
            print(f"总数量: {result['total_count']}")
            print(f"成功数量: {result['success_count']}")
            print(f"风险内容数量: {result['unsafe_count']}")
            
            # 显示详细结果
            print(f"\n📋 审核结果:")
            for i, item in enumerate(result['results'], 1):
                if item['success']:
                    risk_summary = moderation_client.get_risk_summary(item['result'])
                    status = "✅ 安全" if risk_summary['is_safe'] else "⚠️ 风险"
                    print(f"{i}. {item['input'][:30]}... - {status}")
                    if not risk_summary['is_safe']:
                        print(f"   风险类型: {', '.join(risk_summary['risk_types'])}")
                else:
                    print(f"{i}. {item['input'][:30]}... - ❌ 审核失败: {item['error']}")
        else:
            print(f"❌ 批量审核失败: {result['error']}")
    except Exception as e:
        print(f"❌ 批量审核失败: {str(e)}")

def handle_content_safety_check():
    """处理内容安全检查"""
    print("\n🛡️ 内容安全检查")
    
    input_text = input("请输入需要检查的文本内容: ").strip()
    if not input_text:
        print("❌ 检查内容不能为空")
        return
    
    print("🛡️ 安全检查中...")
    try:
        result = moderation_generator.check_content_safety(input_text)
        
        print(f"✅ 内容安全检查完成!")
        print(f"检查内容: {result['input'][:50]}{'...' if len(result['input']) > 50 else ''}")
        print(f"安全状态: {'✅ 安全' if result['is_safe'] else '⚠️ 存在风险'}")
        
        # 显示详细风险分析
        risk_summary = result['risk_summary']
        if not risk_summary['is_safe']:
            print(f"\n⚠️ 详细风险分析:")
            print(f"  风险数量: {risk_summary['risk_count']}")
            print(f"  最高风险等级: {risk_summary['highest_risk_level']}")
            print(f"  风险类型: {', '.join(risk_summary['risk_types'])}")
            
            for detail in risk_summary['details']:
                print(f"  - 内容类型: {detail['content_type']}")
                print(f"    风险等级: {detail['risk_level']}")
                print(f"    风险类型: {', '.join(detail['risk_types'])}")
        else:
            print("✅ 内容完全安全，未发现任何风险")
            
    except Exception as e:
        print(f"❌ 安全检查失败: {str(e)}")

def handle_api_test():
    """处理API测试"""
    print("\n🔧 API连接测试")
    test_text = None
    
    use_test_data = input("是否使用测试文本? (y/n, 默认: y): ").strip().lower() or "y"
    if use_test_data == "y":
        test_text = "这是一个测试内容安全API的样例文本"
    
    print("🔍 测试中...")
    try:
        result = test_moderation_api(test_text)
        
        if result["success"]:
            print("✅ API测试结果:")
            conn_test = result["connection_test"]
            print(f"  连接状态: {'正常' if conn_test else '失败'}")
            print(f"  API端点: {result['api_endpoint']}")
            
            if 'moderation_test' in result:
                moderation_test = result['moderation_test']
                if moderation_test['success']:
                    print(f"  测试审核: 成功审核 '{moderation_test['test_text']}'")
                    print(f"  安全状态: {'安全' if moderation_test['is_safe'] else '存在风险'}")
                    print(f"  风险数量: {moderation_test['risk_count']}")
                else:
                    print(f"  测试审核失败: {moderation_test['error']}")
        else:
            print(f"❌ API测试失败: {result['error']}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def handle_save_results():
    """处理保存审核结果"""
    print("\n💾 保存审核结果到文件")
    
    input_text = input("请输入需要审核的文本内容: ").strip()
    if not input_text:
        print("❌ 审核内容不能为空")
        return
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("💾 审核并保存中...")
    try:
        result = save_moderation_results_to_file(input_text, filename)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"审核内容: {result['input_text']}")
            print(f"安全状态: {'安全' if result['is_safe'] else '存在风险'}")
            print(f"风险数量: {result['risk_count']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_load_results():
    """处理加载审核结果"""
    print("\n📂 从文件加载审核结果")
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("📂 加载中...")
    try:
        result = load_moderation_results_from_file(filename)
        
        if result["success"]:
            print(f"✅ 加载成功!")
            print(f"文件名: {result['filename']}")
            print(f"审核内容: {result['input_text'][:100]}{'...' if len(result['input_text']) > 100 else ''}")
            print(f"安全状态: {'安全' if result['is_safe'] else '存在风险'}")
            
            # 显示风险摘要
            risk_summary = result['risk_summary']
            if not result['is_safe']:
                print(f"\n风险分析:")
                print(f"  风险数量: {risk_summary.get('risk_count', 0)}")
                print(f"  最高风险等级: {risk_summary.get('highest_risk_level', 'unknown')}")
                print(f"  风险类型: {', '.join(risk_summary.get('risk_types', []))}")
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