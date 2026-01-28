from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")


class AskResponse(BaseModel):
    answer: str
    used_tools: bool = False
    tool_name: str | None = None
    tool_input: str | None = None
    tool_output: str | None = None
