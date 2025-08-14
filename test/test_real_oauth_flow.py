#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实的OAuth登录流程
通过模拟OAuth回调来生成真实的token
"""

import os
import sys
import requests
import json
from urllib.parse import parse_qs, urlparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_real_oauth_flow():
    """测试真实的OAuth登录流程"""
    print("=== 真实OAuth登录流程测试 ===")
    
    base_url = "http://localhost:8001"
    
    try:
        # 1. 获取Google OAuth登录URL
        print("\n1. 获取Google OAuth登录URL...")
        response = requests.get(f"{base_url}/api/v1/auth/google/login")
        
        if response.status_code != 200:
            print(f"❌ 获取登录URL失败: {response.status_code}")
            return False
        
        auth_data = response.json()
        auth_url = auth_data.get('authorization_url')
        state = auth_data.get('state')
        
        print(f"✅ 获取登录URL成功")
        print(f"State: {state}")
        
        # 2. 模拟OAuth回调（使用测试数据）
        print("\n2. 模拟OAuth回调...")
        
        # 模拟Google返回的授权码
        mock_code = "test_authorization_code_123"
        
        # 构造回调URL
        callback_url = f"{base_url}/api/v1/auth/google/callback"
        callback_params = {
            "code": mock_code,
            "state": state
        }
        
        # 注意：这个测试会失败，因为我们没有真实的Google授权码
        # 但我们可以看到错误信息来了解流程
        response = requests.get(callback_url, params=callback_params)
        
        print(f"回调响应状态: {response.status_code}")
        print(f"回调响应内容: {response.text[:200]}...")
        
        # 3. 直接测试已存在用户的token生成
        print("\n3. 直接测试已存在用户的token生成...")
        
        # 导入必要的模块来直接创建token
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        
        db = next(get_db())
        user_service = UserService(db)
        
        # 获取测试用户
        test_user = user_service.get_user_by_email("test@example.com")
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        print(f"找到测试用户: ID={test_user.id}, Email={test_user.email}")
        
        # 生成token
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        
        print(f"✅ 生成token成功: {access_token[:50]}...")
        
        # 4. 测试/me端点
        print("\n4. 测试/me端点...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ /me端点测试成功")
            print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
            
            # 验证用户信息
            if (user_info.get('id') == test_user.id and 
                user_info.get('email') == test_user.email):
                print("✅ 用户信息验证正确")
                return True
            else:
                print("❌ 用户信息不匹配")
                return False
        else:
            print(f"❌ /me端点测试失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_auth_status_endpoint():
    """测试认证状态端点"""
    print("\n=== 测试认证状态端点 ===")
    
    base_url = "http://localhost:8001"
    
    try:
        # 导入必要的模块
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        
        db = next(get_db())
        user_service = UserService(db)
        
        # 获取测试用户
        test_user = user_service.get_user_by_email("test@example.com")
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        # 生成token
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        
        # 测试/status端点
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{base_url}/api/v1/auth/status", headers=headers)
        
        if response.status_code == 200:
            status_info = response.json()
            print(f"✅ /status端点测试成功")
            print(f"状态信息: {json.dumps(status_info, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ /status端点测试失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success1 = test_real_oauth_flow()
    success2 = test_auth_status_endpoint()
    
    print("\n=== 总体结果 ===")
    if success1 and success2:
        print("🎉 所有测试通过！用户信息获取功能正常工作")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败")
        sys.exit(1)