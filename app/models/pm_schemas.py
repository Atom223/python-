from pydantic import BaseModel, Field
from typing import Literal, Optional

QueryIntentTag = Literal[
    "Pain_Point_Discovery",
    "Competitor_Analysis",
    "Solution_Exploration",
    "Market_Insight",
    "User_Voice_Snapshot",
    "Theoretical_Framework"
]

class UserPortrait(BaseModel):
    """用户画像"""

    description: str = Field(..., description="描述目标用户画像的信息")
    main_tags: list[str] = Field(..., description="核心用户画像的标签，如年龄段、职业等")
    edge_tags: list[str] = Field(..., description="潜在边缘用户画像的标签，如年龄段、职业等")


class QueryRequest(BaseModel):
    original_idea: str
    conversation_id: Optional[str] = None
    debug: bool = False,
    max_plan_iterations: int = 1,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,

class AnswerResponse(BaseModel):
    report: str
    conversation_id: str

