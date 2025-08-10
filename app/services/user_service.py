import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user_model import User
from app.models.auth_schemas import UserCreate, UserUpdate, UserResponse, OAuthProvider
from app.core.database import get_db

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_provider(self, provider: OAuthProvider, provider_id: str) -> Optional[User]:
        """根据OAuth提供商和ID获取用户"""
        return self.db.query(User).filter(
            User.provider == provider,
            User.provider_id == provider_id
        ).first()
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查是否已存在相同的OAuth用户
            existing_user = self.get_user_by_provider(
                user_data.provider, 
                user_data.provider_id
            )
            if existing_user:
                logger.info(f"User already exists with provider {user_data.provider} and ID {user_data.provider_id}")
                return existing_user
            
            # 检查邮箱是否已被使用
            existing_email_user = self.get_user_by_email(user_data.email)
            if existing_email_user:
                # 如果邮箱已存在但是不同的OAuth提供商，可以考虑合并账户或返回错误
                logger.warning(f"Email {user_data.email} already exists with different provider")
                # 这里可以根据业务需求决定是否允许同一邮箱多个OAuth提供商
                return None
            
            # 创建新用户
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                avatar_url=user_data.avatar_url,
                provider=user_data.provider,
                provider_id=user_data.provider_id,
                is_active=user_data.is_active
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Created new user with ID {db_user.id}")
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating user: {str(e)}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # 更新字段
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user with ID {user_id}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """更新用户最后登录时间"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated last login for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deactivated user with ID {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return False
    
    def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Activated user with ID {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating user {user_id}: {str(e)}")
            return False
    
    def to_response_model(self, user: User) -> UserResponse:
        """转换为响应模型"""
        return UserResponse(
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


def get_user_service(db: Session = next(get_db())) -> UserService:
    """获取用户服务实例"""
    return UserService(db)