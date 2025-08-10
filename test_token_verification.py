#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试token验证逻辑
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_token_verification():
    """直接测试token验证逻辑"""
    print("=== 直接测试token验证逻辑 ===")
    
    try:
        # 导入必要的模块
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        from app.core.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        
        # 获取数据库连接
        db = next(get_db())
        user_service = UserService(db)
        
        # 1. 获取测试用户
        print("\n1. 获取测试用户...")
        test_user = user_service.get_user_by_email("test@example.com")
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        print(f"✅ 找到测试用户: ID={test_user.id}, Email={test_user.email}, Active={test_user.is_active}")
        
        # 2. 生成token
        print("\n2. 生成token...")
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        print(f"✅ 生成token成功: {access_token[:50]}...")
        
        # 3. 直接测试verify_token函数
        print("\n3. 测试verify_token函数...")
        from app.core.security import verify_token
        from fastapi import HTTPException
        
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            token_data = verify_token(access_token, credentials_exception)
            print(f"✅ verify_token成功: user_id={token_data.user_id}, email={token_data.email}")
        except HTTPException as e:
            print(f"❌ verify_token失败: {e.detail}")
            return False
        
        # 4. 测试get_current_user函数
        print("\n4. 测试get_current_user函数...")
        
        # 创建模拟的credentials对象
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=access_token
        )
        
        try:
            import asyncio
            
            # 运行异步函数
            async def test_get_current_user():
                return await get_current_user(credentials, db)
            
            current_user = asyncio.run(test_get_current_user())
            print(f"✅ get_current_user成功: ID={current_user.id}, Email={current_user.email}")
            
        except Exception as e:
            print(f"❌ get_current_user失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 5. 检查用户状态
        print("\n5. 检查用户状态...")
        fresh_user = user_service.get_user_by_id(test_user.id)
        if fresh_user:
            print(f"用户状态: ID={fresh_user.id}, Active={fresh_user.is_active}")
            if not fresh_user.is_active:
                print("❌ 用户未激活，这可能是问题所在")
                # 激活用户
                user_service.activate_user(fresh_user.id)
                print("✅ 已激活用户")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_api_with_activated_user():
    """使用激活的用户测试API"""
    print("\n=== 使用激活用户测试API ===")
    
    try:
        import requests
        
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
        
        # 确保用户已激活
        if not test_user.is_active:
            user_service.activate_user(test_user.id)
            test_user = user_service.get_user_by_id(test_user.id)  # 重新获取
        
        print(f"用户状态: ID={test_user.id}, Active={test_user.is_active}")
        
        # 生成token
        token_response = _create_user_token(test_user)
        access_token = token_response.access_token
        
        # 测试API
        base_url = "http://localhost:8001"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 测试/me端点
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ /me端点测试成功: {user_info}")
            return True
        else:
            print(f"❌ /me端点测试失败: {response.status_code} - {response.text}")
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
    success1 = test_token_verification()
    success2 = test_api_with_activated_user()
    
    print("\n=== 总体结果 ===")
    if success1 and success2:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败")
        sys.exit(1)