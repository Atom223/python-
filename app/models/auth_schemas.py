from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class OAuthProvider(str, Enum):
    """OAuth提供商枚举"""
    GOOGLE = "google"
    GITHUB = "github"


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: Optional[str] = Field(None, description="用户名")
    full_name: Optional[str] = Field(None, description="全名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_active: bool = Field(True, description="是否激活")


class UserCreate(UserBase):
    """创建用户模型"""
    provider: OAuthProvider = Field(..., description="OAuth提供商")
    provider_id: str = Field(..., description="OAuth提供商用户ID")


class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    provider: OAuthProvider
    provider_id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    provider: OAuthProvider
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求模型"""
    code: str = Field(..., description="授权码")
    state: Optional[str] = Field(None, description="状态参数")


class OAuthLoginResponse(BaseModel):
    """OAuth登录响应模型"""
    success: bool
    message: str
    token: Optional[Token] = None
    redirect_url: Optional[str] = None