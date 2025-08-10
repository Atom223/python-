from pydantic import BaseModel, Field

class Resource(BaseModel):
    """
        表示一个被检索的资源信息.
    """

    uri: str = Field(..., description="资源URI地址")
    title: str = Field(..., description="资源名称")
    description: str | None = Field(default=None, description="资源的描述信息")


class Query(BaseModel):
    """
        用于查询和检索的问题信息和关联结果
    """
    query: str = Field(..., description="问题内容")
    rationale: str = Field(..., description="问题描述")
    resources: list[Resource] = Field(default_factory=list, description="问题对应的检索答案")