from fastapi import APIRouter

# 创建API路由器
api_router = APIRouter()

# 导入并包含各个端点路由
from app.api.endpoints.pm_analysis import router as pm_analysis_router
from app.api.endpoints.auth import router as auth_router

api_router.include_router(pm_analysis_router, prefix="/pm", tags=["pm research"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])