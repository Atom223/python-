import aiohttp
import logging
import uuid

from app.models.pm_schemas import QueryRequest, AnswerResponse
from app.agents.product_manager.builder import build_graph

logger = logging.getLogger(__name__)


graph = build_graph()


async def get_idea_report(request: QueryRequest) -> AnswerResponse:
    """分析创业想法"""
    logger.info(f"接收到创业想法分析请求: {request.original_idea}")

    try:

        convo_id = request.conversation_id or str(uuid.uuid4())
        config = {
            "configurable": {
                "thread_id": convo_id,
                "max_plan_iterations": request.max_plan_iterations,
                "max_step_num": request.max_step_num,
                "mcp_settings": {
                    "servers": {
                        "mcp-github-trending": {
                            "transport": "stdio",
                            "command": "uvx",
                            "args": ["mcp-github-trending"],
                            "enabled_tools": ["get_github_trending_repositories"],
                            "add_to_agents": ["researcher"],
                        }
                    }
                },
            },
            "recursion_limit": 100,
        }

        initial_state = {
            # Runtime Variables
            "messages": [{"role": "user", "content": request.original_idea}],
            "auto_accepted_plan": True,
            "enable_background_investigation": request.enable_background_investigation,
        }

        # 调用Agent Chain进行分析
        result = await graph.ainvoke(input=initial_state,
                                     config=config)
        report = result["messages"][-1].content
        logger.info(f"创业想法分析完成")
        return AnswerResponse(
            report=report,
            conversation_id=convo_id
        )
    except Exception as e:
        logger.error(f"创业想法分析失败: {str(e)}")
        return AnswerResponse(
            report={"error": str(e)},
            conversation_id=request.conversation_id or "unknown"
        )