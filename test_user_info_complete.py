#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的用户信息端点测试
包括创建测试用户和JWT token验证
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from jose import jwt

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from app.core.security import create_access_token, SECRET_KEY, ALGORITHM
from app.core.database import get_db
from app.services.user_service import UserService
from app.models.auth_schemas import UserCreate, OAuthProvider

def test_complete_user_info_flow():
    """完整的用户信息流程测试"""
    print("=== 完整用户信息端点测试 ===")
    
    base_url = "http://localhost:8001"
    results = []
    
    try:
        # 1. 创建测试用户
        print("\n1. 创建测试用户...")
        db = next(get_db())
        user_service = UserService(db)
        
        # 创建测试用户数据
        test_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            provider=OAuthProvider.GOOGLE,
            provider_id="test_google_123"
        )
        
        # 检查用户是否已存在
        existing_user = user_service.get_user_by_email("test@example.com")
        if existing_user:
            print(f"   使用现有测试用户 ID: {existing_user.id}")
            test_user = existing_user
        else:
            # 创建新用户
            test_user = user_service.create_user(test_user_data)
            if test_user:
                print(f"   创建测试用户成功，ID: {test_user.id}")
            else:
                print("   ❌ 创建测试用户失败")
                return False
        
        results.append(("创建/获取测试用户", True, "成功"))
        
        # 2. 生成有效的JWT token
        print("\n2. 生成JWT token...")
        token_data = {
            "sub": str(test_user.id),  # 使用字符串类型的'sub'字段
            "email": test_user.email,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        
        access_token = create_access_token(data=token_data)
        print(f"   生成token成功，用户ID: {test_user.id}")
        results.append(("JWT token生成", True, "成功"))
        
        # 3. 测试未认证访问
        print("\n3. 测试未认证访问...")
        response = requests.get(f"{base_url}/api/v1/auth/me")
        if response.status_code == 401:
            print("   ✅ 未认证访问被正确拒绝")
            results.append(("未认证访问拒绝", True, "正确返回401"))
        else:
            print(f"   ❌ 未认证访问应返回401，实际返回: {response.status_code}")
            results.append(("未认证访问拒绝", False, f"返回{response.status_code}"))
        
        # 4. 测试无效token
        print("\n4. 测试无效token...")
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        if response.status_code == 401:
            print("   ✅ 无效token被正确拒绝")
            results.append(("无效token拒绝", True, "正确返回401"))
        else:
            print(f"   ❌ 无效token应返回401，实际返回: {response.status_code}")
            results.append(("无效token拒绝", False, f"返回{response.status_code}"))
        
        # 5. 测试有效token访问
        print("\n5. 测试有效token访问...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ 有效token访问成功")
            print(f"   用户信息: ID={user_info.get('id')}, Email={user_info.get('email')}")
            
            # 验证返回的用户信息
            if (user_info.get('id') == test_user.id and 
                user_info.get('email') == test_user.email):
                print("   ✅ 用户信息验证正确")
                results.append(("有效token访问", True, "成功获取用户信息"))
            else:
                print("   ❌ 用户信息不匹配")
                results.append(("有效token访问", False, "用户信息不匹配"))
        else:
            print(f"   ❌ 有效token访问失败: {response.status_code}")
            if response.status_code == 401:
                print(f"   错误详情: {response.text}")
            results.append(("有效token访问", False, f"返回{response.status_code}"))
        
        # 6. 测试token过期
        print("\n6. 测试过期token...")
        expired_token_data = {
            "sub": str(test_user.id),  # 使用字符串类型的'sub'字段
            "email": test_user.email,
            "exp": datetime.utcnow() - timedelta(minutes=1)  # 过期token
        }
        expired_token = jwt.encode(expired_token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 401:
            print("   ✅ 过期token被正确拒绝")
            results.append(("过期token拒绝", True, "正确返回401"))
        else:
            print(f"   ❌ 过期token应返回401，实际返回: {response.status_code}")
            results.append(("过期token拒绝", False, f"返回{response.status_code}"))
        
        # 7. 清理测试数据（可选）
        print("\n7. 清理测试数据...")
        # 注意：在生产环境中可能不想删除测试用户
        # 这里只是演示，实际使用时可以注释掉
        # user_service.db.delete(test_user)
        # user_service.db.commit()
        print("   保留测试用户用于后续测试")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库连接
        if 'db' in locals():
            db.close()
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    passed = 0
    total = len(results)
    
    for test_name, success, details in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status} - {details}")
        if success:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有用户信息端点测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，需要检查实现")
        return False

if __name__ == "__main__":
    success = test_complete_user_info_flow()
    sys.exit(0 if success else 1)