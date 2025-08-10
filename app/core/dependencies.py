import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.auth_schemas import UserResponse
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)

# 认证异常
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Inactive user",
)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """获取当前认证用户"""
    if not credentials:
        raise credentials_exception
    
    try:
        # 验证token
        token_data = verify_token(credentials.credentials, credentials_exception)
        
        if not token_data.user_id:
            raise credentials_exception
        
        # 获取用户信息
        user_service = UserService(db)
        user = user_service.get_user_by_id(token_data.user_id)
        
        if not user:
            raise credentials_exception
        
        if not user.is_active:
            raise inactive_user_exception
        
        return user_service.to_response_model(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise credentials_exception


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """获取当前活跃用户（已激活）"""
    if not current_user.is_active:
        raise inactive_user_exception
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    """获取当前用户（可选，不强制认证）"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Error getting optional current user: {str(e)}")
        return None


def require_auth(func):
    """装饰器：要求认证"""
    async def wrapper(*args, **kwargs):
        # 这个装饰器可以用于需要认证的函数
        # 在实际使用中，通常直接使用Depends(get_current_user)
        return await func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """装饰器：要求管理员权限（预留）"""
    async def wrapper(*args, **kwargs):
        # 这里可以添加管理员权限检查逻辑
        # 目前项目中没有角色系统，所以暂时预留
        return await func(*args, **kwargs)
    return wrapper