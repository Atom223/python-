from langgraph.graph import MessagesState
from typing import Literal

from app.agents.prompts.planner_model import Plan
from app.agents.rag import Resource



class PMState(MessagesState):
    """State for the product_manager agent system, extends MessagesState with next field."""

    # Runtime Variables
    locale: str = "en-US"
    original_idea: str = ""
    observations: list[str] = []
    resources: list[Resource] = []
    plan_iterations: int = 0
    current_plan: Plan | str = None
    final_report: str = ""
    auto_accepted_plan: bool = False
    enable_background_investigation: bool = True
    background_investigation_results: str = None
