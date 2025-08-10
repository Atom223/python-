#!/usr/bin/env python3
"""
OAuth回调处理功能测试脚本
测试Google和GitHub OAuth回调端点的处理逻辑
"""

import requests
import json
import sys
from urllib.parse import urlencode

# API基础URL
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1"

def test_callback_endpoint_structure():
    """测试回调端点的基本结构和参数验证"""
    print("=== 测试OAuth回调端点结构 ===")
    print()
    
    # 测试Google回调端点
    print("🔍 测试Google回调端点参数验证:")
    google_callback_url = f"{BASE_URL}{API_PREFIX}/auth/google/callback"
    
    # 测试缺少参数的情况
    test_cases = [
        {
            'name': '缺少所有参数',
            'params': {},
            'expected_status': [400, 422]  # 可能的错误状态码
        },
        {
            'name': '只有code参数',
            'params': {'code': 'test_code'},
            'expected_status': [400, 422]
        },
        {
            'name': '只有state参数',
            'params': {'state': 'test_state'},
            'expected_status': [400, 422]
        },
        {
            'name': '无效的state参数',
            'params': {'code': 'test_code', 'state': 'invalid_state'},
            'expected_status': [400]
        }
    ]
    
    google_results = []
    for case in test_cases:
        try:
            url = f"{google_callback_url}?{urlencode(case['params'])}"
            response = requests.get(url, timeout=5)
            
            status_ok = response.status_code in case['expected_status']
            result = {
                'name': case['name'],
                'status_code': response.status_code,
                'expected': case['expected_status'],
                'passed': status_ok
            }
            google_results.append(result)
            
            status_icon = '✅' if status_ok else '❌'
            print(f"  {status_icon} {case['name']}: {response.status_code} (期望: {case['expected_status']})")
            
        except Exception as e:
            print(f"  ❌ {case['name']}: 测试异常 - {str(e)}")
            google_results.append({
                'name': case['name'],
                'status_code': 'ERROR',
                'expected': case['expected_status'],
                'passed': False
            })
    
    print()
    print("🔍 测试GitHub回调端点参数验证:")
    github_callback_url = f"{BASE_URL}{API_PREFIX}/auth/github/callback"
    
    github_results = []
    for case in test_cases:
        try:
            url = f"{github_callback_url}?{urlencode(case['params'])}"
            response = requests.get(url, timeout=5)
            
            status_ok = response.status_code in case['expected_status']
            result = {
                'name': case['name'],
                'status_code': response.status_code,
                'expected': case['expected_status'],
                'passed': status_ok
            }
            github_results.append(result)
            
            status_icon = '✅' if status_ok else '❌'
            print(f"  {status_icon} {case['name']}: {response.status_code} (期望: {case['expected_status']})")
            
        except Exception as e:
            print(f"  ❌ {case['name']}: 测试异常 - {str(e)}")
            github_results.append({
                'name': case['name'],
                'status_code': 'ERROR',
                'expected': case['expected_status'],
                'passed': False
            })
    
    return google_results, github_results

def test_callback_error_handling():
    """测试回调端点的错误处理"""
    print("\n=== 测试OAuth回调错误处理 ===")
    print()
    
    # 测试OAuth错误参数
    error_cases = [
        {
            'name': 'access_denied错误',
            'params': {'error': 'access_denied', 'error_description': 'User denied access'},
            'provider': 'google'
        },
        {
            'name': 'invalid_request错误',
            'params': {'error': 'invalid_request', 'error_description': 'Invalid request'},
            'provider': 'github'
        }
    ]
    
    error_results = []
    for case in error_cases:
        try:
            callback_url = f"{BASE_URL}{API_PREFIX}/auth/{case['provider']}/callback"
            url = f"{callback_url}?{urlencode(case['params'])}"
            response = requests.get(url, timeout=5)
            
            # OAuth错误通常返回400状态码
            status_ok = response.status_code in [400, 401, 403]
            result = {
                'name': case['name'],
                'provider': case['provider'],
                'status_code': response.status_code,
                'passed': status_ok
            }
            error_results.append(result)
            
            status_icon = '✅' if status_ok else '❌'
            print(f"  {status_icon} {case['provider'].title()} - {case['name']}: {response.status_code}")
            
            # 尝试解析响应内容
            try:
                response_data = response.json()
                if 'detail' in response_data:
                    print(f"    📄 错误详情: {response_data['detail']}")
            except:
                pass
                
        except Exception as e:
            print(f"  ❌ {case['provider'].title()} - {case['name']}: 测试异常 - {str(e)}")
            error_results.append({
                'name': case['name'],
                'provider': case['provider'],
                'status_code': 'ERROR',
                'passed': False
            })
    
    return error_results

def test_callback_endpoints_availability():
    """测试回调端点的可用性"""
    print("\n=== 测试OAuth回调端点可用性 ===")
    print()
    
    endpoints = {
        'Google回调': f"{BASE_URL}{API_PREFIX}/auth/google/callback",
        'GitHub回调': f"{BASE_URL}{API_PREFIX}/auth/github/callback"
    }
    
    availability_results = []
    for name, url in endpoints.items():
        try:
            # 发送一个基本的GET请求（不带参数）
            response = requests.get(url, timeout=5)
            
            # 回调端点应该返回400或422（缺少必需参数）
            available = response.status_code in [400, 422]
            result = {
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'available': available
            }
            availability_results.append(result)
            
            status_icon = '✅' if available else '❌'
            print(f"  {status_icon} {name}: {response.status_code} {'(端点可用)' if available else '(端点异常)'}")
            
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {name}: 连接失败")
            availability_results.append({
                'name': name,
                'url': url,
                'status_code': 'CONNECTION_ERROR',
                'available': False
            })
        except Exception as e:
            print(f"  ❌ {name}: 测试异常 - {str(e)}")
            availability_results.append({
                'name': name,
                'url': url,
                'status_code': 'ERROR',
                'available': False
            })
    
    return availability_results

def main():
    """主测试函数"""
    print("🚀 开始OAuth回调处理功能测试\n")
    
    # 测试端点可用性
    availability_results = test_callback_endpoints_availability()
    
    # 测试端点结构和参数验证
    google_results, github_results = test_callback_endpoint_structure()
    
    # 测试错误处理
    error_results = test_callback_error_handling()
    
    print("\n" + "="*60)
    print("📊 测试结果总结:")
    
    # 统计结果
    availability_passed = sum(1 for r in availability_results if r['available'])
    google_passed = sum(1 for r in google_results if r['passed'])
    github_passed = sum(1 for r in github_results if r['passed'])
    error_passed = sum(1 for r in error_results if r['passed'])
    
    print(f"  端点可用性: {availability_passed}/{len(availability_results)} 通过")
    print(f"  Google回调参数验证: {google_passed}/{len(google_results)} 通过")
    print(f"  GitHub回调参数验证: {github_passed}/{len(github_results)} 通过")
    print(f"  错误处理测试: {error_passed}/{len(error_results)} 通过")
    
    total_tests = len(availability_results) + len(google_results) + len(github_results) + len(error_results)
    total_passed = availability_passed + google_passed + github_passed + error_passed
    
    print(f"\n📈 总体通过率: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("\n🎉 OAuth回调处理功能测试全部通过！")
        print("💡 回调端点能够正确处理参数验证和错误情况")
    else:
        print("\n⚠️  部分OAuth回调测试未通过")
        print("🔧 请检查回调端点的实现和错误处理逻辑")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)