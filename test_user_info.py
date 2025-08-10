#!/usr/bin/env python3
"""
用户信息获取功能测试脚本
测试/api/v1/auth/me端点的认证和用户信息返回功能
"""

import os
import sys
import requests
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入应用模块
sys.path.append('/Users/cmy/Downloads/MetaIgnite-backend-main')
from app.core.security import create_access_token

# API基础URL
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1"

def create_test_token(user_id=1, email="test@example.com"):
    """创建测试用的JWT token"""
    try:
        token = create_access_token(
            data={"sub": user_id, "email": email}
        )
        return token
    except Exception as e:
        print(f"❌ 创建测试Token失败: {str(e)}")
        return None

def test_user_info_endpoint_without_auth():
    """测试未认证情况下访问用户信息端点"""
    print("=== 测试未认证访问用户信息端点 ===")
    print()
    
    try:
        url = f"{BASE_URL}{API_PREFIX}/auth/me"
        print(f"📡 请求URL: {url}")
        
        # 不带Authorization头的请求
        response = requests.get(url, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 未认证请求正确被拒绝")
            try:
                error_data = response.json()
                print(f"📄 错误信息: {error_data.get('detail', 'N/A')}")
            except:
                print("📄 响应内容: 非JSON格式")
            return True
        else:
            print(f"❌ 未认证请求应该返回401，实际返回: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_user_info_endpoint_with_invalid_token():
    """测试使用无效token访问用户信息端点"""
    print("\n=== 测试无效Token访问用户信息端点 ===")
    print()
    
    invalid_tokens = [
        {
            'name': '格式错误的Token',
            'token': 'invalid-token-format'
        },
        {
            'name': '空Token',
            'token': ''
        },
        {
            'name': '错误签名的Token',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }
    ]
    
    results = []
    url = f"{BASE_URL}{API_PREFIX}/auth/me"
    
    for case in invalid_tokens:
        try:
            headers = {'Authorization': f'Bearer {case["token"]}'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 401:
                print(f"✅ {case['name']}: 正确拒绝无效Token")
                results.append({'name': case['name'], 'passed': True})
            else:
                print(f"❌ {case['name']}: 应该返回401，实际返回: {response.status_code}")
                results.append({'name': case['name'], 'passed': False})
                
        except Exception as e:
            print(f"❌ {case['name']}: 测试异常 - {str(e)}")
            results.append({'name': case['name'], 'passed': False})
    
    return results

def test_user_info_endpoint_with_valid_token():
    """测试使用有效token访问用户信息端点"""
    print("\n=== 测试有效Token访问用户信息端点 ===")
    print()
    
    # 创建测试token
    test_token = create_test_token(user_id=123, email="testuser@example.com")
    if not test_token:
        print("❌ 无法创建测试Token，跳过此测试")
        return False
    
    print(f"🔑 使用测试Token: {test_token[:50]}...")
    
    try:
        url = f"{BASE_URL}{API_PREFIX}/auth/me"
        headers = {'Authorization': f'Bearer {test_token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                user_data = response.json()
                print("✅ 用户信息获取成功")
                print(f"📄 响应数据结构: {list(user_data.keys())}")
                
                # 检查必要字段
                expected_fields = ['id', 'email', 'username', 'is_active']
                missing_fields = []
                present_fields = []
                
                for field in expected_fields:
                    if field in user_data:
                        present_fields.append(field)
                        print(f"   ✅ {field}: {user_data[field]}")
                    else:
                        missing_fields.append(field)
                        print(f"   ❌ 缺少字段: {field}")
                
                if not missing_fields:
                    print("✅ 用户信息包含所有必要字段")
                    return True
                else:
                    print(f"⚠️  缺少字段: {', '.join(missing_fields)}")
                    return False
                    
            except Exception as json_error:
                print(f"❌ 响应JSON解析失败: {str(json_error)}")
                print(f"📄 原始响应: {response.text}")
                return False
                
        elif response.status_code == 401:
            print("❌ 有效Token被拒绝（可能是认证中间件问题）")
            try:
                error_data = response.json()
                print(f"📄 错误信息: {error_data.get('detail', 'N/A')}")
            except:
                print(f"📄 响应内容: {response.text}")
            return False
        else:
            print(f"❌ 意外的响应状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_user_info_endpoint_structure():
    """测试用户信息端点的基本结构"""
    print("\n=== 测试用户信息端点结构 ===")
    print()
    
    # 检查端点是否存在（通过OPTIONS请求）
    try:
        url = f"{BASE_URL}{API_PREFIX}/auth/me"
        response = requests.options(url, timeout=5)
        
        print(f"📡 OPTIONS请求状态码: {response.status_code}")
        
        # 检查允许的方法
        allow_header = response.headers.get('Allow', '')
        if allow_header:
            print(f"🔧 允许的HTTP方法: {allow_header}")
            if 'GET' in allow_header:
                print("✅ 端点支持GET方法")
                return True
            else:
                print("❌ 端点不支持GET方法")
                return False
        else:
            # 如果没有Allow头，尝试直接GET请求来判断端点是否存在
            get_response = requests.get(url, timeout=5)
            if get_response.status_code != 404:
                print("✅ 端点存在（通过GET请求确认）")
                return True
            else:
                print("❌ 端点不存在")
                return False
                
    except Exception as e:
        print(f"❌ 端点结构测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始用户信息获取功能测试\n")
    
    # 测试端点结构
    structure_ok = test_user_info_endpoint_structure()
    
    # 测试未认证访问
    no_auth_ok = test_user_info_endpoint_without_auth()
    
    # 测试无效token访问
    invalid_token_results = test_user_info_endpoint_with_invalid_token()
    
    # 测试有效token访问
    valid_token_ok = test_user_info_endpoint_with_valid_token()
    
    print("\n" + "="*60)
    print("📊 测试结果总结:")
    
    # 统计结果
    invalid_token_passed = sum(1 for r in invalid_token_results if r['passed'])
    
    print(f"  端点结构: {'✅ 通过' if structure_ok else '❌ 失败'}")
    print(f"  未认证访问拒绝: {'✅ 通过' if no_auth_ok else '❌ 失败'}")
    print(f"  无效Token拒绝: {invalid_token_passed}/{len(invalid_token_results)} 通过")
    print(f"  有效Token访问: {'✅ 通过' if valid_token_ok else '❌ 失败'}")
    
    total_tests = 4
    passed_tests = sum([
        structure_ok,
        no_auth_ok,
        invalid_token_passed == len(invalid_token_results),
        valid_token_ok
    ])
    
    print(f"\n📈 总体通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 用户信息获取功能测试全部通过！")
        print("💡 /api/v1/auth/me端点工作正常，可以安全获取用户信息")
    else:
        print("\n⚠️  部分用户信息获取测试未通过")
        print("🔧 请检查认证中间件和用户信息端点实现")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)