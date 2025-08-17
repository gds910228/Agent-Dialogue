"""
网络诊断工具
帮助诊断和解决语音转文本API连接问题
"""

import os
import sys
import socket
import requests
import subprocess
from typing import Dict, Any, List

class NetworkDiagnostic:
    """网络诊断工具"""
    
    def __init__(self):
        self.zhipu_host = "open.bigmodel.cn"
        self.zhipu_port = 443
        
    def check_internet_connection(self) -> Dict[str, Any]:
        """检查互联网连接"""
        try:
            # 测试DNS解析
            socket.gethostbyname("www.baidu.com")
            
            # 测试HTTP连接
            response = requests.get("http://www.baidu.com", timeout=10)
            
            return {
                "success": True,
                "message": "互联网连接正常"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"互联网连接异常: {str(e)}"
            }
    
    def check_zhipu_connection(self) -> Dict[str, Any]:
        """检查智谱API连接"""
        try:
            # 测试DNS解析
            ip = socket.gethostbyname(self.zhipu_host)
            
            # 测试TCP连接
            sock = socket.create_connection((self.zhipu_host, self.zhipu_port), timeout=10)
            sock.close()
            
            # 测试HTTPS连接
            response = requests.get(f"https://{self.zhipu_host}", timeout=10)
            
            return {
                "success": True,
                "message": f"智谱API连接正常 (IP: {ip})"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"智谱API连接失败: {str(e)}"
            }
    
    def check_proxy_settings(self) -> Dict[str, Any]:
        """检查代理设置"""
        try:
            proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
            proxy_info = {}
            
            for var in proxy_vars:
                value = os.environ.get(var)
                if value:
                    proxy_info[var] = value
            
            if proxy_info:
                return {
                    "success": True,
                    "message": "检测到代理设置",
                    "proxies": proxy_info
                }
            else:
                return {
                    "success": True,
                    "message": "未检测到代理设置"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"代理检查失败: {str(e)}"
            }
    
    def check_firewall(self) -> Dict[str, Any]:
        """检查防火墙设置"""
        try:
            if sys.platform == "win32":
                # Windows防火墙检查
                try:
                    result = subprocess.run(
                        ["netsh", "advfirewall", "show", "allprofiles", "state"],
                        capture_output=True,
                        text=True,
                        encoding='gbk',
                        timeout=10
                    )
                    
                    if result.stdout and "ON" in result.stdout:
                        return {
                            "success": True,
                            "message": "Windows防火墙已启用，可能需要添加例外规则"
                        }
                    else:
                        return {
                            "success": True,
                            "message": "Windows防火墙已关闭"
                        }
                except Exception:
                    return {
                        "success": True,
                        "message": "无法检查防火墙状态，请手动检查"
                    }
            else:
                return {
                    "success": True,
                    "message": "非Windows系统，请手动检查防火墙设置"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"防火墙检查失败: {str(e)}"
            }
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """运行完整诊断"""
        print("🔍 开始网络诊断...")
        print("=" * 50)
        
        results = {}
        
        # 1. 检查互联网连接
        print("1. 检查互联网连接...")
        internet_result = self.check_internet_connection()
        results["internet"] = internet_result
        print(f"   {'✅' if internet_result['success'] else '❌'} {internet_result.get('message', internet_result.get('error'))}")
        
        # 2. 检查智谱API连接
        print("2. 检查智谱API连接...")
        zhipu_result = self.check_zhipu_connection()
        results["zhipu"] = zhipu_result
        print(f"   {'✅' if zhipu_result['success'] else '❌'} {zhipu_result.get('message', zhipu_result.get('error'))}")
        
        # 3. 检查代理设置
        print("3. 检查代理设置...")
        proxy_result = self.check_proxy_settings()
        results["proxy"] = proxy_result
        print(f"   {'✅' if proxy_result['success'] else '❌'} {proxy_result.get('message', proxy_result.get('error'))}")
        if proxy_result.get('proxies'):
            for key, value in proxy_result['proxies'].items():
                print(f"      {key}: {value}")
        
        # 4. 检查防火墙
        print("4. 检查防火墙设置...")
        firewall_result = self.check_firewall()
        results["firewall"] = firewall_result
        print(f"   {'✅' if firewall_result['success'] else '❌'} {firewall_result.get('message', firewall_result.get('error'))}")
        
        print("\n" + "=" * 50)
        
        # 生成建议
        suggestions = self.generate_suggestions(results)
        if suggestions:
            print("💡 建议解决方案:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        return results
    
    def generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """根据诊断结果生成建议"""
        suggestions = []
        
        if not results["internet"]["success"]:
            suggestions.append("检查网络连接，确保能够访问互联网")
        
        if not results["zhipu"]["success"]:
            suggestions.append("智谱API连接失败，可能的解决方案:")
            suggestions.append("  - 检查API密钥是否正确配置")
            suggestions.append("  - 尝试使用VPN或代理")
            suggestions.append("  - 检查防火墙是否阻止了HTTPS连接")
            suggestions.append("  - 联系网络管理员检查企业防火墙设置")
        
        if results["proxy"].get("proxies"):
            suggestions.append("检测到代理设置，确保代理服务器正常工作")
        
        if "防火墙已启用" in results["firewall"].get("message", ""):
            suggestions.append("Windows防火墙已启用，可能需要添加Python程序到例外列表")
        
        return suggestions

def main():
    """主函数"""
    diagnostic = NetworkDiagnostic()
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()