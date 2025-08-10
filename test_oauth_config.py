#!/usr/bin/env python3
"""
OAuth配置测试脚本
验证Google和GitHub OAuth配置是否正确加载
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_oauth_config():
    """测试OAuth配置"""
    print("=== OAuth配置测试 ===")
    print()
    
    # 测试Google OAuth配置
    print("📱 Google OAuth配置:")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    print(f"  Client ID: {'✅ 已配置' if google_client_id and google_client_id != 'your-google-client-id' else '❌ 未配置或使用默认值'}")
    print(f"  Client Secret: {'✅ 已配置' if google_client_secret and google_client_secret != 'your-google-client-secret' else '❌ 未配置或使用默认值'}")
    print(f"  Redirect URI: {google_redirect_uri or '❌ 未配置'}")
    
    if google_client_id and google_client_id != 'your-google-client-id':
        print(f"  Client ID值: {google_client_id[:20]}...")
    
    print()
    
    # 测试GitHub OAuth配置
    print("🐙 GitHub OAuth配置:")
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
    
    print(f"  Client ID: {'✅ 已配置' if github_client_id and github_client_id != 'your-github-client-id' else '❌ 未配置或使用默认值'}")
    print(f"  Client Secret: {'✅ 已配置' if github_client_secret and github_client_secret != 'your-github-client-secret' else '❌ 未配置或使用默认值'}")
    print(f"  Redirect URI: {github_redirect_uri or '❌ 未配置'}")
    
    if github_client_id and github_client_id != 'your-github-client-id':
        print(f"  Client ID值: {github_client_id}")
    
    print()
    
    # 测试JWT配置
    print("🔐 JWT配置:")
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    token_expire = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    
    print(f"  JWT Secret: {'✅ 已配置' if jwt_secret and jwt_secret != 'your-jwt-secret-key-change-this-in-production' else '⚠️  使用默认值（生产环境需更换）'}")
    print(f"  Token过期时间: {token_expire or '1440'} 分钟")
    
    print()
    
    # 测试数据库配置
    print("🗄️  数据库配置:")
    db_url = os.getenv("DATABASE_URL")
    print(f"  Database URL: {db_url or '❌ 未配置'}")
    
    print()
    
    # 配置总结
    google_ok = all([
        google_client_id and google_client_id != 'your-google-client-id',
        google_client_secret and google_client_secret != 'your-google-client-secret',
        google_redirect_uri
    ])
    
    github_ok = all([
        github_client_id and github_client_id != 'your-github-client-id',
        github_client_secret and github_client_secret != 'your-github-client-secret',
        github_redirect_uri
    ])
    
    print("📊 配置状态总结:")
    print(f"  Google OAuth: {'✅ 配置完整' if google_ok else '❌ 配置不完整'}")
    print(f"  GitHub OAuth: {'✅ 配置完整' if github_ok else '❌ 配置不完整'}")
    print(f"  JWT配置: {'✅ 可用' if jwt_secret else '❌ 未配置'}")
    print(f"  数据库配置: {'✅ 可用' if db_url else '❌ 未配置'}")
    
    return google_ok and github_ok and jwt_secret and db_url

if __name__ == "__main__":
    success = test_oauth_config()
    sys.exit(0 if success else 1)