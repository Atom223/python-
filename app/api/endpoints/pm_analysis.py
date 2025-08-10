import logging
import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from app.models.pm_schemas import QueryRequest, AnswerResponse
from app.services.pm_service import get_idea_report

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analysis", response_model=AnswerResponse)
async def pm_analyze(query: QueryRequest):
    """分析创业想法"""
    try:
        logger.info(f"接收到创业想法分析请求")
        report = await get_idea_report(request=query)
        return report
    except Exception as e:
        logger.error(f"处理创业想法分析请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))