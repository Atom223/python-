#!/usr/bin/env python3
"""
GitHub OAuth登录端点测试脚本
测试GitHub OAuth登录流程
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs

# API基础URL
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1"

def test_github_login_endpoint():
    """测试GitHub OAuth登录端点"""
    print("=== 测试GitHub OAuth登录端点 ===")
    print()
    
    try:
        # 测试GitHub登录端点
        url = f"{BASE_URL}{API_PREFIX}/auth/github/login"
        print(f"📡 请求URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GitHub登录端点响应成功")
            print(f"🔗 授权URL: {data.get('auth_url', 'N/A')[:100]}...")
            print(f"🎯 状态参数: {data.get('state', 'N/A')}")
            print(f"💬 消息: {data.get('message', 'N/A')}")
            
            # 验证授权URL格式
            auth_url = data.get('auth_url')
            if auth_url:
                parsed_url = urlparse(auth_url)
                if 'github.com' in parsed_url.netloc:
                    print("✅ 授权URL格式正确（GitHub域名）")
                else:
                    print("⚠️  授权URL域名异常")
                    
                # 检查必要的查询参数
                query_params = parse_qs(parsed_url.query)
                required_params = ['client_id', 'redirect_uri', 'response_type', 'scope', 'state']
                missing_params = []
                present_params = []
                
                for param in required_params:
                    if param not in query_params:
                        missing_params.append(param)
                    else:
                        present_params.append(param)
                        
                print(f"✅ 包含的参数: {', '.join(present_params)}")
                if missing_params:
                    print(f"⚠️  缺少的参数: {', '.join(missing_params)}")
                else:
                    print("✅ 授权URL包含所有必要参数")
                    
                # 检查scope参数
                scope = query_params.get('scope', [''])[0]
                if 'user:email' in scope:
                    print("✅ Scope包含用户邮箱权限")
                else:
                    print(f"⚠️  Scope权限: {scope}")
                    
            return True
            
        else:
            print(f"❌ GitHub登录端点请求失败")
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

def test_both_oauth_endpoints():
    """同时测试Google和GitHub OAuth端点"""
    print("\n=== 对比测试Google和GitHub OAuth端点 ===")
    
    endpoints = {
        'Google': f"{BASE_URL}{API_PREFIX}/auth/google/login",
        'GitHub': f"{BASE_URL}{API_PREFIX}/auth/github/login"
    }
    
    results = {}
    
    for provider, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results[provider] = {
                    'status': '✅ 正常',
                    'has_auth_url': bool(data.get('auth_url')),
                    'has_state': bool(data.get('state')),
                    'message': data.get('message', '')
                }
            else:
                results[provider] = {
                    'status': f'❌ 错误 ({response.status_code})',
                    'has_auth_url': False,
                    'has_state': False,
                    'message': ''
                }
        except Exception as e:
            results[provider] = {
                'status': f'❌ 异常: {str(e)[:50]}',
                'has_auth_url': False,
                'has_state': False,
                'message': ''
            }
    
    # 输出对比结果
    print(f"{'Provider':<10} {'Status':<20} {'Auth URL':<10} {'State':<8} {'Message'}")
    print("-" * 80)
    
    for provider, result in results.items():
        auth_url_status = '✅' if result['has_auth_url'] else '❌'
        state_status = '✅' if result['has_state'] else '❌'
        message = result['message'][:30] + '...' if len(result['message']) > 30 else result['message']
        
        print(f"{provider:<10} {result['status']:<20} {auth_url_status:<10} {state_status:<8} {message}")
    
    return all(result['status'].startswith('✅') for result in results.values())

def main():
    """主测试函数"""
    print("🚀 开始GitHub OAuth登录端点测试\n")
    
    # 测试GitHub登录端点
    github_ok = test_github_login_endpoint()
    
    # 对比测试两个OAuth端点
    comparison_ok = test_both_oauth_endpoints()
    
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"  GitHub登录端点: {'✅ 通过' if github_ok else '❌ 失败'}")
    print(f"  OAuth端点对比: {'✅ 通过' if comparison_ok else '❌ 失败'}")
    
    if github_ok:
        print("\n🎉 GitHub OAuth登录端点测试通过！")
        print("💡 下一步可以测试完整的OAuth流程（需要真实的GitHub账号）")
    else:
        print("\n⚠️  GitHub OAuth登录端点测试未完全通过")
        print("🔧 请检查服务器状态和OAuth配置")
    
    return github_ok and comparison_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)