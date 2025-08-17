"""
网络诊断工具

用于诊断智谱API连接问题
"""

import os
import json
import socket
import requests
import platform
import subprocess
from typing import Dict, Any, List, Optional

class NetworkDiagnostic:
    """网络诊断工具类"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化网络诊断工具
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.api_endpoints = [
            "https://open.bigmodel.cn/api/paas/v4/images/generations"
        ]
        self.dns_servers = ["8.8.8.8", "114.114.114.114"]
        
        # 尝试从配置文件加载API密钥
        self.api_key = None
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载API密钥"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key")
            else:
                print(f"⚠️ 配置文件 {self.config_path} 不存在")
                
                # 尝试从环境变量加载API密钥
                self.api_key = os.environ.get("ZHIPU_API_KEY")
                
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
            # 尝试从环境变量加载API密钥
            self.api_key = os.environ.get("ZHIPU_API_KEY")
    
    def check_internet_connection(self) -> Dict[str, Any]:
        """
        检查互联网连接
        
        Returns:
            检查结果
        """
        print("🔍 检查互联网连接...")
        
        try:
            # 尝试连接到常用网站
            test_sites = ["https://www.baidu.com", "https://www.qq.com", "https://www.bing.com"]
            results = []
            
            for site in test_sites:
                try:
                    response = requests.get(site, timeout=5)
                    results.append({
                        "site": site,
                        "success": response.status_code == 200,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                except Exception as e:
                    results.append({
                        "site": site,
                        "success": False,
                        "error": str(e)
                    })
            
            # 判断整体连接状态
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": success_count > 0,
                "message": f"互联网连接 {'正常' if success_count > 0 else '异常'}",
                "details": f"成功连接 {success_count}/{len(test_sites)} 个测试站点",
                "results": results
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "互联网连接检查失败",
                "error": str(e)
            }
    
    def check_dns_resolution(self) -> Dict[str, Any]:
        """
        检查DNS解析
        
        Returns:
            检查结果
        """
        print("🔍 检查DNS解析...")
        
        try:
            # 尝试解析API域名
            domains = ["open.bigmodel.cn", "aigc-files.bigmodel.cn"]
            results = []
            
            for domain in domains:
                try:
                    ip_addresses = socket.gethostbyname_ex(domain)
                    results.append({
                        "domain": domain,
                        "success": True,
                        "ip_addresses": ip_addresses[2]
                    })
                except Exception as e:
                    results.append({
                        "domain": domain,
                        "success": False,
                        "error": str(e)
                    })
            
            # 判断整体DNS解析状态
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": success_count > 0,
                "message": f"DNS解析 {'正常' if success_count > 0 else '异常'}",
                "details": f"成功解析 {success_count}/{len(domains)} 个域名",
                "results": results
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "DNS解析检查失败",
                "error": str(e)
            }
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """
        检查API端点可达性
        
        Returns:
            检查结果
        """
        print("🔍 检查API端点可达性...")
        
        try:
            results = []
            
            for endpoint in self.api_endpoints:
                try:
                    response = requests.head(endpoint, timeout=5)
                    results.append({
                        "endpoint": endpoint,
                        "success": 200 <= response.status_code < 500,  # 2xx或3xx或4xx都算可达
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "success": False,
                        "error": str(e)
                    })
            
            # 判断整体API端点可达性
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": success_count > 0,
                "message": f"API端点可达性 {'正常' if success_count > 0 else '异常'}",
                "details": f"可达 {success_count}/{len(self.api_endpoints)} 个API端点",
                "results": results
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "API端点检查失败",
                "error": str(e)
            }
    
    def check_api_authentication(self) -> Dict[str, Any]:
        """
        检查API认证
        
        Returns:
            检查结果
        """
        print("🔍 检查API认证...")
        
        if not self.api_key:
            return {
                "success": False,
                "message": "API认证检查失败",
                "error": "API密钥未设置"
            }
        
        try:
            # 尝试发送一个简单的认证请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_endpoints[0],
                headers=headers,
                json={
                    "model": "cogview-3-flash",
                    "prompt": "测试认证",
                    "size": "512x512",
                    "quality": "standard"
                },
                timeout=10
            )
            
            # 判断认证状态
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "API认证正常",
                    "details": "成功通过API认证",
                    "status_code": response.status_code
                }
            elif response.status_code == 401 or response.status_code == 403:
                return {
                    "success": False,
                    "message": "API认证失败",
                    "details": "API密钥无效或已过期",
                    "status_code": response.status_code,
                    "response": response.text
                }
            else:
                return {
                    "success": False,
                    "message": "API认证检查异常",
                    "details": f"API返回非预期状态码: {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "API认证检查失败",
                "error": str(e)
            }
    
    def run_ping_test(self) -> Dict[str, Any]:
        """
        运行Ping测试
        
        Returns:
            测试结果
        """
        print("🔍 运行Ping测试...")
        
        try:
            domains = ["open.bigmodel.cn", "aigc-files.bigmodel.cn"]
            results = []
            
            for domain in domains:
                try:
                    # 根据操作系统选择ping命令参数
                    if platform.system().lower() == "windows":
                        # Windows: ping -n 4 domain
                        ping_cmd = ["ping", "-n", "4", domain]
                    else:
                        # Linux/Mac: ping -c 4 domain
                        ping_cmd = ["ping", "-c", "4", domain]
                    
                    # 执行ping命令
                    process = subprocess.run(
                        ping_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=10
                    )
                    
                    # 解析结果
                    output = process.stdout
                    success = process.returncode == 0
                    
                    results.append({
                        "domain": domain,
                        "success": success,
                        "output": output
                    })
                    
                except Exception as e:
                    results.append({
                        "domain": domain,
                        "success": False,
                        "error": str(e)
                    })
            
            # 判断整体Ping测试状态
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": success_count > 0,
                "message": f"Ping测试 {'正常' if success_count > 0 else '异常'}",
                "details": f"成功Ping {success_count}/{len(domains)} 个域名",
                "results": results
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Ping测试失败",
                "error": str(e)
            }
    
    def check_system_info(self) -> Dict[str, Any]:
        """
        检查系统信息
        
        Returns:
            系统信息
        """
        print("🔍 检查系统信息...")
        
        try:
            return {
                "success": True,
                "message": "系统信息",
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "系统信息检查失败",
                "error": str(e)
            }
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """
        运行完整诊断
        
        Returns:
            诊断结果
        """
        print("🔍 开始网络诊断...")
        
        # 运行所有检查
        internet_check = self.check_internet_connection()
        dns_check = self.check_dns_resolution()
        api_endpoints_check = self.check_api_endpoints()
        ping_test = self.run_ping_test()
        system_info = self.check_system_info()
        
        # 如果有API密钥，也检查API认证
        api_auth_check = None
        if self.api_key:
            api_auth_check = self.check_api_authentication()
        
        # 汇总结果
        checks = [
            ("互联网连接", internet_check),
            ("DNS解析", dns_check),
            ("API端点可达性", api_endpoints_check),
            ("Ping测试", ping_test)
        ]
        
        if api_auth_check:
            checks.append(("API认证", api_auth_check))
        
        # 计算总体状态
        success_count = sum(1 for _, check in checks if check["success"])
        overall_success = success_count >= len(checks) * 0.6  # 60%以上成功算正常
        
        # 打印结果
        print("\n📊 诊断结果摘要:")
        for name, check in checks:
            status = "✅" if check["success"] else "❌"
            print(f"{status} {name}: {check['message']}")
        
        # 打印系统信息
        if system_info["success"]:
            print(f"\n💻 系统信息: {system_info['system']} {system_info['release']} ({system_info['machine']})")
        
        # 提供建议
        print("\n💡 诊断建议:")
        if not overall_success:
            if not internet_check["success"]:
                print("  - 检查网络连接，确保可以访问互联网")
            if not dns_check["success"]:
                print("  - DNS解析问题，尝试使用其他DNS服务器 (如8.8.8.8或114.114.114.114)")
            if not api_endpoints_check["success"]:
                print("  - API端点不可达，可能是网络限制或防火墙问题")
            if api_auth_check and not api_auth_check["success"]:
                print("  - API认证失败，请检查API密钥是否正确设置")
            print("  - 如果问题持续，可能需要使用VPN或代理服务器")
        else:
            print("  - 网络诊断未发现明显问题")
            if api_auth_check and not api_auth_check["success"]:
                print("  - 但API认证失败，请检查API密钥是否正确设置")
        
        # 返回完整结果
        return {
            "success": overall_success,
            "message": f"诊断完成，状态: {'正常' if overall_success else '异常'}",
            "details": f"通过 {success_count}/{len(checks)} 项检查",
            "checks": {name: check for name, check in checks},
            "system_info": system_info
        }


# 测试代码
if __name__ == "__main__":
    diagnostic = NetworkDiagnostic()
    diagnostic.run_full_diagnostic()