#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Token调试测试
检查token生成和验证的字段匹配问题
"""

import os
import sys
from datetime import datetime, timedelta
from jose import jwt, JWTError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import create_access_token, verify_token, SECRET_KEY, ALGORITHM
from app.models.auth_schemas import TokenData

def debug_token_fields():
    """调试token字段匹配问题"""
    print("=== JWT Token字段调试 ===")
    
    # 1. 测试当前的token生成方式
    print("\n1. 测试当前token生成...")
    token_data = {
        "user_id": 123,
        "email": "test@example.com"
    }
    
    token = create_access_token(data=token_data)
    print(f"生成的token: {token[:50]}...")
    
    # 2. 解码token查看payload
    print("\n2. 解码token查看payload...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token payload: {payload}")
        print(f"包含的字段: {list(payload.keys())}")
    except JWTError as e:
        print(f"解码失败: {e}")
        return False
    
    # 3. 测试verify_token函数
    print("\n3. 测试verify_token函数...")
    try:
        class MockException(Exception):
            pass
        
        token_data_result = verify_token(token, MockException)
        print(f"验证成功: user_id={token_data_result.user_id}, email={token_data_result.email}")
    except Exception as e:
        print(f"验证失败: {e}")
        print("问题：verify_token期望'sub'字段，但token包含'user_id'字段")
    
    # 4. 测试修正后的token生成
    print("\n4. 测试修正后的token生成...")
    corrected_token_data = {
        "sub": 123,  # 使用'sub'而不是'user_id'
        "email": "test@example.com"
    }
    
    corrected_token = create_access_token(data=corrected_token_data)
    print(f"修正后的token: {corrected_token[:50]}...")
    
    # 5. 验证修正后的token
    print("\n5. 验证修正后的token...")
    try:
        token_data_result = verify_token(corrected_token, MockException)
        print(f"✅ 验证成功: user_id={token_data_result.user_id}, email={token_data_result.email}")
        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def test_auth_endpoint_token_generation():
    """测试auth端点中的token生成方式"""
    print("\n=== 检查auth端点token生成 ===")
    
    # 查看auth.py中_create_user_token函数的实现
    try:
        with open('/Users/cmy/Downloads/MetaIgnite-backend-main/app/api/endpoints/auth.py', 'r') as f:
            content = f.read()
            
        # 查找_create_user_token函数
        if '_create_user_token' in content:
            lines = content.split('\n')
            in_function = False
            function_lines = []
            
            for line in lines:
                if 'def _create_user_token' in line:
                    in_function = True
                    function_lines.append(line)
                elif in_function:
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        break
                    function_lines.append(line)
            
            print("_create_user_token函数实现:")
            for line in function_lines:
                print(line)
        else:
            print("未找到_create_user_token函数")
            
    except Exception as e:
        print(f"读取文件失败: {e}")

if __name__ == "__main__":
    success1 = debug_token_fields()
    test_auth_endpoint_token_generation()
    
    print("\n=== 结论 ===")
    if success1:
        print("✅ 问题已识别：需要使用'sub'字段而不是'user_id'字段")
        print("建议：修改token生成逻辑或verify_token函数以保持一致性")
    else:
        print("❌ 仍有其他问题需要解决")
    
    sys.exit(0 if success1 else 1)