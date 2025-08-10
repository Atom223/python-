#!/usr/bin/env python3
"""
Google OAuth登录端点测试脚本
测试Google OAuth登录流程
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs

# API基础URL
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1"

def test_google_login_endpoint():
    """测试Google OAuth登录端点"""
    print("=== 测试Google OAuth登录端点 ===")
    print()
    
    try:
        # 测试Google登录端点
        url = f"{BASE_URL}{API_PREFIX}/auth/google/login"
        print(f"📡 请求URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Google登录端点响应成功")
            print(f"🔗 授权URL: {data.get('auth_url', 'N/A')[:100]}...")
            print(f"🎯 状态参数: {data.get('state', 'N/A')}")
            print(f"💬 消息: {data.get('message', 'N/A')}")
            
            # 验证授权URL格式
            auth_url = data.get('auth_url')
            if auth_url:
                parsed_url = urlparse(auth_url)
                if 'accounts.google.com' in parsed_url.netloc:
                    print("✅ 授权URL格式正确（Google域名）")
                else:
                    print("⚠️  授权URL域名异常")
                    
                # 检查必要的查询参数
                query_params = parse_qs(parsed_url.query)
                required_params = ['client_id', 'redirect_uri', 'response_type', 'scope']
                missing_params = []
                
                for param in required_params:
                    if param not in query_params:
                        missing_params.append(param)
                        
                if not missing_params:
                    print("✅ 授权URL包含所有必要参数")
                else:
                    print(f"⚠️  授权URL缺少参数: {', '.join(missing_params)}")
                    
            return True
            
        else:
            print(f"❌ Google登录端点请求失败")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保服务器正在运行 (http://localhost:8001)")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

def test_api_docs_accessibility():
    """测试API文档是否可访问"""
    print("\n=== 测试API文档可访问性 ===")
    
    try:
        docs_url = f"{BASE_URL}/docs"
        response = requests.get(docs_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ API文档可访问")
            print(f"📖 文档地址: {docs_url}")
            return True
        else:
            print(f"⚠️  API文档访问异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API文档访问测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Google OAuth登录端点测试\n")
    
    # 测试API文档可访问性
    docs_ok = test_api_docs_accessibility()
    
    # 测试Google登录端点
    google_ok = test_google_login_endpoint()
    
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"  API文档访问: {'✅ 通过' if docs_ok else '❌ 失败'}")
    print(f"  Google登录端点: {'✅ 通过' if google_ok else '❌ 失败'}")
    
    if google_ok:
        print("\n🎉 Google OAuth登录端点测试通过！")
        print("💡 下一步可以测试完整的OAuth流程（需要真实的Google账号）")
    else:
        print("\n⚠️  Google OAuth登录端点测试未完全通过")
        print("🔧 请检查服务器状态和OAuth配置")
    
    return google_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)