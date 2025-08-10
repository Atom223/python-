import logging
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.auth_schemas import (
    OAuthProvider, 
    OAuthCallbackRequest, 
    OAuthLoginResponse, 
    Token,
    UserResponse
)
from app.services.oauth_service import oauth_service
from app.services.user_service import UserService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# 存储OAuth状态的临时存储（生产环境应使用Redis等）
oauth_states: Dict[str, str] = {}


@router.get("/google/login")
async def google_login():
    """Google OAuth登录 - 重定向到Google授权页面"""
    try:
        auth_url, state = oauth_service.get_google_auth_url()
        oauth_states[state] = "google"  # 存储状态
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "请访问auth_url进行Google登录授权"
        }
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google登录初始化失败"
        )


@router.get("/github/login")
async def github_login():
    """GitHub OAuth登录 - 重定向到GitHub授权页面"""
    try:
        auth_url, state = oauth_service.get_github_auth_url()
        oauth_states[state] = "github"  # 存储状态
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "请访问auth_url进行GitHub登录授权"
        }
    except Exception as e:
        logger.error(f"GitHub login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub登录初始化失败"
        )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """Google OAuth回调处理"""
    try:
        # 验证状态参数
        if state not in oauth_states or oauth_states[state] != "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态参数"
            )
        
        # 清理状态
        del oauth_states[state]
        
        # 交换授权码获取用户信息
        user_data = await oauth_service.exchange_google_code(code)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google授权失败"
            )
        
        # 处理用户登录/注册
        user_service = UserService(db)
        user = await _handle_oauth_user(user_service, user_data, OAuthProvider.GOOGLE)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户创建或登录失败"
            )
        
        # 生成访问令牌
        token = _create_user_token(user)
        
        return OAuthLoginResponse(
            success=True,
            message="Google登录成功",
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google登录回调处理失败"
        )


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """GitHub OAuth回调处理"""
    try:
        # 验证状态参数
        if state not in oauth_states or oauth_states[state] != "github":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态参数"
            )
        
        # 清理状态
        del oauth_states[state]
        
        # 交换授权码获取用户信息
        user_data = await oauth_service.exchange_github_code(code)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub授权失败"
            )
        
        # 处理用户登录/注册
        user_service = UserService(db)
        user = await _handle_oauth_user(user_service, user_data, OAuthProvider.GITHUB)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户创建或登录失败"
            )
        
        # 生成访问令牌
        token = _create_user_token(user)
        
        return OAuthLoginResponse(
            success=True,
            message="GitHub登录成功",
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub登录回调处理失败"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_user)
):
    """用户登出"""
    # 在实际应用中，这里可以将token加入黑名单
    # 或者使用Redis等存储来管理token状态
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/status")
async def auth_status(
    current_user: UserResponse = Depends(get_current_user)
):
    """检查认证状态"""
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email
    }


async def _handle_oauth_user(user_service: UserService, user_data: Dict, provider: OAuthProvider):
    """处理OAuth用户登录/注册"""
    try:
        # 检查用户是否已存在
        existing_user = user_service.get_user_by_provider(
            provider, 
            user_data["provider_id"]
        )
        
        if existing_user:
            # 用户已存在，更新最后登录时间
            user_service.update_last_login(existing_user.id)
            logger.info(f"User {existing_user.id} logged in via {provider}")
            return existing_user
        else:
            # 创建新用户
            user_create = oauth_service.create_user_from_oauth(user_data, provider)
            new_user = user_service.create_user(user_create)
            
            if new_user:
                user_service.update_last_login(new_user.id)
                logger.info(f"New user {new_user.id} registered via {provider}")
                return new_user
            else:
                logger.error(f"Failed to create user via {provider}")
                return None
                
    except Exception as e:
        logger.error(f"Error handling OAuth user: {str(e)}")
        return None


def _create_user_token(user) -> Token:
    """创建用户访问令牌"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},  # 将user.id转换为字符串
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )