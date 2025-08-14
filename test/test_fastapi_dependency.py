#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试FastAPI依赖注入系统
"""

import os
import sys
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fastapi_dependency():
    """测试FastAPI依赖注入"""
    print("=== 测试FastAPI依赖注入 ===")
    
    try:
        # 导入FastAPI应用
        from app.main import app
        
        # 创建测试客户端
        client = TestClient(app)
        
        # 导入必要的模块
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        
        # 获取测试用户和token
        db = next(get_db())
        user_service = UserService(db)
        test_user = user_service.get_user_by_email("test@example.com")
        
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        # 确保用户已激活
        if not test_user.is_active:
            user_service.activate_user(test_user.id)
            test_user = user_service.get_user_by_id(test_user.id)
        
        print(f"测试用户: ID={test_user.id}, Email={test_user.email}, Active={test_user.is_active}")
        
        # 生成token
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        
        print(f"生成的token: {access_token[:50]}...")
        
        # 1. 测试未认证访问
        print("\n1. 测试未认证访问...")
        response = client.get("/api/v1/auth/me")
        print(f"未认证访问状态: {response.status_code}")
        
        # 2. 测试有效token访问
        print("\n2. 测试有效token访问...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        print(f"有效token访问状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 用户信息获取成功: {user_info}")
            return True
        else:
            print(f"❌ 用户信息获取失败")
            
            # 3. 调试：检查token解析
            print("\n3. 调试token解析...")
            from app.core.security import verify_token
            from fastapi import HTTPException
            
            credentials_exception = HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
            try:
                token_data = verify_token(access_token, credentials_exception)
                print(f"Token解析成功: user_id={token_data.user_id}, email={token_data.email}")
                
                # 检查用户是否存在
                user = user_service.get_user_by_id(token_data.user_id)
                if user:
                    print(f"用户存在: ID={user.id}, Active={user.is_active}")
                else:
                    print("❌ 用户不存在")
                    
            except Exception as e:
                print(f"❌ Token解析失败: {e}")
            
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_auth_endpoints():
    """测试所有认证端点"""
    print("\n=== 测试所有认证端点 ===")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # 导入必要的模块
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        
        # 获取测试用户和token
        db = next(get_db())
        user_service = UserService(db)
        test_user = user_service.get_user_by_email("test@example.com")
        
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 测试各个端点
        endpoints = [
            ("/api/v1/auth/me", "GET", "用户信息"),
            ("/api/v1/auth/status", "GET", "认证状态"),
        ]
        
        results = []
        
        for endpoint, method, name in endpoints:
            print(f"\n测试 {name} ({method} {endpoint})...")
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, headers=headers)
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            
            success = response.status_code == 200
            results.append((name, success))
        
        # 汇总结果
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n认证端点测试结果: {passed}/{total} 通过")
        
        for name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {name}")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success1 = test_fastapi_dependency()
    success2 = test_auth_endpoints()
    
    print("\n=== 总体结果 ===")
    if success1 and success2:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败")
        sys.exit(1)