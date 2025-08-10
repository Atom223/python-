#!/usr/bin/env python3
"""
JWT Token生成和验证机制测试脚本
测试JWT token的创建、验证、过期等功能
"""

import os
import sys
import jwt
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入应用模块
sys.path.append('/Users/cmy/Downloads/MetaIgnite-backend-main')

# 重新加载环境变量以确保正确读取
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440')

from app.core.security import create_access_token, verify_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.auth_schemas import TokenData
from fastapi import HTTPException, status

def test_jwt_configuration():
    """测试JWT配置"""
    print("=== 测试JWT配置 ===")
    print()
    
    # 检查JWT密钥
    print(f"🔐 JWT Secret Key: {'✅ 已配置' if SECRET_KEY and SECRET_KEY != 'your-secret-key-change-this-in-production' else '⚠️  使用默认值'}")
    print(f"🔧 算法: {ALGORITHM}")
    print(f"⏰ Token过期时间: {ACCESS_TOKEN_EXPIRE_MINUTES} 分钟")
    
    # 检查密钥长度
    if len(SECRET_KEY) < 32:
        print("⚠️  JWT密钥长度较短，建议使用更长的密钥")
    else:
        print("✅ JWT密钥长度符合安全要求")
    
    return True

def test_token_creation():
    """测试Token创建功能"""
    print("\n=== 测试Token创建功能 ===")
    print()
    
    test_cases = [
        {
            'name': '基本用户数据',
            'data': {'sub': 1, 'email': 'test@example.com'},
            'expires_delta': None
        },
        {
            'name': '自定义过期时间',
            'data': {'sub': 2, 'email': 'user2@example.com'},
            'expires_delta': timedelta(minutes=60)
        },
        {
            'name': '包含额外数据',
            'data': {'sub': 3, 'email': 'user3@example.com', 'role': 'admin'},
            'expires_delta': timedelta(hours=1)
        }
    ]
    
    results = []
    for case in test_cases:
        try:
            token = create_access_token(
                data=case['data'],
                expires_delta=case['expires_delta']
            )
            
            # 验证token格式
            if token and len(token.split('.')) == 3:
                print(f"✅ {case['name']}: Token创建成功")
                print(f"   Token长度: {len(token)} 字符")
                
                # 解码验证内容
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    print(f"   包含数据: {list(payload.keys())}")
                    print(f"   用户ID: {payload.get('sub')}")
                    print(f"   邮箱: {payload.get('email')}")
                    
                    # 检查过期时间
                    exp = payload.get('exp')
                    if exp:
                        exp_time = datetime.fromtimestamp(exp)
                        print(f"   过期时间: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    results.append({'name': case['name'], 'success': True, 'token': token})
                except Exception as decode_error:
                    print(f"❌ {case['name']}: Token解码失败 - {str(decode_error)}")
                    results.append({'name': case['name'], 'success': False, 'token': None})
            else:
                print(f"❌ {case['name']}: Token格式无效")
                results.append({'name': case['name'], 'success': False, 'token': None})
                
        except Exception as e:
            print(f"❌ {case['name']}: Token创建失败 - {str(e)}")
            results.append({'name': case['name'], 'success': False, 'token': None})
        
        print()
    
    return results

def test_token_verification(token_results):
    """测试Token验证功能"""
    print("=== 测试Token验证功能 ===")
    print()
    
    # 创建验证异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    verification_results = []
    
    # 测试有效token验证
    for result in token_results:
        if result['success'] and result['token']:
            try:
                token_data = verify_token(result['token'], credentials_exception)
                print(f"✅ {result['name']}: Token验证成功")
                print(f"   用户ID: {token_data.user_id}")
                print(f"   邮箱: {token_data.email}")
                verification_results.append({'name': result['name'], 'verified': True})
            except Exception as e:
                print(f"❌ {result['name']}: Token验证失败 - {str(e)}")
                verification_results.append({'name': result['name'], 'verified': False})
        else:
            print(f"⏭️  {result['name']}: 跳过验证（Token创建失败）")
            verification_results.append({'name': result['name'], 'verified': False})
        print()
    
    # 测试无效token
    invalid_tokens = [
        {
            'name': '空Token',
            'token': ''
        },
        {
            'name': '格式错误的Token',
            'token': 'invalid.token.format'
        },
        {
            'name': '错误签名的Token',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }
    ]
    
    print("🔍 测试无效Token处理:")
    for invalid_case in invalid_tokens:
        try:
            token_data = verify_token(invalid_case['token'], credentials_exception)
            print(f"❌ {invalid_case['name']}: 应该验证失败但成功了")
            verification_results.append({'name': invalid_case['name'], 'verified': False})
        except HTTPException:
            print(f"✅ {invalid_case['name']}: 正确拒绝无效Token")
            verification_results.append({'name': invalid_case['name'], 'verified': True})
        except Exception as e:
            print(f"⚠️  {invalid_case['name']}: 验证异常 - {str(e)}")
            verification_results.append({'name': invalid_case['name'], 'verified': False})
    
    print()
    return verification_results

def test_token_expiration():
    """测试Token过期功能"""
    print("=== 测试Token过期功能 ===")
    print()
    
    # 创建一个很快过期的token
    short_lived_token = create_access_token(
        data={'sub': 999, 'email': 'expire@test.com'},
        expires_delta=timedelta(seconds=1)
    )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 立即验证（应该成功）
    try:
        token_data = verify_token(short_lived_token, credentials_exception)
        print("✅ 新创建的Token验证成功")
        print(f"   用户ID: {token_data.user_id}")
    except Exception as e:
        print(f"❌ 新创建的Token验证失败: {str(e)}")
        return False
    
    # 等待token过期
    print("⏳ 等待Token过期...")
    time.sleep(2)
    
    # 再次验证（应该失败）
    try:
        token_data = verify_token(short_lived_token, credentials_exception)
        print("❌ 过期Token验证成功（应该失败）")
        return False
    except HTTPException:
        print("✅ 过期Token正确被拒绝")
        return True
    except Exception as e:
        print(f"⚠️  过期Token验证异常: {str(e)}")
        return False

def test_token_payload_integrity():
    """测试Token载荷完整性"""
    print("\n=== 测试Token载荷完整性 ===")
    print()
    
    # 创建包含特殊字符的token
    special_data = {
        'sub': 12345,
        'email': 'test+special@example.com',
        'name': '测试用户',
        'roles': ['user', 'admin']
    }
    
    try:
        token = create_access_token(data=special_data)
        
        # 手动解码验证数据完整性
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 检查数据完整性
        integrity_checks = [
            ('用户ID', payload.get('sub') == special_data['sub']),
            ('邮箱', payload.get('email') == special_data['email']),
            ('姓名', payload.get('name') == special_data['name']),
            ('角色', payload.get('roles') == special_data['roles']),
            ('过期时间', 'exp' in payload)
        ]
        
        all_passed = True
        for check_name, passed in integrity_checks:
            status_icon = '✅' if passed else '❌'
            print(f"  {status_icon} {check_name}: {'通过' if passed else '失败'}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ Token载荷完整性测试通过")
        else:
            print("\n❌ Token载荷完整性测试失败")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Token载荷完整性测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始JWT Token生成和验证机制测试\n")
    
    # 测试JWT配置
    config_ok = test_jwt_configuration()
    
    # 测试Token创建
    token_results = test_token_creation()
    
    # 测试Token验证
    verification_results = test_token_verification(token_results)
    
    # 测试Token过期
    expiration_ok = test_token_expiration()
    
    # 测试载荷完整性
    integrity_ok = test_token_payload_integrity()
    
    print("\n" + "="*60)
    print("📊 测试结果总结:")
    
    # 统计结果
    creation_success = sum(1 for r in token_results if r['success'])
    verification_success = sum(1 for r in verification_results if r['verified'])
    
    print(f"  JWT配置: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"  Token创建: {creation_success}/{len(token_results)} 通过")
    print(f"  Token验证: {verification_success}/{len(verification_results)} 通过")
    print(f"  Token过期处理: {'✅ 通过' if expiration_ok else '❌ 失败'}")
    print(f"  载荷完整性: {'✅ 通过' if integrity_ok else '❌ 失败'}")
    
    total_tests = 5  # 总共5个主要测试项
    passed_tests = sum([
        config_ok,
        creation_success == len(token_results),
        verification_success == len(verification_results),
        expiration_ok,
        integrity_ok
    ])
    
    print(f"\n📈 总体通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 JWT Token生成和验证机制测试全部通过！")
        print("💡 JWT系统运行正常，可以安全处理用户认证")
    else:
        print("\n⚠️  部分JWT测试未通过")
        print("🔧 请检查JWT配置和实现逻辑")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)