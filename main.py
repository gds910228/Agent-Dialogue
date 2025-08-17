"""
AI Text Tokenizer System - Main Entry Point

A comprehensive text tokenization system supporting Zhipu tokenizer models.
Provides both MCP server capabilities and direct text tokenization functionality.
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
from zhipu_tokenizer_client import ZhipuTokenizerClient
from network_diagnostic import NetworkDiagnostic

# Create an MCP server
mcp = FastMCP("AI Text Tokenizer System")

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

tokenizer_base_url = config.get("api_settings", {}).get("base_url", "https://open.bigmodel.cn")
tokenizer_client = ZhipuTokenizerClient(api_key=api_key or "", base_url=tokenizer_base_url)

# Text Tokenization Entry Point
class TokenizerGenerator:
    """主要的文本分词入口类"""
    
    def __init__(self):
        self.tokenizer_client = tokenizer_client
        self.outputs_dir = OUTPUTS_DIR
    
    def tokenize_text(self, 
                     messages: List[Dict[str, str]],
                     model: str = "glm-4-plus") -> Dict[str, Any]:
        """
        主要的文本分词入口
        
        Args:
            messages: 消息列表，每个消息包含role和content
            model: 使用的分词模型
            
        Returns:
            分词结果
        """
        return self.tokenizer_client.tokenize(
            messages=messages,
            model=model
        )
    
    def get_token_count(self, messages: List[Dict[str, str]], 
                       model: str = "glm-4-plus") -> int:
        """获取文本的token数量"""
        return self.tokenizer_client.count_tokens_for_messages(messages, model)

# 创建全局文本分词实例
tokenizer_generator = TokenizerGenerator()

@mcp.tool()
def tokenize_text(
    messages: List[Dict[str, str]],
    model: str = "glm-4-plus"
) -> Dict[str, Any]:
    """
    对文本进行分词
    
    Args:
        messages: 消息列表，每个消息包含role和content
        model: 分词模型名称
    
    Returns:
        包含分词结果的字典
    """
    try:
        if not messages or len(messages) == 0:
            return {
                "success": False,
                "error": "消息列表不能为空"
            }
        
        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                return {
                    "success": False,
                    "error": "消息格式错误，每个消息必须包含role和content字段"
                }
        
        result = tokenizer_generator.tokenize_text(
            messages=messages,
            model=model
        )
        
        return {
            "success": True,
            "model": model,
            "usage": result.get("usage", {}),
            "request_id": result.get("id", ""),
            "created": result.get("created", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"文本分词失败: {str(e)}"
        }

@mcp.tool()
def get_token_count(
    messages: List[Dict[str, str]],
    model: str = "glm-4-plus"
) -> Dict[str, Any]:
    """
    获取文本的token数量
    
    Args:
        messages: 消息列表，每个消息包含role和content
        model: 分词模型名称
    
    Returns:
        包含token数量的字典
    """
    try:
        if not messages or len(messages) == 0:
            return {
                "success": False,
                "error": "消息列表不能为空"
            }
        
        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                return {
                    "success": False,
                    "error": "消息格式错误，每个消息必须包含role和content字段"
                }
        
        token_count = tokenizer_generator.get_token_count(
            messages=messages,
            model=model
        )
        
        result = {
            "success": True,
            "model": model,
            "token_count": token_count
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取token数量失败: {str(e)}"
        }

@mcp.tool()
def get_supported_tokenizer_models() -> Dict[str, Any]:
    """
    获取支持的分词模型列表
    
    Returns:
        包含支持模型的结果字典
    """
    try:
        models = tokenizer_client.get_available_models()
        
        return {
            "success": True,
            "models": models,
            "default_model": "glm-4-plus",
            "model_info": {
                "glm-4-plus": "智谱AI GLM-4-Plus模型的分词器",
                "glm-4": "智谱AI GLM-4模型的分词器",
                "glm-3-turbo": "智谱AI GLM-3-Turbo模型的分词器"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取支持的模型失败: {str(e)}"
        }

@mcp.tool()
def test_tokenizer_api(test_messages: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    测试文本分词API连接和功能
    
    Args:
        test_messages: 可选的测试消息列表
    
    Returns:
        包含测试结果的字典
    """
    try:
        # 测试API连接
        connection_test = tokenizer_client.test_connection()
        
        result = {
            "success": True,
            "connection_test": connection_test,
            "supported_models": tokenizer_client.get_available_models()
        }
        
        # 如果提供了测试数据，进行分词测试
        if test_messages:
            try:
                tokenize_result = tokenizer_client.tokenize(test_messages, "glm-4-plus")
                tokenize_test_result = {
                    "success": True,
                    "message_count": len(test_messages),
                    "token_count": tokenize_result.get("usage", {}).get("prompt_tokens", 0)
                }
                result["tokenize_test"] = tokenize_test_result
            except Exception as e:
                result["tokenize_test"] = {
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
def save_tokenize_results_to_file(
    messages: List[Dict[str, str]],
    filename: str,
    model: str = "glm-4-plus"
) -> Dict[str, Any]:
    """
    将分词结果保存到文件
    
    Args:
        messages: 消息列表
        filename: 保存的文件名
        model: 分词模型名称
    
    Returns:
        保存结果字典
    """
    try:
        if not messages or not filename:
            return {
                "success": False,
                "error": "消息列表和文件名都是必需的"
            }
        
        # 获取分词结果
        tokenize_result = tokenizer_generator.tokenize_text(messages, model)
        
        # 准备保存数据
        save_data = {
            "model": model,
            "timestamp": time.time(),
            "messages": messages,
            "usage": tokenize_result.get("usage", {}),
            "request_id": tokenize_result.get("id", ""),
            "created": tokenize_result.get("created", 0)
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
            "message_count": len(messages),
            "token_count": tokenize_result.get("usage", {}).get("prompt_tokens", 0),
            "model": model
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"保存分词结果失败: {str(e)}"
        }

@mcp.tool()
def load_tokenize_results_from_file(filename: str) -> Dict[str, Any]:
    """
    从文件加载分词结果
    
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
            "model": data.get("model"),
            "message_count": len(data.get("messages", [])),
            "timestamp": data.get("timestamp"),
            "usage": data.get("usage", {}),
            "messages": data.get("messages", [])
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"加载分词结果失败: {str(e)}"
        }

def run_interactive_mode():
    """运行交互式文本分词模式"""
    print("=" * 60)
    print("🔤 AI文本分词系统 - 交互模式")
    print("=" * 60)
    print("支持的功能:")
    print("1. 文本分词")
    print("2. 获取Token数量")
    print("3. 查看支持的模型")
    print("4. 测试API连接")
    print("5. 保存分词结果到文件")
    print("6. 从文件加载分词结果")
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
                handle_text_tokenize()
            elif choice == "2":
                handle_token_count()
            elif choice == "3":
                handle_model_info()
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

def handle_text_tokenize():
    """处理文本分词"""
    print("\n🔤 文本分词")
    
    messages = []
    print("请输入消息 (格式: role:content，每行一个，空行结束):")
    print("例如: user:Hello, how are you?")
    print("      assistant:I'm doing well, thank you for asking!")
    
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            role, content = line.split(":", 1)
            messages.append({
                "role": role.strip(),
                "content": content.strip()
            })
        except ValueError:
            print("❌ 格式错误，请使用 'role:content' 格式")
    
    if not messages:
        print("❌ 没有输入任何消息")
        return
    
    models = tokenizer_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: glm-4-plus): ").strip() or "glm-4-plus"
    
    print("🔍 分词中...")
    try:
        result = tokenize_text(messages, model)
        
        if result["success"]:
            print(f"✅ 文本分词成功!")
            print(f"模型: {result['model']}")
            print(f"消息数量: {len(messages)}")
            print(f"\n使用情况:")
            print(f"  Token数量: {result['usage'].get('prompt_tokens', 0)}")
            print(f"  请求ID: {result['request_id']}")
            print(f"  创建时间: {result['created']}")
        else:
            print(f"❌ 分词失败: {result['error']}")
    except Exception as e:
        print(f"❌ 分词失败: {str(e)}")

def handle_token_count():
    """处理获取Token数量"""
    print("\n🔢 获取Token数量")
    
    messages = []
    print("请输入消息 (格式: role:content，每行一个，空行结束):")
    print("例如: user:Hello, how are you?")
    print("      assistant:I'm doing well, thank you for asking!")
    
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            role, content = line.split(":", 1)
            messages.append({
                "role": role.strip(),
                "content": content.strip()
            })
        except ValueError:
            print("❌ 格式错误，请使用 'role:content' 格式")
    
    if not messages:
        print("❌ 没有输入任何消息")
        return
    
    models = tokenizer_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: glm-4-plus): ").strip() or "glm-4-plus"
    
    print("🔍 计算中...")
    try:
        result = get_token_count(messages, model)
        
        if result["success"]:
            print(f"✅ Token计算成功!")
            print(f"模型: {result['model']}")
            print(f"消息数量: {len(messages)}")
            print(f"Token数量: {result['token_count']}")
        else:
            print(f"❌ 计算失败: {result['error']}")
    except Exception as e:
        print(f"❌ 计算失败: {str(e)}")

def handle_model_info():
    """处理模型信息查看"""
    print("\n🔧 支持的分词模型")
    try:
        result = get_supported_tokenizer_models()
        
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
    test_messages = None
    
    use_test_data = input("是否使用测试数据? (y/n, 默认: y): ").strip().lower() or "y"
    if use_test_data == "y":
        test_messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    
    print("🔍 测试中...")
    try:
        result = test_tokenizer_api(test_messages)
        
        if result["success"]:
            print("✅ API测试结果:")
            conn_test = result["connection_test"]
            print(f"  连接状态: {'正常' if conn_test else '失败'}")
            print(f"  支持的模型: {', '.join(result['supported_models'])}")
            
            if 'tokenize_test' in result:
                tokenize_test = result['tokenize_test']
                if tokenize_test['success']:
                    print(f"  测试分词: 成功处理 {tokenize_test['message_count']} 个消息")
                    print(f"  Token数量: {tokenize_test['token_count']}")
                else:
                    print(f"  测试分词失败: {tokenize_test['error']}")
        else:
            print(f"❌ API测试失败: {result['error']}")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def handle_save_results():
    """处理保存分词结果"""
    print("\n💾 保存分词结果到文件")
    
    messages = []
    print("请输入消息 (格式: role:content，每行一个，空行结束):")
    print("例如: user:Hello, how are you?")
    print("      assistant:I'm doing well, thank you for asking!")
    
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            role, content = line.split(":", 1)
            messages.append({
                "role": role.strip(),
                "content": content.strip()
            })
        except ValueError:
            print("❌ 格式错误，请使用 'role:content' 格式")
    
    if not messages:
        print("❌ 没有输入任何消息")
        return
    
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    models = tokenizer_client.get_available_models()
    print(f"\n可用的模型: {', '.join(models)}")
    model = input("请选择模型 (默认: glm-4-plus): ").strip() or "glm-4-plus"
    
    print("💾 保存中...")
    try:
        result = save_tokenize_results_to_file(messages, filename, model)
        
        if result["success"]:
            print(f"✅ 保存成功!")
            print(f"文件路径: {result['file_path']}")
            print(f"文件大小: {result['size']} 字节")
            print(f"消息数量: {result['message_count']}")
            print(f"Token数量: {result['token_count']}")
        else:
            print(f"❌ 保存失败: {result['error']}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def handle_load_results():
    """处理加载分词结果"""
    print("\n📂 从文件加载分词结果")
    filename = input("请输入文件名: ").strip()
    if not filename:
        print("❌ 文件名不能为空")
        return
    
    print("📂 加载中...")
    try:
        result = load_tokenize_results_from_file(filename)
        
        if result["success"]:
            print(f"✅ 加载成功!")
            print(f"文件名: {result['filename']}")
            print(f"模型: {result['model']}")
            print(f"消息数量: {result['message_count']}")
            print(f"Token数量: {result['usage'].get('prompt_tokens', 0)}")
            
            # 显示消息内容
            print("\n消息内容:")
            for i, msg in enumerate(result['messages']):
                print(f"{i+1}. {msg['role']}: {msg['content'][:50]}...")
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