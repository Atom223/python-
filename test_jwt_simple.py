#!/usr/bin/env python3
"""
简化的JWT Token测试脚本
直接测试JWT核心功能
"""

import os
import sys
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入应用模块
sys.path.append('/Users/cmy/Downloads/MetaIgnite-backend-main')

def test_jwt_direct():
    """直接测试JWT功能"""
    print("=== 直接测试JWT核心功能 ===")
    print()
    
    # 从环境变量获取配置
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    print(f"🔐 使用的JWT密钥: {SECRET_KEY[:20]}...")
    print(f"🔧 算法: {ALGORITHM}")
    print(f"⏰ 过期时间: {ACCESS_TOKEN_EXPIRE_MINUTES} 分钟")
    print()
    
    # 测试数据
    test_data = {
        'sub': 123,
        'email': 'test@example.com',
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    try:
        # 1. 创建Token
        print("📝 步骤1: 创建JWT Token")
        token = jwt.encode(test_data, SECRET_KEY, algorithm=ALGORITHM)
        print(f"✅ Token创建成功: {token[:50]}...")
        print(f"   Token长度: {len(token)} 字符")
        print()
        
        # 2. 解码验证Token
        print("🔍 步骤2: 解码验证Token")
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Token解码成功")
        print(f"   用户ID: {decoded_payload.get('sub')}")
        print(f"   邮箱: {decoded_payload.get('email')}")
        print(f"   过期时间: {datetime.fromtimestamp(decoded_payload.get('exp')).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 3. 验证数据完整性
        print("🧪 步骤3: 验证数据完整性")
        data_integrity = [
            ('用户ID匹配', decoded_payload.get('sub') == test_data['sub']),
            ('邮箱匹配', decoded_payload.get('email') == test_data['email']),
            ('包含过期时间', 'exp' in decoded_payload)
        ]
        
        all_integrity_passed = True
        for check_name, passed in data_integrity:
            status_icon = '✅' if passed else '❌'
            print(f"  {status_icon} {check_name}")
            if not passed:
                all_integrity_passed = False
        
        if all_integrity_passed:
            print("✅ 数据完整性验证通过")
        else:
            print("❌ 数据完整性验证失败")
        print()
        
        # 4. 测试应用的JWT函数
        print("🔧 步骤4: 测试应用JWT函数")
        try:
            from app.core.security import create_access_token, SECRET_KEY as APP_SECRET, ALGORITHM as APP_ALGORITHM
            
            # 检查配置一致性
            config_match = [
                ('密钥一致', SECRET_KEY == APP_SECRET),
                ('算法一致', ALGORITHM == APP_ALGORITHM)
            ]
            
            config_ok = True
            for check_name, passed in config_match:
                status_icon = '✅' if passed else '❌'
                print(f"  {status_icon} {check_name}")
                if not passed:
                    config_ok = False
                    if check_name == '密钥一致':
                        print(f"    环境变量密钥: {SECRET_KEY[:20]}...")
                        print(f"    应用模块密钥: {APP_SECRET[:20]}...")
            
            if config_ok:
                # 使用应用函数创建token
                app_token = create_access_token(
                    data={'sub': 456, 'email': 'app@test.com'}
                )
                print(f"✅ 应用函数创建Token成功: {app_token[:50]}...")
                
                # 验证应用创建的token
                app_decoded = jwt.decode(app_token, SECRET_KEY, algorithms=[ALGORITHM])
                print(f"✅ 应用Token解码成功")
                print(f"   用户ID: {app_decoded.get('sub')}")
                print(f"   邮箱: {app_decoded.get('email')}")
            else:
                print("❌ 应用配置不一致")
                
        except Exception as e:
            print(f"❌ 应用JWT函数测试失败: {str(e)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ JWT测试失败: {str(e)}")
        return False

def test_token_expiration_simple():
    """简单的Token过期测试"""
    print("=== 测试Token过期机制 ===")
    print()
    
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM = "HS256"
    
    # 创建一个已过期的token
    expired_data = {
        'sub': 999,
        'email': 'expired@test.com',
        'exp': datetime.utcnow() - timedelta(minutes=1)  # 1分钟前过期
    }
    
    try:
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)
        print(f"📝 创建过期Token: {expired_token[:50]}...")
        
        # 尝试解码过期token
        try:
            decoded = jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])
            print("❌ 过期Token解码成功（应该失败）")
            return False
        except jwt.ExpiredSignatureError:
            print("✅ 过期Token正确被拒绝")
            return True
        except Exception as e:
            print(f"⚠️  过期Token处理异常: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 过期测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始简化JWT Token测试\n")
    
    # 直接测试JWT功能
    jwt_ok = test_jwt_direct()
    
    # 测试过期机制
    expiration_ok = test_token_expiration_simple()
    
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"  JWT核心功能: {'✅ 通过' if jwt_ok else '❌ 失败'}")
    print(f"  Token过期机制: {'✅ 通过' if expiration_ok else '❌ 失败'}")
    
    if jwt_ok and expiration_ok:
        print("\n🎉 JWT Token核心功能测试全部通过！")
        print("💡 JWT系统基础功能正常，可以进行用户认证")
        return True
    else:
        print("\n⚠️  JWT测试未完全通过")
        print("🔧 请检查JWT配置和依赖库")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)