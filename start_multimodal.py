"""
多模态内容分析器启动脚本
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'flask',
        'requests',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_config():
    """检查配置文件"""
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("❌ 配置文件 config.json 不存在")
        return False
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api_keys' not in config or 'zhipu' not in config['api_keys']:
            print("❌ 配置文件中缺少智谱API密钥")
            return False
        
        if not config['api_keys']['zhipu']:
            print("❌ 智谱API密钥为空")
            return False
        
        print("✅ 配置文件检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

def start_server(mode="web"):
    """启动服务器"""
    if mode == "web":
        print("🌐 启动Web服务器...")
        subprocess.run([sys.executable, "multimodal_server.py"])
    elif mode == "mcp":
        print("🔧 启动MCP服务器...")
        subprocess.run([sys.executable, "main.py"])
    else:
        print("❌ 未知的启动模式")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI多模态内容分析器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查配置
    if not check_config():
        return
    
    # 选择启动模式
    print("\n请选择启动模式:")
    print("1. Web界面模式 (推荐)")
    print("2. MCP服务器模式")
    print("3. 运行测试")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == "1":
        start_server("web")
    elif choice == "2":
        start_server("mcp")
    elif choice == "3":
        print("🧪 运行测试...")
        subprocess.run([sys.executable, "test_multimodal.py"])
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()