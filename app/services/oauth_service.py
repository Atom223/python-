import os
import httpx
import logging
from typing import Dict, Optional, Tuple
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.models.auth_schemas import OAuthProvider, UserCreate
from app.core.security import generate_state_token

logger = logging.getLogger(__name__)


class OAuthConfig:
    """OAuth配置类"""
    def __init__(self):
        # Google OAuth配置
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/api/v1/auth/google/callback")
        
        # GitHub OAuth配置
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8001/api/v1/auth/github/callback")
        
        # OAuth端点
        self.google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        self.github_auth_url = "https://github.com/login/oauth/authorize"
        self.github_token_url = "https://github.com/login/oauth/access_token"
        self.github_user_info_url = "https://api.github.com/user"
        self.github_user_email_url = "https://api.github.com/user/emails"


class OAuthService:
    """OAuth认证服务"""
    
    def __init__(self):
        self.config = OAuthConfig()
    
    def get_google_auth_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """获取Google OAuth授权URL"""
        if not state:
            state = generate_state_token()
        
        client = AsyncOAuth2Client(
            client_id=self.config.google_client_id,
            redirect_uri=self.config.google_redirect_uri
        )
        
        auth_url, _ = client.create_authorization_url(
            self.config.google_auth_url,
            scope="openid email profile",
            state=state
        )
        
        return auth_url, state
    
    def get_github_auth_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """获取GitHub OAuth授权URL"""
        if not state:
            state = generate_state_token()
        
        client = AsyncOAuth2Client(
            client_id=self.config.github_client_id,
            redirect_uri=self.config.github_redirect_uri
        )
        
        auth_url, _ = client.create_authorization_url(
            self.config.github_auth_url,
            scope="user:email",
            state=state
        )
        
        return auth_url, state
    
    async def exchange_google_code(self, code: str) -> Optional[Dict]:
        """交换Google授权码获取用户信息"""
        try:
            async with httpx.AsyncClient() as client:
                # 交换授权码获取访问令牌
                token_data = {
                    "client_id": self.config.google_client_id,
                    "client_secret": self.config.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.config.google_redirect_uri,
                }
                
                token_response = await client.post(
                    self.config.google_token_url,
                    data=token_data
                )
                token_response.raise_for_status()
                token_info = token_response.json()
                
                access_token = token_info.get("access_token")
                if not access_token:
                    logger.error("Failed to get access token from Google")
                    return None
                
                # 使用访问令牌获取用户信息
                user_response = await client.get(
                    self.config.google_user_info_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_response.raise_for_status()
                user_info = user_response.json()
                
                return {
                    "provider_id": user_info.get("id"),
                    "email": user_info.get("email"),
                    "full_name": user_info.get("name"),
                    "avatar_url": user_info.get("picture"),
                    "username": user_info.get("email", "").split("@")[0],
                }
                
        except Exception as e:
            logger.error(f"Error exchanging Google code: {str(e)}")
            return None
    
    async def exchange_github_code(self, code: str) -> Optional[Dict]:
        """交换GitHub授权码获取用户信息"""
        try:
            async with httpx.AsyncClient() as client:
                # 交换授权码获取访问令牌
                token_data = {
                    "client_id": self.config.github_client_id,
                    "client_secret": self.config.github_client_secret,
                    "code": code,
                }
                
                token_response = await client.post(
                    self.config.github_token_url,
                    data=token_data,
                    headers={"Accept": "application/json"}
                )
                token_response.raise_for_status()
                token_info = token_response.json()
                
                access_token = token_info.get("access_token")
                if not access_token:
                    logger.error("Failed to get access token from GitHub")
                    return None
                
                headers = {
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # 获取用户基本信息
                user_response = await client.get(
                    self.config.github_user_info_url,
                    headers=headers
                )
                user_response.raise_for_status()
                user_info = user_response.json()
                
                # 获取用户邮箱（如果公开邮箱为空）
                email = user_info.get("email")
                if not email:
                    email_response = await client.get(
                        self.config.github_user_email_url,
                        headers=headers
                    )
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next(
                            (e["email"] for e in emails if e.get("primary")), 
                            None
                        )
                        if primary_email:
                            email = primary_email
                
                if not email:
                    logger.error("No email found for GitHub user")
                    return None
                
                return {
                    "provider_id": str(user_info.get("id")),
                    "email": email,
                    "full_name": user_info.get("name"),
                    "avatar_url": user_info.get("avatar_url"),
                    "username": user_info.get("login"),
                }
                
        except Exception as e:
            logger.error(f"Error exchanging GitHub code: {str(e)}")
            return None
    
    def create_user_from_oauth(self, user_data: Dict, provider: OAuthProvider) -> UserCreate:
        """从OAuth数据创建用户模型"""
        return UserCreate(
            email=user_data["email"],
            username=user_data.get("username"),
            full_name=user_data.get("full_name"),
            avatar_url=user_data.get("avatar_url"),
            provider=provider,
            provider_id=user_data["provider_id"]
        )


# 全局OAuth服务实例
oauth_service = OAuthService()