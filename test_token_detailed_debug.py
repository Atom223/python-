#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的JWT Token调试
逐步检查token验证过程中的每个步骤
"""

import os
import sys
from datetime import datetime, timedelta
from jose import jwt, JWTError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import SECRET_KEY, ALGORITHM
from app.models.auth_schemas import TokenData

def detailed_token_debug():
    """详细调试token验证过程"""
    print("=== 详细JWT Token调试 ===")
    
    # 1. 创建token
    print("\n1. 创建测试token...")
    token_data = {
        "sub": 1,  # 用户ID
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Token: {token}")
    
    # 2. 解码token
    print("\n2. 解码token...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload: {payload}")
        print(f"Sub字段: {payload.get('sub')} (类型: {type(payload.get('sub'))})")
        print(f"Email字段: {payload.get('email')} (类型: {type(payload.get('email'))})")
    except JWTError as e:
        print(f"解码失败: {e}")
        return False
    
    # 3. 手动验证token逻辑
    print("\n3. 手动验证token逻辑...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        print(f"提取的user_id: {user_id} (类型: {type(user_id)})")
        print(f"提取的email: {email} (类型: {type(email)})")
        
        if user_id is None:
            print("❌ user_id为None")
            return False
        else:
            print("✅ user_id不为None")
        
        # 创建TokenData对象
        token_data_obj = TokenData(user_id=user_id, email=email)
        print(f"✅ TokenData创建成功: user_id={token_data_obj.user_id}, email={token_data_obj.email}")
        
    except JWTError as e:
        print(f"❌ JWT解码错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False
    
    # 4. 测试实际的verify_token函数
    print("\n4. 测试verify_token函数...")
    try:
        from app.core.security import verify_token
        
        class TestException(Exception):
            pass
        
        result = verify_token(token, TestException)
        print(f"✅ verify_token成功: user_id={result.user_id}, email={result.email}")
        return True
        
    except TestException:
        print("❌ verify_token抛出了credentials_exception")
        return False
    except Exception as e:
        print(f"❌ verify_token其他错误: {e}")
        return False

def test_with_real_auth_endpoint():
    """使用真实的auth端点生成token进行测试"""
    print("\n=== 使用真实auth端点生成的token测试 ===")
    
    try:
        # 导入必要的模块
        from app.core.database import get_db
        from app.services.user_service import UserService
        from app.api.endpoints.auth import _create_user_token
        
        # 获取测试用户
        db = next(get_db())
        user_service = UserService(db)
        test_user = user_service.get_user_by_email("test@example.com")
        
        if not test_user:
            print("❌ 未找到测试用户")
            return False
        
        print(f"找到测试用户: ID={test_user.id}, Email={test_user.email}")
        
        # 使用真实的_create_user_token函数
        token_response = _create_user_token(test_user)
        print(f"生成的token: {token_response.access_token[:50]}...")
        
        # 测试这个token
        from app.core.security import verify_token
        
        class TestException(Exception):
            pass
        
        result = verify_token(token_response.access_token, TestException)
        print(f"✅ 真实token验证成功: user_id={result.user_id}, email={result.email}")
        
        # 测试API调用
        import requests
        headers = {"Authorization": f"Bearer {token_response.access_token}"}
        response = requests.get("http://localhost:8001/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API调用成功: {user_info}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success1 = detailed_token_debug()
    success2 = test_with_real_auth_endpoint()
    
    print("\n=== 总结 ===")
    if success1 and success2:
        print("✅ 所有测试通过，JWT系统正常工作")
        sys.exit(0)
    else:
        print("❌ 存在问题需要解决")
        sys.exit(1)